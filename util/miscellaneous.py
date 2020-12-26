from module import logger as log
from Utility import resources as ex
from module.keys import bot_prefix, bot_support_server_link, api_port, bot_id, bot_name, translate_private_key
import discord
import random
import json


class Miscellaneous:
    async def check_for_nword(self, message):
        """Processes new messages that contains the N word."""
        message_sender = message.author
        if not message_sender.bot:
            message_content = message.clean_content
            if ex.u_miscellaneous.check_message_not_empty(message):
                # check if the message belongs to the bot
                    if message_content[0] != '%':
                        if ex.u_miscellaneous.check_nword(message_content):
                            ex.cache.n_words_per_minute += 1
                            author_id = message_sender.id
                            current_amount = ex.cache.n_word_counter.get(author_id)
                            if current_amount:
                                await ex.conn.execute("UPDATE general.nword SET nword = $1 WHERE userid = $2::bigint",
                                                        current_amount + 1, author_id)
                                ex.cache.n_word_counter[author_id] = current_amount + 1
                            else:
                                await ex.conn.execute("INSERT INTO general.nword VALUES ($1,$2)", author_id, 1)
                                ex.cache.n_word_counter[author_id] = 1

    async def check_if_temp_channel(self, channel_id):
        """Check if a channel is a temp channel"""
        return ex.cache.temp_channels.get(channel_id) is not None  # do not change structure

    async def get_temp_channels(self):
        """Get all temporary channels in the DB."""
        return await ex.conn.fetch("SELECT chanid, delay FROM general.tempchannels")

    async def delete_temp_messages(self, message):
        """Delete messages that are temp channels"""
        if await self.check_if_temp_channel(message.channel.id):
            await message.delete(delay=ex.cache.temp_channels.get(message.channel.id))

    async def get_disabled_server_interactions(self, server_id):
        """Get a server's disabled interactions."""
        interactions = await ex.conn.fetchrow("SELECT interactions FROM general.disabledinteractions WHERE serverid = $1", server_id)
        return ex.first_result(interactions)

    async def disable_interaction(self, server_id, interaction):
        """Disable an interaction (to a specific server)"""
        interaction = interaction.lower()
        interactions = await self.get_disabled_server_interactions(server_id)
        if not interactions:
            await ex.conn.execute("INSERT INTO general.disabledinteractions(serverid, interactions) VALUES ($1, $2)", server_id, interaction)
        else:
            interactions = interactions.split(',')
            interactions.append(interaction)
            interactions = ','.join(interactions)
            await ex.conn.execute("UPDATE general.disabledinteractions SET interactions = $1 WHERE serverid = $2", interactions, server_id)

    async def enable_interaction(self, server_id, interaction):
        """Reenable an interaction that was disabled by a server"""
        interactions = await self.get_disabled_server_interactions(server_id)
        if not interactions:
            return
        else:
            interactions = interactions.split(',')
            interactions.remove(interaction)
            interactions = ','.join(interactions)
            if not interactions:
                return await ex.conn.execute("DELETE FROM general.disabledinteractions WHERE serverid = $1", server_id)
            await ex.conn.execute("UPDATE general.disabledinteractions SET interactions = $1 WHERE serverid = $2", interactions, server_id)

    async def interact_with_user(self, ctx, user, interaction, interaction_type, self_interaction=False):
        await ex.u_patreon.reset_patreon_cooldown(ctx)
        try:
            if user == discord.Member:
                user = ctx.author
            list_of_links = await ex.conn.fetch("SELECT url FROM general.interactions WHERE interaction = $1", interaction_type)
            if not self_interaction:
                if ctx.author.id == user.id:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send(f"> **{ctx.author.display_name}, you cannot perform this interaction on yourself.**")
            link = random.choice(list_of_links)
            embed = discord.Embed(title=f"**{ctx.author.display_name}** {interaction} **{user.display_name}**", color=ex.get_random_color())
            if not await ex.u_patreon.check_if_patreon(ctx.author.id):
                embed.set_footer(text=f"Become a {await ex.get_server_prefix_by_context(ctx)}patreon to get rid of interaction cooldowns!")
            embed.set_image(url=link[0])
            return await ctx.send(embed=embed)
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> **{ctx.author.display_name}, there are no links saved for this interaction yet.**")

    async def add_command_count(self, command_name):
        """Add 1 to the specific command count and to the count of the current minute."""
        ex.cache.commands_per_minute += 1
        session_id = await ex.u_cache.get_session_id()
        command_count = self.cache.command_counter.get(command_name)
        if not command_count:
            await ex.conn.execute("INSERT INTO stats.commands(sessionid, commandname, count) VALUES($1, $2, $3)", session_id, command_name, 1)
            ex.cache.command_counter[command_name] = 1
        else:
            await ex.conn.execute("UPDATE stats.commands SET count = $1 WHERE commandname = $2 AND sessionid = $3", command_count + 1, command_name, session_id)
            ex.cache.command_counter[command_name] += 1

    async def add_session_count(self):
        """Adds one to the current session count for commands used and for the total used."""
        session_id = await ex.u_cache.get_session_id()
        ex.cache.current_session += 1
        ex.cache.total_used += 1
        await ex.conn.execute("UPDATE stats.sessions SET session = $1, totalused = $2 WHERE sessionid = $3", self.cache.current_session, self.cache.total_used, session_id)

    async def process_commands(self, message):
        message_sender = message.author
        if not message_sender.bot:
            message_content = message.clean_content
            message_channel = message.channel
            server_prefix = await ex.get_server_prefix_by_context(message)
            # check if the user mentioned the bot and send them a help message.
            if await self.check_for_bot_mentions(message):
                await message.channel.send(
                    f"Type `{server_prefix}help` for information on commands.")
            if len(message_content) >= len(server_prefix):
                changing_prefix = [bot_prefix + 'setprefix', bot_prefix + 'checkprefix']
                if message.content[0:len(server_prefix)].lower() == server_prefix.lower() or message.content.lower() in changing_prefix:
                    msg_without_prefix = message.content[len(server_prefix):len(message.content)]
                    # only replace the prefix portion back to the default prefix if it is not %setprefix or %checkprefix
                    if message.content.lower() not in changing_prefix:
                        # change message.content so all on_message listeners have a bot prefix
                        message.content = bot_prefix + msg_without_prefix
                    # if a user is banned from the bot.
                    if await self.check_if_bot_banned(message_sender.id):
                        try:
                            guild_id = await ex.get_server_id(message)
                        except Exception as e:
                            guild_id = None
                        if await self.check_message_is_command(message) or await ex.u_custom_commands.check_custom_command_name_exists(guild_id, msg_without_prefix):
                            await self.send_ban_message(message_channel)
                    else:
                        await ex.client.process_commands(message)

    async def send_maintenance_message(self, channel):
        try:
            reason = ""
            if ex.cache.maintenance_reason:
                reason = f"\nREASON: {ex.cache.maintenance_reason}"
            await channel.send(
                f">>> **A maintenance is currently in progress. Join the support server for more information. <{bot_support_server_link}>{reason}**")
        except Exception as e:
            pass

    async def get_api_status(self):
        end_point = f"http://127.0.0.1:{api_port}"
        try:
            async with ex.session.get(end_point) as r:
                return r.status == 200
        except Exception as e:
            pass

    async def get_db_status(self):
        end_point = f"http://127.0.0.1:{5050}"
        try:
            async with ex.session.get(end_point) as r:
                return r.status == 200

        except Exception as e:
            pass

    async def get_images_status(self):
        end_point = f"http://images.irenebot.com/index.html"
        try:
            async with ex.session.get(end_point) as r:
                return r.status == 200
        except Exception as e:
            pass

    @staticmethod
    async def check_if_moderator(ctx):
        """Check if a user is a moderator on a server"""
        return (ctx.author.permissions_in(ctx.channel)).manage_messages

    @staticmethod
    async def check_for_bot_mentions(message):
        """Returns true if the message is only a bot mention and nothing else."""
        return message.content == f"<@!{bot_id}>"

    async def check_message_is_command(self, message, is_command_name=False):
        """Check if a message is a command."""
        if not is_command_name:
            for command_name in ex.client.all_commands:
                if command_name in message.content:
                    if len(command_name) != 1:
                        return True
            return False
        if is_command_name:
            return message in ex.client.all_commands

    @staticmethod
    async def send_ban_message(channel):
        """A message to send for a user that is banned from the bot."""
        await channel.send(
            f"> **You are banned from using {bot_name}. Join <{bot_support_server_link}>**")

    async def ban_user_from_bot(self, user_id):
        """Bans a user from using the bot."""
        await ex.conn.execute("INSERT INTO general.blacklisted(userid) VALUES ($1)", user_id)
        ex.cache.bot_banned.append(user_id)

    async def unban_user_from_bot(self, user_id):
        """UnBans a user from the bot."""
        await ex.conn.execute("DELETE FROM general.blacklisted WHERE userid = $1", user_id)
        try:
            ex.cache.bot_banned.remove(user_id)
        except Exception as e:
            pass

    async def check_if_bot_banned(self, user_id):
        """Check if the user can use the bot."""
        return user_id in ex.cache.bot_banned

    @staticmethod
    def check_nword(message_content):
        """Check if a message contains the NWord."""
        message_split = message_content.lower().split()
        return 'nigga' in message_split or 'nigger' in message_split and ':' not in message_split

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
    def check_message_not_empty(message):
        """Check if a message has content."""
        # do not simplify
        try:
            if message.clean_content:
                return True
        except Exception as e:
            pass

    async def translate(self, text, src_lang, target_lang):
        try:
            data = {
                'text': text,
                'src_lang': await self.get_language_code(src_lang),
                'target_lang': await self.get_language_code(target_lang),
                'p_key': translate_private_key
            }
            end_point = f"http://127.0.0.1:{api_port}/translate"
            if ex.test_bot:
                end_point = f"https://api.irenebot.com/translate"
            async with ex.session.post(end_point, data=data) as r:
                ex.cache.bot_api_translation_calls += 1
                if r.status == 200:
                    return json.loads(await r.text())
                else:
                    return None
        except Exception as e:
            log.console(e)

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

    def get_user_count(self):
        """Get the amount of users that the bot is watching over."""
        counter = 0
        for guild in ex.client.guilds:
            counter += guild.member_count
        return counter

    def get_server_count(self):
        """Returns the guild count the bot is connected to."""
        return len(ex.client.guilds)

    def get_channel_count(self):
        """Returns the channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in ex.client.guilds:
            count += len(guild.channels)
        return count

    def get_text_channel_count(self):
        """Returns the text channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in ex.client.guilds:
            count += len(guild.text_channels)
        return count

    def get_voice_channel_count(self):
        """Returns the voice channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in ex.client.guilds:
            count += len(guild.voice_channels)
        return count
