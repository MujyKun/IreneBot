import asyncio
import discord
from random import *
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
from datetime import datetime, date


# noinspection PyBroadException,PyPep8
class Miscellaneous(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex

    async def on_message_user_notifications(self, message):
        # user phrase notifications
        try:
            if message.author.bot:
                return

            message_split = message.content.lower().split(" ")
            for guild_id, user_id, phrase in self.ex.cache.user_notifications:
                await asyncio.sleep(0)
                if phrase not in message_split or guild_id != message.guild.id:
                    continue
                if message.author.id == user_id or user_id not in [member.id for member in message.channel.members]:
                    continue

                log.console(f"message_notifications 1 - {phrase} to {user_id}")
                dm_channel = await self.ex.get_dm_channel(user_id)
                log.console(f"message_notifications 2 - {phrase} to {user_id}")
                start_loc = (message.content.lower()).find(phrase)
                end_loc = start_loc + len(phrase)
                new_message_content = f"{message.content[0:start_loc]}`{message.content[start_loc:end_loc]}`" \
                    f"{message.content[end_loc:len(message.content)]}"
                title_desc = f"""
Phrase: {phrase}
Message Author: {message.author}

**Message:** {new_message_content}
[Click to go to the Message]({message.jump_url})
"""
                embed = await self.ex.create_embed(title="Phrase Found", color=self.ex.get_random_color(),
                                                   title_desc=title_desc)
                await dm_channel.send(embed=embed)
        except Exception as e:
            log.useless(f"{e} (Exception) - User Phrase",
                        method=self.on_message_user_notifications)

    @commands.command()
    async def setlanguage(self, ctx, language_choice):
        """Changes language of Irene. Available Choices: en_us"""
        user = await self.ex.get_user(ctx.author.id)
        language_choice = language_choice.lower()
        if language_choice in self.ex.cache.languages.keys():
            await user.set_language(language_choice)
            msg_str = self.ex.cache.languages[language_choice]['miscellaneous']['set_language_success']
        else:
            msg_str = await self.ex.get_msg(user, "miscellaneous", "set_language_fail")

        msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["language", user.language],
                                                  ["languages", ", ".join(self.ex.cache.languages.keys())]])

        return await ctx.send(msg_str)

    @commands.command()
    async def vote(self, ctx):
        """
        Link to Voting for Irene on Top.gg

        [Format: %vote]
        """
        return await ctx.send(f"> https://top.gg/bot/{self.ex.keys.bot_id}/vote")

    @commands.command()
    async def choose(self, ctx, *, options):
        """
        Choose between a selection of options. Underscores are spaces between words. Spaces separate choices.

        [Format: %choose (option_1 option_2 option_3)]
        """
        options = options.split(' ')
        random_choice = (choice(options)).replace('_', ' ')
        embed = await self.ex.create_embed(title="Random Choice", title_desc=f"{ctx.author.display_name}, your choice "
                                                                             f"is **{random_choice}**")
        return await ctx.send(embed=embed)

    @commands.command()
    async def displayemoji(self, ctx, emoji: discord.PartialEmoji):
        """
        Display an emoji.

        [Format: %displayemoji :emoji:]
        """
        return await ctx.send(emoji.url)

    @commands.command()
    async def addnoti(self, ctx, *, phrase):
        """
        Receive a DM whenever a phrase or word is said in the current server.

        [Format: %addnoti (phrase/word)]
        """
        try:
            check_exists = self.ex.first_result(
                await self.ex.conn.fetchrow("SELECT COUNT(*) FROM general.notifications WHERE guildid = $1 AND "
                                            "userid = $2 AND phrase = $3", ctx.guild.id, ctx.author.id, phrase.lower()))
            if check_exists:
                raise Exception
            await self.ex.conn.execute("INSERT INTO general.notifications(guildid,userid,phrase) VALUES($1, $2, $3)",
                                       ctx.guild.id, ctx.author.id, phrase.lower())
            user = await self.ex.get_user(ctx.author.id)
            user.notifications.append([ctx.guild.id, phrase.lower()])
            self.ex.cache.user_notifications.append([ctx.guild.id, ctx.author.id, phrase.lower()])  # full list
            await ctx.send(f"> **{ctx.author.display_name}, I added `{phrase}` to your notifications.**")
        except AttributeError:
            return await ctx.send(f"> **{ctx.author.display_name}, You are not allowed to use this command in DMs.**")
        except:
            await ctx.send(f"> **{ctx.author.display_name}, You are already receiving notifications for `{phrase}`**")

    @commands.command(aliases=["deletenoti"])
    async def removenoti(self, ctx, *, phrase):
        """
        Remove a phrase/word when it said in the current server.

        [Format: %removenoti (phrase/word)]
        """
        if isinstance(ctx.channel, discord.DMChannel):
            raise commands.NoPrivateMessage

        try:
            await self.ex.conn.execute("DELETE FROM general.notifications WHERE guildid=$1 AND userid=$2 AND phrase=$3",
                                       ctx.guild.id, ctx.author.id, phrase.lower())
            try:
                user = await self.ex.get_user(ctx.author.id)
                user.notifications.remove([ctx.guild.id, phrase.lower()])
                self.ex.cache.user_notifications.remove([ctx.guild.id, ctx.author.id, phrase.lower()])  # full list
            except Exception as e:
                log.useless(f"{e} (Exception) - Failed to remove user phrase", method=self.removenoti)
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "noti_removed"))
        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(ctx, "general", "error", ["e", e]))

    @commands.command()
    async def listnoti(self, ctx):
        """
        list all your notification phrases that exist in the current server.

        [Format: %listnoti]
        """
        try:
            user = await self.ex.get_user(ctx.author.id)
            if not user.notifications:
                raise AttributeError
            final_list = ""
            counter = 0
            current_guild_id = ctx.guild.id
            for guild_id, phrase in user.notifications:
                await asyncio.sleep(0)
                counter += 1
                if guild_id != current_guild_id:
                    continue
                if counter != len(user.notifications):
                    final_list += f"**{phrase}**,"
                else:
                    final_list += f"**{phrase}**"
            await ctx.send(final_list)
        except AttributeError:
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "no_notis"))
        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(ctx, "general", "error", ["e", e]))

    @commands.command(aliases=['patron'])
    async def patreon(self, ctx):
        """
        Displays Patreon Information.

        [Format: %patreon]
        """
        await ctx.send(f"**Please support <@{self.ex.keys.bot_id}>'s development at {self.ex.keys.patreon_link}.**")

    @commands.command()
    async def botinfo(self, ctx):
        """Get information about the bot."""
        maintenance_status = api_status = db_status = images_status = d_py_status = \
            irene_cache_status = ":red_circle:"

        working = ":green_circle:"
        if await self.ex.u_miscellaneous.get_api_status():
            api_status = working
        if await self.ex.u_miscellaneous.get_db_status():
            db_status = working
        if await self.ex.u_miscellaneous.get_images_status():
            images_status = working
        if self.ex.cache.maintenance_mode:
            maintenance_status = working
        if self.ex.discord_cache_loaded:
            d_py_status = working
        if self.ex.irene_cache_loaded:
            irene_cache_status = working

        try:
            current_server_prefix = await self.ex.get_server_prefix(ctx.guild.id)
        except:
            current_server_prefix = self.ex.keys.bot_prefix
        app = await self.ex.client.application_info()
        app_id = app.id
        app_name = app.name
        app_owner = app.owner
        app_icon_url = app.icon_url
        patreon_url = self.ex.keys.patreon_link
        bot_uptime = await self.ex.u_miscellaneous.get_cooldown_time((datetime.now() -
                                                                      self.ex.keys.startup_time).total_seconds())
        bot_server_links = """
[Top.gg](https://top.gg/bot/520369375325454371)
[Discord Bots](https://discord.bots.gg/bots/520369375325454371)
[Bots on Discord](https://bots.ondiscord.xyz/bots/520369375325454371)
[Discord Boats](https://discord.boats/bot/520369375325454371)
        """
        mods = ""
        for bot_mod in self.ex.keys.mods_list:
            await asyncio.sleep(0)
            mods += f"<@{bot_mod}> | "
        title_desc = f"""I was made with Python using the discord.py wrapper.

API Status: {api_status} 
Images Status: {images_status} 
Database Status: {db_status} 
Irene Cache: {irene_cache_status}
discord.py Cache: {d_py_status}
Maintenance Status: {maintenance_status}
"""
        embed = await self.ex.create_embed(title=f"I am {app_name}! ({app_id})", title_desc=title_desc)
        embed.set_thumbnail(url=app_icon_url)

        embed.add_field(name="Servers Connected", value=f"{self.ex.u_miscellaneous.get_server_count()} Servers",
                        inline=True)
        embed.add_field(name="Text/Voice Channels Watched",
                        value=f"{self.ex.u_miscellaneous.get_text_channel_count()}/"
                              f"{self.ex.u_miscellaneous.get_voice_channel_count()} Channels", inline=True)
        embed.add_field(name="Servers/Channels Logged",
                        value=f"{len(await self.ex.u_logging.get_servers_logged())}"
                              f"/{len(await self.ex.u_logging.get_channels_logged())} Logged", inline=True)
        embed.add_field(name="Bot Uptime", value=bot_uptime, inline=True)
        embed.add_field(name="Total Commands Used", value=f"{self.ex.cache.total_used} Commands", inline=True)
        embed.add_field(name=f"This Session ({self.ex.cache.session_id} | {date.today()})",
                        value=f"{self.ex.cache.current_session} Commands", inline=True)
        embed.add_field(name="Playing Music", value=f"{len(self.ex.client.voice_clients)} Wavelink Players",
                        inline=True)
        embed.add_field(name="Playing Guessing/Bias/Unscramble/BlackJack",
                        value=f"{len(self.ex.cache.guessing_games)}/{len(self.ex.cache.bias_games)}"
                              f"/{len(self.ex.cache.unscramble_games)}/{len(self.ex.cache.blackjack_games)} Games",
                        inline=True)
        embed.add_field(name="Ping", value=f"{self.ex.get_ping()} ms", inline=True)
        embed.add_field(name="Shards", value=f"{self.ex.client.shard_count}", inline=True)
        embed.add_field(name="Bot Owner", value=f"<@{app_owner.id}>", inline=True)
        if mods:
            embed.add_field(name="Bot Mods", value=mods, inline=True)
        embed.add_field(name="Support Server", value=f"[Invite to Server]({self.ex.keys.bot_support_server_link})",
                        inline=False)
        embed.add_field(name="Website", value=self.ex.keys.bot_website, inline=False)
        embed.add_field(name="Github", value=f"https://github.com/MujyKun/IreneBot", inline=False)
        embed.add_field(name="Discord Invite", value=self.ex.keys.bot_invite_link, inline=False)
        embed.add_field(name="Bot Server Links", value=bot_server_links, inline=False)
        embed.add_field(name="Suggest", value=f"Suggest a feature using `{current_server_prefix}suggest`.",
                        inline=False)
        if patreon_url:
            embed.add_field(name="Patreon", value=f"[Please Support <@{self.ex.keys.bot_id}> here.]({patreon_url})",
                            inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def checkprefix(self, ctx):
        """Check the current prefix using the default prefix."""
        # noinspection PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException
        try:
            await ctx.send(f"> **Your current server prefix is {await self.ex.get_server_prefix(ctx.guild.id)}**")
        except:
            await ctx.send(f"> **Your current prefix is {self.ex.keys.bot_prefix}**.")

    @commands.command(aliases=['trans', 't'])
    async def translate(self, ctx, from_language, to_language, *, message):
        """
        Translate between languages using Papago

        [Format: %translate English Korean this is a test phrase.]
        """
        try:
            response = await self.ex.u_miscellaneous.translate(message, from_language, to_language)
            if not response:
                return await ctx.send(
                    "**My Papago Translation Service is currently turned off and cannot process requests "
                    "OR you did not enter the right format.**")
            code = response['code']
            if code != 0:
                return await ctx.send("> **Something went wrong and I did not receive a proper response from Papago.**")
            text = response['text']
            target_lang = response['source']
            msg = f"Original ({target_lang}): {message} \nTranslated ({to_language}): {text} "
            return await ctx.send(msg)
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "error", ["e", e]))
            log.console(e)

    @commands.command()
    async def report(self, ctx, *, issue):
        """
        Report an issue with Irene.

        Format: [%report (issue)]
        """
        desc = f"**{issue}**"
        embed = discord.Embed(title="Bug Report", color=0xff00f6)
        embed.set_author(name="Irene", url=self.ex.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a report.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        try:
            # 403 error ( no access ) on testing
            channel = await self.ex.client.fetch_channel(self.ex.keys.report_channel_id)
            msg = await channel.send(embed=embed)
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "bug_sent"))
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except:
            # Error would occur on test bot if the client does not have access to a certain channel id
            # this try-except will also be useful if a server removed the bot.
            await ctx.send(await self.ex.get_msg(ctx, "general", "error",
                                                 ["e", "Could not fetch channel to report to."]))

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        """
        Suggest a feature for Irene.

        Format: [%suggest (suggestion)]
        """
        desc = f"**{suggestion}**"
        embed = discord.Embed(title="Suggestion", color=0xff00f6)
        embed.set_author(name="Irene", url=self.ex.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a suggestion.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        try:
            channel = await self.ex.client.fetch_channel(self.ex.keys.suggest_channel_id)  # 403 error on testing
            msg = await channel.send(embed=embed)
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "suggestion_sent"))
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(ctx, "general", "error",
                                                 ["e", "Could not fetch channel to report to."]))

    @commands.command(aliases=['rand', 'randint', 'r'])
    async def random(self, ctx, a: int, b: int):
        """Choose a random number from a range (a,b)."""
        try:
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "random_number", ["result", randint(a, b)]))
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "error", ["e", e]))

    @commands.command(aliases=['coinflip', 'f'])
    async def flip(self, ctx):
        """
        Flips a coin

        [Format: %flip]
        [Aliases: coinflip, f]
        """
        await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "coin_flip", ["result", choice(['Heads', 'Tails'])]))

    @commands.command(aliases=['define', 'u'])
    async def urban(self, ctx, term=None, number=1, override=0):
        """
        Search a term through UrbanDictionary. Underscores are spaces.

        [Format: %urban (term) (definition number)]
        [Aliases: define,u]
        """
        if not ctx.channel.is_nsfw() and not override == 1:
            server_prefix = await self.ex.get_server_prefix(ctx)
            return await ctx.send(f">>> **This text channel must be NSFW to use {server_prefix}"
                                  f"urban (Guidelines set by top.gg).**\nTo override this, You may add a **1** "
                                  f"after the definition number.\nExample: {server_prefix}urban hello "
                                  f"(definition number) **1**.")
        if not term:
            return await ctx.send("> **Please enter a word for me to define**")
        term = term.replace("_", " ")
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        querystring = {"term": f"{term}"}
        async with self.ex.session.get(url, headers=self.ex.keys.X_RapidAPI_headers, params=querystring) as r:
            self.ex.cache.urban_per_minute += 1
            if r.status != 200:
                log.console(f"The connection to the UrbanDictionary API failed. -> {r.status}")
                return await ctx.send("> **The connection to the UrbanDictionary API failed.**")
            result = await r.json()
            try:
                first_result = (result['list'])[number-1]
            except:
                return await ctx.send(f"> **It is not possible to find definition number `{number}` for the word: "
                                      f"`{term}`.**")
            await ctx.send(f">>> **`Word: {term}`\n`Definition Number: {number}`\n{first_result['definition']}**")

    @commands.command()
    async def invite(self, ctx):
        """Invite Link to add Irene to a server."""
        await ctx.send(f"> **Invite Link:** {self.ex.keys.bot_invite_link}")

    @commands.command()
    async def support(self, ctx):
        """Invite Link to Irene's Discord Server"""
        await ctx.send(f"> **Support Server:** {self.ex.keys.bot_support_server_link}")

    @commands.command()
    @commands.is_owner()
    async def announce(self, ctx, *, new_message):
        """
        Sends a bot message to system text channels.

        NOTE: This should not be used if a lot of servers are using the bot.
        """
        desc = f"{new_message}"
        embed = discord.Embed(title=f"Announcement from {ctx.author} ({ctx.author.id})", description=desc,
                              color=0xff00f6)
        embed.set_author(name="Irene", url=self.ex.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %support for an invite to Irene's discord server.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        # embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)

        guilds = self.ex.client.guilds
        for guild in guilds:
            try:
                await guild.system_channel.send(embed=embed)
            except Exception as e:
                log.console(e)

    @commands.command()
    async def servercount(self, ctx):
        """
        Shows how many servers the bot has

        [Format: %servercount]
        """
        await ctx.send(f"> **I am connected to {self.ex.u_miscellaneous.get_server_count()} servers.**")

    @commands.command()
    async def serverinfo(self, ctx):
        """
        View information about the current guild.

        [Format: %serverinfo]
        """
        try:
            guild = ctx.guild
            embed = discord.Embed(title=f"{guild.name} ({guild.id})", color=0xffb6c1, url=f"{guild.icon_url}")
            embed.set_author(name="Irene", url=self.ex.keys.bot_website,
                             icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
            embed.set_footer(text="Thanks for using Irene.",
                             icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner.id})", inline=True)
            embed.add_field(name="Region", value=guild.region, inline=True)
            embed.add_field(name="Users", value=guild.member_count, inline=True)
            embed.add_field(name="Roles", value=f"{len(guild.roles)}", inline=True)
            embed.add_field(name="Emojis", value=f"{len(guild.emojis)}", inline=True)
            embed.add_field(name="Description", value=guild.description, inline=True)
            embed.add_field(name="Channels", value=f"{len(guild.channels)}", inline=True)
            embed.add_field(name="AFK Timeout", value=f"{guild.afk_timeout/60} minutes", inline=True)
            embed.add_field(name="Since", value=guild.created_at, inline=True)

            await ctx.send(embed=embed)
        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "not_in_cache"))

    @commands.command(name="8ball", aliases=['8'])
    async def _8ball(self, ctx, *, question=None):
        """
        Asks the 8ball a question.

        [Format: %8ball Question]
        """
        if question:
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "prompt_answer",
                                                 [["result", question],
                                                  ["result2", choice(self.ex.cache.eight_ball_responses)]]))
        else:
            await ctx.send(await self.ex.get_msg(ctx, "miscellaneous", "prompt"))

    @commands.command(aliases=['stopgame', 'endgame', 'endgames'])
    async def stopgames(self, ctx):
        """End all games that you are hosting or that may exist in the text channel.

        BlackJack can only be terminated by the players themselves and not a moderator.

        [Format: %stopgames]
        [Aliases: stopgame, endgame, endgames]
        """
        user = await self.ex.get_user(ctx.author.id)
        msg = await self.ex.get_msg(user, "miscellaneous", "terminating_games", ["name", ctx.author.display_name])
        await ctx.send(msg)
        await self.ex.stop_game(ctx, self.ex.cache.bias_games)  # stop any bias games.

        await self.ex.stop_game(ctx, self.ex.cache.guessing_games)  # stop any guessing games.

        await self.ex.stop_game(ctx, self.ex.cache.unscramble_games)  # stop any unscramble games.

        blackjack_game = await self.ex.u_blackjack.find_game(user)
        if blackjack_game:
            await blackjack_game.end_game()  # stop any blackjack game.

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """
        Shows Latency to Discord

        [Format: %ping]
        """
        try:
            await ctx.send(f"> **My ping is currently {self.ex.get_ping()}ms.**")
        except:
            await ctx.send("> Cannot determine ping at this time.")

    @commands.command(aliases=["shardinfo"])
    async def shard(self, ctx):
        """
        Shows information about the current shard.

        [Format: %shard]
        """
        if not ctx.guild:
            no_dm_msg = await self.ex.get_msg(ctx, "general", "no_dm")
            return await ctx.send(no_dm_msg)
        shard_id = ctx.guild.shard_id
        shard = self.ex.client.get_shard(shard_id)
        embed_title = f"Shard Details for {ctx.guild.name}"
        embed = await self.ex.create_embed(title=embed_title)
        embed.add_field(name="Shard ID", value=shard_id)
        embed.add_field(name="Latency", value=f"{int(shard.latency * 1000)} ms")
        embed.add_field(name="Closed", value=f"{shard.is_closed()}")
        embed.add_field(name="Rate-Limited", value=f"{shard.is_ws_ratelimited()}")
        await ctx.send(embed=embed)



