from module import keys, logger as log, cache
from discord.ext import tasks
import datetime
import discord
import random
import asyncio
import aiofiles
import os
import math
import tweepy
import filetype
import json
import time


"""
Utility.py
Resource Center for Irene
Any potentially useful/repeated functions will end up here
"""


class Utility:
    def __init__(self):
        self.test_bot = None  # this is changed in run.py
        self.client = keys.client
        self.session = keys.client_session
        self.conn = None
        self.cache = cache.Cache()
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.api = tweepy.API(auth)

    ##################
    # ## DATABASE ## #
    ##################
    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def set_db_connection(self):
        """Looping Until A Stable Connection to DB is formed. This is to confirm Irene starts before the DB connects."""
        if self.client.loop.is_running():
            try:
                self.conn = await self.get_db_connection()
                # Delete all active blackjack games
                await self.delete_all_games()
            except Exception as e:
                log.console(e)
            self.set_db_connection.stop()

    @tasks.loop(seconds=0, minutes=1, reconnect=True)
    async def show_irene_alive(self):
        """Looped every minute to send a connection to localhost:5123 to show bot is working well."""
        source_link = "http://127.0.0.1:5123"
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
        await self.process_cache_time(self.update_dc_channels, "DCAPP Channels")
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
        log.console(f"Cache Completely Created in {await self.get_cooldown_time(time.time() - past_time)}.")

    async def update_command_counter(self):
        """Updates Cache for command counter and sessions"""
        self.cache.command_counter = {}
        session_id = await self.get_session_id()
        all_commands = await self.conn.fetch("SELECT commandname, count FROM stats.commands WHERE sessionid = $1", session_id)
        for command in all_commands:
            self.cache.command_counter[command[0]] = command[1]
        self.cache.current_session = self.first_result(
            await self.conn.fetchrow("SELECT session FROM stats.sessions WHERE date = $1", datetime.date.today()))

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
                self.cache.session_id = self.get_session_id()

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
            self.cache.temp_channels[channel[0]] = channel[1]

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
            normal_patrons = await self.get_patreon_role_members(super=False)
            super_patrons = await self.get_patreon_role_members(super=True)
            for patron in normal_patrons:
                self.cache.patrons[patron.id] = False
            # super patrons must go after normal patrons to have a proper boolean set because
            # super patrons have both roles.
            for patron in super_patrons:
                self.cache.patrons[patron.id] = True
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

    async def update_dc_channels(self):
        """Set cache for dc channels"""
        self.cache.user_notifications = {}
        channels = await self.get_dc_channels()
        for channel in channels:
            self.cache.dc_app_channels[channel[0]] = channel[1]

    async def update_groups(self):
        """Set cache for group photo count"""
        past_time = time.time()
        self.cache.group_photos = {}
        all_group_counts = await self.conn.fetch("SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id GROUP BY g.groupid ORDER BY g.groupname")
        for group in all_group_counts:
            self.cache.group_photos[group[0]] = group[2]
        log.console(f"Group Photo Count Cache Updated in {await self.get_cooldown_time(time.time() - past_time)}.")

    @tasks.loop(seconds=0, minutes=0, hours=12, reconnect=True)
    async def update_group_photo_count(self):
        """Looped every 12 hours to update the group photo count."""
        while self.conn is None:
            await asyncio.sleep(1)
        await self.update_groups()

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def update_patron_cache(self):
        """Looped until patron cache is loaded
        This was added due to intents slowing d.py cache loading rate.
        """
        if await self.process_cache_time(self.update_patreons, "Patrons"):
            self.update_patron_cache.stop()

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
    async def send_maintenance_message(self, channel):
        try:
            await channel.send(
                f"> **A maintenance is currently in progress. Join the support server for more information. <{keys.bot_support_server_link}>**")
        except Exception as e:
            pass

    async def process_commands(self, message):
        message_sender = message.author
        message_content = message.clean_content
        message_channel = message.channel
        server_prefix = await self.get_server_prefix_by_context(message)
        if len(message_content) >= len(server_prefix):
            if message.content[0:len(server_prefix)].lower() == server_prefix.lower() or message.content == (
                    keys.bot_prefix + 'setprefix') or message.content == (keys.bot_prefix + 'checkprefix'):
                # only replace the prefix portion back to the default prefix
                msg_without_prefix = message.content[len(server_prefix):len(message.content)]
                message.content = keys.bot_prefix + msg_without_prefix
                # if a user is banned from the bot.
                if await self.check_if_bot_banned(message_sender.id):
                    if self.check_message_is_command(message):
                        await self.send_ban_message(message_channel)
                else:
                    await self.client.process_commands(message)

    async def check_for_nword(self, message):
        """Processes new messages that contains the N word."""
        message_sender = message.author
        if not message_sender.bot:
            message_content = message.clean_content
            if self.check_message_not_empty(message):
                # check if the message belongs to the bot
                    if message_content[0] != '%':
                        if self.check_nword(message_content):
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
            # log.console(e)
            return None
        except Exception as e:
            # log.console(e)
            return None

    async def check_if_temp_channel(self, channel_id):
        """Check if a channel is a temp channel"""
        return self.cache.temp_channels.get(channel_id) is not None

    async def get_temp_channels(self):
        """Get all temporary channels in the DB."""
        return await self.conn.fetch("SELECT chanID, delay FROM currency.TempChannels")

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
            server_id = ctx.guild.id
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
        """Add 1 to the specific command count."""
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

    def check_message_is_command(self, message):
        """Check if a message is a command."""
        for command_name in self.client.all_commands:
            if command_name in message.content:
                if len(command_name) != 1:
                    return True
        return False

    @staticmethod
    async def send_ban_message(channel):
        """A message to send for a user that is banned from the bot."""
        await channel.send(
            f"> **You are banned from using {keys.bot}. Join <{keys.bot_support_server_link}>**")

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

    @staticmethod
    def get_none_if_list_is_empty(new_list):
        """Returns none if a list is empty, otherwise, it will return the list."""
        if len(new_list) == 0:
            return None
        else:
            return new_list

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
        if prefix is None:
            return keys.bot_prefix
        else:
            return prefix

    async def get_bot_statuses(self):
        """Get the displayed messages for the bot."""
        statuses = await self.conn.fetch("SELECT status FROM general.botstatus")
        if len(statuses) == 0:
            return None
        else:
            return statuses

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
    async def check_channel_sending_photos(self, channel_id):
        """Checks a text channel ID to see if it is restricted from having idol photos sent."""
        counter = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.restricted WHERE channelid = $1 AND sendhere = $2", channel_id, 0))
        return counter == 0  # returns False if they are restricted.

    async def check_server_sending_photos(self, server_id):
        """Checks a server to see if it has a specific channel to send idol photos to"""
        counter = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.restricted WHERE serverid = $1 AND sendhere = $2", server_id, 1))
        return counter == 1  # returns True if they are supposed to send it to a specific channel.

    async def get_channel_sending_photos(self, server_id):
        """Returns a text channel from a server that requires idol photos to be sent to a specific text channel."""
        channel_id = self.first_result(await self.conn.fetchrow("SELECT channelid FROM groupmembers.restricted WHERE serverid = $1 AND sendhere = $2", server_id, 1))
        return await self.client.fetch_channel(channel_id)

    async def get_photo_count_of_group(self, group_id):
        """Gets the total amount of photos that a group has."""
        group_result = await self.conn.fetchrow("SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id AND g.groupid = $1 GROUP BY g.groupid", group_id)
        if group_result is None:
            return 0
        return group_result[2]

    @staticmethod
    def log_idol_command(message):
        """Log an idol photo that was called."""
        log.console(f"IDOL LOG: ChannelID = {message.channel.id} - {message.author} "
                    f"({message.author.id})|| {message.clean_content} ")

    async def get_all_images_count(self):
        """Get the amount of images the bot has."""
        return self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.imagelinks"))

    async def get_idol_called(self, member_id):
        """Get the amount of times an idol has been called."""
        return self.first_result(await self.conn.fetchrow("SELECT Count FROM groupmembers.Count WHERE MemberID = $1", member_id))

    @staticmethod
    async def check_if_folder(url):
        """Check if a url is a folder."""
        async with keys.client_session.get(url) as r:
            if r.status == 200:
                return True
            return False

    async def get_idol_count(self, member_id):
        """Get the amount of photos for an idol."""
        return self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.imagelinks WHERE memberid = $1", member_id))

    async def get_random_idol_id(self):
        """Get a random idol."""
        photo_count = 0
        member_ids = await self.get_all_members()
        while photo_count == 0:  # confirm the idol has a photo before sending to API.
            member_id = random.choice(member_ids)[0]
            photo_count = await self.get_idol_count(member_id)
        return member_id

    async def get_all_members(self):
        """Get all idols."""
        return await self.conn.fetch("SELECT id, fullname, stagename FROM groupmembers.Member ORDER BY id")

    async def get_all_groups(self):
        """Get all groups."""
        return await self.conn.fetch("SELECT groupid, groupname FROM groupmembers.groups ORDER BY groupname")

    async def get_members_in_group(self, group_name=None, group_id=None):
        """Get the members in a specific group."""
        if group_id is None:
            group_id = self.first_result(await self.conn.fetchrow(f"SELECT groupid FROM groupmembers.groups WHERE groupname = $1", group_name))
        members = await self.conn.fetch("SELECT idolid FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)
        return [member[0] for member in members]

    async def check_member_in_group(self, member_id, group_id):
        return group_id in await self.get_groups_from_member(member_id)

    async def get_member(self, member_id):
        """Get an idol based on their ID."""
        return await self.conn.fetchrow("SELECT id, fullname, stagename FROM groupmembers.member WHERE id = $1", member_id)

    async def get_aliases(self, object_id, group=False):
        """Get the aliases of an idol or group."""
        aliases = await self.conn.fetch("SELECT alias FROM groupmembers.aliases WHERE objectid = $1 AND isgroup = $2", object_id, int(group))
        return [alias[0] for alias in aliases]

    async def get_group_name(self, group_id):
        """Get a group's name based on their ID."""
        return self.first_result(await self.conn.fetchrow("SELECT groupname FROM groupmembers.groups WHERE groupid = $1", group_id))

    async def get_groups_from_member(self, member_id):
        """Return all the group ids an idol is in."""
        groups = await self.conn.fetch("SELECT groupid FROM groupmembers.idoltogroup WHERE idolid = $1", member_id)
        return [group[0] for group in groups]

    async def add_idol_to_group(self, member_id: int, group_id: int):
        return await self.conn.execute("INSERT INTO groupmembers.idoltogroup(idolid, groupid) VALUES($1, $2)", member_id, group_id)

    async def remove_idol_from_group(self, member_id: int, group_id: int):
        return await self.conn.execute("DELETE FROM groupmembers.idoltogroup WHERE idolid = $1 AND groupid = $2", member_id, group_id)

    async def send_names(self, ctx, mode, user_page_number=1, group_ids=None):
        """Send the names of all idols in an embed with many pages."""
        async def check_mode(embed_temp):
            """Check if it is grabbing their full names or stage names."""
            if mode == "fullname":
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {await self.get_server_prefix_by_context(ctx)}members for Stage Names.")
            else:
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {await self.get_server_prefix_by_context(ctx)}fullnames for Full Names.")
            return embed_temp
        is_mod = self.check_if_mod(ctx)
        embed_lists = []
        all_groups = await self.get_all_groups()
        page_number = 1
        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
        counter = 1
        for group in all_groups:
            names = []
            group_id = group[0]
            group_name = group[1]
            if group_name != "NULL" or is_mod:
                if group_ids is None or len(group_ids) == 0 or group_id in group_ids:
                    member_in_group_ids = await self.get_members_in_group(group_id=group_id)
                    for member_in_group_id in member_in_group_ids:
                        member = await self.get_member(member_in_group_id)
                        if mode == "fullname":
                            member_name = member[1]
                        else:
                            member_name = member[2]
                        if is_mod:
                            names.append(f"{member_name} ({member[0]}) | ")
                        else:
                            names.append(f"{member_name} | ")
                    final_names = "".join(names)
                    if len(final_names) == 0:
                        final_names = "None"
                    if is_mod:
                        embed.insert_field_at(counter, name=f"{group_name} ({group_id})", value=final_names, inline=False)
                    else:
                        embed.insert_field_at(counter, name=f"{group_name}", value=final_names, inline=False)
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

    async def set_embed_with_all_aliases(self, mode):
        """Send the names of all aliases in an embed with many pages."""
        if mode == "Group":
            all_info = await self.get_all_groups()
            is_group = True
        else:
            all_info = await self.get_all_members()
            is_group = False
        embed_list = []
        count = 0
        page_number = 1
        embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=self.get_random_color())
        for info in all_info:
            id = info[0]
            name = info[1]
            aliases = ",".join(await self.get_aliases(id, is_group))
            if not is_group:
                stage_name = info[2]
            if len(aliases) != 0:
                if not is_group:
                    embed.add_field(name=f"{name} ({stage_name}) [{id}]", value=aliases, inline=True)
                else:
                    embed.add_field(name=f"{name} [{id}]", value=aliases, inline=True)
                count += 1
            if count == 10:
                count = 0
                embed_list.append(embed)
                page_number += 1
                embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=self.get_random_color())
        if count != 0:
            embed_list.append(embed)
        return embed_list

    async def check_idol_post_reactions(self, message, user_msg, idol_id, link):
        """Check the reactions on an idol post."""
        try:
            if message is not None:
                reload_image_emoji = keys.reload_emoji
                dead_link_emoji = keys.dead_emoji
                await message.add_reaction(reload_image_emoji)
                await message.add_reaction(dead_link_emoji)
                message = await message.channel.fetch_message(message.id)

                def image_check(user_reaction, reaction_user):
                    """check the user that reacted to it and which emoji it was."""
                    user_check = (reaction_user == user_msg.author) or (reaction_user.id == keys.owner_id) or reaction_user.id in keys.mods_list
                    return user_check and (str(user_reaction.emoji) == dead_link_emoji or str(user_reaction.emoji) ==
                                           reload_image_emoji) and user_reaction.message.id == message.id

                async def reload_image(message1, link):
                    """Wait for a user to react, and reload the image if it's the reload emoji."""
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=image_check, timeout=60)
                        if str(reaction) == reload_image_emoji:
                            channel = message1.channel
                            await message1.delete()
                            # message1 = await channel.send(embed=embed)
                            message1 = await channel.send(link)
                            await self.check_idol_post_reactions(message1, user_msg, idol_id, link)
                        elif str(reaction) == dead_link_emoji:
                            try:
                                link = message1.embeds[0].url
                            except:
                                link = message1.content
                            if await self.check_if_patreon(user.id):
                                await message1.delete()
                            else:
                                await message1.clear_reactions()
                                await message1.edit(content=f"Report images as dead links (2nd reaction) ONLY if the image does not load or it's not a photo of the idol.\nYou can have this message removed by becoming a {await self.get_server_prefix_by_context(message1)}patreon", suppress=True, delete_after=45)
                            await self.get_dead_links()
                            try:
                                channel = self.client.get_channel(keys.dead_image_channel_id)
                                if channel is not None:
                                    await self.send_dead_image(channel, link, user, idol_id)
                            except Exception as e:
                                pass
                    except asyncio.TimeoutError:
                        await message1.clear_reactions()
                    except Exception as e:
                        log.console(e)
                        pass
                await reload_image(message, link)
        except Exception as e:
            pass

    async def get_dead_links(self):
        return await self.conn.fetch("SELECT deadlink, messageid, idolid FROM groupmembers.deadlinkfromuser")

    async def delete_dead_link(self, link, idol_id):
        return await self.conn.execute("DELETE FROM groupmembers.deadlinkfromuser WHERE deadlink = $1 AND idolid = $2", link, idol_id)

    async def set_forbidden_link(self, link, idol_id):
        return await self.conn.execute("INSERT INTO groupmembers.forbiddenlinks(link, idolid) VALUES($1, $2)", link, idol_id)

    async def send_dead_image(self, channel, link, user, idol_id):
        try:
            idol = await self.get_member(idol_id)
            special_message = f"""**Dead Image For {idol[1]} ({idol[2]}) ({idol[0]})
Sent in by {user.name}#{user.discriminator} ({user.id}).**"""
            msg, api_url = await self.idol_post(channel, idol[0], photo_link=link, special_message=special_message)
            await self.conn.execute(
                "INSERT INTO groupmembers.DeadLinkFromUser(deadlink, userid, messageid, idolid) VALUES($1, $2, $3, $4)",
                link, user.id, msg.id, idol_id)
            await msg.add_reaction(keys.check_emoji)
            await msg.add_reaction(keys.trash_emoji)
        except Exception as e:
            log.console(f"Send Dead Image - {e}")

    async def get_id_where_member_matches_name(self, name, mode=0):
        """Get member ids if the name matches."""
        all_members = await self.get_all_members()
        id_list = []
        name = name.lower()
        for member in all_members:
            member_id = member[0]
            full_name = member[1].lower()
            stage_name = member[2].lower()
            aliases = await self.get_aliases(member_id)
            if mode == 0:
                if name == full_name or name == stage_name:
                    id_list.append(member_id)
            else:
                if stage_name.lower() in name or full_name.lower() in name:
                    id_list.append(member_id)
            for alias in aliases:
                if mode == 0:
                    if alias == name:
                        id_list.append(member_id)
                else:
                    if alias in name:
                        id_list.append(member_id)
        # remove any duplicates
        id_list = list(dict.fromkeys(id_list))
        return id_list

    async def get_idol_id_by_both_names(self, full_name, stage_name):
        """Returns the first idol id where the full name and stage name match (CASE-SENSITIVE)"""
        return self.first_result(await self.conn.fetchrow("SELECT id FROM groupmembers.member WHERE fullname=$1 AND stagename=$2", full_name, stage_name))

    async def get_id_where_group_matches_name(self, name, mode=0):
        """Get group ids for a specific name."""
        all_groups = await self.get_all_groups()
        id_list = []
        name = name.lower()
        for group in all_groups:
            try:
                group_id = group[0]
                group_name = group[1].lower()
                aliases = await self.get_aliases(group_id, group=True)
                if mode == 0:
                    if name == group_name.lower():
                        id_list.append(group_id)
                else:
                    if group_name.lower() in name:
                        id_list.append(group_id)
                        name = (name.lower()).replace(group_name, "")
                for alias in aliases:
                    if mode == 0:
                        if alias == name:
                            id_list.append(group_id)
                    else:
                        if alias in name:
                            id_list.append(group_id)
                            name = (name.lower()).replace(alias, "")
            except Exception as e:
                log.console(e)
        # remove any duplicates
        id_list = list(dict.fromkeys(id_list))
        # print(id_list)
        if mode == 0:
            return id_list
        else:
            return id_list, name

    async def process_names(self, ctx, page_number_or_group, mode):
        """Structures the input for idol names commands and sends information to transfer the names to the channels."""
        if type(page_number_or_group) == int:
            await self.send_names(ctx, mode, page_number_or_group)
        elif type(page_number_or_group) == str:
            group_ids, name = await self.get_id_where_group_matches_name(page_number_or_group, mode=1)
            await self.send_names(ctx, mode, group_ids=group_ids)

    async def check_group_and_idol(self, message):
        """Check if a specific idol is being called from a reference to a group. ex: redvelvet irene"""
        group_ids, new_message = await self.get_id_where_group_matches_name(message, mode=1)
        member_list = []
        member_ids = await self.get_id_where_member_matches_name(new_message, 1)
        for group_id in group_ids:
            members_in_group = await self.get_members_in_group(await self.get_group_name(group_id))
            for member_id in member_ids:
                for group_member_id in members_in_group:
                    if member_id == group_member_id:
                        member_list.append(member_id)
        return self.get_none_if_list_is_empty(member_list)

    async def get_random_photo_from_member(self, member_id):
        """Get a random photo from an idol."""
        return self.first_result(await self.conn.fetchrow("SELECT link FROM groupmembers.imagelinks WHERE memberid = $1 ORDER BY RANDOM() LIMIT 1", member_id))

    async def update_member_count(self, member_id):
        """Update the amount of times an idol has been called."""
        count = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = $1", member_id))
        if count == 0:
            await self.conn.execute("INSERT INTO groupmembers.Count VALUES($1, $2)", member_id, 1)
        else:
            count = self.first_result(await self.conn.fetchrow("SELECT Count FROM groupmembers.Count WHERE MemberID = $1", member_id))
            count += 1
            await self.conn.execute("UPDATE groupmembers.Count SET Count = $1 WHERE MemberID = $2", count, member_id)

    @staticmethod
    def remove_custom_characters(file_name):
        """Only allow 0-9, a-z as a file name and remove any other characters."""
        allowed_characters = "abcdefghijklmnopqrstuvwxyz1234567890."
        for character in file_name:
            if character not in allowed_characters:
                file_name = file_name.replace(character, "z")
        return file_name

    @staticmethod
    def get_file_type(file_location):
        try:
            kind = filetype.guess(file_location)
            if kind is None:
                return None
            return f".{kind.extension}"
        except Exception as e:
            return None

    async def get_google_drive_link(self, api_url):
        return self.first_result(await self.conn.fetchrow("SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", api_url))

    async def get_image_msg(self, member_id, group_id, channel, member_info, photo_link, user_id=None, guild_id=None, api_url=None, special_message=None):
        file = None
        if api_url is None:
            try:
                find_post = True
                data = {
                    'p_key': keys.translate_private_key
                }
                end_point = f"http://127.0.0.1:{keys.api_port}/photos/{member_id}"
                if self.test_bot:
                    end_point = f"https://api.irenebot.com/photos/{member_id}"
                while find_post:  # guarantee we get a post sent to the user.
                    async with self.session.post(end_point, data=data) as r:
                        if r.status == 200 or r.status == 301:
                            api_url = r.url
                            find_post = False
                        elif r.status == 415:
                            # video
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
                            log.console(f"No photos were found for this idol ({member_id}).")
                            msg = await channel.send(f"**No photos were found for this idol ({member_id}).**")
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

        if file is not None:
            # send the video and return the message with the api url.
            if special_message is None:
                msg = await channel.send(file=file)
            else:
                msg = await channel.send(special_message, file=file)
            return msg, api_url

        # an image url should exist at this point, and should not equal None.
        try:
            # after host was swapped back to digitalocean,some images were not loading by discord
            # so a small sleep will be put in place.
            await asyncio.sleep(0.5)
            embed = await self.get_idol_post_embed(group_id, member_info, str(api_url), user_id=user_id,
                                                   guild_id=channel.guild.id)
            embed.set_image(url=api_url)
            if special_message is None:
                msg = await channel.send(embed=embed)
            else:
                msg = await channel.send(special_message, embed=embed)
        except Exception as e:
            await channel.send(f"> An API issue has occurred. If this is constantly occurring, please join our support server.")
            log.console(f" {e} - An API issue has occurred. If this is constantly occurring, please join our support server.")
            return None, None
        return msg, api_url

    async def get_idol_post_embed(self, group_id, member_info, photo_link, user_id=None, guild_id=None):
        """The embed for an idol post."""
        if group_id is None:
            embed = discord.Embed(title=f"{member_info[1]} ({member_info[2]})", color=self.get_random_color(),
                                  url=photo_link)
        else:
            embed = discord.Embed(title=f"{await self.get_group_name(group_id)} ({member_info[2]})",
                                  color=self.get_random_color(), url=photo_link)
        patron_msg = f"Please consider becoming a {await self.get_server_prefix(guild_id)}patreon."

        # when user_id is None, the post goes to the dead images channel.
        if user_id is not None:
            if not await self.check_if_patreon(user_id):
                embed.set_footer(text=patron_msg)
        return embed

    async def idol_post(self, channel, member_id, photo_link=None, group_id=None, special_message=None, user_id=None):
        """The main process for posting an idol's photo."""
        try:
            member_info = await self.get_member(member_id)
            await self.update_member_count(member_id)
            try:
                msg, api_url = await self.get_image_msg(member_id, group_id, channel, member_info, photo_link, user_id=user_id, guild_id=channel.guild.id, api_url=photo_link, special_message=special_message)
            except Exception as e:
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

    ######################
    # ## DREAMCATCHER ## #
    ######################
    async def get_dc_channel_role(self, channel_id):
        """Get the role id that notifies the users on a new dc app post."""
        return self.first_result(await self.conn.fetchrow("SELECT roleid from dreamcatcher.dreamcatcher WHERE channelid = $1", channel_id))

    async def get_dc_channel_exists(self, channel_id):
        """Returns 1 if the dc channel is being notified, otherwise returns 0."""
        return channel_id in self.cache.dc_app_channels

    async def get_dc_channels(self):
        """Get all the servers that receive DC APP Updates."""
        return await self.conn.fetch("SELECT channelid, roleid FROM dreamcatcher.dreamcatcher")

    async def get_video_and_bat_list(self, page_soup):
        """Get a list of all the .bat and video files."""
        try:
            video_list = (page_soup.findAll("div", {"class": "swiper-slide img-box video-box width"}))
            if len(video_list) == 0:
                video_list = (page_soup.findAll("div", {"class": "swiper-slide img-box video-box height"}))
            count_numbers = 0
            video_name_list = []
            bat_name_list = []
            for video in video_list:
                count_numbers += 1
                new_video_url = video.source["src"]
                bat_name = "{}DC.bat".format(count_numbers)
                bat_name_list.append(bat_name)
                ab = open("Videos\{}".format(bat_name), "a+")
                video_name = "{}DCVideo.mp4".format(count_numbers)
                info = 'ffmpeg -i "{}" -c:v libx264 -preset slow -crf 22 "Videos/{}"'.format(new_video_url,
                                                                                             video_name)
                os.system(info)
                video_name_list.append(video_name)
                ab.write(info)
                ab.close()
        except Exception as e:
            log.console(e)
        return self.get_none_if_list_is_empty(video_name_list), self.get_none_if_list_is_empty(bat_name_list)

    @staticmethod
    def get_videos(video_name_list):
        """Return a list of discord.File that contains videos."""
        dc_videos = []
        try:
            if video_name_list is not None:
                for video_name in video_name_list:
                    dc_video = discord.File(fp='Videos/{}'.format(video_name),
                                            filename=video_name)
                    dc_videos.append(dc_video)
            else:
                return None
        except Exception as e:
            log.console(e)
            pass
        return dc_videos

    @staticmethod
    def get_photos(photo_name_list):
        """Return a list of discord.File that contains photos."""
        dc_photos = []
        try:
            if photo_name_list is not None:
                for file_name in photo_name_list:
                    dc_photo = discord.File(fp='DCApp/{}'.format(file_name),
                                            filename=file_name)
                    dc_photos.append(dc_photo)
            else:
                return None
        except Exception as e:
            log.console(e)
        return dc_photos

    async def get_embed(self, image_links, member_name):
        """Create the embed for a DC APP post."""
        embed_list = []
        for link in image_links:
            embed = discord.Embed(title=member_name, color=self.get_random_color(), url=link)
            embed.set_image(url=link)
            embed = await self.set_embed_author_and_footer(embed, "Thanks for using Irene.")
            embed_list.append(embed)
        return self.get_none_if_list_is_empty(embed_list)

    @staticmethod
    async def send_content(channel, dc_photos_embeds, dc_videos):
        """Send the DC APP post to the channels."""
        try:
            if dc_photos_embeds is not None:
                for dc_photo_embed in dc_photos_embeds:
                    await channel.send(embed=dc_photo_embed)
            if dc_videos is not None:
                for video in dc_videos:
                    await channel.send(file=video)
        except Exception as e:
            log.console(e)

    @staticmethod
    def delete_content():
        """Delete any videos or photos that were downloaded."""
        all_videos = os.listdir('Videos')
        for video in all_videos:
            try:
                os.unlink('Videos/{}'.format(video))
            except Exception as e:
                log.console(e)
                pass
        all_photos = os.listdir('DCApp')
        for photo in all_photos:
            try:
                os.unlink('DCApp/{}'.format(photo))
            except Exception as e:
                log.console(e)
                pass

    @staticmethod
    def get_member_name_and_id(username, member_list):
        """return the member name and id of a post."""
        member_id = None
        member_name = None
        if username == member_list[0]:
            member_name = "Gahyeon"
            member_id = 163
        if username == member_list[1]:
            member_name = "Siyeon"
            member_id = 159
        if username == member_list[2]:
            member_name = "Yoohyeon"
            member_id = 161
        if username == member_list[3]:
            member_name = "JIU"
            member_id = 157
        if username == member_list[4]:
            member_name = "SUA"
            member_id = 158
        if username == member_list[5]:
            member_name = "DC"
        if username == member_list[6]:
            member_name = "Dami"
            member_id = 162
        if username == member_list[7]:
            member_name = "Handong"
            member_id = 160
        return member_name, member_id

    async def add_post_to_db(self, image_links, member_id, member_name, post_number, post_url):
        """Add a post's information to the database."""
        if image_links is not None:
            for link in image_links:
                try:
                    if member_id is not None:
                        await self.conn.execute("INSERT INTO groupmembers.imagelinks VALUES ($1,$2)", link, member_id)
                    await self.conn.execute("INSERT INTO dreamcatcher.DCHDLinks VALUES ($1,$2,$3)", link, member_name.lower(), post_number)
                    await self.conn.execute("UPDATE dreamcatcher.DCUrl SET url = $1 WHERE member = $2", post_url, "latest")
                    await self.conn.execute("UPDATE dreamcatcher.DCUrl SET url = $1 WHERE member = $2", post_url, member_name.lower())
                except Exception as e:
                    log.console(e)
                    pass

    async def send_new_post(self, channel_id, role_id, channel, member_name, status_message, post_url, translated_message):
        """Send the status information to a channel."""
        try:
            if role_id is None:
                role_mention = ""
            else:
                role_mention = f"<@&{role_id}>, "
            if translated_message is not None:
                if len(translated_message) != 0:
                    translated_message = translated_message['text']
                    return await channel.send(
                        f">>> **{role_mention}New {member_name} Post\n<{post_url}>\nStatus Message: {status_message}\nTranslated (KR to EN): {translated_message}**")
            return await channel.send(f">>> **{role_mention}New {member_name} Post\n<{post_url}>\nStatus Message: {status_message}**")
        except AttributeError:
            try:
                await self.conn.execute("DELETE from dreamcatcher.dreamcatcher WHERE channelid = $1", channel_id)
            except Exception as e:
                log.console(e)
        except Exception as e:
            await channel.send(f">>> **New {member_name} Post\n<{post_url}>**")

    @staticmethod
    async def open_bat_file(bat_list):
        """Open a bat file to process the video with ffmpeg."""
        for bat_name in bat_list:
            # open bat file
            check_bat = await asyncio.create_subprocess_exec("Videos/{}".format(bat_name),
                                                             stderr=asyncio.subprocess.PIPE)
            await check_bat.wait()

    async def get_image_list(self, image_url, post_url, image_links):
        """Downloads Thumbnail Photos//This was before embeds were being used and was very inefficient. || Not Used"""
        photo_name_list = []
        new_count = -1
        final_image_list = []
        for image in image_url:
            new_count += 1
            new_image_url = image.img["src"]
            file_name = new_image_url[82:]
            async with self.session.get(new_image_url) as resp:
                fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                await fd.write(await resp.read())
                await fd.close()
                file_size = (os.path.getsize(f'DCApp/{file_name}'))
                if file_size <= 20000:
                    keep_going = True
                    loop_count = 0
                    while keep_going:
                        log.console(f"Stuck in a loop {loop_count}")
                        loop_count += 1
                        try:
                            os.unlink(f'DCApp/{file_name}')
                        except Exception as e:
                            log.console(e)
                        fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                        await fd.write(await resp.read())
                        await fd.close()
                        file_size = (os.path.getsize(f'DCApp/{file_name}'))
                        if file_size > 20000:
                            photo_name_list.append(file_name)
                            keep_going = False
                        if loop_count == 30:
                            try:
                                final_image_list.append(image_links[new_count])
                                os.unlink(f'DCApp/{file_name}')
                                keep_going = False
                            except Exception as e:
                                log.console(e)
                                keep_going = False
                elif file_size > 20000:
                    photo_name_list.append(file_name)
        return self.get_none_if_list_is_empty(photo_name_list), self.get_none_if_list_is_empty(final_image_list)

    @staticmethod
    async def download_dc_photos(image_url):
        """Return the list of HD links."""
        image_links = []
        for image in image_url:
            new_image_url = image.img["src"]
            dc_date = new_image_url[41:49]
            unique_id = new_image_url[55:87]
            file_format = new_image_url[93:]
            hd_link = f'https://file.candlemystar.com/post/{dc_date}{unique_id}{file_format}'
            image_links.append(hd_link)
            # do not download hd links so that they are sent to channels quicker.
            """
            async with session.get(hd_link) as resp:
                fd = await aiofiles.open(
                    'DreamHD/{}'.format(f"{unique_id[:8]}{file_format}"), mode='wb')
                await fd.write(await resp.read())
                await fd.close()
            """
        return image_links

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
        # if d.py cache has not yet loaded (unlikely, but just incase)
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


resources = Utility()
