from Utility import resources as ex
from discord.ext import tasks
from util import logger as log
import time
import asyncio
import aiofiles
import datetime
import json


# noinspection PyBroadException,PyPep8
class Cache:

    @staticmethod
    async def process_cache_time(method, name):
        """Process the cache time."""
        past_time = time.time()
        result = await method()
        if result is None or result:  # expecting False on methods that fail to load, do not simplify None.
            log.console(
                f"Cache for {name} Created in {await ex.u_miscellaneous.get_cooldown_time(time.time() - past_time)}.")
        return result

    async def create_cache(self, on_boot_up=True):
        """Create the general cache on startup"""
        past_time = time.time()
        # reset custom user cache
        ex.cache.users = {}
        await self.process_cache_time(self.load_language_packs, "Language Packs")
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
        await self.process_cache_time(self.create_twitch_cache, "Twitch Channels")
        await self.process_cache_time(self.create_gg_filter_cache, "Guessing Game Filter")
        await self.process_cache_time(self.create_currency_cache, "Currency")
        await self.process_cache_time(self.create_levels_cache, "Levels")
        await self.process_cache_time(self.create_langauge_cache, "User Language")

        # if the discord cache is loaded, make sure to update the patreon cache since our user objects are reset.
        # every time this function is called.
        if ex.discord_cache_loaded:
            await self.process_cache_time(self.update_patreons, "Reload Patreon Cache")

        # do not load weverse cache if the bot has already been running.
        if not ex.test_bot and not ex.weverse_client.cache_loaded and on_boot_up:
            # noinspection PyUnusedLocal
            task = asyncio.create_task(self.process_cache_time(ex.weverse_client.start, "Weverse"))
        log.console(
            f"Cache Completely Created in {await ex.u_miscellaneous.get_cooldown_time(time.time() - past_time)}.")
        ex.irene_cache_loaded = True

    @staticmethod
    async def create_langauge_cache():
        """Create cache for user languages."""

        async def get_lang_info():
            try:
                for t_user_id, t_language in await ex.sql.fetch_languages():
                    yield t_user_id, t_language
            except:
                return

        async for user_id, language in get_lang_info():
            user = await ex.get_user(user_id)
            user.language = language

    async def load_language_packs(self):
        """Create cache for language packs."""
        ex.cache.languages = {}

        async def get_file_names():
            # get the file names available
            for t_file_name in ex.cache.languages_available:
                yield t_file_name

        async def get_language_module_and_message():
            # get the modules and messages for each language
            for t_language in ex.cache.languages.values():
                for t_module in t_language.values():
                    for t_message_name in t_module.keys():
                        yield t_module, t_message_name

        # load the json for every language to cache
        async for file_name in get_file_names():
            async with aiofiles.open(f"languages/{file_name}.json") as file:
                ex.cache.languages[file_name] = json.loads(await file.read())

        # make the content of all curly braces bolded in all available languages.
        async for module, message_name in get_language_module_and_message():
            module[message_name] = self.apply_bold_to_braces(module[message_name])

    @staticmethod
    def apply_bold_to_braces(text: str) -> str:
        """Applys bold markdown in between braces."""
        text = text.replace("{", "**{")
        text = text.replace("}", "}**")
        return text

    @staticmethod
    async def create_levels_cache():
        """Create the cache for user levels."""

        async def get_levels():
            # get rob, daily, beg, and profile levels of all users
            try:
                for t_user_id, t_rob, t_daily, t_beg, t_profile_level in await ex.sql.fetch_levels():
                    yield t_user_id, t_rob, t_daily, t_beg, t_profile_level
            except:
                return

        async for user_id, rob, daily, beg, profile_level in get_levels():
            user = await ex.get_user(user_id)
            if rob:
                user.rob_level = rob
            if daily:
                user.daily_level = daily
            if beg:
                user.beg_level = beg
            if profile_level:
                user.profile_level = profile_level

    @staticmethod
    async def create_currency_cache():
        """Create cache for currency"""
        async def get_currency():
            # get all user id and their balance
            try:
                for t_user_id, t_money in await ex.sql.fetch_currency():
                    yield t_user_id, t_money
            except:
                return

        async for user_id, money in get_currency():
            user = await ex.get_user(user_id)
            user.balance = int(money)

    @staticmethod
    async def create_gg_filter_cache():
        """Create filtering of guessing game cache."""
        async def get_users_filtered():
            # get all users with their guessing game filter enabled
            try:
                for t_user_info in await ex.sql.fetch_filter_enabled():
                    yield t_user_info
            except:
                return

        async def get_users():
            # get all users
            for t_user in ex.cache.users.values():
                yield t_user

        async def get_user_group_filters():
            # get the groups users have filtered.
            try:
                for t_user_id, t_group_id in await ex.sql.fetch_filtered_groups():
                    yield t_user_id, t_group_id
            except:
                return

        async for user_info in get_users_filtered():
            user_id = user_info[0]
            user = await ex.get_user(user_id)
            user.gg_filter = True

        # reset cache for filtered groups
        async for user in get_users():
            user.gg_groups = []

        # go through all filtered groups regardless if it is enabled
        # so we do not have to change during filter toggle.
        async for user_id, group_id in get_user_group_filters():
            user = await ex.get_user(user_id)
            group = await ex.u_group_members.get_group(group_id)
            user.gg_groups.append(group)

    @staticmethod
    async def create_twitch_cache():
        """Create cache for twitch followings"""
        ex.cache.twitch_channels = {}
        ex.cache.twitch_guild_to_channels = {}
        ex.cache.twitch_guild_to_roles = {}

        async def get_twitch_guilds():
            # get guild id, channel id, and role id for followings on twitch.
            try:
                for t_guild_id, t_channel_id, t_role_id in await ex.sql.fetch_twitch_guilds():
                    yield t_guild_id, t_channel_id, t_role_id
            except:
                return

        async def get_twitch_notis():
            # get the twitch username and guild id that is following them.
            try:
                for t_username, t_guild_id in await ex.sql.fetch_twitch_notifications():
                    yield t_username, t_guild_id
            except:
                return

        async for guild_id, channel_id, role_id in get_twitch_guilds():
            ex.cache.twitch_guild_to_channels[guild_id] = channel_id
            ex.cache.twitch_guild_to_roles[guild_id] = role_id

        async for username, guild_id in get_twitch_notis():
            guilds_in_channel = ex.cache.twitch_channels.get(username)
            if guilds_in_channel:
                guilds_in_channel.append(username)
            else:
                ex.cache.twitch_channels[username] = [guild_id]

    @staticmethod
    async def create_guessing_game_cache():
        """Create cache for guessing game scores"""
        ex.cache.guessing_game_counter = {}

        async def get_gg_stats():
            # get all gg stats from all users
            try:
                for t_user_id, t_easy, t_medium, t_hard in await ex.sql.fetch_gg_stats():
                    yield t_user_id, t_easy, t_medium, t_hard
            except:
                return

        async for user_id, easy_score, medium_score, hard_score in get_gg_stats():
            ex.cache.guessing_game_counter[user_id] = {"easy": easy_score, "medium": medium_score, "hard": hard_score}

    @staticmethod
    async def create_timezone_cache():
        """Create cache for timezones"""
        async def get_timezones():
            # get all timezones
            try:
                for t_user_id, t_timezone in await ex.sql.fetch_timezones():
                    yield t_user_id, t_timezone
            except:
                return

        async for user_id, timezone in get_timezones():
            user = await ex.get_user(user_id)
            user.timezone = timezone

    @staticmethod
    async def create_reminder_cache():
        """Create cache for reminders"""
        async def get_reminders():
            # get all reminders
            try:
                for t_reason_id, t_user_id, t_reason, t_time_stamp in await ex.sql.fetch_reminders():
                    yield t_reason_id, t_user_id, t_reason, t_time_stamp
            except:
                return

        async for reason_id, user_id, reason, time_stamp in get_reminders():
            user = await ex.get_user(user_id)
            reason_list = [reason_id, reason, time_stamp]
            if user.reminders:
                user.reminders.append(reason_list)
            else:
                user.reminders = [reason_list]

    @staticmethod
    async def create_self_assignable_role_cache():
        """Create cache for self assignable roles"""
        ex.cache.assignable_roles = {}

        async def get_all_roles():
            # get all self assignable roles
            try:
                for t_role_id, t_role_name, t_server_id in await ex.sql.fetch_all_self_assign_roles():
                    yield t_role_id, t_role_name, t_server_id
            except:
                return

        async def get_all_channels():
            # get all channels and server ids that have self assignable roles
            try:
                for t_channel_id, t_server_id in await ex.sql.fetch_all_self_assign_channels():
                    yield t_channel_id, t_server_id
            except:
                return

        async for role_id, role_name, server_id in get_all_roles():
            cache_info = ex.cache.assignable_roles.get(server_id)
            if not cache_info:
                ex.cache.assignable_roles[server_id] = {}
                cache_info = ex.cache.assignable_roles.get(server_id)
            if not cache_info.get('roles'):
                cache_info['roles'] = [[role_id, role_name]]
            else:
                cache_info['roles'].append([role_id, role_name])

        async for channel_id, server_id in get_all_channels():
            cache_info = ex.cache.assignable_roles.get(server_id)
            if cache_info:
                cache_info['channel_id'] = channel_id
            else:
                ex.cache.assignable_roles[server_id] = {'channel_id': channel_id}

    @staticmethod
    async def create_weverse_channel_cache():
        """Create cache for channels that are following a community on weverse."""
        ex.cache.weverse_channels = {}

        async def get_weverse():
            # get all weverse subscriptions
            try:
                for t_channel_id, t_community_name, t_role_id, t_comments_disabled in await ex.sql.fetch_weverse():
                    yield t_channel_id, t_community_name, t_role_id, t_comments_disabled
            except:
                return

        async for channel_id, community_name, role_id, comments_disabled in get_weverse():
            await ex.u_weverse.add_weverse_channel_to_cache(channel_id, community_name)
            await ex.u_weverse.add_weverse_role(channel_id, community_name, role_id)
            await ex.u_weverse.change_weverse_comment_status(channel_id, community_name, comments_disabled)

    async def update_command_counter(self):
        """Updates Cache for command counter and sessions"""
        ex.cache.command_counter = {}
        session_id = await self.get_session_id()

        async def get_commands():
            # gets all commands and their usage amount
            try:
                for t_command_name, t_count in await ex.sql.fetch_command(session_id):
                    yield t_command_name, t_count
            except:
                return

        async for command_name, count in get_commands():
            ex.cache.command_counter[command_name] = count

        ex.cache.current_session = ex.first_result(await ex.sql.fetch_session_usage(datetime.date.today()))

    @staticmethod
    async def create_restricted_channel_cache():
        """Create restricted idol channel cache"""
        async def get_restricted_channels():
            # gets all restricted idol photo channels
            try:
                for t_channel_id, t_server_id, t_send_here in await ex.sql.fetch_restricted_channels():
                    yield t_channel_id, t_server_id, t_send_here
            except:
                return

        async for channel_id, server_id, send_here in get_restricted_channels():
            ex.cache.restricted_channels[channel_id] = [server_id, send_here]

    @staticmethod
    async def create_bot_command_cache():
        """Create custom command cache"""
        ex.cache.custom_commands = {}

        async def get_custom_commands():
            try:
                for t_server_id, t_command_name, t_message in await ex.sql.fetch_custom_commands():
                    yield t_server_id, t_command_name, t_message
            except:
                return

        async for server_id, command_name, message in get_custom_commands():
            cache_info = ex.cache.custom_commands.get(server_id)
            if cache_info:
                cache_info[command_name] = message
            else:
                ex.cache.custom_commands[server_id] = {command_name: message}

    @staticmethod
    async def create_bot_status_cache():
        ex.cache.bot_statuses = []

        async def get_statuses():
            # get all bot statuses
            try:
                for t_status in await ex.sql.fetch_bot_statuses():
                    yield t_status
            except:
                return

        async for status in get_statuses():
            ex.cache.bot_statuses.append(status[0])

    @staticmethod
    async def create_dead_link_cache():
        """Creates Dead Link Cache"""
        ex.cache.dead_image_cache = {}
        try:
            ex.cache.dead_image_channel = await ex.client.fetch_channel(ex.keys.dead_image_channel_id)
        except:
            pass

        async def get_dead_links():
            try:
                for t_dead_link, t_user_id, t_message_id, t_idol_id, t_guessing_game in await ex.sql.fetch_dead_links():
                    yield t_dead_link, t_user_id, t_message_id, t_idol_id, t_guessing_game
            except:
                return

        async for dead_link, user_id, message_id, idol_id, guessing_game in get_dead_links():
            ex.cache.dead_image_cache[message_id] = [dead_link, user_id, idol_id, guessing_game]

    @staticmethod
    async def create_idol_cache():
        """Create Idol Objects and store them as cache."""
        ex.cache.idols = []
        # Clear and update these cache values to prevent breaking the memory reference made by
        # ex.cache.difficulty_selection and ex.cache.gender_selection
        ex.cache.idols_female.clear()
        ex.cache.idols_male.clear()
        ex.cache.idols_easy.clear()
        ex.cache.idols_medium.clear()
        ex.cache.idols_hard.clear()

        async def get_idols():
            # get all idols
            try:
                for t_idol in await ex.sql.fetch_all_idols():
                    yield t_idol
            except:
                return

        async for idol in get_idols():
            idol_obj = ex.u_objects.Idol(**idol)
            idol_obj.aliases, idol_obj.local_aliases = await ex.u_group_members.get_db_aliases(idol_obj.id)
            # add all group ids and remove potential duplicates
            idol_obj.groups = list(dict.fromkeys(await ex.u_group_members.get_db_groups_from_member(idol_obj.id)))
            idol_obj.called = await ex.u_group_members.get_db_idol_called(idol_obj.id)
            idol_obj.photo_count = ex.cache.idol_photos.get(idol_obj.id) or 0
            ex.cache.idols.append(idol_obj)

            if not idol_obj.photo_count:
                continue

            # all of the below conditions must be idols with photos.
            if idol_obj.gender == 'f':
                ex.cache.idols_female.add(idol_obj)
            if idol_obj.gender == 'm':
                ex.cache.idols_male.add(idol_obj)
            # add all idols to the easy difficulty
            ex.cache.idols_easy.add(idol_obj)
            if idol_obj.difficulty == 'medium':
                ex.cache.idols_medium.add(idol_obj)
            if idol_obj.difficulty == 'hard':
                ex.cache.idols_hard.add(idol_obj)

        ex.cache.gender_selection['all'] = set(ex.cache.idols)

    @staticmethod
    async def create_group_cache():
        """Create Group Objects and store them as cache"""
        ex.cache.groups = []

        async def get_groups():
            try:
                for t_group in await ex.sql.fetch_all_groups():
                    yield t_group
            except:
                return

        async for group in get_groups():
            group_obj = ex.u_objects.Group(**group)
            group_obj.aliases, group_obj.local_aliases = await ex.u_group_members.get_db_aliases(group_obj.id,
                                                                                                 group=True)
            # add all idol ids and remove potential duplicates
            group_obj.members = list(
                dict.fromkeys(await ex.u_group_members.get_db_members_in_group(group_obj.id)))
            group_obj.photo_count = ex.cache.group_photos.get(group_obj.id) or 0
            ex.cache.groups.append(group_obj)

    async def process_session(self):
        """Sets the new session id, total used, and time format for distinguishing days."""
        current_time_format = datetime.date.today()
        if ex.cache.session_id is None:
            if ex.cache.total_used is None:
                ex.cache.total_used = (ex.first_result(await ex.sql.fetch_total_session_usage())) or 0
            try:
                await ex.sql.add_new_session(ex.cache.total_used, 0, current_time_format)
            except:
                # session for today already exists.
                pass
            ex.cache.session_id = ex.first_result(await ex.sql.fetch_session_id(datetime.date.today()))
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
        async def get_n_word():
            # get all users n word count
            try:
                for t_user_id, t_n_word_counter in await ex.sql.fetch_n_word():
                    yield t_user_id, t_n_word_counter
            except:
                return

        async for user_id, n_word_counter in get_n_word():
            user = await ex.get_user(user_id)
            user.n_word = n_word_counter

    @staticmethod
    async def update_temp_channels():
        """Create the cache for temp channels."""
        ex.cache.temp_channels = {}

        async def get_temp_channels():
            # get all temp channels
            try:
                for t_channel_id, t_delay in await ex.sql.fetch_temp_channels():
                    yield t_channel_id, t_delay
            except:
                return

        async for channel_id, delay in get_temp_channels():
            removal_time = delay
            if removal_time < 60:
                removal_time = 60
            ex.cache.temp_channels[channel_id] = removal_time

    @staticmethod
    async def update_welcome_message_cache():
        """Create the cache for welcome messages."""
        ex.cache.welcome_messages = {}

        async def get_welcome_messages():
            # get all welcome messages
            try:
                for t_channel_id, t_server_id, t_message_id, t_enabled in await ex.sql.fetch_welcome_messages():
                    yield t_channel_id, t_server_id, t_message_id, t_enabled
            except:
                return

        async for channel_id, server_id, message_id, enabled in get_welcome_messages():
            ex.cache.welcome_messages[server_id] = {"channel_id": channel_id, "message": message_id, "enabled": enabled}

    @staticmethod
    async def update_server_prefixes():
        """Create the cache for server prefixes."""
        ex.cache.server_prefixes = {}

        async def get_server_prefixes():
            # get all server prefixes
            try:
                for t_server_id, t_prefix in await ex.sql.fetch_server_prefixes():
                    yield t_server_id, t_prefix
            except:
                return

        async for server_id, prefix in get_server_prefixes():
            ex.cache.server_prefixes[server_id] = prefix

    @staticmethod
    async def update_logging_channels():
        """Create the cache for logged servers and channels."""
        ex.cache.logged_channels = {}
        ex.cache.list_of_logged_channels = []

        async def get_logged_servers():
            # get all logged servers
            try:
                for t_p_id, t_server_id, t_channel_id, t_send_all in await ex.sql.fetch_logged_servers():
                    yield t_p_id, t_server_id, t_channel_id, t_send_all
            except:
                return

        async def get_logged_channels(primary_key):
            # get all logged channels
            try:
                for t_channel_id in await ex.sql.fetch_logged_channels(primary_key):
                    yield t_channel_id
            except:
                return

        async for p_id, server_id, channel_id, send_all in get_logged_servers():
            channel_ids = []
            async for channel in get_logged_channels(p_id):
                ex.cache.list_of_logged_channels.append(channel[0])
                channel_ids.append(channel[0])
            ex.cache.logged_channels[server_id] = {
                "send_all": send_all,
                "logging_channel": channel_id,
                "channels": channel_ids
            }

    @staticmethod
    async def update_bot_bans():
        """Create the cache for banned users from the bot."""
        async def get_bot_banned_users():
            # get bot banned users
            try:
                for t_user_id in await ex.sql.fetch_bot_bans():
                    yield t_user_id
            except:
                return

        async for user in get_bot_banned_users():
            user_id = user[0]
            user_obj = await ex.get_user(user_id)
            user_obj.bot_banned = True

    @staticmethod
    async def update_mod_mail():
        """Create the cache for existing mod mail"""
        ex.cache.mod_mail = {}

        async def get_mod_mail():
            # get mod mail users and channels
            try:
                for t_user_id, t_channel_id in await ex.sql.fetch_mod_mail():
                    yield t_user_id, t_channel_id
            except:
                return

        async for user_id, channel_id in get_mod_mail():
            user = await ex.get_user(user_id)
            user.mod_mail_channel_id = channel_id
            ex.cache.mod_mail[user_id] = [channel_id]  # full list

    @staticmethod
    async def update_patreons():
        """Create the cache for Patrons."""
        try:
            permanent_patrons = await ex.u_patreon.get_patreon_users()
            # normal patrons contains super patrons as well
            # TODO: remove function dependency on these 3 variables
            normal_patrons = [patron.id for patron in await ex.u_patreon.get_patreon_role_members(super_patron=False)]
            super_patrons = [patron.id for patron in await ex.u_patreon.get_patreon_role_members(super_patron=True)]

            # the reason for db cache is because of the new discord rate limit
            # where it now takes 20+ minutes for discord cache to fully load, meaning we can only
            # access the roles after 20 minutes on boot.
            # this is an alternative to get patreons instantly and later modifying the cache after the cache loads.
            # remove any patrons from db set cache that should not exist or should be modified.
            async def get_cached_patrons():
                # get cached patrons
                try:
                    for t_user_id, t_super_patron in await ex.sql.fetch_cached_patrons():
                        yield t_user_id, t_super_patron
                except:
                    return

            async def get_patrons(t_super_patron: bool = False):
                try:
                    for t_patron in await ex.u_patreon.get_patreon_role_members(super_patron=t_super_patron):
                        yield t_patron
                except:
                    return

            async def get_permanent_patrons():
                try:
                    for t_patron in await ex.u_patreon.get_patreon_users():
                        yield t_patron
                except:
                    return

            cached_patrons = []  # list of user ids removing patron status.
            async for user_id, super_patron in get_cached_patrons():
                cached_patrons.append(user_id)
                if user_id not in normal_patrons:
                    # they are not a patron at all, so remove them from db cache
                    await ex.sql.delete_patron(user_id)
                elif user_id in super_patrons and not super_patron:
                    # if they are a super patron but their db is cache is a normal patron
                    await ex.sql.update_patron(user_id, 1)
                elif user_id not in super_patrons and super_patron:
                    # if they are not a super patron, but the db cache says they are.
                    await ex.sql.update_patron(user_id, 0)

            # fix db cache and live Irene cache
            async for patron in get_patrons():
                if patron not in cached_patrons:
                    # patron includes both normal and super patrons.
                    await ex.sql.add_patron(patron, 0)
                user = await ex.get_user(patron)
                user.patron = True

            async for patron in get_patrons(t_super_patron=True):
                if patron not in cached_patrons:
                    await ex.sql.update_patron(patron, 1)
                user = await ex.get_user(patron)
                user.patron = True
                user.super_patron = True

            async for patron in get_permanent_patrons():
                user = await ex.get_user(patron[0])
                user.patron = True
                user.super_patron = True
            return True
        except:
            return False

    @staticmethod
    async def update_user_notifications():
        """Set the cache for user phrases"""
        ex.cache.user_notifications = []
        notifications = await ex.conn.fetch("SELECT guildid,userid,phrase FROM general.notifications")
        for guild_id, user_id, phrase in notifications:
            user = await ex.get_user(user_id)
            user.notifications.append([guild_id, phrase])
            ex.cache.user_notifications.append([guild_id, user_id, phrase])  # full list.

    @staticmethod
    async def update_groups():
        """Set cache for group photo count"""
        ex.cache.group_photos = {}
        all_group_counts = await ex.conn.fetch(
            "SELECT g.groupid, g.groupname, COUNT(f.link) FROM groupmembers.groups g, groupmembers.member m, groupmembers.idoltogroup l, groupmembers.imagelinks f WHERE m.id = l.idolid AND g.groupid = l.groupid AND f.memberid = m.id GROUP BY g.groupid ORDER BY g.groupname")
        for group in all_group_counts:
            ex.cache.group_photos[group[0]] = group[2]

    @staticmethod
    async def update_guild_cache():
        """Update the DB Guild Cache. Useful for updating info for API."""
        # much simpler to just delete all of the cache and reinsert instead of updating fields.
        try:
            log.console("Attempting to send guild information to DB.")
            await ex.conn.execute("DELETE FROM stats.guilds")

            guild_data = []
            for guild in ex.client.guilds:
                guild_data.append(
                    (guild.id, guild.name, len(guild.emojis), f"{guild.region}", guild.afk_timeout, guild.icon,
                     guild.owner_id,
                     guild.banner, guild.description, guild.mfa_level, guild.splash,
                     guild.premium_tier, guild.premium_subscription_count, len(guild.text_channels),
                     len(guild.voice_channels), len(guild.categories), guild.emoji_limit, guild.member_count,
                     len(guild.roles), guild.shard_id, guild.created_at)
                )

            async with ex.conn.acquire() as direct_conn:
                await direct_conn.copy_records_to_table('guilds', records=guild_data, schema_name="stats")
        except Exception as e:
            log.console(f"{e} - Failed to update guild cache")

    @staticmethod
    async def update_idols():
        """Set cache for idol photo count"""
        ex.cache.idol_photos = {}
        all_idol_counts = await ex.conn.fetch(
            "SELECT memberid, COUNT(link) FROM groupmembers.imagelinks GROUP BY memberid")
        for idol_id, count in all_idol_counts:
            ex.cache.idol_photos[idol_id] = count

    @tasks.loop(seconds=0, minutes=0, hours=12, reconnect=True)
    async def update_cache(self):
        """Looped every 12 hours to update the cache in case of anything faulty."""
        while not ex.conn:
            await asyncio.sleep(1)
        await self.create_cache()

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def update_patron_and_guild_cache(self):
        """Looped until patron cache is loaded.
        This was added due to intents slowing d.py cache loading rate.
        """
        # create a temporary patron list based on the db cache while waiting for the discord cache to load
        try:
            if ex.conn:
                if not ex.temp_patrons_loaded:
                    while not ex.irene_cache_loaded:
                        # wait until Irene's cache has been loaded before creating temporary patrons
                        # this is so that the user objects do not overwrite each other
                        # when being created.
                        await asyncio.sleep(5)
                    cached_patrons = await ex.conn.fetch("SELECT userid, super FROM patreon.cache")
                    for user_id, super_patron in cached_patrons:
                        user = await ex.get_user(user_id)
                        if super_patron:
                            log.console(f"Made {user_id} a temporary super patron & patron.")
                            user.super_patron = True
                        else:
                            log.console(f"Made {user_id} a temporary patron.")
                        user.patron = True
                    ex.temp_patrons_loaded = True
                    log.console("Cache for Temporary Patrons has been created.")
                while not ex.discord_cache_loaded:
                    await asyncio.sleep(60)  # check every minute if discord cache has loaded.
                # update guild cache
                await self.process_cache_time(self.update_guild_cache, "DB Guild")

                # update patron cache
                if await self.process_cache_time(self.update_patreons, "Patrons"):
                    self.update_patron_cache_hour.start()
                    self.update_patron_and_guild_cache.stop()
        except Exception as e:
            log.console(e)

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
                user_notifications = 0
                patron_count = 0
                mod_mail = 0
                bot_banned = 0
                active_user_reminders = 0
                for user in ex.cache.users.values():
                    user_notifications += len(user.notifications)
                    if user.patron:
                        patron_count += 1
                    if user.mod_mail_channel_id:
                        mod_mail += 1
                    if user.bot_banned:
                        bot_banned += 1
                    active_user_reminders += len(user.reminders)

                metric_info = {
                    'total_commands_used': ex.cache.total_used,
                    'bias_games': len(ex.cache.bias_games),
                    'guessing_games': len(ex.cache.guessing_games),
                    'patrons': patron_count,
                    'custom_server_prefixes': len(ex.cache.server_prefixes),
                    'session_commands_used': ex.cache.current_session,
                    'user_notifications': user_notifications,
                    'mod_mail': mod_mail,
                    'banned_from_bot': bot_banned,
                    'logged_servers': len(ex.cache.logged_channels),
                    # server count is based on discord.py guild cache which takes a large amount of time to load fully.
                    # There may be inaccurate data points on a new instance of the bot due to the amount of
                    # time that it takes.
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
                    'active_user_reminders': active_user_reminders,
                    'weverse_channels_following': sum([len(channels) for channels in ex.cache.weverse_channels.
                                                      values()]),
                    'weverse_following_txt': len(ex.cache.weverse_channels.get("txt") or []),
                    'weverse_following_bts': len(ex.cache.weverse_channels.get("bts") or []),
                    'weverse_following_gfriend': len(ex.cache.weverse_channels.get("gfriend") or []),
                    'weverse_following_seventeen': len(ex.cache.weverse_channels.get("seventeen") or []),
                    'weverse_following_enhypen': len(ex.cache.weverse_channels.get("enhypen") or []),
                    'weverse_following_nuest': len(ex.cache.weverse_channels.get("nu'est") or []),
                    'weverse_following_cl': len(ex.cache.weverse_channels.get("cl") or []),
                    'weverse_following_p1harmony': len(ex.cache.weverse_channels.get("p1harmony") or []),
                    'weverse_following_weeekly': len(ex.cache.weverse_channels.get("weeekly") or []),
                    'weverse_following_sunmi': len(ex.cache.weverse_channels.get("sunmi") or []),
                    'weverse_following_henry': len(ex.cache.weverse_channels.get("henry") or []),
                    'weverse_following_dreamcatcher': len(ex.cache.weverse_channels.get("dreamcatcher") or []),
                    'twitch_channels_followed': len(ex.cache.twitch_channels.keys() or []),
                    'text_channels_following_twitch': sum([len(channels) for channels in ex.cache.twitch_channels.
                                                          values()]),
                    'voice_clients': len(ex.client.voice_clients or []),
                    'servers_using_self_assignable_roles': len(ex.cache.assignable_roles.keys() or []),
                    'total_amount_of_self_assignable_roles': sum([len(channel_and_roles.get('roles') or [])
                                                                  for channel_and_roles in
                                                                  ex.cache.assignable_roles.values()])
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
