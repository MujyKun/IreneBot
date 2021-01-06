from Utility import resources as ex
from discord.ext import tasks
from module import logger as log
from module.keys import dead_image_channel_id
import time
import asyncio
import datetime


# noinspection PyBroadException,PyPep8
class Cache:

    @staticmethod
    async def process_cache_time(method, name):
        """Process the cache time."""
        past_time = time.time()
        result = await method()
        if result is None or result:  # expecting False on methods that fail to load, do not simplify None.
            log.console(f"Cache for {name} Created in {await ex.u_miscellaneous.get_cooldown_time(time.time() - past_time)}.")
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
        await self.process_cache_time(self.create_guessing_game_cache, "Guessing Game Scores")
        if not ex.test_bot and not ex.weverse_client.cache_loaded:
            # noinspection PyUnusedLocal
            task = asyncio.create_task(self.process_cache_time(ex.weverse_client.start, "Weverse"))
        log.console(f"Cache Completely Created in {await ex.u_miscellaneous.get_cooldown_time(time.time() - past_time)}.")

    @staticmethod
    async def create_guessing_game_cache():
        ex.cache.guessing_game_counter = {}
        all_scores = await ex.conn.fetch("SELECT userid, easy, medium, hard FROM stats.guessinggame")
        for user_id, easy_score, medium_score, hard_score in all_scores:
            ex.cache.guessing_game_counter[user_id] = {"easy": easy_score, "medium": medium_score, "hard": hard_score}

    @staticmethod
    async def create_timezone_cache():
        ex.cache.timezones = {}  # reset cache
        timezones = await ex.u_reminder.get_all_timezones_from_db()
        for user_id, timezone in timezones:
            ex.cache.timezones[user_id] = timezone

    @staticmethod
    async def create_reminder_cache():
        """Create cache for reminders"""
        ex.cache.reminders = {}  # reset cache
        all_reminders = await ex.u_reminder.get_all_reminders_from_db()
        for reason_id, user_id, reason, time_stamp in all_reminders:
            reason_list = [reason_id, reason, time_stamp]
            user_reminder = ex.cache.reminders.get(user_id)
            if user_reminder:
                user_reminder.append(reason_list)
            else:
                ex.cache.reminders[user_id] = [reason_list]

    @staticmethod
    async def create_self_assignable_role_cache():
        """Create cache for self assignable roles"""
        all_roles = await ex.conn.fetch("SELECT roleid, rolename, serverid FROM selfassignroles.roles")
        all_channels = await ex.conn.fetch("SELECT channelid, serverid FROM selfassignroles.channels")
        for role_id, role_name, server_id in all_roles:
            cache_info = ex.cache.assignable_roles.get(server_id)
            if not cache_info:
                ex.cache.assignable_roles[server_id] = {}
                cache_info = ex.cache.assignable_roles.get(server_id)
            if not cache_info.get('roles'):
                cache_info['roles'] = [[role_id, role_name]]
            else:
                cache_info['roles'].append([role_id, role_name])
        for channel_id, server_id in all_channels:
            cache_info = ex.cache.assignable_roles.get(server_id)
            if cache_info:
                cache_info['channel_id'] = channel_id
            else:
                ex.cache.assignable_roles[server_id] = {'channel_id': channel_id}

    @staticmethod
    async def create_weverse_channel_cache():
        """Create cache for channels that are following a community on weverse."""
        all_channels = await ex.conn.fetch("SELECT channelid, communityname, roleid, commentsdisabled FROM weverse.channels")
        for channel_id, community_name, role_id, comments_disabled in all_channels:
            await ex.u_weverse.add_weverse_channel_to_cache(channel_id, community_name)
            await ex.u_weverse.add_weverse_role(channel_id, community_name, role_id)
            await ex.u_weverse.change_weverse_comment_status(channel_id, community_name, comments_disabled)

    async def update_command_counter(self):
        """Updates Cache for command counter and sessions"""
        ex.cache.command_counter = {}
        session_id = await self.get_session_id()
        all_commands = await ex.conn.fetch("SELECT commandname, count FROM stats.commands WHERE sessionid = $1", session_id)
        for command_name, count in all_commands:
            ex.cache.command_counter[command_name] = count
        ex.cache.current_session = ex.first_result(
            await ex.conn.fetchrow("SELECT session FROM stats.sessions WHERE date = $1", datetime.date.today()))

    @staticmethod
    async def create_restricted_channel_cache():
        """Create restricted idol channel cache"""
        restricted_channels = await ex.conn.fetch("SELECT channelid, serverid, sendhere FROM groupmembers.restricted")
        for channel_id, server_id, send_here in restricted_channels:
            ex.cache.restricted_channels[channel_id] = [server_id, send_here]

    @staticmethod
    async def create_bot_command_cache():
        """Create custom command cache"""
        server_commands = await ex.conn.fetch("SELECT serverid, commandname, message FROM general.customcommands")
        ex.cache.custom_commands = {}
        for server_id, command_name, message in server_commands:
            cache_info = ex.cache.custom_commands.get(server_id)
            if cache_info:
                cache_info[command_name] = message
            else:
                ex.cache.custom_commands[server_id] = {command_name: message}

    @staticmethod
    async def create_bot_status_cache():
        statuses = await ex.conn.fetch("SELECT status FROM general.botstatus")
        ex.cache.bot_statuses = [status[0] for status in statuses] or None

    @staticmethod
    async def create_dead_link_cache():
        """Creates Dead Link Cache"""
        ex.cache.dead_image_cache = {}
        try:
            ex.cache.dead_image_channel = await ex.client.fetch_channel(dead_image_channel_id)
        except:
            pass
        dead_images = await ex.conn.fetch("SELECT deadlink, userid, messageid, idolid, guessinggame FROM groupmembers.deadlinkfromuser")
        for dead_link, user_id, message_id, idol_id, guessing_game in dead_images:
            ex.cache.dead_image_cache[message_id] = [dead_link, user_id, idol_id, guessing_game]

    @staticmethod
    async def create_idol_cache():
        """Create Idol Objects and store them as cache."""
        ex.cache.idols = []
        for idol in await ex.u_group_members.get_db_all_members():
            idol_obj = ex.u_group_members.Idol(**idol)
            idol_obj.aliases, idol_obj.local_aliases = await ex.u_group_members.get_db_aliases(idol_obj.id)
            # add all group ids and remove potential duplicates
            idol_obj.groups = list(dict.fromkeys(await ex.u_group_members.get_db_groups_from_member(idol_obj.id)))
            idol_obj.called = await ex.u_group_members.get_db_idol_called(idol_obj.id)
            idol_obj.photo_count = ex.cache.idol_photos.get(idol_obj.id) or 0
            ex.cache.idols.append(idol_obj)

    @staticmethod
    async def create_group_cache():
        """Create Group Objects and store them as cache"""
        ex.cache.groups = []
        for group in await ex.u_group_members.get_all_groups():
            group_obj = ex.u_group_members.Group(**group)
            group_obj.aliases, group_obj.local_aliases = await ex.u_group_members.get_db_aliases(group_obj.id, group=True)
            # add all idol ids and remove potential duplicates
            group_obj.members = list(dict.fromkeys(await ex.u_group_members.get_db_members_in_group(group_id=group_obj.id)))
            group_obj.photo_count = ex.cache.group_photos.get(group_obj.id) or 0
            ex.cache.groups.append(group_obj)

    async def process_session(self):
        """Sets the new session id, total used, and time format for distinguishing days."""
        current_time_format = datetime.date.today()
        if ex.cache.session_id is None:
            if ex.cache.total_used is None:
                ex.cache.total_used = (ex.first_result(await ex.conn.fetchrow("SELECT totalused FROM stats.sessions ORDER BY totalused DESC"))) or 0
            try:
                await ex.conn.execute("INSERT INTO stats.sessions(totalused, session, date) VALUES ($1, $2, $3)", ex.cache.total_used, 0, current_time_format)
            except:
                # session for today already exists.
                pass
            ex.cache.session_id = ex.first_result(await ex.conn.fetchrow("SELECT sessionid FROM stats.sessions WHERE date = $1", current_time_format))
            ex.cache.session_time_format = current_time_format
        else:
            # check that the date is correct, and if not, call get_session_id to get the new session id.
            if current_time_format != ex.cache.session_time_format:
                ex.cache.current_session = 0
                ex.cache.session_id = None
                ex.cache.session_id = await self.get_session_id()

    async def get_session_id(self):
        """Force get the session id, this will also set total used and the session id."""
        await self.process_session()
        return ex.cache.session_id

    @staticmethod
    async def update_n_word_counter():
        """Update NWord Cache"""
        ex.cache.n_word_counter = {}
        user_info = await ex.conn.fetch("SELECT userid, nword FROM general.nword")
        for user_id, n_word_counter in user_info:
            ex.cache.n_word_counter[user_id] = n_word_counter

    @staticmethod
    async def update_temp_channels():
        """Create the cache for temp channels."""
        ex.cache.temp_channels = {}
        channels = await ex.u_miscellaneous.get_temp_channels()
        for channel_id, delay in channels:
            removal_time = delay
            if removal_time < 60:
                removal_time = 60
            ex.cache.temp_channels[channel_id] = removal_time

    @staticmethod
    async def update_welcome_message_cache():
        """Create the cache for welcome messages."""
        ex.cache.welcome_messages = {}
        info = await ex.conn.fetch("SELECT channelid, serverid, message, enabled FROM general.welcome")
        for channel_id, server_id, message_id, enabled in info:
            ex.cache.welcome_messages[server_id] = {"channel_id": channel_id, "message": message_id, "enabled": enabled}

    @staticmethod
    async def update_server_prefixes():
        """Create the cache for server prefixes."""
        ex.cache.server_prefixes = {}
        info = await ex.conn.fetch("SELECT serverid, prefix FROM general.serverprefix")
        for server_id, prefix in info:
            ex.cache.server_prefixes[server_id] = prefix

    @staticmethod
    async def update_logging_channels():
        """Create the cache for logged servers and channels."""
        ex.cache.logged_channels = {}
        ex.cache.list_of_logged_channels = []
        logged_servers = await ex.conn.fetch("SELECT id, serverid, channelid, sendall FROM logging.servers WHERE status = $1", 1)
        for p_id, server_id, channel_id, send_all in logged_servers:
            channels = await ex.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1", p_id)
            for channel in channels:
                ex.cache.list_of_logged_channels.append(channel[0])
            ex.cache.logged_channels[server_id] = {
                "send_all": send_all,
                "logging_channel": channel_id,
                "channels": [channel[0] for channel in channels]
            }

    @staticmethod
    async def update_bot_bans():
        """Create the cache for banned users from the bot."""
        ex.cache.bot_banned = []
        banned_users = await ex.conn.fetch("SELECT userid FROM general.blacklisted")
        for user in banned_users:
            user_id = user[0]
            ex.cache.bot_banned.append(user_id)

    @staticmethod
    async def update_mod_mail():
        """Create the cache for existing mod mail"""
        ex.cache.mod_mail = {}
        mod_mail = await ex.conn.fetch("SELECT userid, channelid FROM general.modmail")
        for user_id, channel_id in mod_mail:
            ex.cache.mod_mail[user_id] = [channel_id]

    @staticmethod
    async def update_patreons():
        """Create the cache for Patrons."""
        try:
            ex.cache.patrons = {}
            permanent_patrons = await ex.u_patreon.get_patreon_users()
            # normal patrons contains super patrons as well
            normal_patrons = [patron.id for patron in await ex.u_patreon.get_patreon_role_members(super_patron=False)]
            super_patrons = [patron.id for patron in await ex.u_patreon.get_patreon_role_members(super_patron=True)]

            # the reason for db cache is because of the new discord rate limit
            # where it now takes 20+ minutes for discord cache to fully load, meaning we can only
            # access the roles after 20 minutes on boot.
            # this is an alternative to get patreons instantly and later modifying the cache after the cache loads.
            # remove any patrons from db set cache that should not exist or should be modified.
            cached_patrons = await ex.conn.fetch("SELECT userid, super FROM patreon.cache")
            for user_id, super_patron in cached_patrons:
                if user_id not in normal_patrons:
                    # they are not a patron at all, so remove them from db cache
                    await ex.conn.execute("DELETE FROM patreon.cache WHERE userid = $1", user_id)
                elif user_id in super_patrons and not super_patron:
                    # if they are a super patron but their db is cache is a normal patron
                    await ex.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 1, user_id)
                elif user_id not in super_patrons and super_patron:
                    # if they are not a super patron, but the db cache says they are.
                    await ex.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 0, user_id)
            cached_patrons = [patron[0] for patron in cached_patrons]  # list of user ids removing patron status.

            # fix db cache and live Irene cache
            for patron in normal_patrons:
                if patron not in cached_patrons:
                    # patron includes both normal and super patrons.
                    await ex.conn.execute("INSERT INTO patreon.cache(userid, super) VALUES($1, $2)", patron, 0)
                ex.cache.patrons[patron] = False
            # super patrons must go after normal patrons to have a proper boolean set because
            # super patrons have both roles.
            for patron in super_patrons:
                if patron not in cached_patrons:
                    await ex.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", 1, patron)
                ex.cache.patrons[patron] = True
            for patron in permanent_patrons:
                ex.cache.patrons[patron[0]] = True
            return True
        except:
            return False

    @staticmethod
    async def update_user_notifications():
        """Set the cache for user phrases"""
        ex.cache.user_notifications = []
        notifications = await ex.conn.fetch("SELECT guildid,userid,phrase FROM general.notifications")
        for guild_id, user_id, phrase in notifications:
            ex.cache.user_notifications.append([guild_id, user_id, phrase])

    @staticmethod
    async def update_groups():
        """Set cache for group photo count"""
        ex.cache.group_photos = {}
        all_group_counts = await ex.conn.fetch("SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id GROUP BY g.groupid ORDER BY g.groupname")
        for group in all_group_counts:
            ex.cache.group_photos[group[0]] = group[2]

    @staticmethod
    async def update_idols():
        """Set cache for idol photo count"""
        ex.cache.idol_photos = {}
        all_idol_counts = await ex.conn.fetch("SELECT memberid, COUNT(link) FROM groupmembers.imagelinks GROUP BY memberid")
        for idol_id, count in all_idol_counts:
            ex.cache.idol_photos[idol_id] = count

    @tasks.loop(seconds=0, minutes=0, hours=12, reconnect=True)
    async def update_cache(self):
        """Looped every 12 hours to update the cache in case of anything faulty."""
        while not ex.conn:
            await asyncio.sleep(1)
        await self.create_cache()

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def update_patron_cache(self):
        """Looped until patron cache is loaded.
        This was added due to intents slowing d.py cache loading rate.
        """
        # create a temporary patron list based on the db cache while waiting for the discord cache to load
        if ex.conn:
            if not ex.temp_patrons_loaded:
                ex.cache.patrons = {}
                cached_patrons = await ex.conn.fetch("SELECT userid, super FROM patreon.cache")
                for user_id, super_patron in cached_patrons:
                    ex.cache.patrons[user_id] = bool(super_patron)
                ex.temp_patrons_loaded = True
            while not ex.discord_cache_loaded:
                await asyncio.sleep(1)
            if await self.process_cache_time(self.update_patreons, "Patrons"):
                self.update_patron_cache_hour.start()
                self.update_patron_cache.stop()

    @tasks.loop(seconds=0, minutes=0, hours=1, reconnect=True)
    async def update_patron_cache_hour(self):
        """Update Patron Cache every hour in the case of unaccounted errors."""
        # this is to make sure on the first run it doesn't update since it is created elsewhere.
        if ex.loop_count:
            await self.process_cache_time(self.update_patreons, "Patrons")
        ex.loop_count += 1

    @tasks.loop(seconds=0, minutes=1, hours=0, reconnect=True)
    async def send_cache_data_to_data_dog(self):
        """Sends metric information about cache to data dog every minute."""
        try:
            if ex.thread_pool:
                active_user_reminders = 0
                for user_id in ex.cache.reminders:
                    reminders = ex.cache.reminders.get(user_id)
                    if reminders:
                        active_user_reminders += len(reminders)
                metric_info = {
                    'total_commands_used': ex.cache.total_used,
                    'bias_games': len(ex.cache.bias_games),
                    'guessing_games': len(ex.cache.guessing_games),
                    'patrons': len(ex.cache.patrons),
                    'custom_server_prefixes': len(ex.cache.server_prefixes),
                    'session_commands_used': ex.cache.current_session,
                    'user_notifications': len(ex.cache.user_notifications),
                    'mod_mail': len(ex.cache.mod_mail),
                    'banned_from_bot': len(ex.cache.bot_banned),
                    'logged_servers': len(ex.cache.logged_channels),
                    # server count is based on discord.py guild cache which takes a large amount of time to load fully.
                    # There may be inaccurate data points on a new instance of the bot due to the amount of time it takes.
                    'server_count': len(ex.client.guilds),
                    'welcome_messages': len(ex.cache.welcome_messages),
                    'temp_channels': len(ex.cache.temp_channels),
                    'amount_of_idols': len(ex.cache.idols),
                    'amount_of_groups': len(ex.cache.groups),
                    'channels_restricted': len(ex.cache.restricted_channels),
                    'amount_of_bot_statuses': len(ex.cache.bot_statuses),
                    'commands_per_minute': ex.cache.commands_per_minute,
                    'amount_of_custom_commands': len(ex.cache.custom_commands),
                    'discord_ping': ex.get_ping(),
                    'n_words_per_minute': ex.cache.n_words_per_minute,
                    'bot_api_idol_calls': ex.cache.bot_api_idol_calls,
                    'bot_api_translation_calls': ex.cache.bot_api_translation_calls,
                    'messages_received_per_min': ex.cache.messages_received_per_minute,
                    'errors_per_minute': ex.cache.errors_per_minute,
                    'wolfram_per_minute': ex.cache.wolfram_per_minute,
                    'urban_per_minute': ex.cache.urban_per_minute,
                    'active_user_reminders': active_user_reminders
                }

                # set all per minute metrics to 0 since this is a 60 second loop.
                ex.cache.n_words_per_minute = 0
                ex.cache.commands_per_minute = 0
                ex.cache.bot_api_idol_calls = 0
                ex.cache.bot_api_translation_calls = 0
                ex.cache.messages_received_per_minute = 0
                ex.cache.errors_per_minute = 0
                ex.cache.wolfram_per_minute = 0
                ex.cache.urban_per_minute = 0
                for metric_name in metric_info:
                    try:
                        metric_value = metric_info.get(metric_name)
                        # add to thread pool to prevent blocking.
                        # noinspection PyUnusedLocal
                        result = (ex.thread_pool.submit(ex.u_data_dog.send_metric, metric_name, metric_value)).result()
                    except Exception as e:
                        log.console(e)
        except Exception as e:
            # loop appears to stop working after a while and no errors were recognized in log file
            # adding this try except to see if issue continues.
            log.console(e)
