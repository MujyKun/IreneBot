from module import keys, logger as log, cache, exceptions
from discord.ext import tasks
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from datadog import initialize, api
from Weverse.weverseasync import WeverseAsync
import datetime
import discord
import random
import asyncio
import os
import math
import tweepy
import json
import time
import sys
import aiofiles
import re
import pytz
import parsedatetime

"""
Utility.py
Resource Center for Irene -> Essentially serves as a client for Irene.
Any potentially useful/repeated functions will end up here
"""


class Utility:
    def __init__(self):
        self.test_bot = None  # this is changed in run.py
        self.client = keys.client
        self.session = keys.client_session
        self.conn = None  # db connection
        self.discord_cache_loaded = False
        self.cache = cache.Cache()
        self.temp_patrons_loaded = False
        self.running_loop = None  # current asyncio running loop
        self.thread_pool = None  # ThreadPoolExecutor for operations that block the event loop.
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.loop_count = 0
        self.recursion_limit = 10000
        self.api_issues = 0
        self.weverse_client = WeverseAsync(authorization=keys.weverse_auth_token, web_session=self.session,
                                           verbose=True, loop=asyncio.get_event_loop())
        self.exceptions = exceptions

    ##################
    # ## DATABASE ## #
    ##################
    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def set_start_up_connection(self):
        """Looping Until A Stable Connection to DB is formed. This is to confirm Irene starts before the DB connects.
        Also creates thread pool and increases recursion limit.
        """
        if self.client.loop.is_running():
            try:
                self.conn = await self.get_db_connection()
                # Delete all active blackjack games
                await self.delete_all_games()
                self.running_loop = asyncio.get_running_loop()
                await self.create_thread_pool()
                sys.setrecursionlimit(self.recursion_limit)
            except Exception as e:
                log.console(e)
            self.set_start_up_connection.stop()

    async def create_thread_pool(self):
        self.thread_pool = ThreadPoolExecutor()

    @tasks.loop(seconds=0, minutes=1, reconnect=True)
    async def show_irene_alive(self):
        """Looped every minute to send a connection to localhost:5123 to show bot is working well."""
        source_link = "http://127.0.0.1:5123/restartBot"
        async with self.session.get(source_link) as resp:
            pass

    @staticmethod
    async def get_db_connection():
        """Retrieve Database Connection"""
        return await keys.connect_to_db()

    @staticmethod
    def first_result(record):
        """Returns the first item of a record if there is one."""
        if record is None:
            return None
        else:
            return record[0]

    ###############
    # ## CACHE ## #
    ###############
    async def process_cache_time(self, method, name):
        """Process the cache time."""
        past_time = time.time()
        result = await method()
        if result is None or result is True:
            log.console(f"Cache for {name} Created in {await self.get_cooldown_time(time.time() - past_time)}.")
        return result

    async def create_cache(self):
        """Create the general cache on startup"""
        past_time = time.time()
        await self.process_cache_time(self.update_idols, "Idol Photo Count")
        await self.process_cache_time(self.update_groups, "Group Photo Count")
        await self.process_cache_time(self.update_user_notifications, "User Notifications")
        # after intents was pushed in place, d.py cache loaded a lot slower and patrons are not added properly.
        # therefore it must be looped instead.
        # await self.process_cache_time(self.update_patreons, "Patrons")
        await self.process_cache_time(self.update_mod_mail, "ModMail")
        await self.process_cache_time(self.update_bot_bans, "Bot Bans")
        await self.process_cache_time(self.update_logging_channels, "Logged Channels")
        await self.process_cache_time(self.update_server_prefixes, "Server Prefixes")
        await self.process_cache_time(self.update_welcome_message_cache, "Welcome Messages")
        await self.process_cache_time(self.update_temp_channels, "Temp Channels")
        await self.process_cache_time(self.update_n_word_counter, "NWord Counter")
        await self.process_cache_time(self.update_command_counter, "Command Counter")
        await self.process_cache_time(self.create_idol_cache, "Idol Objects")
        await self.process_cache_time(self.create_group_cache, "Group Objects")
        await self.process_cache_time(self.create_restricted_channel_cache, "Restricted Idol Channels")
        await self.process_cache_time(self.create_dead_link_cache, "Dead Links")
        await self.process_cache_time(self.create_bot_status_cache, "Bot Status")
        await self.process_cache_time(self.create_bot_command_cache, "Custom Commands")
        await self.process_cache_time(self.create_weverse_channel_cache, "Weverse Text Channels")
        await self.process_cache_time(self.create_self_assignable_role_cache, "Self-Assignable Roles")
        await self.process_cache_time(self.create_reminder_cache, "Reminders")
        await self.process_cache_time(self.create_timezone_cache, "Timezones")
        if not self.test_bot:
            task = asyncio.create_task(self.process_cache_time(self.weverse_client.start, "Weverse"))
        log.console(f"Cache Completely Created in {await self.get_cooldown_time(time.time() - past_time)}.")

    async def create_timezone_cache(self):
        self.cache.timezones = {}  # reset cache
        timezones = await self.get_all_timezones_from_db()
        for timezone_info in timezones:
            user_id = timezone_info[0]
            timezone = timezone_info[1]
            self.cache.timezones[user_id] = timezone

    async def create_reminder_cache(self):
        """Create cache for reminders"""
        self.cache.reminders = {}  # reset cache
        all_reminders = await self.get_all_reminders_from_db()
        for reminder_info in all_reminders:
            reason_id = reminder_info[0]
            user_id = reminder_info[1]
            reason = reminder_info[2]
            time_stamp = reminder_info[3]
            reason_list = [reason_id, reason, time_stamp]
            user_reminder = self.cache.reminders.get(user_id)
            if user_reminder:
                user_reminder.append(reason_list)
            else:
                self.cache.reminders[user_id] = [reason_list]

    async def create_self_assignable_role_cache(self):
        """Create cache for self assignable roles"""
        all_roles = await self.conn.fetch("SELECT roleid, rolename, serverid FROM selfassignroles.roles")
        all_channels = await self.conn.fetch("SELECT channelid, serverid FROM selfassignroles.channels")
        for role in all_roles:
            role_id = role[0]
            role_name = role[1]
            server_id = role[2]
            cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info:
                self.cache.assignable_roles[server_id] = {}
                cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info.get('roles'):
                cache_info['roles'] = [[role_id, role_name]]
            else:
                cache_info['roles'].append([role_id, role_name])
        for channel in all_channels:
            channel_id = channel[0]
            server_id = channel[1]
            cache_info = self.cache.assignable_roles.get(server_id)
            if cache_info:
                cache_info['channel_id'] = channel_id
            else:
                self.cache.assignable_roles[server_id] = {'channel_id': channel_id}

    async def create_weverse_channel_cache(self):
        """Create cache for channels that are following a community on weverse."""
        all_channels = await self.conn.fetch("SELECT channelid, communityname, roleid, commentsdisabled FROM weverse.channels")
        for channel in all_channels:
            channel_id = channel[0]
            community_name = channel[1]
            role_id = channel[2]
            comments_disabled = channel[3]
            await self.add_weverse_channel_to_cache(channel_id, community_name)
            await self.add_weverse_role(channel_id, community_name, role_id)
            await self.change_weverse_comment_status(channel_id, community_name, comments_disabled)

    async def update_command_counter(self):
        """Updates Cache for command counter and sessions"""
        self.cache.command_counter = {}
        session_id = await self.get_session_id()
        all_commands = await self.conn.fetch("SELECT commandname, count FROM stats.commands WHERE sessionid = $1", session_id)
        for command in all_commands:
            self.cache.command_counter[command[0]] = command[1]
        self.cache.current_session = self.first_result(
            await self.conn.fetchrow("SELECT session FROM stats.sessions WHERE date = $1", datetime.date.today()))

    async def create_restricted_channel_cache(self):
        """Create restricted idol channel cache"""
        restricted_channels = await self.conn.fetch("SELECT channelid, serverid, sendhere FROM groupmembers.restricted")
        for restricted_channel in restricted_channels:
            self.cache.restricted_channels[restricted_channel[0]] = [restricted_channel[1], restricted_channel[2]]

    async def create_bot_command_cache(self):
        """Create custom command cache"""
        server_commands = await self.conn.fetch("SELECT serverid, commandname, message FROM general.customcommands")
        self.cache.custom_commands = {}
        for server_command in server_commands:
            server_id = server_command[0]
            command_name = server_command[1]
            message = server_command[2]
            cache_info = self.cache.custom_commands.get(server_id)
            if cache_info:
                cache_info[command_name] = message
            else:
                self.cache.custom_commands[server_id] = {command_name: message}

    async def create_bot_status_cache(self):
        statuses = await self.conn.fetch("SELECT status FROM general.botstatus")
        self.cache.bot_statuses = [status[0] for status in statuses] or None

    async def create_dead_link_cache(self):
        """Creates Dead Link Cache"""
        self.cache.dead_image_cache = {}
        try:
            self.cache.dead_image_channel = await self.client.fetch_channel(keys.dead_image_channel_id)
        except:
            pass
        dead_images = await self.conn.fetch("SELECT deadlink, userid, messageid, idolid, guessinggame FROM groupmembers.deadlinkfromuser")
        for dead_image in dead_images:
            self.cache.dead_image_cache[dead_image[2]] = [dead_image[0], dead_image[1], dead_image[3], dead_image[4]]

    async def create_idol_cache(self):
        """Create Idol Objects and store them as cache."""
        self.cache.idols = []
        for idol in await self.get_db_all_members():
            idol_obj = Idol(**idol)
            idol_obj.aliases, idol_obj.local_aliases = await self.get_db_aliases(idol_obj.id)
            # add all group ids and remove potential duplicates
            idol_obj.groups = list(dict.fromkeys(await self.get_db_groups_from_member(idol_obj.id)))
            idol_obj.called = await self.get_db_idol_called(idol_obj.id)
            idol_obj.photo_count = self.cache.idol_photos.get(idol_obj.id) or 0
            self.cache.idols.append(idol_obj)

    async def create_group_cache(self):
        """Create Group Objects and store them as cache"""
        self.cache.groups = []
        for group in await self.get_all_groups():
            group_obj = Group(**group)
            group_obj.aliases, group_obj.local_aliases = await self.get_db_aliases(group_obj.id, group=True)
            # add all idol ids and remove potential duplicates
            group_obj.members = list(dict.fromkeys(await self.get_db_members_in_group(group_id=group_obj.id)))
            group_obj.photo_count = self.cache.group_photos.get(group_obj.id) or 0
            self.cache.groups.append(group_obj)

    async def process_session(self):
        """Sets the new session id, total used, and time format for distinguishing days."""
        current_time_format = datetime.date.today()
        if self.cache.session_id is None:
            if self.cache.total_used is None:
                self.cache.total_used = (self.first_result(await self.conn.fetchrow("SELECT totalused FROM stats.sessions ORDER BY totalused DESC"))) or 0
            try:
                await self.conn.execute("INSERT INTO stats.sessions(totalused, session, date) VALUES ($1, $2, $3)", self.cache.total_used, 0, current_time_format)
            except Exception as e:
                # session for today already exists.
                pass
            self.cache.session_id = self.first_result(await self.conn.fetchrow("SELECT sessionid FROM stats.sessions WHERE date = $1", current_time_format))
            self.cache.session_time_format = current_time_format
        else:
            # check that the date is correct, and if not, call get_session_id to get the new session id.
            if current_time_format != self.cache.session_time_format:
                self.cache.current_session = 0
                self.cache.session_id = None
                self.cache.session_id = await self.get_session_id()

    async def get_session_id(self):
        """Force get the session id, this will also set total used and the session id."""
        await self.process_session()
        return self.cache.session_id

    async def update_n_word_counter(self):
        """Update NWord Cache"""
        self.cache.n_word_counter = {}
        user_info = await self.conn.fetch("SELECT userid, nword FROM general.nword")
        for user in user_info:
            self.cache.n_word_counter[user[0]] = user[1]

    async def update_temp_channels(self):
        """Create the cache for temp channels."""
        self.cache.temp_channels = {}
        channels = await self.get_temp_channels()
        for channel in channels:
            removal_time = channel[1]
            if removal_time < 60:
                removal_time = 60
            self.cache.temp_channels[channel[0]] = removal_time

    async def update_welcome_message_cache(self):
        """Create the cache for welcome messages."""
        self.cache.welcome_messages = {}
        info = await self.conn.fetch("SELECT channelid, serverid, message, enabled FROM general.welcome")
        for server in info:
            self.cache.welcome_messages[server[1]] = {"channel_id": server[0], "message": server[2], "enabled": server[3]}

    async def update_server_prefixes(self):
        """Create the cache for server prefixes."""
        self.cache.server_prefixes = {}
        info = await self.conn.fetch("SELECT serverid, prefix FROM general.serverprefix")
        for server in info:
            self.cache.server_prefixes[server[0]] = server[1]

    async def update_logging_channels(self):
        """Create the cache for logged servers and channels."""
        self.cache.logged_channels = {}
        self.cache.list_of_logged_channels = []
        logged_servers = await self.conn.fetch("SELECT id, serverid, channelid, sendall FROM logging.servers WHERE status = $1", 1)
        for logged_server in logged_servers:
            channels = await self.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1", logged_server[0])
            for channel in channels:
                self.cache.list_of_logged_channels.append(channel[0])
            self.cache.logged_channels[logged_server[1]] = {
                "send_all": logged_server[3],
                "logging_channel": logged_server[2],
                "channels": [channel[0] for channel in channels]
            }

    async def update_bot_bans(self):
        """Create the cache for banned users from the bot."""
        self.cache.bot_banned = []
        banned_users = await self.conn.fetch("SELECT userid FROM general.blacklisted")
        for user in banned_users:
            user_id = user[0]
            self.cache.bot_banned.append(user_id)

    async def update_mod_mail(self):
        """Create the cache for existing mod mail"""
        self.cache.mod_mail = {}
        mod_mail = await self.conn.fetch("SELECT userid, channelid FROM general.modmail")
        for mail in mod_mail:
            user_id = mail[0]
            channel_id = mail[1]
            self.cache.mod_mail[user_id] = [channel_id]

    async def update_patreons(self):
        """Create the cache for Patrons."""
        try:
            self.cache.patrons = {}
            permanent_patrons = await self.get_patreon_users()
            # normal patrons contains super patrons as well
            normal_patrons = [patron.id for patron in await self.get_patreon_role_members(super=False)]
            super_patrons = [patron.id for patron in await self.get_patreon_role_members(super=True)]

            # the reason for db cache is because of the new discord rate limit
            # where it now takes 20+ minutes for discord cache to fully load, meaning we can only
            # access the roles after 20 minutes on boot.
            # this is an alternative to get patreons instantly and later modifying the cache after the cache loads.
            # remove any patrons from db set cache that should not exist or should be modified.
            cached_patrons = await self.conn.fetch("SELECT userid, super FROM patreon.cache")
            for patron in cached_patrons:
                if patron[0] not in normal_patrons:
                    # they are not a patron at all, so remove them from db cache
                    await self.conn.execute("DELETE FROM patreon.cache WHERE userid = $1", patron[0])
                elif patron[0] in super_patrons and patron[1] == 0:
                    # if they are a super patron but their db is cache is a normal patron
                    await self.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 1, patron[0])
                elif patron[0] not in super_patrons and patron[1] == 1:
                    # if they are not a super patron, but the db cache says they are.
                    await self.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 0, patron[0])
            cached_patrons = [patron[0] for patron in cached_patrons]  # list of user ids removing patron status.

            # fix db cache and live Irene cache
            for patron in normal_patrons:
                if patron not in cached_patrons:
                    # patron includes both normal and super patrons.
                    await self.conn.execute("INSERT INTO patreon.cache(userid, super) VALUES($1, $2)", patron, 0)
                self.cache.patrons[patron] = False
            # super patrons must go after normal patrons to have a proper boolean set because
            # super patrons have both roles.
            for patron in super_patrons:
                if patron not in cached_patrons:
                    await self.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 1, patron)
                self.cache.patrons[patron] = True
            for patron in permanent_patrons:
                self.cache.patrons[patron[0]] = True
            return True
        except Exception as e:
            return False

    async def update_user_notifications(self):
        """Set the cache for user phrases"""
        self.cache.user_notifications = []
        notifications = await self.conn.fetch("SELECT guildid,userid,phrase FROM general.notifications")
        for notification in notifications:
            guild_id = notification[0]
            user_id = notification[1]
            phrase = notification[2]
            self.cache.user_notifications.append([guild_id, user_id, phrase])

    async def update_groups(self):
        """Set cache for group photo count"""
        self.cache.group_photos = {}
        all_group_counts = await self.conn.fetch("SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id GROUP BY g.groupid ORDER BY g.groupname")
        for group in all_group_counts:
            self.cache.group_photos[group[0]] = group[2]

    async def update_idols(self):
        """Set cache for idol photo count"""
        self.cache.idol_photos = {}
        all_idol_counts = await self.conn.fetch("SELECT memberid, COUNT(link) FROM groupmembers.imagelinks GROUP BY memberid")
        for idol in all_idol_counts:
            self.cache.idol_photos[idol[0]] = idol[1]

    @tasks.loop(seconds=0, minutes=0, hours=12, reconnect=True)
    async def update_cache(self):
        """Looped every 12 hours to update the cache in case of anything faulty."""
        while self.conn is None:
            await asyncio.sleep(1)
        await self.create_cache()

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def update_patron_cache(self):
        """Looped until patron cache is loaded.
        This was added due to intents slowing d.py cache loading rate.
        """
        # create a temporary patron list based on the db cache while waiting for the discord cache to load
        if self.conn is not None:
            if not self.temp_patrons_loaded:
                self.cache.patrons = {}
                cached_patrons = await self.conn.fetch("SELECT userid, super FROM patreon.cache")
                for patron in cached_patrons:
                    self.cache.patrons[patron[0]] = bool(patron[1])
                self.temp_patrons_loaded = True
            while not self.discord_cache_loaded:
                await asyncio.sleep(1)
            if await self.process_cache_time(self.update_patreons, "Patrons"):
                self.update_patron_cache_hour.start()
                self.update_patron_cache.stop()

    @tasks.loop(seconds=0, minutes=0, hours=1, reconnect=True)
    async def update_patron_cache_hour(self):
        """Update Patron Cache every hour in the case of unaccounted errors."""
        # this is to make sure on the first run it doesn't update since it is created elsewhere.
        if self.loop_count != 0:
            await self.process_cache_time(self.update_patreons, "Patrons")
        self.loop_count += 1

    @tasks.loop(seconds=0, minutes=1, hours=0, reconnect=True)
    async def send_cache_data_to_data_dog(self):
        """Sends metric information about cache to data dog every minute."""
        if self.thread_pool:
            active_user_reminders = 0
            for user_id in self.cache.reminders:
                reminders = self.cache.reminders.get(user_id)
                if reminders:
                    active_user_reminders += len(reminders)
            metric_info = {
                'total_commands_used': self.cache.total_used,
                'bias_games': len(self.cache.bias_games),
                'guessing_games': len(self.cache.guessing_games),
                'patrons': len(self.cache.patrons),
                'custom_server_prefixes': len(self.cache.server_prefixes),
                'session_commands_used': self.cache.current_session,
                'user_notifications': len(self.cache.user_notifications),
                'mod_mail': len(self.cache.mod_mail),
                'banned_from_bot': len(self.cache.bot_banned),
                'logged_servers': len(self.cache.logged_channels),
                # server count is based on discord.py guild cache which takes a large amount of time to load fully.
                # There may be inaccurate data points on a new instance of the bot due to the amount of time it takes.
                'server_count': len(self.client.guilds),
                'welcome_messages': len(self.cache.welcome_messages),
                'temp_channels': len(self.cache.temp_channels),
                'amount_of_idols': len(self.cache.idols),
                'amount_of_groups': len(self.cache.groups),
                'channels_restricted': len(self.cache.restricted_channels),
                'amount_of_bot_statuses': len(self.cache.bot_statuses),
                'commands_per_minute': self.cache.commands_per_minute,
                'amount_of_custom_commands': len(self.cache.custom_commands),
                'discord_ping': self.get_ping(),
                'n_words_per_minute': self.cache.n_words_per_minute,
                'bot_api_idol_calls': self.cache.bot_api_idol_calls,
                'bot_api_translation_calls': self.cache.bot_api_translation_calls,
                'messages_received_per_min': self.cache.messages_received_per_minute,
                'errors_per_minute': self.cache.errors_per_minute,
                'wolfram_per_minute': self.cache.wolfram_per_minute,
                'urban_per_minute': self.cache.urban_per_minute,
                'active_user_reminders': active_user_reminders
            }

            # set all per minute metrics to 0 since this is a 60 second loop.
            self.cache.n_words_per_minute = 0
            self.cache.commands_per_minute = 0
            self.cache.bot_api_idol_calls = 0
            self.cache.bot_api_translation_calls = 0
            self.cache.messages_received_per_minute = 0
            self.cache.errors_per_minute = 0
            self.cache.wolfram_per_minute = 0
            self.cache.urban_per_minute = 0
            for metric_name in metric_info:
                metric_value = metric_info.get(metric_name)
                # add to thread pool to prevent blocking.
                result = (self.thread_pool.submit(self.send_metric, metric_name, metric_value)).result()

    ##################
    # ## CURRENCY ## #
    ##################

    async def register_user(self, user_id):
        """Register a user to the database if they are not already registered."""
        count = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM currency.Currency WHERE UserID = $1", user_id))
        if count == 0:
            await self.conn.execute("INSERT INTO currency.Currency (UserID, Money) VALUES ($1, $2)", user_id, "100")
            return True
        elif count == 1:
            return False

    async def get_user_has_money(self, user_id):
        """Check if a user has money."""
        return not self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM currency.Currency WHERE UserID = $1", user_id)) == 0

    async def get_balance(self, user_id):
        """Get current balance of a user."""
        if not (await self.register_user(user_id)):
            money = await self.conn.fetchrow("SELECT money FROM currency.currency WHERE userid = $1", user_id)
            return int(self.first_result(money))
        else:
            return 100

    @staticmethod
    async def shorten_balance(money):  # money must be passed in as a string.
        """Shorten an amount of money to it's value places."""
        place_names = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion', 'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quatturodecillion', 'Quindecillion', 'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion', 'Centillion']
        try:
            place_values = int(math.log10(int(money)) // 3)
        except Exception as e:
            # This will have a math domain error when the amount of balance is 0.
            return "0"
        try:
            return f"{int(money) // (10 ** (3 * place_values))} {place_names[place_values]}"
        except Exception as e:
            return "Too Fucking Much$"

    async def update_balance(self, user_id, new_balance):
        """Update a user's balance."""
        await self.conn.execute("UPDATE currency.Currency SET Money = $1::text WHERE UserID = $2", str(new_balance), user_id)

    @staticmethod
    async def get_robbed_amount(author_money, user_money, level):
        """The amount to rob a specific person based on their rob level."""
        max_amount = int(user_money // 100)  # b value
        if max_amount > int(author_money // 2):
            max_amount = int(author_money // 2)
        min_amount = int((max_amount * level) // 100)
        if min_amount > max_amount:  # kind of ironic, but it is possible for min to surpass max in this case
            robbed_amount = random.randint(max_amount, min_amount)
        else:
            robbed_amount = random.randint(min_amount, max_amount)
        return robbed_amount

    @staticmethod
    def remove_commas(amount):
        """Remove all commas from a string and make it an integer."""
        return int(amount.replace(',', ''))

    #######################
    # ## MISCELLANEOUS ## #
    #######################
    async def kill_api(self):
        """restart the api"""
        source_link = "http://127.0.0.1:5123/restartAPI"
        async with self.session.get(source_link) as resp:
            log.console("Restarting API.")

    async def get_number_of_emojis(self, emojis, animated=False):
        not_animated_emojis = []
        animated_emojis = []
        for emoji in emojis:
            if emoji.animated:
                animated_emojis.append(emoji)
            else:
                not_animated_emojis.append(emoji)
        return len(animated_emojis) if animated else len(not_animated_emojis)

    @staticmethod
    async def get_server_id(ctx):
        """Get the server id by context."""
        if ctx.guild:
            return ctx.guild.id  # this line would error with the function as one line since ctx.guild may not exist.

    async def check_if_moderator(self, ctx):
        """Check if a user is a moderator on a server"""
        return (ctx.author.permissions_in(ctx.channel)).manage_messages

    async def check_for_bot_mentions(self, message):
        """Returns true if the message is only a bot mention and nothing else."""
        return message.content == f"<@!{keys.bot_id}>"

    async def get_api_status(self):
        end_point = f"http://127.0.0.1:{keys.api_port}"
        try:
            async with self.session.get(end_point) as r:
                return r.status == 200
        except Exception as e:
            pass
        return False

    async def get_db_status(self):
        end_point = f"http://127.0.0.1:{5050}"
        try:
            async with self.session.get(end_point) as r:
                return r.status == 200

        except Exception as e:
            pass
        return False

    async def get_images_status(self):
        end_point = f"http://images.irenebot.com/index.html"
        try:
            async with self.session.get(end_point) as r:
                return r.status == 200
        except Exception as e:
            pass
        return False

    async def send_maintenance_message(self, channel):
        try:
            reason = ""
            if self.cache.maintenance_reason:
                reason = f"\nREASON: {self.cache.maintenance_reason}"
            await channel.send(
                f">>> **A maintenance is currently in progress. Join the support server for more information. <{keys.bot_support_server_link}>{reason}**")
        except Exception as e:
            pass

    async def process_commands(self, message):
        message_sender = message.author
        if not message_sender.bot:
            message_content = message.clean_content
            message_channel = message.channel
            server_prefix = await self.get_server_prefix_by_context(message)
            # check if the user mentioned the bot and send them a help message.
            if await self.check_for_bot_mentions(message):
                await message.channel.send(
                    f"Type `{server_prefix}help` for information on commands.")
            if len(message_content) >= len(server_prefix):
                changing_prefix = [keys.bot_prefix + 'setprefix', keys.bot_prefix + 'checkprefix']
                if message.content[0:len(server_prefix)].lower() == server_prefix.lower() or message.content.lower() in changing_prefix:
                    msg_without_prefix = message.content[len(server_prefix):len(message.content)]
                    # only replace the prefix portion back to the default prefix if it is not %setprefix or %checkprefix
                    if message.content.lower() not in changing_prefix:
                        # change message.content so all on_message listeners have a bot prefix
                        message.content = keys.bot_prefix + msg_without_prefix
                    # if a user is banned from the bot.
                    if await self.check_if_bot_banned(message_sender.id):
                        try:
                            guild_id = await self.get_guild_id(message)
                        except Exception as e:
                            guild_id = None
                        if await self.check_message_is_command(message) or await self.check_custom_command_name_exists(guild_id, msg_without_prefix):
                            await self.send_ban_message(message_channel)
                    else:
                        await self.client.process_commands(message)

    async def get_guild_id(self, message):
        try:
            guild_id = message.guild.id
        except Exception as e:
            guild_id = None
        return guild_id

    async def check_for_nword(self, message):
        """Processes new messages that contains the N word."""
        message_sender = message.author
        if not message_sender.bot:
            message_content = message.clean_content
            if self.check_message_not_empty(message):
                # check if the message belongs to the bot
                    if message_content[0] != '%':
                        if self.check_nword(message_content):
                            self.cache.n_words_per_minute += 1
                            author_id = message_sender.id
                            current_amount = self.cache.n_word_counter.get(author_id)
                            if current_amount is not None:
                                await self.conn.execute("UPDATE general.nword SET nword = $1 WHERE userid = $2::bigint",
                                                        current_amount + 1, author_id)
                                self.cache.n_word_counter[author_id] = current_amount + 1
                            else:
                                await self.conn.execute("INSERT INTO general.nword VALUES ($1,$2)", author_id, 1)
                                self.cache.n_word_counter[author_id] = 1

    async def get_dm_channel(self, user_id=None, user=None):
        try:
            if user_id is not None:
                # user = await self.client.fetch_user(user_id)
                user = self.client.get_user(user_id)
            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel
            return dm_channel
        except discord.errors.HTTPException as e:
            log.console(f"{e} - get_dm_channel 1")
            return None
        except Exception as e:
            log.console(f"{e} - get_dm_channel 2")
            return None

    async def check_if_temp_channel(self, channel_id):
        """Check if a channel is a temp channel"""
        return self.cache.temp_channels.get(channel_id) is not None

    async def get_temp_channels(self):
        """Get all temporary channels in the DB."""
        return await self.conn.fetch("SELECT chanID, delay FROM general.TempChannels")

    async def delete_temp_messages(self, message):
        """Delete messages that are temp channels"""
        if await self.check_if_temp_channel(message.channel.id):
            await message.delete(delay=self.cache.temp_channels.get(message.channel.id))

    async def get_disabled_server_interactions(self, server_id):
        """Get a server's disabled interactions."""
        interactions = await self.conn.fetchrow("SELECT interactions FROM general.disabledinteractions WHERE serverid = $1", server_id)
        return self.first_result(interactions)

    @staticmethod
    async def check_interaction_enabled(ctx=None, server_id=None, interaction=None):
        """Check if the interaction is disabled in the current server, RETURNS False when it is disabled."""
        if server_id is None and interaction is None:
            server_id = await Utility.get_server_id(ctx)
            interaction = ctx.command.name
        interactions = await resources.get_disabled_server_interactions(server_id)
        if interactions is None:
            return True
        interaction_list = interactions.split(',')
        if interaction in interaction_list:
            # normally we would alert the user that the command is disabled, but discord.py uses this function.
            return False
        return True

    async def disable_interaction(self, server_id, interaction):
        """Disable an interaction (to a specific server)"""
        interaction = interaction.lower()
        interactions = await self.get_disabled_server_interactions(server_id)
        if interactions is None:
            await self.conn.execute("INSERT INTO general.disabledinteractions(serverid, interactions) VALUES ($1, $2)", server_id, interaction)
        else:
            interactions = interactions.split(',')
            interactions.append(interaction)
            interactions = ','.join(interactions)
            await self.conn.execute("UPDATE general.disabledinteractions SET interactions = $1 WHERE serverid = $2", interactions, server_id)

    async def enable_interaction(self, server_id, interaction):
        """Reenable an interaction that was disabled by a server"""
        interactions = await self.get_disabled_server_interactions(server_id)
        if interactions is None:
            return
        else:
            interactions = interactions.split(',')
            interactions.remove(interaction)
            interactions = ','.join(interactions)
            if len(interactions) == 0:
                return await self.conn.execute("DELETE FROM general.disabledinteractions WHERE serverid = $1", server_id)
            await self.conn.execute("UPDATE general.disabledinteractions SET interactions = $1 WHERE serverid = $2", interactions, server_id)

    async def interact_with_user(self, ctx, user, interaction, interaction_type, self_interaction=False):
        await self.reset_patreon_cooldown(ctx)
        try:
            if user == discord.Member:
                user = ctx.author
            list_of_links = await self.conn.fetch("SELECT url FROM general.interactions WHERE interaction = $1", interaction_type)
            if not self_interaction:
                if ctx.author.id == user.id:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send(f"> **{ctx.author.display_name}, you cannot perform this interaction on yourself.**")
            link = random.choice(list_of_links)
            embed = discord.Embed(title=f"**{ctx.author.display_name}** {interaction} **{user.display_name}**", color=self.get_random_color())
            if not await self.check_if_patreon(ctx.author.id):
                embed.set_footer(text=f"Become a {await self.get_server_prefix_by_context(ctx)}patreon to get rid of interaction cooldowns!")
            embed.set_image(url=link[0])
            return await ctx.send(embed=embed)
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> **{ctx.author.display_name}, there are no links saved for this interaction yet.**")

    async def add_command_count(self, command_name):
        """Add 1 to the specific command count and to the count of the current minute."""
        self.cache.commands_per_minute += 1
        session_id = await self.get_session_id()
        command_count = self.cache.command_counter.get(command_name)
        if command_count is None:
            await self.conn.execute("INSERT INTO stats.commands(sessionid, commandname, count) VALUES($1, $2, $3)", session_id, command_name, 1)
            self.cache.command_counter[command_name] = 1
        else:
            await self.conn.execute("UPDATE stats.commands SET count = $1 WHERE commandname = $2 AND sessionid = $3", command_count + 1, command_name, session_id)
            self.cache.command_counter[command_name] += 1

    async def add_session_count(self):
        """Adds one to the current session count for commands used and for the total used."""
        session_id = await self.get_session_id()
        self.cache.current_session += 1
        self.cache.total_used += 1
        await self.conn.execute("UPDATE stats.sessions SET session = $1, totalused = $2 WHERE sessionid = $3", self.cache.current_session, self.cache.total_used, session_id)

    async def check_message_is_command(self, message, is_command_name=False):
        """Check if a message is a command."""
        if not is_command_name:
            for command_name in self.client.all_commands:
                if command_name in message.content:
                    if len(command_name) != 1:
                        return True
            return False
        if is_command_name:
            return message in self.client.all_commands

    @staticmethod
    async def send_ban_message(channel):
        """A message to send for a user that is banned from the bot."""
        await channel.send(
            f"> **You are banned from using {keys.bot_name}. Join <{keys.bot_support_server_link}>**")

    async def ban_user_from_bot(self, user_id):
        """Bans a user from using the bot."""
        await self.conn.execute("INSERT INTO general.blacklisted(userid) VALUES ($1)", user_id)
        self.cache.bot_banned.append(user_id)

    async def unban_user_from_bot(self, user_id):
        """UnBans a user from the bot."""
        await self.conn.execute("DELETE FROM general.blacklisted WHERE userid = $1", user_id)
        try:
            self.cache.bot_banned.remove(user_id)
        except Exception as e:
            pass

    async def check_if_bot_banned(self, user_id):
        """Check if the user can use the bot."""
        return user_id in self.cache.bot_banned

    @staticmethod
    def check_nword(message_content):
        """Check if a message contains the NWord."""
        message_split = message_content.lower().split()
        return 'nigga' in message_split or 'nigger' in message_split and ':' not in message_split

    @staticmethod
    def check_if_mod(ctx, mode=0):  # as mode = 1, ctx is the author id.
        """Check if the user is a bot mod/owner."""
        if mode == 0:
            user_id = ctx.author.id
            return user_id in keys.mods_list or user_id == keys.owner_id
        else:
            return ctx in keys.mods_list or ctx == keys.owner_id

    def get_ping(self):
        """Get the client's ping."""
        return int(self.client.latency * 1000)

    @staticmethod
    def get_int_index(original, index):
        """Retrieves the specific index of an integer. Ex: Calling index 0 for integer 51 will return 5."""
        entire_selection = ""
        counter = 0
        for value in str(original):
            if counter < index:
              entire_selection += value
            counter += 1
        return int(entire_selection)

    @staticmethod
    def get_random_color():
        """Retrieves a random hex color."""
        r = lambda: random.randint(0, 255)
        return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present

    async def create_embed(self, title="Irene", color=None, title_desc=None, footer_desc="Thanks for using Irene!"):
        """Create a discord Embed."""
        if color is None:
            color = self.get_random_color()
        if title_desc is None:
            embed = discord.Embed(title=title, color=color)
        else:
            embed = discord.Embed(title=title, color=color, description=title_desc)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def check_reaction(self, msg, user_id, reaction_needed):
        """Wait for a user's reaction on a message."""
        def react_check(reaction_used, user_reacted):
            return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=react_check)
            return True
        except asyncio.TimeoutError:
            await msg.delete()
            return False

    @staticmethod
    async def get_cooldown_time(time):
        """Turn command cooldown of seconds into hours, minutes, and seconds."""
        time = round(time)
        time_returned = ""
        if time < 1:
            return (f"{time}s")
        if time % 86400 != time:
            days = int(time//86400)
            if days != 0:
                time = time-(days*86400)
                time_returned += f"{days}d "
        if time % 3600 != time:
            hours = int(time//3600)
            if hours != 0:
                time_returned += f"{hours}h "
        if time % 3600 != 0:
            minutes = int((time % 3600) // 60)
            if minutes != 0:
                time_returned += f"{minutes}m "
        if (time % 3600) % 60 < 60:
            seconds = (time % 3600) % 60
            if seconds != 0:
                time_returned += f"{seconds}s"
        return time_returned

    @staticmethod
    def check_embed_exists(message):
        """Check if a message has embeds."""
        try:
            for embed_check in message.embeds:
                if len(embed_check) > 0:
                    return True
        except Exception as e:
            pass
        return False

    @staticmethod
    def check_message_not_empty(message):
        """Check if a message has content."""
        try:
            if len(message.clean_content) >= 1:
                return True
        except Exception as e:
            pass
        return False

    def get_message_prefix(self, message):
        """Get the prefix of a message."""
        try:
            if self.check_message_not_empty(message):
                return message.clean_content[0]
        except Exception as e:
            pass
        return None

    async def check_left_or_right_reaction_embed(self, msg, embed_lists, original_page_number=0, reaction1=keys.previous_emoji, reaction2=keys.next_emoji):
        """This method is used for going between pages of embeds."""
        await msg.add_reaction(reaction1)  # left arrow by default
        await msg.add_reaction(reaction2)  # right arrow by default

        def reaction_check(user_reaction, reaction_user):
            """Check if the reaction is the right emoji and right user."""
            return ((user_reaction.emoji == '➡') or (
                        user_reaction.emoji == '⬅')) and reaction_user != msg.author and user_reaction.message.id == msg.id

        async def change_page(c_page):
            """Waits for the user's reaction and then changes the page based on their reaction."""
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=reaction_check)
                if reaction.emoji == '➡':
                    c_page += 1
                    if c_page >= len(embed_lists):
                        c_page = 0  # start from the beginning of the list
                    await msg.edit(embed=embed_lists[c_page])

                elif reaction.emoji == '⬅':
                    c_page -= 1
                    if c_page < 0:
                        c_page = len(embed_lists) - 1  # going to the end of the list
                    await msg.edit(embed=embed_lists[c_page])

                # await msg.clear_reactions()
                # await msg.add_reaction(reaction1)
                # await msg.add_reaction(reaction2)
                # only remove user's reaction instead of all reactions
                try:
                    await reaction.remove(user)
                except Exception as e:
                    pass
                await change_page(c_page)
            except Exception as e:
                log.console(f"check_left_or_right_reaction_embed - {e}")
                await change_page(c_page)
        await change_page(original_page_number)

    @staticmethod
    async def set_embed_author_and_footer(embed, footer_message):
        """Sets the author and footer of an embed."""
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_message,
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def translate(self, text, src_lang, target_lang):
        try:
            data = {
                'text': text,
                'src_lang': await self.get_language_code(src_lang),
                'target_lang': await self.get_language_code(target_lang),
                'p_key': keys.translate_private_key
            }
            end_point = f"http://127.0.0.1:{keys.api_port}/translate"
            if self.test_bot:
                end_point = f"https://api.irenebot.com/translate"
            async with self.session.post(end_point, data=data) as r:
                self.cache.bot_api_translation_calls += 1
                if r.status == 200:
                    return json.loads(await r.text())
                else:
                    return None
        except Exception as e:
            log.console(e)
            return None

    @staticmethod
    async def get_language_code(language):
        """Returns a language code that is compatible with the papago framework."""
        language = language.lower()
        languages = ['ko', 'en', 'ja', 'zh-CN', 'zh-TW', 'es', 'fr', 'vi', 'th', 'id']
        ko_keywords = ['korean', 'ko', 'kr', 'korea', 'kor']
        eng_keywords = ['en', 'eng', 'english']
        ja_keywords = ['jp', 'jap', 'japanese', 'japan']
        zh_CN_keywords = ['chinese', 'ch', 'zh-cn', 'zhcn', 'c', 'china']
        es_keywords = ['es', 'espanol', 'spanish', 'sp']
        fr_keywords = ['french', 'fr', 'f', 'fren']
        vi_keywords = ['viet', 'vi', 'vietnamese', 'vietnam']
        th_keywords = ['th', 'thai', 'thailand']
        id_keywords = ['id', 'indonesian', 'indonesia', 'ind']
        if language in ko_keywords:
            return languages[0]
        elif language in eng_keywords:
            return languages[1]
        elif language in ja_keywords:
            return languages[2]
        elif language in zh_CN_keywords:
            return languages[3]
        elif language in es_keywords:
            return languages[5]
        elif language in fr_keywords:
            return languages[6]
        elif language in vi_keywords:
            return languages[7]
        elif language in th_keywords:
            return languages[8]
        elif languages in id_keywords:
            return languages[9]
        return None

    async def get_server_prefix(self, server_id):
        """Gets the prefix of a server by the server ID."""
        prefix = self.cache.server_prefixes.get(server_id)
        if prefix is None:
            return keys.bot_prefix
        else:
            return prefix

    async def get_server_prefix_by_context(self, ctx):  # this can also be passed in as a message
        """Gets the prefix of a server by the context."""
        try:
            server_id = ctx.guild.id
        except Exception as e:
            return keys.bot_prefix
        prefix = self.cache.server_prefixes.get(server_id)
        return prefix or keys.bot_prefix

    def get_user_count(self):
        """Get the amount of users that the bot is watching over."""
        counter = 0
        for guild in self.client.guilds:
            counter += guild.member_count
        return counter

    def get_server_count(self):
        """Returns the guild count the bot is connected to."""
        return len(self.client.guilds)

    def get_channel_count(self):
        """Returns the channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.channels)
        return count

    def get_text_channel_count(self):
        """Returns the text channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.text_channels)
        return count

    def get_voice_channel_count(self):
        """Returns the voice channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.voice_channels)
        return count


    ###################
    # ## BLACKJACK ## #
    ###################

    async def check_in_game(self, user_id, ctx):  # this is meant for when it is accessed by commands outside of BlackJack.
        """Check if a user is in a game."""
        check = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) From blackjack.games WHERE player1 = $1 OR player2 = $1", user_id))
        if check == 1:
            await ctx.send(f"> **{ctx.author}, you are already in a pending/active game. Please type {await self.get_server_prefix_by_context(ctx)}endgame.**")
            return True
        else:
            return False

    async def add_bj_game(self, user_id, bid, ctx, mode):
        """Add the user to a blackjack game."""
        await self.conn.execute("INSERT INTO blackjack.games (player1, bid1, channelid) VALUES ($1, $2, $3)", user_id, str(bid), ctx.channel.id)
        game_id = await self.get_game_by_player(user_id)
        if mode != "bot":
            await ctx.send(f"> **There are currently 1/2 members signed up for BlackJack. To join the game, please type {await self.get_server_prefix_by_context(ctx)}joingame {game_id} (bid)** ")

    async def process_bj_game(self, ctx, amount, user_id):
        """pre requisites for joining a blackjack game."""
        if amount >= 0:
            if not await self.check_in_game(user_id, ctx):
                if amount > await self.get_balance(user_id):
                    await ctx.send(f"> **{ctx.author}, you can not bet more than your current balance.**")
                else:
                    return True
        else:
            await ctx.send(f"> **{ctx.author}, you can not bet a negative number.**")
        return False

    async def get_game_by_player(self, player_id):
        """Get the current game of a player."""
        return self.first_result(await self.conn.fetchrow("SELECT gameid FROM blackjack.games WHERE player1 = $1 OR player2 = $1", player_id))

    async def get_game(self, game_id):
        """Get the game from its ID"""
        return await self.conn.fetchrow("SELECT gameid, player1, player2, bid1, bid2, channelid FROM blackjack.games WHERE gameid = $1", game_id)

    async def add_player_two(self, game_id, user_id, bid):
        """Add a second player to a blackjack game."""
        await self.conn.execute("UPDATE blackjack.games SET player2 = $1, bid2 = $2 WHERE gameid = $3 ", user_id, str(bid), game_id)

    async def get_current_cards(self, user_id):
        """Get the current cards of a user."""
        in_hand = self.first_result(await self.conn.fetchrow("SELECT inhand FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if in_hand is None:
            return []
        return in_hand.split(',')

    async def check_player_standing(self, user_id):
        """Check if a player is standing."""
        return self.first_result(await self.conn.fetchrow("SELECT stand FROM blackjack.currentstatus WHERE userid = $1", user_id)) == 1

    async def set_player_stand(self, user_id):
        """Set a player to stand."""
        await self.conn.execute("UPDATE blackjack.currentstatus SET stand = $1 WHERE userid = $2", 1, user_id)

    async def delete_player_status(self, user_id):
        """Remove a player's status from a game."""
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", user_id)

    async def add_player_status(self, user_id):
        """Add a player's status to a game."""
        await self.delete_player_status(user_id)
        await self.conn.execute("INSERT INTO blackjack.currentstatus (userid, stand, total) VALUES ($1, $2, $2)", user_id, 0)

    async def get_player_total(self, user_id):
        """Get a player's total score."""
        return self.first_result(await self.conn.fetchrow("SELECT total FROM blackjack.currentstatus WHERE userid = $1", user_id))

    async def get_card_value(self, card):
        """Get the value of a card."""
        return self.first_result(await self.conn.fetchrow("SELECT value FROM blackjack.cards WHERE id = $1", card))

    async def get_all_cards(self):
        """Get all the cards from a deck."""
        card_tuple = await self.conn.fetch("SELECT id FROM blackjack.cards")
        all_cards = []
        for card in card_tuple:
            all_cards.append(card[0])
        return all_cards

    async def get_available_cards(self, game_id):  # pass in a list of card ids
        """Get the cards that are not occupied."""
        all_cards = await self.get_all_cards()
        available_cards = []
        game = await self.get_game(game_id)
        player1_cards = await self.get_current_cards(game[1])
        player2_cards = await self.get_current_cards(game[2])
        for card in all_cards:
            if card not in player1_cards and card not in player2_cards:
                available_cards.append(card)
        return available_cards

    async def get_card_name(self, card_id):
        """Get the name of a card."""
        return self.first_result(await self.conn.fetchrow("SELECT name FROM blackjack.cards WHERE id = $1", card_id))

    async def check_if_ace(self, card_id, user_id):
        """Check if the card is an ace and is not used."""
        aces = ["1", "14", "27", "40"]
        aces_used = await self.get_aces_used(user_id)
        if card_id in aces and card_id not in aces_used:
            aces_used.append(card_id)
            await self.set_aces_used(aces_used, user_id)
            return True
        return False

    async def set_aces_used(self, card_list, user_id):
        """Mark an ace as used."""
        separator = ','
        cards = separator.join(card_list)
        await self.conn.execute("UPDATE blackjack.currentstatus SET acesused = $1 WHERE userid = $2", cards, user_id)

    async def get_aces_used(self, user_id):
        """Get the aces that were changed from 11 to 1."""
        aces_used = self.first_result(await self.conn.fetchrow("SELECT acesused FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if aces_used is None:
            return []
        return aces_used.split(',')

    def check_if_bot(self, user_id):
        """Check if the player is a bot. (The bot would be Irene)"""
        return str(self.get_int_index(keys.bot_id, 9)) in str(user_id)

    async def add_card(self, user_id):
        """Check status of a game, it's player, manages the bot that plays, and then adds a card."""
        end_game = False
        check = 0

        separator = ','
        current_cards = await self.get_current_cards(user_id)
        game_id = await self.get_game_by_player(user_id)
        game = await self.get_game(game_id)
        channel = await self.client.fetch_channel(game[5])
        stand = await self.check_player_standing(user_id)
        player1_score = await self.get_player_total(game[1])
        player2_score = await self.get_player_total(game[2])
        player1_cards = await self.get_current_cards(game[1])
        if not stand:
            available_cards = await self.get_available_cards(game_id)
            random_card = random.choice(available_cards)
            current_cards.append(str(random_card))
            cards = separator.join(current_cards)
            current_total = await self.get_player_total(user_id)
            random_card_value = await self.get_card_value(random_card)
            if current_total + random_card_value > 21:
                for card in current_cards:  # this includes the random card
                    if await self.check_if_ace(card, user_id) and check != 1:
                        check = 1
                        current_total = (current_total + random_card_value) - 10
                if check == 0:  # if there was no ace
                    current_total = current_total + random_card_value
            else:
                current_total = current_total + random_card_value
            await self.conn.execute("UPDATE blackjack.currentstatus SET inhand = $1, total = $2 WHERE userid = $3", cards, current_total, user_id)
            if current_total > 21:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if player1_score > 21 and current_total >= 16:
                        end_game = True
                        await self.set_player_stand(game[1])
                        await self.set_player_stand(game[2])
                    elif player1_score > 21 and current_total < 16:
                        await self.add_card(game[2])
                    elif player1_score < 22 and current_total > 21:
                        pass
                    else:
                        end_game = True
                elif self.check_if_bot(game[2]) and not self.check_if_bot(user_id):  # if user_id is not the bot
                    if player2_score < 16:
                        await self.add_card(game[2])
                    else:
                        await self.set_player_stand(user_id)
                        await self.set_player_stand(game[2])
                        end_game = True
            else:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if current_total < 16143478541328187392 and len(player1_cards) > 2:
                        await self.add_card(game[2])
                    if await self.check_player_standing(game[1]) and current_total >= 16:
                        end_game = True
            if not self.check_if_bot(user_id):
                if self.check_if_bot(game[2]):
                    await self.send_cards_to_channel(channel, user_id, random_card, True)
                else:
                    await self.send_cards_to_channel(channel, user_id, random_card)
        else:
            await channel.send(f"> **You already stood.**")
            if await self.check_game_over(game_id):
                await self.finish_game(game_id, channel)
        if end_game:
            await self.finish_game(game_id, channel)

    async def send_cards_to_channel(self, channel, user_id, card, bot_mode=False):
        """Send the cards to a specific channel."""
        if bot_mode:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=False)
        else:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=True)
        total_score = str(await self.get_player_total(user_id))
        if len(total_score) == 1:
            total_score = '0' + total_score  # this is to prevent being able to detect the number of digits by the spoiler
        card_name = await self.get_card_name(card)
        if bot_mode:
            await channel.send(f"<@{user_id}> pulled {card_name}. Their current score is {total_score}", file=card_file)
        else:
            await channel.send(f"<@{user_id}> pulled ||{card_name}||. Their current score is ||{total_score}||", file=card_file)

    async def compare_channels(self, user_id, channel):
        """Check if the channel is the correct channel."""
        game_id = await self.get_game_by_player(user_id)
        game = await self.get_game(game_id)
        if game[5] == channel.id:
            return True
        else:
            await channel.send(f"> **{user_id}, that game ({game_id}) is not available in this text channel.**")
            return False

    async def start_game(self, game_id):
        """Start out the game of blackjack."""
        game = await self.get_game(game_id)
        player1 = game[1]
        player2 = game[2]
        await self.add_player_status(player1)
        await self.add_player_status(player2)
        # Add Two Cards to both players [ Not in a loop because the messages should be in order on discord ]
        await self.add_card(player1)
        await self.add_card(player1)
        await self.add_card(player2)
        await self.add_card(player2)

    async def check_game_over(self, game_id):
        """Check if the blackjack game is over."""
        game = await self.get_game(game_id)
        player1_stand = await self.check_player_standing(game[1])
        player2_stand = await self.check_player_standing(game[2])
        if player1_stand and player2_stand:
            return True
        else:
            return False

    @staticmethod
    def determine_winner(score1, score2):
        """Check which player won the blackjack game."""
        if score1 == score2:
            return 'tie'
        elif score1 == 21:
            return 'player1'
        elif score2 == 21:
            return 'player2'
        elif score1 > 21 or score2 > 21:
            if score1 > 21 and score2 > 21:
                if score1 - 21 < score2 - 21:
                    return 'player1'
                else:
                    return 'player2'
            elif score1 > 21 and score2 < 21:
                return 'player2'
            elif score1 < 21 and score2 > 21:
                return 'player1'
        elif score1 < 21 and score2 < 21:
            if score1 - score2 > 0:
                return 'player1'
            else:
                return 'player2'
        else:
            return None

    async def announce_winner(self, channel, winner, loser, winner_points, loser_points, win_amount):
        """Send a message to the channel of who won the game."""
        if self.check_if_bot(winner):
            await channel.send(f"> **<@{keys.bot_id}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")
        elif self.check_if_bot(loser):
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{keys.bot_id}> with {loser_points}.**")
        else:
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")

    async def announce_tie(self, channel, player1, player2, tied_points):
        """Send a message to the channel of a tie."""
        if self.check_if_bot(player1) or self.check_if_bot(player2):
            await channel.send(f"> **<@{player1}> and <@{keys.bot_id}> have tied with {tied_points}**")
        else:
            await channel.send(f"> **<@{player1}> and <@{player2}> have tied with {tied_points}**")

    async def finish_game(self, game_id, channel):
        """Finish off a blackjack game and terminate it."""
        game = await self.get_game(game_id)
        player1_score = await self.get_player_total(game[1])
        player2_score = await self.get_player_total(game[2])
        if player2_score < 12 and self.check_if_bot(game[2]):
            await self.add_card(game[2])
        else:
            winner = self.determine_winner(player1_score, player2_score)
            player1_current_bal = await self.get_balance(game[1])
            player2_current_bal = await self.get_balance(game[2])
            if winner == 'player1':
                await self.update_balance(game[1], player1_current_bal + int(game[4]))
                if not self.check_if_bot(game[2]):
                    await self.update_balance(game[2], player2_current_bal - int(game[4]))
                await self.announce_winner(channel, game[1], game[2], player1_score, player2_score, game[4])
            elif winner == 'player2':
                if not self.check_if_bot(game[2]):
                    await self.update_balance(game[2], player2_current_bal + int(game[3]))
                await self.update_balance(game[1], player1_current_bal - int(game[3]))
                await self.announce_winner(channel, game[2], game[1], player2_score, player1_score, game[3])
            elif winner == 'tie':
                await self.announce_tie(channel, game[1], game[2], player1_score)
            await self.delete_game(game_id)

    async def delete_game(self, game_id):
        """Delete a blackjack game."""
        game = await self.get_game(game_id)
        await self.conn.execute("DELETE FROM blackjack.games WHERE gameid = $1", game_id)
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[1])
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[2])
        log.console(f"Game {game_id} deleted.")

    async def delete_all_games(self):
        """Delete all blackjack games."""
        all_games = await self.conn.fetch("SELECT gameid FROM blackjack.games")
        for games in all_games:
            game_id = games[0]
            await self.delete_game(game_id)
    ################
    # ## LEVELS ## #
    ################

    async def get_level(self, user_id, command):
        """Get the level of a command (rob/beg/daily)."""
        count = self.first_result(await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1 AND {command} > $2", user_id, 1))
        if count == 0:
            level = 1
        else:
            level = self.first_result(await self.conn.fetchrow(f"SELECT {command} FROM currency.Levels WHERE UserID = $1", user_id))
        return int(level)

    async def set_level(self, user_id, level, command):
        """Set the level of a user for a specific command."""
        async def update_level():
            """Updates a user's level."""
            await self.conn.execute(f"UPDATE currency.Levels SET {command} = $1 WHERE UserID = $2", level, user_id)

        count = self.first_result(await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1", user_id))
        if count == 0:
            await self.conn.execute("INSERT INTO currency.Levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)
            await update_level()
        else:
            await update_level()

    @staticmethod
    async def get_xp(level, command):
        """Returns money/experience needed for a certain level."""
        if command == "profile":
            return 250 * level
        return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)

    @staticmethod
    async def get_rob_percentage(level):
        """Get the percentage of being able to rob. (Every 1 is 5%)"""
        chance = int(6 + (level // 10))  # first 10 levels is 6 for 30% chance
        if chance > 16:
            chance = 16
        return chance

    #######################
    # ## GROUP MEMBERS ## #
    #######################
    async def get_if_user_voted(self, user_id):
        time_stamp = self.first_result(await self.conn.fetchrow("SELECT votetimestamp FROM general.lastvoted WHERE userid = $1", user_id))
        if time_stamp:
            tz_info = time_stamp.tzinfo
            current_time = datetime.datetime.now(tz_info)
            check = current_time - time_stamp
            if check.seconds <= 43200:
                return True
        return False

    @staticmethod
    def check_idol_object(obj):
        return type(obj) == Idol

    async def send_vote_message(self, message):
        server_prefix = await self.get_server_prefix_by_context(message)
        vote_message = f"""> **To call more idol photos for the next 12 hours, please support Irene by voting or becoming a patron through the links at `{server_prefix}vote` or `{server_prefix}patreon`!**"""
        return await message.channel.send(vote_message)

    async def set_global_alias(self, obj, alias):
        """Set an idol/group alias for the bot."""
        obj.aliases.append(alias)
        is_group = int(not self.check_idol_object(obj))
        await self.conn.execute("INSERT INTO groupmembers.aliases(objectid, alias, isgroup) VALUES($1, $2, $3)", obj.id, alias, is_group)

    async def set_local_alias(self, obj, alias, server_id):
        """Set an idol/group alias for a server"""
        local_aliases = obj.local_aliases.get(server_id)
        if local_aliases:
            local_aliases.append(alias)
        else:
            obj.local_aliases[server_id] = [alias]
        is_group = int(not self.check_idol_object(obj))
        await self.conn.execute("INSERT INTO groupmembers.aliases(objectid, alias, isgroup, serverid) VALUES($1, $2, $3, $4)", obj.id, alias, is_group, server_id)

    async def remove_global_alias(self, obj, alias):
        obj.aliases.remove(alias)
        is_group = int(not self.check_idol_object(obj))
        await self.conn.execute("DELETE FROM groupmembers.aliases WHERE alias = $1 AND isgroup = $2 AND objectid = $3 AND serverid IS NULL", alias, is_group, obj.id)

    async def remove_local_alias(self, obj, alias, server_id):
        is_group = int(not self.check_idol_object(obj))
        local_aliases = obj.local_aliases.get(server_id)
        if local_aliases:
            local_aliases.remove(alias)
        await self.conn.execute("DELETE FROM groupmembers.aliases WHERE alias = $1 AND isgroup = $2 AND serverid = $3 AND objectid = $4", alias, is_group, server_id, obj.id)

    async def get_member(self, idol_id):
        for idol in self.cache.idols:
            if idol.id == idol_id:
                return idol

    async def get_group(self, group_id):
        for group in self.cache.groups:
            if group.id == group_id:
                return group

    async def set_embed_card_info(self, obj, group=False, server_id=None):
        """Sets General Information about a Group or Idol."""
        description = ""
        if obj.description:
            description += f"{obj.description}\n\n"
        if obj.id:
            description += f"ID: {obj.id}\n"
        if obj.gender:
            description += f"Gender: {obj.gender}\n"
        if group:
            title = f"{obj.name} [{obj.id}]\n"
            if obj.name:
                description += f"Name: {obj.name}\n"
            if obj.debut_date:
                description += f"Debut Date: {obj.debut_date}\n"
            if obj.disband_date:
                description += f"Disband Date: {obj.disband_date}\n"
            if obj.fandom:
                description += f"Fandom Name: {obj.fandom}\n"
            if obj.company:
                description += f"Company: {obj.company}\n"
            if obj.website:
                description += f"[Official Website]({obj.website})\n"
        else:
            title = f"{obj.full_name} ({obj.stage_name}) [{obj.id}]\n"
            if obj.full_name:
                description += f"Full Name: {obj.full_name}\n"
            if obj.stage_name:
                description += f"Stage Name: {obj.stage_name}\n"
            if obj.former_full_name:
                description += f"Former Full Name: {obj.former_full_name}\n"
            if obj.former_stage_name:
                description += f"Former Stage Name: {obj.former_stage_name}\n"
            if obj.birth_date:
                description += f"Birth Date: {obj.birth_date}\n"
            if obj.birth_country:
                description += f"Birth Country: {obj.birth_country}\n"
            if obj.birth_city:
                description += f"Birth City: {obj.birth_city}\n"
            if obj.height:
                description += f"Height: {obj.height}cm\n"
            if obj.zodiac:
                description += f"Zodiac Sign: {obj.zodiac}\n"
            if obj.blood_type:
                description += f"Blood Type: {obj.blood_type}\n"
            if obj.called:
                description += f"Called: {obj.called} times\n"
        if obj.twitter:
            description += f"[Twitter](https://twitter.com/{obj.twitter})\n"
        if obj.youtube:
            description += f"[Youtube](https://www.youtube.com/channel/{obj.youtube})\n"
        if obj.melon:
            description += f"[Melon](https://www.melon.com/artist/song.htm?artistId={obj.melon})\n"
        if obj.instagram:
            description += f"[Instagram](https://instagram.com/{obj.instagram})\n"
        if obj.vlive:
            description += f"[V Live](https://channels.vlive.tv/{obj.vlive})\n"
        if obj.spotify:
            description += f"[Spotify](https://open.spotify.com/artist/{obj.spotify})\n"
        if obj.fancafe:
            description += f"[FanCafe](https://m.cafe.daum.net/{obj.fancafe})\n"
        if obj.facebook:
            description += f"[Facebook](https://www.facebook.com/{obj.facebook})\n"
        if obj.tiktok:
            description += f"[TikTok](https://www.tiktok.com/{obj.tiktok})\n"
        if obj.photo_count:
            description += f"Photo Count: {obj.photo_count}\n"
        embed = await self.create_embed(title=title,
                                      color=self.get_random_color(), title_desc=description)
        if obj.tags:
            embed.add_field(name="Tags", value=', '.join(obj.tags), inline=False)
        if obj.aliases:
            embed.add_field(name="Aliases", value=', '.join(obj.aliases), inline=False)
        if obj.local_aliases.get(server_id):
            embed.add_field(name="Server Aliases", value=', '.join(obj.local_aliases.get(server_id)), inline=False)
        if group:
            if obj.members:
                value = f"{' | '.join([(await self.get_member(idol_id)).full_name for idol_id in obj.members])}\n"
                embed.add_field(name="Members", value=value, inline=False)

        else:
            if obj.groups:
                value = await self.get_group_names_as_string(obj)
                embed.add_field(name="Groups", value=value)
        if obj.thumbnail:
            embed.set_thumbnail(url=obj.thumbnail)
        if obj.banner:
            embed.set_image(url=obj.banner)
        return embed

    async def get_group_names_as_string(self, idol):
        """Get the group names split by a | ."""
        # note that this used to be simplified to one line, but in the case there are groups that do not exist,
        # a proper check and deletion of fake groups are required
        group_names = []
        for group_id in idol.groups:
            group = await self.get_group(group_id)
            if group:
                group_names.append(group.name)
            else:
                # make sure the cache exists first before deleting.
                if self.cache.groups:
                    # delete the group connections if it doesn't exist.
                    await self.conn.execute("DELETE FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)
        return f"{' | '.join(group_names)}\n"

    async def check_channel_sending_photos(self, channel_id):
        """Checks a text channel ID to see if it is restricted from having idol photos sent."""
        channel = self.cache.restricted_channels.get(channel_id)
        if channel:
            if channel[1] == 0:
                return False  # returns False if they are restricted.
        return True

    async def delete_restricted_channel_from_cache(self, channel_id, send_all):
        """Deletes restricted channel from cache."""
        r_channel = self.cache.restricted_channels.get(channel_id)
        if r_channel:
            if r_channel[1] == send_all:
                self.cache.restricted_channels.pop(channel_id)

    async def check_server_sending_photos(self, server_id):
        """Checks a server to see if it has a specific channel to send idol photos to"""
        for channel in self.cache.restricted_channels:
            channel_info = self.cache.restricted_channels.get(channel)
            if channel_info[0] == server_id and channel_info[1] == 1:
                return True  # returns True if they are supposed to send it to a specific channel.

    async def get_channel_sending_photos(self, server_id):
        """Returns a text channel from a server that requires idol photos to be sent to a specific text channel."""
        for channel_id in self.cache.restricted_channels:
            channel_info = self.cache.restricted_channels.get(channel_id)
            if channel_info[0] == server_id and channel_info[1] == 1:
                return self.client.get_channel(channel_id)

    async def get_db_photo_count_of_group(self, group_id):
        """Gets the total amount of photos that a group has from the db."""
        group_result = await self.conn.fetchrow("SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id AND g.groupid = $1 GROUP BY g.groupid", group_id)
        return 0 if not group_result else group_result[2]

    @staticmethod
    def log_idol_command(message):
        """Log an idol photo that was called."""
        log.console(f"IDOL LOG: ChannelID = {message.channel.id} - {message.author} "
                    f"({message.author.id})|| {message.clean_content} ")

    async def get_all_images_count(self):
        """Get the amount of images the bot has."""
        return self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.imagelinks"))

    async def get_db_idol_called(self, member_id):
        """Get the amount of times an idol has been called from the database."""
        return self.first_result(await self.conn.fetchrow("SELECT Count FROM groupmembers.Count WHERE MemberID = $1", member_id))

    @staticmethod
    async def check_if_folder(url):
        """Check if a url is a folder."""
        async with keys.client_session.get(url) as r:
            if r.status == 200:
                return True
            return False

    async def get_db_idol_count(self, member_id):
        """Get the amount of photos for an idol."""
        return self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.imagelinks WHERE memberid = $1", member_id))

    async def get_random_idol(self):
        """Get a random idol with at least 1 photo."""
        idol = random.choice(self.cache.idols)
        if not idol.photo_count:
            idol = await self.get_random_idol()
        return idol

    async def get_db_all_members(self):
        """Get all idols from the database."""
        return await self.conn.fetch("""SELECT id, fullname, stagename, formerfullname, formerstagename, birthdate,
        birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify,
        fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags FROM groupmembers.Member ORDER BY id""")

    async def get_all_groups(self):
        """Get all groups."""
        return await self.conn.fetch("""SELECT groupid, groupname, debutdate, disbanddate, description, twitter, youtube,
                                     melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company,
                                      website, thumbnail, banner, gender, tags FROM groupmembers.groups ORDER BY groupname""")

    async def get_db_members_in_group(self, group_name=None, group_id=None):
        """Get the members in a specific group from database."""
        if group_id is None:
            group_id = self.first_result(await self.conn.fetchrow(f"SELECT groupid FROM groupmembers.groups WHERE groupname = $1", group_name))
        members = await self.conn.fetch("SELECT idolid FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)
        return [member[0] for member in members]

    async def check_db_member_in_group(self, member_id, group_id):
        """Check if an idol is in a group from DB."""
        return group_id in await self.get_db_groups_from_member(member_id)

    async def get_db_member(self, member_id):
        """Get an idol based on their ID."""
        return await self.conn.fetchrow("SELECT id, fullname, stagename FROM groupmembers.member WHERE id = $1", member_id)

    async def get_db_aliases(self, object_id, group=False):
        """Get the aliases of an idol or group from the database."""
        aliases = await self.conn.fetch("SELECT alias, serverid FROM groupmembers.aliases WHERE objectid = $1 AND isgroup = $2", object_id, int(group))
        global_aliases = []
        local_aliases = {}
        for alias_info in aliases:
            alias = alias_info[0]
            server_id = alias_info[1]
            if server_id:
                server_list = local_aliases.get(server_id)
                if server_list:
                    server_list.append(alias)
                else:
                    local_aliases[server_id] = [alias]
            else:
                global_aliases.append(alias)
        return global_aliases, local_aliases

    async def get_db_group_name(self, group_id):
        """Get a group's name based on their ID."""
        return self.first_result(await self.conn.fetchrow("SELECT groupname FROM groupmembers.groups WHERE groupid = $1", group_id))

    async def get_db_groups_from_member(self, member_id):
        """Return all the group ids an idol is in from the database."""
        groups = await self.conn.fetch("SELECT groupid FROM groupmembers.idoltogroup WHERE idolid = $1", member_id)
        return [group[0] for group in groups]

    async def add_idol_to_group(self, member_id: int, group_id: int):
        return await self.conn.execute("INSERT INTO groupmembers.idoltogroup(idolid, groupid) VALUES($1, $2)", member_id, group_id)

    async def remove_idol_from_group(self, member_id: int, group_id: int):
        return await self.conn.execute("DELETE FROM groupmembers.idoltogroup WHERE idolid = $1 AND groupid = $2", member_id, group_id)

    async def send_names(self, ctx, mode, user_page_number=1, group_ids=None):
        """Send the names of all idols in an embed with many pages."""
        server_prefix = await self.get_server_prefix_by_context(ctx)

        async def check_mode(embed_temp):
            """Check if it is grabbing their full names or stage names."""
            if mode == "fullname":
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {server_prefix}members for Stage Names.")
            else:
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {server_prefix}fullnames for Full Names.")
            return embed_temp
        is_mod = self.check_if_mod(ctx)
        embed_lists = []
        page_number = 1
        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
        counter = 1
        for group in self.cache.groups:
            names = []
            if (group.name != "NULL" and group.photo_count != 0) or is_mod:
                if not group_ids or group.id in group_ids:
                    for group_member in group.members:
                        member = await self.get_member(group_member)
                        if member:
                            if member.photo_count != 0 or is_mod:
                                if mode == "fullname":
                                    member_name = member.full_name
                                else:
                                    member_name = member.stage_name
                                if is_mod:
                                    names.append(f"{member_name} ({member.id}) | ")
                                else:
                                    names.append(f"{member_name} | ")
                    final_names = "".join(names)
                    if len(final_names) == 0:
                        final_names = "None"
                    if is_mod:
                        embed.insert_field_at(counter, name=f"{group.name} ({group.id})", value=final_names, inline=False)
                    else:
                        embed.insert_field_at(counter, name=f"{group.name}", value=final_names, inline=False)
                    if counter == 10:
                        page_number += 1
                        await check_mode(embed)
                        embed_lists.append(embed)
                        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
                        counter = 0
                    counter += 1
        # if counter did not reach 10, current embed needs to be saved.
        await check_mode(embed)
        embed_lists.append(embed)
        if user_page_number > len(embed_lists) or user_page_number < 1:
            user_page_number = 1
        msg = await ctx.send(embed=embed_lists[user_page_number-1])
        # if embeds list only contains 1 embed, do not paginate.
        if len(embed_lists) > 1:
            await self.check_left_or_right_reaction_embed(msg, embed_lists, user_page_number-1)

    async def set_embed_with_aliases(self, name, server_id=None):
        """Create an embed with the aliases of the names of groups or idols sent in"""
        members = await self.get_idol_where_member_matches_name(name, mode=1, server_id=server_id)
        groups, group_names = await self.get_group_where_group_matches_name(name, mode=1, server_id=server_id)
        embed_list = []
        count = 0
        page_number = 1
        embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="", color=self.get_random_color())
        for member in members:
            aliases = ', '.join(member.aliases)
            local_aliases = member.local_aliases.get(server_id)
            if local_aliases:
                aliases += ", ".join(local_aliases)
            embed.add_field(name=f"{member.full_name} ({member.stage_name}) [Idol {member.id}]", value=aliases or "None", inline=True)
            count += 1
            if count == 24:
                count = 0
                page_number += 1
                embed_list.append(embed)
                embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="",
                                      color=self.get_random_color())
        for group in groups:
            aliases = ', '.join(group.aliases)
            embed.add_field(name=f"{group.name} [Group {group.id}]", value=aliases or "None", inline=True)
            count += 1
            if count == 24:
                count = 0
                page_number += 1
                embed_list.append(embed)
                embed = discord.Embed(title=f"{name} Aliases Page {page_number}", description="",
                                      color=self.get_random_color())
        if count != 0:
            embed_list.append(embed)
        return embed_list

    async def set_embed_with_all_aliases(self, mode, server_id=None):
        """Send the names of all aliases in an embed with many pages."""
        def create_embed():
            return discord.Embed(title=f"{mode} Global/Local Aliases Page {page_number}", color=self.get_random_color())
        if mode == "Group":
            all_info = self.cache.groups
            is_group = True
        else:
            all_info = self.cache.idols
            is_group = False
        embed_list = []
        count = 0
        page_number = 1
        embed = create_embed()
        for info in all_info:
            aliases = ",".join(info.aliases)
            local_aliases = info.local_aliases.get(server_id)
            if local_aliases:
                aliases += ", ".join(local_aliases)
            if aliases:
                if not is_group:
                    embed.add_field(name=f"{info.full_name} ({info.stage_name}) [{info.id}]", value=aliases, inline=True)
                else:
                    embed.add_field(name=f"{info.name} [{info.id}]", value=aliases, inline=True)
                count += 1
            if count == 10:
                count = 0
                embed_list.append(embed)
                page_number += 1
                embed = create_embed()
        if count != 0:
            embed_list.append(embed)
        return embed_list

    async def check_idol_post_reactions(self, message, user_msg, idol, link, guessing_game=False):
        """Check the reactions on an idol post or guessing game."""
        try:
            if message is not None:
                reload_image_emoji = keys.reload_emoji
                dead_link_emoji = keys.dead_emoji
                if not guessing_game:
                    await message.add_reaction(reload_image_emoji)
                await message.add_reaction(dead_link_emoji)
                message = await message.channel.fetch_message(message.id)

                def image_check(user_reaction, reaction_user):
                    """check the user that reacted to it and which emoji it was."""
                    user_check = (reaction_user == user_msg.author) or (reaction_user.id == keys.owner_id) or reaction_user.id in keys.mods_list
                    dead_link_check = str(user_reaction.emoji) == dead_link_emoji
                    reload_image_check = str(user_reaction.emoji) == reload_image_emoji
                    guessing_game_check = user_check and dead_link_check and user_reaction.message.id == message.id
                    idol_post_check = user_check and (dead_link_check or reload_image_check) and user_reaction.message.id == message.id
                    if guessing_game:
                        return guessing_game_check
                    return idol_post_check

                async def reload_image():
                    """Wait for a user to react, and reload the image if it's the reload emoji."""
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=image_check, timeout=60)
                        if str(reaction) == reload_image_emoji:
                            channel = message.channel
                            await message.delete()
                            # message1 = await channel.send(embed=embed)
                            message1 = await channel.send(link)
                            await self.check_idol_post_reactions(message1, user_msg, idol, link)
                        elif str(reaction) == dead_link_emoji:
                            if await self.check_if_patreon(user.id):
                                await message.delete()
                            else:
                                await message.clear_reactions()
                                server_prefix = await self.get_server_prefix_by_context(message)
                                warning_msg = f"Report images as dead links (2nd reaction) ONLY if the image does not load or it's not a photo of the idol.\nYou can have this message removed by becoming a {server_prefix}patreon"
                                if guessing_game:
                                    warning_msg = f"This image has been reported as a dead image, not a photo of the idol, or a photo with several idols.\nYou can have this message removed by becoming a {server_prefix}patreon"
                                await message.edit(content=warning_msg, suppress=True, delete_after=45)
                            await self.get_dead_links()
                            try:
                                channel = self.cache.dead_image_channel
                                if channel is not None:
                                    await self.send_dead_image(channel, link, user, idol, int(guessing_game))
                            except Exception as e:
                                pass
                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                    except Exception as e:
                        log.console(e)
                        pass
                await reload_image()
        except Exception as e:
            pass

    async def get_dead_links(self):
        return await self.conn.fetch("SELECT deadlink, messageid, idolid FROM groupmembers.deadlinkfromuser")

    async def delete_dead_link(self, link, idol_id):
        return await self.conn.execute("DELETE FROM groupmembers.deadlinkfromuser WHERE deadlink = $1 AND idolid = $2", link, idol_id)

    async def set_forbidden_link(self, link, idol_id):
        return await self.conn.execute("INSERT INTO groupmembers.forbiddenlinks(link, idolid) VALUES($1, $2)", link, idol_id)

    async def send_dead_image(self, channel, link, user, idol, is_guessing_game):
        try:
            game = ""
            if is_guessing_game:
                game = "-- Guessing Game"
            special_message = f"""**Dead Image For {idol.full_name} ({idol.stage_name}) ({idol.id}) {game}
Sent in by {user.name}#{user.discriminator} ({user.id}).**"""
            msg, api_url = await self.idol_post(channel, idol, photo_link=link, special_message=special_message)
            self.cache.dead_image_cache[msg.id] = [str(link), user.id, idol.id, is_guessing_game]
            await self.conn.execute(
                "INSERT INTO groupmembers.deadlinkfromuser(deadlink, userid, messageid, idolid, guessinggame) VALUES($1, $2, $3, $4, $5)",
                str(link), user.id, msg.id, idol.id, is_guessing_game)
            await msg.add_reaction(keys.check_emoji)
            await msg.add_reaction(keys.trash_emoji)
            await msg.add_reaction(keys.next_emoji)
        except Exception as e:
            log.console(f"Send Dead Image - {e}")

    async def get_idol_where_member_matches_name(self, name, mode=0, server_id=None):
        """Get idol object if the name matches an idol"""
        idol_list = []
        name = name.lower()
        for idol in self.cache.idols:
            local_aliases = None
            if server_id:
                local_aliases = idol.local_aliases.get(server_id)
            if mode == 0:
                if idol.full_name and idol.stage_name:
                    if name == idol.full_name.lower() or name == idol.stage_name.lower():
                        idol_list.append(idol)
            else:
                if idol.full_name and idol.stage_name:
                    if idol.stage_name.lower() in name or idol.full_name.lower() in name:
                        idol_list.append(idol)
            for alias in idol.aliases:
                if mode == 0:
                    if alias == name:
                        idol_list.append(idol)
                else:
                    if alias in name:
                        idol_list.append(idol)
            if local_aliases:
                for alias in local_aliases:
                    if await self.check_to_add_alias_to_list(alias, name, mode):
                        idol_list.append(idol)

        # remove any duplicates
        idols = list(dict.fromkeys(idol_list))
        return idols

    async def get_idol_by_both_names(self, full_name, stage_name):
        """Returns the first idol id where the full name and stage name match (CASE-SENSITIVE)"""
        for idol in self.cache.idols:
            if idol.stage_name == stage_name and idol.full_name == full_name:
                return idol

    async def check_to_add_alias_to_list(self, alias, name, mode=0):
        """Check whether to add an alias to a list. Compares a name with an existing alias."""
        if mode == 0:
            if alias == name:
                return True
        else:
            if alias in name:
                return True
        return False

    async def get_group_where_group_matches_name(self, name, mode=0, server_id=None):
        """Get group ids for a specific name."""
        group_list = []
        name = name.lower()
        for group in self.cache.groups:
            try:
                aliases = group.aliases
                local_aliases = None
                if server_id:
                    local_aliases = group.local_aliases.get(server_id)
                if mode == 0:
                    if group.name:
                        if name == group.name.lower():
                            group_list.append(group)
                else:
                    if group.name:
                        if group.name.lower() in name:
                            group_list.append(group)
                            name = (name.lower()).replace(group.name, "")
                for alias in aliases:
                    if await self.check_to_add_alias_to_list(alias, name, mode):
                        group_list.append(group)
                        if mode:
                            name = (name.lower()).replace(alias, "")
                if local_aliases:
                    for alias in local_aliases:
                        if await self.check_to_add_alias_to_list(alias, name, mode):
                            group_list.append(group)
                            if mode:
                                name = (name.lower()).replace(alias, "")

            except Exception as e:
                log.console(e)
        # remove any duplicates
        group_list = list(dict.fromkeys(group_list))
        # print(id_list)
        if mode == 0:
            return group_list
        else:
            return group_list, name

    async def process_names(self, ctx, page_number_or_group, mode):
        """Structures the input for idol names commands and sends information to transfer the names to the channels."""
        if type(page_number_or_group) == int:
            await self.send_names(ctx, mode, page_number_or_group)
        elif type(page_number_or_group) == str:
            server_id = await self.get_server_id(ctx)
            groups, name = await self.get_group_where_group_matches_name(page_number_or_group, mode=1, server_id=server_id)
            await self.send_names(ctx, mode, group_ids=[group.id for group in groups])

    async def check_group_and_idol(self, message_content, server_id=None):
        """returns specific idols being called from a reference to a group ex: redvelvet irene"""
        groups, new_message = await self.get_group_where_group_matches_name(message_content, mode=1, server_id=server_id)
        member_list = []
        members = await self.get_idol_where_member_matches_name(new_message, mode=1, server_id=server_id)
        for group in groups:
            for member in members:
                if member.id in group.members:
                    member_list.append(member)
        return member_list or None

    async def update_member_count(self, idol):
        """Update the amount of times an idol has been called."""
        if not idol.called:
            idol.called = 1
            await self.conn.execute("INSERT INTO groupmembers.count VALUES($1, $2)", idol.id, 1)
        else:
            idol.called += 1
            await self.conn.execute("UPDATE groupmembers.Count SET Count = $1 WHERE MemberID = $2", idol.called, idol.id)

    async def set_as_group_photo(self, link):
        await self.conn.execute("UPDATE groupmembers.imagelinks SET groupphoto = $1 WHERE link = $2", 1, str(link))

    async def get_google_drive_link(self, api_url):
        """Get the google drive link based on the api's image url."""
        return self.first_result(await self.conn.fetchrow("SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", str(api_url)))

    async def get_image_msg(self, idol, group_id, channel, photo_link, user_id=None, guild_id=None, api_url=None, special_message=None, guessing_game=False, scores=None):
        """Get the image link from the API and return the message containing the image."""
        async def post_msg(m_file=None, m_embed=None, repeated=0):
            """Send the message to the channel and return it."""
            message = None
            try:
                if not special_message:
                    message = await channel.send(embed=m_embed, file=m_file)
                else:
                    message = await channel.send(special_message, embed=m_embed, file=m_file)
            except Exception as e:
                # cannot access API or API Link -> attempt to post it 5 times.
                # this happens because the image link may not be properly registered.
                if repeated < 5:
                    if not message:
                        await asyncio.sleep(0.5)
                        message = await post_msg(m_file=m_file, m_embed=m_embed, repeated=repeated + 1)
            return message

        file = None
        if not api_url:
            try:
                find_post = True

                data = {
                    'p_key': keys.translate_private_key,
                    'no_group_photos': int(guessing_game)
                }
                end_point = f"http://127.0.0.1:{keys.api_port}/photos/{idol.id}"
                if self.test_bot:
                    end_point = f"https://api.irenebot.com/photos/{idol.id}"
                while find_post:  # guarantee we get a post sent to the user.
                    async with self.session.post(end_point, data=data) as r:
                        self.cache.bot_api_idol_calls += 1
                        if r.status == 200 or r.status == 301:
                            api_url = r.url
                            find_post = False
                        elif r.status == 415:
                            # video
                            if guessing_game:
                                # do not allow videos in the guessing game.
                                return self.get_image_msg(idol, group_id, channel, photo_link, user_id, guild_id, api_url, special_message, guessing_game, scores)
                            url_data = json.loads(await r.text())
                            api_url = url_data.get('final_image_link')
                            file_location = url_data.get('location')
                            file_name = url_data.get('file_name')
                            file_size = os.path.getsize(file_location)
                            if file_size < 8388608:  # 8 MB
                                file = discord.File(file_location, file_name)
                                find_post = False
                        elif r.status == 403:
                            log.console("API Key Missing or Invalid Key.")
                            find_post = False
                        elif r.status == 404 or r.status == 400:
                            # No photos were found.
                            log.console(f"No photos were found for this idol ({idol.id}).")
                            msg = await channel.send(f"**No photos were found for this idol ({idol.id}).**")
                            find_post = False
                            return msg, None
                        elif r.status == 502:
                            msg = await channel.send("API is currently being overloaded with requests.")
                            log.console("API is currently being overloaded with requests or is down.")
                            find_post = False
                            return msg, None
                        else:
                            # error unaccounted for.
                            log.console(f"{r.status} - Status Code from API.")
            except Exception as e:
                log.console(e)

        if guessing_game:
            # sleep for 2 seconds because of bad loading times on discord
            await asyncio.sleep(2)
        try:
            if file:
                # send the video and return the message with the api url.
                msg = await post_msg(m_file=file)
                if not msg:
                    raise Exception
                return msg, api_url

            # an image url should exist at this point, and should not equal None.
            embed = await self.get_idol_post_embed(group_id, idol, str(api_url), user_id=user_id,
                                                   guild_id=channel.guild.id, guessing_game=guessing_game, scores=scores)
            embed.set_image(url=api_url)
            msg = await post_msg(m_embed=embed)
            if not msg:
                raise Exception

        except Exception as e:
            self.api_issues += 1
            if self.api_issues >= 50:
                await self.kill_api()
                self.api_issues = 0
            await channel.send(f"> An API issue has occurred. If this is constantly occurring, please join our support server.")
            log.console(f" {e} - An API issue has occurred. If this is constantly occurring, please join our support server.")
            return None, None
        return msg, api_url

    async def get_idol_post_embed(self, group_id, idol, photo_link, user_id=None, guild_id=None, guessing_game=False, scores=None):
        """The embed for an idol post."""
        if not guessing_game:
            if not group_id:
                embed = discord.Embed(title=f"{idol.full_name} ({idol.stage_name})", color=self.get_random_color(),
                                      url=photo_link)
            else:
                group = await self.get_group(group_id)
                embed = discord.Embed(title=f"{group.name} ({idol.stage_name})",
                                      color=self.get_random_color(), url=photo_link)
            patron_msg = f"Please consider becoming a {await self.get_server_prefix(guild_id)}patreon."

            # when user_id is None, the post goes to the dead images channel.
            if user_id:
                if not await self.check_if_patreon(user_id):
                    embed.set_footer(text=patron_msg)
        else:
            current_scores = ""
            if scores:
                for user_id in scores:
                    current_scores += f"<@{user_id}> -> {scores.get(user_id)}\n"
            embed = discord.Embed(description=current_scores,
                                  color=self.get_random_color(), url=photo_link)
        return embed

    async def idol_post(self, channel, idol, photo_link=None, group_id=None, special_message=None, user_id=None,
        guessing_game=False, scores=None):
        """The main process for posting an idol's photo."""
        try:
            try:
                msg, api_url = await self.get_image_msg(idol, group_id, channel, photo_link, user_id=user_id, guild_id=channel.guild.id, api_url=photo_link, special_message=special_message, guessing_game=guessing_game, scores=scores)
                if not msg and not api_url:
                    self.api_issues += 1
                await self.update_member_count(idol)
            except Exception as e:
                if guessing_game:
                    return self.idol_post(channel, idol, photo_link, group_id, special_message, user_id, guessing_game, scores)
                await channel.send(f"> An error has occurred. If you are in DMs, It is not possible to receive Idol Photos.")
                return None, None
            return msg, api_url
        except Exception as e:
            log.console(e)
            return None, None

    #################
    # ## LOGGING ## #
    #################

    async def get_servers_logged(self):
        """Get the servers that are being logged."""
        return [server_id for server_id in self.cache.logged_channels]

    async def get_channels_logged(self):
        """Get all the channels that are being logged."""
        return self.cache.list_of_logged_channels

    async def add_to_logging(self, server_id, channel_id):  # return true if status is on
        """Add a channel to be logged."""
        if (self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM logging.servers WHERE serverid = $1", server_id))) == 0:
            await self.conn.execute("INSERT INTO logging.servers (serverid, channelid, status, sendall) VALUES ($1, $2, $3, $4)", server_id, channel_id, 1, 1)
            server = self.cache.logged_channels.get(server_id)
            if server is None:
                self.cache.logged_channels[server_id] = {"send_all": 1, "logging_channel": channel_id, "channels": []}
            else:
                self.cache.list_of_logged_channels.append(channel_id)
                server['channels'].append(channel_id)
        else:
            await self.set_logging_status(server_id, 1)
            current_channel_id = self.first_result(await self.conn.fetchrow("SELECT channelid FROM logging.servers WHERE serverid = $1", server_id))
            if current_channel_id != channel_id:
                await self.conn.execute("UPDATE logging.servers SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        return True

    async def check_if_logged(self, server_id=None, channel_id=None):  # only one parameter should be passed in
        """Check if a server or channel is being logged."""
        if channel_id is not None:
            return channel_id in self.cache.list_of_logged_channels
        elif server_id is not None:
            return server_id in self.cache.logged_channels

    async def get_send_all(self, server_id):
        return (self.cache.logged_channels.get(server_id))['send_all']

    async def set_logging_status(self, server_id, status):  # status can only be 0 or 1
        """Set a server's logging status."""
        await self.conn.execute("UPDATE logging.servers SET status = $1 WHERE serverid = $2", status, server_id)
        if status == 0:
            self.cache.logged_channels.pop(server_id, None)
        else:
            logged_server = await self.conn.fetchrow("SELECT id, serverid, channelid, sendall FROM logging.servers WHERE serverid = $1", server_id)
            channels = await self.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1", logged_server[0])
            for channel in channels:
                self.cache.list_of_logged_channels.append(channel[0])
            self.cache.logged_channels[logged_server[1]] = {
                "send_all": logged_server[3],
                "logging_channel": logged_server[2],
                "channels": [channel[0] for channel in channels]
            }

    async def get_logging_id(self, server_id):
        """Get the ID in the table of a server."""
        return self.first_result(await self.conn.fetchrow("SELECT id FROM logging.servers WHERE serverid = $1", server_id))

    async def check_logging_requirements(self, message):
        """Check if a message meets all the logging requirements."""
        try:
            if not message.author.bot:
                if await self.check_if_logged(server_id=message.guild.id):
                    if await self.check_if_logged(channel_id=message.channel.id):
                        return True
        except Exception as e:
            pass
        return False

    @staticmethod
    async def get_attachments(message):
        """Get the attachments of a message."""
        files = None
        if len(message.attachments) != 0:
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())
        return files

    async def get_log_channel_id(self, message):
        """Get the channel where logs are made on a server."""
        return self.client.get_channel((self.cache.logged_channels.get(message.guild.id))['logging_channel'])

    #################
    # ## TWITTER ## #
    #################
    async def update_status(self, context):
        self.api.update_status(status=context)
        tweet = self.api.user_timeline(user_id=f'{keys.twitter_account_id}', count=1)[0]
        return f"https://twitter.com/{keys.twitter_username}/status/{tweet.id}"

    async def delete_status(self, context):
        self.api.destroy_status(context)

    async def recent_tweets(self, context):
        tweets = self.api.user_timeline(user_id=f'{keys.twitter_account_id}', count=context)
        final_tweet = ""
        for tweet in tweets:
            final_tweet += f"> **Tweet ID:** {tweet.id} | **Tweet:** {tweet.text}\n"
        return final_tweet

    #################
    # ## LAST FM ## #
    #################

    @staticmethod
    def create_fm_payload(method, user=None, limit=None, time_period=None):
        """Creates the payload to be sent to Last FM"""
        payload = {
            'api_key': keys.last_fm_api_key,
            'method': method,
            'format': 'json'
        }
        if user is not None:
            payload['user'] = user
        if limit is not None:
            payload['limit'] = limit
        if time_period is not None:
            payload['period'] = time_period
        return payload

    async def get_fm_response(self, method, user=None, limit=None, time_period=None):
        """Receives the response from Last FM"""
        async with self.session.get(keys.last_fm_root_url, headers=keys.last_fm_headers, params=self.create_fm_payload(method, user, limit, time_period)) as response:
            return await response.json()

    async def get_fm_username(self, user_id):
        """Gets Last FM username from the DB."""
        return self.first_result(await self.conn.fetchrow("SELECT username FROM lastfm.users WHERE userid = $1", user_id))

    async def set_fm_username(self, user_id, username):
        """Sets Last FM username to the DB."""
        try:
            if await self.get_fm_username(user_id) is None:
                await self.conn.execute("INSERT INTO lastfm.users(userid, username) VALUES ($1, $2)", user_id, username)
            else:
                await self.conn.execute("UPDATE lastfm.users SET username = $1 WHERE userid = $2", username, user_id)
            return True
        except Exception as e:
            log.console(e)
            return e

    #################
    # ## PATREON ## #
    #################
    async def get_patreon_users(self):
        """Get the permanent patron users"""
        return await self.conn.fetch("SELECT userid from patreon.users")

    async def get_patreon_role_members(self, super=False):
        """Get the members in the patreon roles."""
        support_guild = self.client.get_guild(int(keys.bot_support_server_id))
        # API call will not show role.members
        if not super:
            patreon_role = support_guild.get_role(int(keys.patreon_role_id))
        else:
            patreon_role = support_guild.get_role(int(keys.patreon_super_role_id))
        return patreon_role.members

    async def check_if_patreon(self, user_id, super=False):
        """Check if the user is a patreon.
        There are two ways to check if a user ia a patreon.
        The first way is getting the members in the Patreon/Super Patreon Role.
        The second way is a table to check for permanent patreon users that are directly added by the bot owner.
        -- After modifying -> We take it straight from cache now.
        """
        if user_id in self.cache.patrons:
            if super:
                return self.cache.patrons.get(user_id) == super
            return True
        else:
            return False

    async def add_to_patreon(self, user_id):
        """Add user as a permanent patron."""
        try:
            user_id = int(user_id)
            await self.conn.execute("INSERT INTO patreon.users(userid) VALUES($1)", user_id)
            self.cache.patrons[user_id] = True
        except Exception as e:
            pass

    async def remove_from_patreon(self, user_id):
        """Remove user from being a permanent patron."""
        try:
            user_id = int(user_id)
            await self.conn.execute("DELETE FROM patreon.users WHERE userid = $1", user_id)
            self.cache.patrons.pop(user_id, None)
        except Exception as e:
            pass

    async def reset_patreon_cooldown(self, ctx):
        """Checks if the user is a patreon and resets their cooldown."""
        # Super Patrons also have the normal Patron role.
        if await self.check_if_patreon(ctx.author.id):
            ctx.command.reset_cooldown(ctx)

    ###################
    # ## MODERATOR ## #
    ###################
    async def add_welcome_message_server(self, channel_id, guild_id, message, enabled):
        """Adds a new welcome message server."""
        await self.conn.execute(
            "INSERT INTO general.welcome(channelid, serverid, message, enabled) VALUES($1, $2, $3, $4)", channel_id,
            guild_id, message, enabled)
        self.cache.welcome_messages[guild_id] = {"channel_id": channel_id, "message": message, "enabled": enabled}

    async def check_welcome_message_enabled(self, server_id):
        """Check if a welcome message server is enabled."""
        return self.cache.welcome_messages[server_id]['enabled'] == 1

    async def update_welcome_message_enabled(self, server_id, enabled):
        """Update a welcome message server's enabled status"""
        await self.conn.execute("UPDATE general.welcome SET enabled = $1 WHERE serverid = $2", int(enabled), server_id)
        self.cache.welcome_messages[server_id]['enabled'] = int(enabled)

    async def update_welcome_message_channel(self, server_id, channel_id):
        """Update the welcome message channel."""
        await self.conn.execute("UPDATE general.welcome SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        self.cache.welcome_messages[server_id]['channel_id'] = channel_id

    async def update_welcome_message(self, server_id, message):
        await self.conn.execute("UPDATE general.welcome SET message = $1 WHERE serverid = $2", message, server_id)
        self.cache.welcome_messages[server_id]['message'] = message

    ########################
    # ## CUSTOM COMMANDS## #
    ########################

    async def check_custom_command_name_exists(self, server_id, command_name):
        if server_id:
            custom_commands = self.cache.custom_commands.get(server_id)
            if custom_commands:
                if command_name.lower() in custom_commands:
                    return True
        return False

    async def add_custom_command(self, server_id, command_name, message):
        await self.conn.execute("INSERT INTO general.customcommands(serverid, commandname, message) VALUES ($1, $2, $3)", server_id, command_name, message)
        custom_commands = self.cache.custom_commands.get(server_id)
        if custom_commands:
            custom_commands[command_name] = message
        else:
            self.cache.custom_commands[server_id] = {command_name: message}

    async def remove_custom_command(self, server_id, command_name):
        await self.conn.execute("DELETE FROM general.customcommands WHERE serverid = $1 AND commandname = $2", server_id, command_name)
        custom_commands = self.cache.custom_commands.get(server_id)
        try:
            custom_commands.pop(command_name)
        except Exception as e:
            log.console(e)

    async def get_custom_command(self, server_id, command_name):
        commands = self.cache.custom_commands.get(server_id)
        return commands.get(command_name)
    ###################
    # ## BIAS GAME ## #
    ###################

    async def create_bias_game_image(self, first_idol_id, second_idol_id):
        """Uses thread pool to create bias game image to prevent IO blocking."""
        result = (self.thread_pool.submit(self.merge_images, first_idol_id, second_idol_id)).result()
        return f"{keys.bias_game_location}{first_idol_id}_{second_idol_id}.png"

    def merge_images(self, first_idol_id, second_idol_id):
        """Merge Idol Images if the merge doesn't exist already."""
        file_name = f"{first_idol_id}_{second_idol_id}.png"
        if not self.check_file_exists(f"{keys.bias_game_location}{file_name}"):
            # open the images.
            versus_image = Image.open(f'{keys.bias_game_location}versus.png')
            first_idol_image = Image.open(f'{keys.idol_avatar_location}{first_idol_id}_IDOL.png')
            second_idol_image = Image.open(f'{keys.idol_avatar_location}{second_idol_id}_IDOL.png')

            # define the dimensions
            idol_image_width = 150
            idol_image_height = 150
            first_image_area = (0, 0)
            second_image_area = (versus_image.width - idol_image_width, 0)
            image_size = (idol_image_width, idol_image_height)

            # resize the idol images
            first_idol_image = first_idol_image.resize(image_size)
            second_idol_image = second_idol_image.resize(image_size)

            # add the idol images onto the VS image.
            versus_image.paste(first_idol_image, first_image_area)
            versus_image.paste(second_idol_image, second_image_area)

            # save the versus image.
            versus_image.save(f"{keys.bias_game_location}{file_name}")

    @staticmethod
    def check_file_exists(file_name):
        return os.path.isfile(file_name)

    async def create_bias_game_bracket(self, all_games, user_id, bracket_winner):
        result = (self.thread_pool.submit(self.create_bracket, all_games, user_id, bracket_winner)).result()
        return f"{keys.bias_game_location}{user_id}.png"

    def create_bracket(self, all_games, user_id, bracket_winner):
        def get_battle_images(idol_1_id, idol_2_id):
            return Image.open(f'{keys.idol_avatar_location}{idol_1_id}_IDOL.png'), Image.open(f'{keys.idol_avatar_location}{idol_2_id}_IDOL.png')

        def resize_images(first_img, second_img, first_img_size, second_img_size):
            return first_img.resize(first_img_size), second_img.resize(second_img_size)

        def paste_image(first_idol_img, second_idol_img, first_img_area, second_img_area):
            bracket.paste(first_idol_img, first_img_area)
            bracket.paste(second_idol_img, second_img_area)

        bracket = Image.open(f'{keys.bias_game_location}bracket8.png')
        count = 1
        for c_round in all_games:
            if len(c_round) <= 4:
                for battle in c_round:
                    first_idol, second_idol = battle[0], battle[1]
                    first_idol_info = self.cache.stored_bracket_positions.get(count)
                    second_idol_info = self.cache.stored_bracket_positions.get(count + 1)

                    # get images
                    first_idol_image, second_idol_image = get_battle_images(first_idol.id, second_idol.id)

                    # resize images
                    first_idol_image, second_idol_image = resize_images(first_idol_image, second_idol_image, first_idol_info.get('img_size'), second_idol_info.get('img_size'))

                    # paste image to bracket
                    paste_image(first_idol_image, second_idol_image, first_idol_info.get('pos'), second_idol_info.get('pos'))

                    count = count + 2

        # add winner
        idol_info = self.cache.stored_bracket_positions.get(count)
        idol_image = Image.open(f'{keys.idol_avatar_location}{bracket_winner.id}_IDOL.png')
        idol_image = idol_image.resize(idol_info.get('img_size'))
        bracket.paste(idol_image, idol_info.get('pos'))
        bracket.save(f"{keys.bias_game_location}{user_id}.png")

    #######################
    # ## GENERAL GAMES ## #
    #######################

    async def stop_game(self, ctx, games):
        """Delete an ongoing game."""
        is_moderator = await self.check_if_moderator(ctx)
        game = self.find_game(ctx.channel, games)
        if game:
            if ctx.author.id == game.host or is_moderator:
                # these are passed by reference, so can directly remove from them.
                games.remove(game)
                return await game.end_game()
            else:
                return await ctx.send("> You must be a moderator or the host of the game in order to end the game.")
        return await ctx.send("> No game is currently in session.")

    @staticmethod
    def find_game(channel, games):
        """Return a game from a list of game objects if it exists in the channel."""
        for game in games:
            if game.channel == channel:
                return game

    #################
    # ## DATADOG ## #
    #################
    @staticmethod
    def initialize_data_dog():
        """Initialize The DataDog Class"""
        initialize()

    def send_metric(self, metric_name, value):
        """Send a metric value to DataDog."""
        # some values at 0 are important such as active games, this was put in place to make sure they are updated at 0.
        metrics_at_zero = ['bias_games', 'guessing_games', 'commands_per_minute', 'n_words_per_minute',
                           'bot_api_idol_calls', 'bot_api_translation_calls', 'messages_received_per_min',
                           'errors_per_minute', 'wolfram_per_minute', 'urban_per_minute']
        if metric_name in metrics_at_zero and not value:
            value = 0
        else:
            if not value:
                return
        if self.test_bot:
            metric_name = 'test_bot_' + metric_name
        else:
            metric_name = 'irene_' + metric_name
        api.Metric.send(metric=metric_name, points=[(time.time(), value)])

    #################
    # ## WEVERSE ## #
    #################
    async def add_weverse_channel(self, channel_id, community_name):
        """Add a channel to get updates for a community"""
        community_name = community_name.lower()
        await self.conn.execute("INSERT INTO weverse.channels(channelid, communityname) VALUES($1, $2)", channel_id, community_name)
        await self.add_weverse_channel_to_cache(channel_id, community_name)

    async def add_weverse_channel_to_cache(self, channel_id, community_name):
        """Add a weverse channel to cache."""
        community_name = community_name.lower()
        channels = self.cache.weverse_channels.get(community_name)
        if channels:
            channels.append([channel_id, None, False])
        else:
            self.cache.weverse_channels[community_name] = [[channel_id, None, False]]

    async def check_weverse_channel(self, channel_id, community_name):
        """Check if a channel is already getting updates for a community"""
        channels = self.cache.weverse_channels.get(community_name.lower())
        if channels:
            for channel in channels:
                if channel_id == channel[0]:
                    return True
        return False

    async def get_weverse_channels(self, community_name):
        """Get all of the channel ids for a specific community name"""
        return self.cache.weverse_channels.get(community_name.lower())

    async def delete_weverse_channel(self, channel_id, community_name):
        """Delete a community from a channel's updates."""
        community_name = community_name.lower()
        await self.conn.execute("DELETE FROM weverse.channels WHERE channelid = $1 AND communityname = $2", channel_id, community_name)
        channels = await self.get_weverse_channels(community_name)
        for channel in channels:
            if channel[0] == channel_id:
                if channels:
                    channels.remove(channel)
                else:
                    self.cache.weverse_channels.pop(community_name)

    async def add_weverse_role(self, channel_id, community_name, role_id):
        """Add a weverse role to notify."""
        await self.conn.execute("UPDATE weverse.channels SET roleid = $1 WHERE channelid = $2 AND communityname = $3", role_id, channel_id, community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, role_id)

    async def delete_weverse_role(self, channel_id, community_name):
        """Remove a weverse role from a server (no longer notifies a role)."""
        await self.conn.execute("UPDATE weverse.channels SET roleid = NULL WHERE channel_id = $1 AND communityname = $2", channel_id, community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, None)

    async def replace_cache_role_id(self, channel_id, community_name, role_id):
        """Replace the server role that gets notified on Weverse Updates."""
        channels = self.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[1] = role_id

    async def change_weverse_comment_status(self, channel_id, community_name, comments_disabled, updated=False):
        """Change a channel's subscription and whether or not they receive updates on comments."""
        comments_disabled = bool(comments_disabled)
        community_name = community_name.lower()
        if updated:
            await self.conn.execute("UPDATE weverse.channels SET commentsdisabled = $1 WHERE channelid = $2 AND communityname = $3", int(comments_disabled), channel_id, community_name)
        channels = self.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[2] = comments_disabled

    async def set_comment_embed(self, notification, embed_title):
        """Set Comment Embed for Weverse."""
        artist_comments = await self.weverse_client.fetch_artist_comments(notification.community_id, notification.contents_id)
        if not artist_comments:
            return
        comment = artist_comments[0]
        embed_description = f"**{notification.message}**\n\n" \
            f"Content: **{comment.body}**\n" \
            f"Translated Content: **{await self.weverse_client.translate(comment.id, is_comment=True, p_obj=comment, community_id=notification.community_id)}**"
        embed = await self.create_embed(title=embed_title, title_desc=embed_description)
        return embed

    async def set_post_embed(self, notification, embed_title):
        """Set Post Embed for Weverse."""
        post = self.weverse_client.get_post_by_id(notification.contents_id)
        if post:
            # artist = self.weverse_client.get_artist_by_id(notification.artist_id)
            embed_description = f"**{notification.message}**\n\n" \
                f"Artist: **{post.artist.name} ({post.artist.list_name[0]})**\n" \
                f"Content: **{post.body}**\n" \
                f"Translated Content: **{await self.weverse_client.translate(post.id, is_post=True, p_obj=post, community_id=notification.community_id)}**"
            embed = await self.create_embed(title=embed_title, title_desc=embed_description)
            message = "\n".join([await self.download_weverse_post(photo.original_img_url, photo.file_name) for photo in post.photos])
            return embed, message
        return None, None

    async def download_weverse_post(self, url, file_name):
        """Downloads an image url and returns image host url."""
        async with self.session.get(url) as resp:
            fd = await aiofiles.open(keys.weverse_image_folder + file_name, mode='wb')
            await fd.write(await resp.read())
        return f"https://images.irenebot.com/weverse/{file_name}"

    async def set_media_embed(self, notification, embed_title):
        """Set Media Embed for Weverse."""
        media = self.weverse_client.get_media_by_id(notification.contents_id)
        if media:
            embed_description = f"**{notification.message}**\n\n" \
                f"Title: **{media.title}**\n" \
                f"Content: **{media.body}**\n"
            embed = await self.create_embed(title=embed_title, title_desc=embed_description)
            message = media.video_link
            return embed, message
        return None, None

    async def send_weverse_to_channel(self, channel_info, message_text, embed, is_comment, community_name):
        channel_id = channel_info[0]
        role_id = channel_info[1]
        comments_disabled = channel_info[2]
        if not (is_comment and comments_disabled):
            try:
                channel = self.client.get_channel(channel_id)
                if not channel:
                    # fetch channel instead (assuming discord.py cache did not load)
                    channel = await self.client.fetch_channel(channel_id)
            except Exception as e:
                # remove the channel from future updates as it cannot be found.
                return await self.delete_weverse_channel(channel_id, community_name.lower())
            try:
                await channel.send(embed=embed)
                if message_text:
                    # Since an embed already exists, any individual content will not load
                    # as an embed -> Make it it's own message.
                    if role_id:
                        message_text = f"<@&{role_id}>\n{message_text}"
                    await channel.send(message_text)
            except Exception as e:
                # no permission to post
                return

    #########################
    # ## SelfAssignRoles ## #
    #########################
    async def add_self_role(self, role_id, role_name, server_id):
        """Adds a self-assignable role to a server."""
        role_info = [role_id, role_name]
        await self.conn.execute("INSERT INTO selfassignroles.roles(roleid, rolename, serverid) VALUES ($1, $2, $3)", role_id, role_name, server_id)
        roles = await self.get_assignable_server_roles(server_id)
        if roles:
            roles.append(role_info)
        else:
            cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info:
                self.cache.assignable_roles[server_id] = {}
                cache_info = self.cache.assignable_roles.get(server_id)
            cache_info['roles'] = [role_info]

    async def get_self_role(self, message_content, server_id):
        """Returns a discord.Object that can be used for adding or removing a role to a member."""
        roles = await self.get_assignable_server_roles(server_id)
        if roles:
            for role in roles:
                role_id = role[0]
                role_name = role[1]
                if role_name.lower() == message_content.lower():
                    return discord.Object(role_id), role_name
        return None, None

    async def check_self_role_exists(self, role_id, role_name, server_id):
        """Check if a role exists as a self-assignable role in a server."""
        cache_info = self.cache.assignable_roles.get(server_id)
        if cache_info:
            roles = cache_info.get('roles')
            if roles:
                for role in roles:
                    c_role_id = role[0]
                    c_role_name = role[1]
                    if c_role_id == role_id or c_role_name == role_name:
                        return True
        return False

    async def remove_self_role(self, role_name, server_id):
        """Remove a self-assignable role from a server."""
        await self.conn.execute("DELETE FROM selfassignroles.roles WHERE rolename = $1 AND serverid = $2", role_name, server_id)
        cache_info = self.cache.assignable_roles.get(server_id)
        if cache_info:
            roles = cache_info.get('roles')
            if roles:
                for role in roles:
                    if role[1].lower() == role_name.lower():
                        roles.remove(role)

    async def modify_channel_role(self, channel_id, server_id):
        """Add or Change a server's self-assignable role channel."""
        def update_cache():
            cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info:
                self.cache.assignable_roles[server_id] = {'channel_id': channel_id}
            else:
                cache_info['channel_id'] = channel_id

        amount_of_results = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM selfassignroles.channels WHERE serverid = $1", server_id))
        if amount_of_results:
            update_cache()
            return await self.conn.execute("UPDATE selfassignroles.channels SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        await self.conn.execute("INSERT INTO selfassignroles.channels(channelid, serverid) VALUES($1, $2)", channel_id, server_id)
        update_cache()

    async def get_assignable_server_roles(self, server_id):
        """Get all the self-assignable roles from a server."""
        results = self.cache.assignable_roles.get(server_id)
        if results:
            return results.get('roles')

    async def check_for_self_assignable_role(self, message):
        """Main process for processing self-assignable roles."""
        try:
            author = message.author
            server_id = await self.get_server_id(message)
            if await self.check_self_assignable_channel(server_id, message.channel):
                if message.content:
                    prefix = message.content[0]
                    if len(message.content) > 1:
                        msg = message.content[1:len(message.content)]
                    else:
                        return
                    role, role_name = await self.get_self_role(msg, server_id)
                    await self.process_member_roles(message, role, role_name, prefix, author)
        except Exception as e:
            log.console(e)

    async def check_self_assignable_channel(self, server_id, channel):
        """Check if a channel is a self assignable role channel."""
        if server_id:
            cache_info = self.cache.assignable_roles.get(server_id)
            if cache_info:
                channel_id = cache_info.get('channel_id')
                if channel_id:
                    if channel_id == channel.id:
                        return True

    @staticmethod
    async def check_member_has_role(member_roles, role_id):
        """Check if a member has a role"""
        for role in member_roles:
            if role.id == role_id:
                return True

    async def process_member_roles(self, message, role, role_name, prefix, author):
        """Adds or removes a (Self-Assignable) role from a member"""
        if role:
            if prefix == '-':
                if await self.check_member_has_role(author.roles, role.id):
                    await author.remove_roles(role, reason="Self-Assignable Role", atomic=True)
                    return await message.channel.send(f"> {author.display_name}, You no longer have the {role_name} role.", delete_after=10)
                else:
                    return await message.channel.send(f"> {author.display_name}, You do not have the {role_name} role.", delete_after=10)
            elif prefix == '+':
                if await self.check_member_has_role(author.roles, role.id):
                    return await message.channel.send(f"> {author.display_name}, You already have the {role_name} role.", delete_after=10)
                await author.add_roles(role, reason="Self-Assignable Role", atomic=True)
                return await message.channel.send(f"> {author.display_name}, You have been given the {role_name} role.", delete_after=10)
            await message.delete()

    ##################
    # ## REMINDER ## #
    ##################

    @staticmethod
    async def determine_time_type(user_input):
        """Determine if time is relative time or absolute time
        relative time: remind me to _____ in 6 days
        absolute time: remind me to _____ at 6PM"""

        in_index = user_input.rfind(" in ")
        at_index = user_input.rfind(" at ")
        if in_index == at_index:
            return None, None
        if in_index > at_index:
            return True, in_index
        return False, at_index

    @staticmethod
    async def process_reminder_reason(user_input, type_index):
        """Return the reminder reason that comes before in/at"""
        user_text = user_input.split()
        if user_text[0].lower() == "to":
            return user_input[3: type_index]
        return user_input[0: type_index]

    async def process_reminder_time(self, user_input, type_index, is_relative_time, user_id):
        """Return the datetime of the reminder depending on the time format"""
        remind_time = user_input[type_index + len(" in "): len(user_input)]

        if is_relative_time:
            if await self.process_relative_time_input(remind_time) > 2 * 3.154e7:  # 2 years in seconds
                raise exceptions.TooLarge
            return datetime.datetime.now() + datetime.timedelta(seconds=await self.process_relative_time_input(remind_time))

        return await self.process_absolute_time_input(remind_time, user_id)

    @staticmethod
    async def process_relative_time_input(time_input):
        """Returns the relative time of the input in seconds"""
        year_aliases = ["years", "year", "yr", "y"]
        month_aliases = ["months", "month", "mo"]
        day_aliases = ["days", "day", "d"]
        hour_aliases = ["hours", "hour", "hrs", "hr", "h"]
        minute_aliases = ["minutes", "minute", "mins", "min", "m"]
        second_aliases = ["seconds", "second", "secs", "sec", "s"]
        time_units = [[year_aliases, 3.154e7], [month_aliases, 2.628e6], [day_aliases, 8.64e4], [hour_aliases, 3600], [minute_aliases, 60], [second_aliases, 1]]

        remind_time = 0  # in seconds
        input_elements = re.findall(r"[^\W\d_]+|\d+", time_input)

        all_aliases = [alias for time_unit in time_units for alias in time_unit[0]]
        if not any(alias in input_elements for alias in all_aliases):
            raise exceptions.ImproperFormat

        for time_element in input_elements:
            try:
                int(time_element)
            except Exception as e:
                # purposefully creating an error to locate which elements are words vs integers.
                for time_unit in time_units:
                    if time_element in time_unit[0]:
                        remind_time += time_unit[1] * int(input_elements[input_elements.index(time_element) - 1])
        return remind_time

    async def process_absolute_time_input(self, time_input, user_id):
        """Returns the absolute date time of the input"""
        user_timezone = await self.get_user_timezone(user_id)
        if not user_timezone:
            raise exceptions.NoTimeZone
        cal = parsedatetime.Calendar()
        try:
            datetime_obj, _ = cal.parseDT(datetimeString=time_input, tzinfo=pytz.timezone(user_timezone))
        except:
            raise exceptions.ImproperFormat
        return datetime_obj

    async def get_user_timezone(self, user_id):
        """Returns the user's timezone"""
        return self.cache.timezones.get(user_id)

    async def set_user_timezone(self, user_id, timezone):
        """Set user timezone"""
        user_timezone = self.cache.timezones.get(user_id)
        self.cache.timezones[user_id] = timezone
        if user_timezone:
            await self.conn.execute("UPDATE reminders.timezones SET timezone = $1 WHERE userid = $2", timezone, user_id)
        else:
            await self.conn.execute("INSERT INTO reminders.timezones(userid, timezone) VALUES ($1, $2)", user_id, timezone)

    async def remove_user_timezone(self, user_id):
        """Remove user timezone"""
        try:
            self.cache.timezones.pop(user_id)
            await self.conn.execute("DELETE FROM reminders.timezones WHERE userid = $1", user_id)
        except:
            pass

    @staticmethod
    async def process_timezone_input(timezone, country_code):
        """Convert timezone abbreviation and country code to standard timezone name - taken from stackoverflow"""
        try:
            timezone = timezone.upper()
            country_code = country_code.upper()
        except:
            pass

        # see if it's already a valid time zone name
        if timezone in pytz.all_timezones:
            return timezone

        # if it's a number value, then use the Etc/GMT code
        try:
            offset = int(timezone)
            if offset > 0:
                offset = '+' + str(offset)
            else:
                offset = str(offset)
            return 'Etc/GMT' + offset
        except ValueError:
            pass

        # look up the abbreviation
        country_tzones = None
        try:
            country_tzones = pytz.country_timezones[country_code]
        except:
            pass

        set_zones = set()
        if country_tzones and len(country_tzones):
            for name in country_tzones:
                tzone = pytz.timezone(name)
                tzabbrev = datetime.datetime.now(tzone).tzname()
                if tzabbrev.upper() == timezone.upper():
                    set_zones.add(name)

            if len(set_zones):
                return min(set_zones, key=len)

            # none matched, at least pick one in the right country
            return min(country_tzones, key=len)

        # invalid country, just try to match the timezone abbreviation to any time zone
        for name in pytz.all_timezones:
            tzone = pytz.timezone(name)
            tzabbrev = datetime.datetime.now(tzone).tzname()
            if tzabbrev.upper() == timezone.upper():
                set_zones.add(name)

        if not set_zones:
            return None
        return min(set_zones, key=len)

    async def set_reminder(self, remind_reason, remind_time, user_id):
        """Add reminder date to cache and db."""
        await self.conn.execute("INSERT INTO reminders.reminders(userid, reason, timestamp) VALUES ($1, $2, $3)", user_id, remind_reason, remind_time)
        remind_id = self.first_result(await self.conn.fetchrow("SELECT id FROM reminders.reminders WHERE userid=$1 AND reason=$2 AND timestamp=$3 ORDER BY id DESC", user_id, remind_reason, remind_time))
        user_reminders = self.cache.reminders.get(user_id)
        remind_info = [remind_id, remind_reason, remind_time]
        if user_reminders:
            user_reminders.append(remind_info)
        else:
            self.cache.reminders[user_id] = [remind_info]

    async def get_reminders(self, user_id):
        """Get the reminders of a user"""
        return self.cache.reminders.get(user_id)

    async def remove_user_reminder(self, user_id, reminder_id):
        """Remove a reminder from the cache and the database."""
        try:
            # remove from cache
            reminders = self.cache.reminders.get(user_id)
            if reminders:
                for reminder in reminders:
                    current_reminder_id = reminder[0]
                    if current_reminder_id == reminder_id:
                        reminders.remove(reminder)
            print(reminders)
        except Exception as e:
            log.console(e)
        await self.conn.execute("DELETE FROM reminders.reminders WHERE id = $1", reminder_id)

    async def get_all_reminders_from_db(self):
        """Get all reminders from the db (all users)"""
        return await self.conn.fetch("SELECT id, userid, reason, timestamp FROM reminders.reminders")

    async def get_all_timezones_from_db(self):
        """Get all timezones from the db (all users)"""
        return await self.conn.fetch("SELECT userid, timezone FROM reminders.timezones")


class Idol:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.full_name = kwargs.get('fullname')
        self.stage_name = kwargs.get('stagename')
        self.former_full_name = kwargs.get('formerfullname')
        self.former_stage_name = kwargs.get('formerstagename')
        self.birth_date = kwargs.get('birthdate')
        self.birth_country = kwargs.get('birthcountry')
        self.birth_city = kwargs.get('birthcity')
        self.gender = kwargs.get('gender')
        self.description = kwargs.get('description')
        self.height = kwargs.get('height')
        self.twitter = kwargs.get('twitter')
        self.youtube = kwargs.get('youtube')
        self.melon = kwargs.get('melon')
        self.instagram = kwargs.get('instagram')
        self.vlive = kwargs.get('vlive')
        self.spotify = kwargs.get('spotify')
        self.fancafe = kwargs.get('fancafe')
        self.facebook = kwargs.get('facebook')
        self.tiktok = kwargs.get('tiktok')
        self.aliases = []
        self.local_aliases = {}  # server_id: [aliases]
        self.groups = []
        self.zodiac = kwargs.get('zodiac')
        self.thumbnail = kwargs.get('thumbnail')
        self.banner = kwargs.get('banner')
        self.blood_type = kwargs.get('bloodtype')
        self.photo_count = 0
        # amount of times the idol has been called.
        self.called = 0
        self.tags = kwargs.get('tags')
        if self.tags:
            self.tags = self.tags.split(',')


class Group:
    def __init__(self, **kwargs):
        self.id = kwargs.get('groupid')
        self.name = kwargs.get('groupname')
        self.debut_date = kwargs.get('debutdate')
        self.disband_date = kwargs.get('disbanddate')
        self.description = kwargs.get('description')
        self.twitter = kwargs.get('twitter')
        self.youtube = kwargs.get('youtube')
        self.melon = kwargs.get('melon')
        self.instagram = kwargs.get('instagram')
        self.vlive = kwargs.get('vlive')
        self.spotify = kwargs.get('spotify')
        self.fancafe = kwargs.get('fancafe')
        self.facebook = kwargs.get('facebook')
        self.tiktok = kwargs.get('tiktok')
        self.aliases = []
        self.local_aliases = {}  # server_id: [aliases]
        self.members = []
        self.fandom = kwargs.get('fandom')
        self.company = kwargs.get('company')
        self.website = kwargs.get('website')
        self.thumbnail = kwargs.get('thumbnail')
        self.banner = kwargs.get('banner')
        self.gender = kwargs.get('gender')
        self.photo_count = 0
        self.tags = kwargs.get('tags')
        if self.tags:
            self.tags = self.tags.split(',')


resources = Utility()
