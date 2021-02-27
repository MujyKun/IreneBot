import discord
from random import *
from discord.ext import commands
from module import keys
from module import logger as log
from Utility import resources as ex
import datetime


# noinspection PyBroadException,PyPep8
class Miscellaneous(commands.Cog):
    @staticmethod
    async def on_message_user_notifications(message):
        # user phrase notifications
        try:
            if message.author.bot:
                return

            message_split = message.content.lower().split(" ")
            for guild_id, user_id, phrase in ex.cache.user_notifications:
                if phrase not in message_split or guild_id != message.guild.id:
                    continue
                if message.author.id == user_id or user_id not in [member.id for member in message.channel.members]:
                    continue

                log.console(f"message_notifications 1 - {phrase} to {user_id}")
                dm_channel = await ex.get_dm_channel(user_id)
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
                embed = await ex.create_embed(title="Phrase Found", color=ex.get_random_color(), title_desc=title_desc)
                await dm_channel.send(embed=embed)
        except:
            pass

    @commands.command()
    async def vote(self, ctx):
        """Link to Voting for Irene on Top.gg
        [Format: %vote]"""
        return await ctx.send(f"> https://top.gg/bot/{keys.bot_id}/vote")

    @commands.command()
    async def choose(self, ctx, *, options):
        """Choose between a selection of options. Underscores are spaces between words. Spaces separate choices.
        [Format: %choose (option_1 option_2 option_3)]"""
        options = options.split(' ')
        random_choice = (choice(options)).replace('_', ' ')
        return await ctx.send(f"{ctx.author.display_name}, your choice is {random_choice}")

    @commands.command()
    async def displayemoji(self, ctx, emoji: discord.PartialEmoji):
        """Display an emoji. [Format: %displayemoji :emoji:]"""
        return await ctx.send(emoji.url)

    @commands.command()
    async def addnoti(self, ctx, *, phrase):
        """Receive a DM whenever a phrase or word is said in the current server. [Format: %addnoti (phrase/word)]"""
        try:
            check_exists = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM general.notifications WHERE guildid = $1 AND userid = $2 AND phrase = $3", ctx.guild.id, ctx.author.id, phrase.lower()))
            if check_exists:
                raise Exception
            await ex.conn.execute("INSERT INTO general.notifications(guildid,userid,phrase) VALUES($1, $2, $3)", ctx.guild.id, ctx.author.id, phrase.lower())
            user = await ex.get_user(ctx.author.id)
            user.notifications.append([ctx.guild.id, phrase.lower()])
            ex.cache.user_notifications.append([ctx.guild.id, ctx.author.id, phrase.lower()])  # full list
            await ctx.send(f"> **{ctx.author.display_name}, I added `{phrase}` to your notifications.**")
        except AttributeError:
            return await ctx.send(f"> **{ctx.author.display_name}, You are not allowed to use this command in DMs.**")
        except:
            await ctx.send(f"> **{ctx.author.display_name}, You are already receiving notifications for `{phrase}`**")

    @commands.command(aliases=["deletenoti"])
    async def removenoti(self, ctx, *, phrase):
        """Remove a phrase/word when it said in the current server. [Format: %removenoti (phrase/word)]"""
        try:
            await ex.conn.execute("DELETE FROM general.notifications WHERE guildid=$1 AND userid=$2 AND phrase=$3", ctx.guild.id, ctx.author.id, phrase.lower())
            try:
                user = await ex.get_user(ctx.author.id)
                user.notifications.remove([ctx.guild.id, phrase.lower()])
                ex.cache.user_notifications.remove([ctx.guild.id, ctx.author.id, phrase.lower()])  # full list
            except AttributeError:
                return await ctx.send(
                    f"> **{ctx.author.display_name}, You are not allowed to use this command in DMs.**")
            except:
                pass
            await ctx.send(f"> **{ctx.author.display_name}, if you were receiving notifications for that phrase, it has been removed.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something Went Wrong, please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command()
    async def listnoti(self, ctx):
        """list all your notification phrases that exist in the current server. [Format: %listnoti]"""
        try:
            user = await ex.get_user(ctx.author.id)
            if not user.notifications:
                raise AttributeError
            final_list = ""
            counter = 0
            current_guild_id = ctx.guild.id
            for guild_id, phrase in user.notifications:
                counter += 1
                if guild_id != current_guild_id:
                    continue
                if counter != len(user.notifications):
                    final_list += f"**{phrase}**,"
                else:
                    final_list += f"**{phrase}**"
            await ctx.send(final_list)
        except AttributeError:
            return await ctx.send(
                f"> **{ctx.author.display_name}, You do not have any notification phrases on this server.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something Went Wrong, please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command(aliases=['patron'])
    async def patreon(self, ctx):
        """Displays Patreon Information. [Format: %patreon]"""
        await ctx.send(f"**Please support <@{keys.bot_id}>'s development at {keys.patreon_link}.**")

    @commands.command()
    @commands.is_owner()
    async def addpatreon(self, ctx, *, users):
        """Adds a patreon. [Format: %addpatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.u_patreon.add_to_patreon(user)
        await ctx.send(f">>> **Added {users} to Patreon.**")

    @commands.command()
    @commands.is_owner()
    async def removepatreon(self, ctx, *, users):
        """Removes a patreon. [Format: %removepatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.u_patreon.remove_from_patreon(user)
        await ctx.send(f">>> **Removed {users} from Patreon.**")

    @commands.command()
    async def botinfo(self, ctx):
        """Get information about the bot."""
        maintenance_status = api_status = db_status = images_status = weverse_status = d_py_status = irene_cache_status \
            = ":red_circle:"

        working = ":green_circle:"
        if await ex.u_miscellaneous.get_api_status():
            api_status = working
        if await ex.u_miscellaneous.get_db_status():
            db_status = working
        if await ex.u_miscellaneous.get_images_status():
            images_status = working
        if ex.cache.maintenance_mode:
            maintenance_status = working
        if await ex.weverse_client.check_token_works():
            weverse_status = working
        if ex.discord_cache_loaded:
            d_py_status = working
        if ex.irene_cache_loaded:
            irene_cache_status = working

        try:
            current_server_prefix = await ex.get_server_prefix(ctx.guild.id)
        except:
            current_server_prefix = await ex.client.get_prefix(ctx.message)
        app = await ex.client.application_info()
        app_id = app.id
        app_name = app.name
        app_owner = app.owner
        app_icon_url = app.icon_url
        patreon_url = keys.patreon_link
        bot_uptime = await ex.u_miscellaneous.get_cooldown_time((keys.datetime.now() - keys.startup_time).total_seconds())
        bot_server_links = """
[Top.gg](https://top.gg/bot/520369375325454371)
[Discord Bots](https://discord.bots.gg/bots/520369375325454371)
[Bots on Discord](https://bots.ondiscord.xyz/bots/520369375325454371)
[Discord Boats](https://discord.boats/bot/520369375325454371)
        """
        mods = ""
        for bot_mod in keys.mods_list:
            mods += f"<@{bot_mod}> | "
        title_desc = f"""I was made with Python using the discord.py wrapper.

API Status: {api_status} 
Images Status: {images_status} 
Database Status: {db_status} 
Weverse Status: {weverse_status}
Irene Cache: {irene_cache_status}
discord.py Cache: {d_py_status}
Maintenance Status: {maintenance_status}
"""
        embed = await ex.create_embed(title=f"I am {app_name}! ({app_id})", title_desc=title_desc)
        embed.set_thumbnail(url=app_icon_url)
        embed.add_field(name=f"Servers Connected", value=f"{ex.u_miscellaneous.get_server_count()} Servers", inline=True)
        embed.add_field(name=f"Text/Voice Channels Watched", value=f"{ex.u_miscellaneous.get_text_channel_count()}/{ex.u_miscellaneous.get_voice_channel_count()} Channels", inline=True)
        embed.add_field(name=f"Servers/Channels Logged", value=f"{len(await ex.u_logging.get_servers_logged())}/{len(await ex.u_logging.get_channels_logged())} Logged", inline=True)
        embed.add_field(name=f"Bot Uptime", value=bot_uptime, inline=True)
        embed.add_field(name=f"Total Commands Used", value=f"{ex.cache.total_used} Commands", inline=True)
        embed.add_field(name=f"This Session ({ex.cache.session_id} | {datetime.date.today()})", value=f"{ex.cache.current_session} Commands", inline=True)
        embed.add_field(name=f"Playing Music", value=f"{len(ex.client.voice_clients)} Voice Clients", inline=True)
        embed.add_field(name=f"Playing Guessing/Bias", value=f"{len(ex.cache.guessing_games)}/{len(ex.cache.bias_games)} Games", inline=True)
        embed.add_field(name=f"Ping", value=f"{ex.get_ping()} ms", inline=True)
        embed.add_field(name=f"Shards", value=f"{ex.client.shard_count}", inline=True)
        embed.add_field(name=f"Bot Owner", value=f"<@{app_owner.id}>", inline=True)
        if mods:
            embed.add_field(name=f"Bot Mods", value=mods, inline=True)
        embed.add_field(name=f"Support Server", value=f"[Invite to Server]({keys.bot_support_server_link})", inline=False)
        embed.add_field(name=f"Website", value=keys.bot_website, inline=False)
        embed.add_field(name=f"Github", value=f"https://github.com/MujyKun/IreneBot", inline=False)
        embed.add_field(name=f"Discord Invite", value=keys.bot_invite_link, inline=False)
        embed.add_field(name=f"Bot Server Links", value=bot_server_links, inline=False)
        embed.add_field(name=f"Suggest", value=f"Suggest a feature using `{current_server_prefix}suggest`.", inline=False)
        if patreon_url:
            embed.add_field(name=f"Patreon", value=f"[Please Support <@{keys.bot_id}> here.]({patreon_url})", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def checkprefix(self, ctx):
        """Check the current prefix using the default prefix."""
        # noinspection PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException
        try:
            await ctx.send(f"> **Your current server prefix is {await ex.get_server_prefix(ctx.guild.id)}**")
        except:
            await ctx.send(f"> **Your current prefix is {await ex.client.get_prefix(ctx.message)}")

    @commands.command(aliases=['trans', 't'])
    async def translate(self, ctx, from_language, to_language, *, message):
        """Translate between languages using Papago [Format: %translate English Korean this is a test phrase.]"""
        try:
            response = await ex.u_miscellaneous.translate(message, from_language, to_language)
            if not response:
                return await ctx.send(
                    f"**My Papago Translation Service is currently turned off and cannot process requests OR you did not enter the right format.**")
            code = response['code']
            if code != 0:
                return await ctx.send("> **Something went wrong and I did not receive a proper response from Papago.**")
            text = response['text']
            target_lang = response['source']
            msg = f"Original ({target_lang}): {message} \nTranslated ({to_language}): {text} "
            return await ctx.send(msg)
        except Exception as e:
            await ctx.send("An error has occurred with the Translation.")
            log.console(e)

    @commands.command()
    async def report(self, ctx, *, issue):
        """Report an issue with Irene. Format: [%report (issue)]"""
        desc = f"**{issue}**"
        embed = discord.Embed(title="Bug Report", color=0xff00f6)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a report.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        try:
            channel = await ex.client.fetch_channel(keys.report_channel_id)  # 403 error ( no access ) on testing
            msg = await channel.send(embed=embed)
            await ctx.send("> **Your bug report has been sent.**")
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except:
            # Error would occur on test bot if the client does not have access to a certain channel id
            # this try-except will also be useful if a server removed the bot.
            await ctx.send("Could not fetch channel to report to.")

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        """Suggest a feature for Irene. Format: [%suggest (suggestion)]"""
        desc = f"**{suggestion}**"
        embed = discord.Embed(title="Suggestion", color=0xff00f6)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a suggestion.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        try:
            channel = await ex.client.fetch_channel(keys.suggest_channel_id)  # 403 error on testing
            msg = await channel.send(embed=embed)
            await ctx.send("> **Your suggestion has been sent.**")
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except Exception as e:
            log.console(e)
            await ctx.send("Could not fetch channel to suggest to.")

    @commands.command()
    async def nword(self, ctx, user: discord.Member = None):
        """Checks how many times a user has said the N Word [Format: %nword @user]"""
        if not user:
            user = ctx.author
        current_amount = (await ex.get_user(user.id)).n_word
        if not current_amount:
            return await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")
        else:
            await ctx.send(f"> **<@{user.id}> has said the N-Word {current_amount} time(s)!**")

    @commands.is_owner()
    @commands.command()
    async def clearnword(self, ctx, user: discord.Member = None):
        """Clear A User's Nword Counter [Format: %clearnword @user]"""
        if not user:
            return await ctx.send("> **Please @ a user**")

        if not (await ex.get_user(user.id)).n_word:
            return await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")

        await ex.conn.execute("DELETE FROM general.nword where userid = $1", user.id)
        (await ex.get_user(user.id)).n_word = 0
        await ctx.send("**> Cleared.**")

    @commands.command(aliases=["nwl"])
    async def nwordleaderboard(self, ctx, mode="server"):
        """Shows leaderboards for how many times the nword has been said. [Format: %nwl (server/global)]"""
        embed = discord.Embed(title=f"NWord Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url=keys.bot_website, icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=f"Type {await ex.get_server_prefix_by_context(ctx)}nword (user) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')

        guild_id = await ex.get_server_id(ctx)
        if not guild_id:
            # server rankings can not be accessed from DMs.
            mode = "global"

        guild = ex.client.get_guild(guild_id)
        member_list = [member.id for member in guild.members]
        n_word_list = {}  # user_id : n_word_count

        for user in ex.cache.users.values():
            if mode.lower() == "global":
                n_word_list[user.id] = user.n_word
            else:
                # server
                if user.id in member_list:
                    n_word_list[user.id] = user.n_word

        sorted_n_word = {key: value for key, value in sorted(n_word_list.items(), key=lambda item: item[1], reverse=True)}
        for count, user_id in enumerate(sorted_n_word):
            value = sorted_n_word.get(user_id)
            if not value:
                continue
            if count >= 10:
                break
            try:
                user_name = (ex.client.get_user(user_id)).name
            except:
                # if the user is not in discord.py's member cache, then set the user's name to null.
                user_name = "NULL"
            embed.add_field(name=f"{count+1}) {user_name} ({user_id})", value=value)
        await ctx.send(embed=embed)

    @commands.command(aliases=['rand', 'randint', 'r'])
    async def random(self, ctx, a: int, b: int):
        """Choose a random number from a range (a,b). """
        try:
            await ctx.send(f"> **Your random number is {randint(a, b)}.**")
        except Exception as e:
            await ctx.send(f"> **{e}**")

    @commands.command(aliases=['coinflip', 'f'])
    async def flip(self, ctx):
        """Flips a coin [Format: %flip][Aliases: coinflip, f]"""
        await ctx.send(f"> **You flipped {choice(['Heads', 'Tails'])}.**")

    @commands.command(aliases=['define', 'u'])
    async def urban(self, ctx, term=None, number=1, override=0):
        """Search a term through UrbanDictionary. Underscores are spaces.
        [Format: %urban (term) (definition number)][Aliases: define,u]"""
        if not ctx.channel.is_nsfw() and not override == 1:
            server_prefix = await ex.get_server_prefix_by_context(ctx)
            return await ctx.send(f">>> **This text channel must be NSFW to use {server_prefix}"
                           f"urban (Guidelines set by top.gg).**\nTo override this, You may add a **1** after the "
                           f"definition number.\nExample: {server_prefix}urban hello (definition number) **1**.")
        if not term:
            return await ctx.send("> **Please enter a word for me to define**")
        term = term.replace("_", " ")
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        querystring = {"term": f"{term}"}
        async with ex.session.get(url, headers=keys.X_RapidAPI_headers, params=querystring) as r:
            ex.cache.urban_per_minute += 1
            if r.status != 200:
                log.console(f"The connection to the UrbanDictionary API failed. -> {r.status}")
                return await ctx.send("> **The connection to the UrbanDictionary API failed.**")
            result = await r.json()
            try:
                first_result = (result['list'])[number-1]
            except:
                return await ctx.send(f"> **It is not possible to find definition number `{number}` for the word: `{term}`.**")
            await ctx.send(f">>> **`Word: {term}`\n`Definition Number: {number}`\n{first_result['definition']}**")

    @commands.command()
    async def invite(self, ctx):
        """Invite Link to add Irene to a server."""
        await ctx.send(f"> **Invite Link:** {keys.bot_invite_link}")

    @commands.command()
    async def support(self, ctx):
        """Invite Link to Irene's Discord Server"""
        await ctx.send(f"> **Support Server:** {keys.bot_support_server_link}")

    @commands.command()
    @commands.is_owner()
    async def announce(self, ctx, *, new_message):
        """Sends a bot message to system text channels.
        NOTE: This should not be used if a lot of servers are using the bot."""
        desc = f"{new_message}"
        embed = discord.Embed(title=f"Announcement from {ctx.author} ({ctx.author.id})", description=desc, color=0xff00f6)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %support for an invite to Irene's discord server.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        # embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)

        guilds = ex.client.guilds
        for guild in guilds:
            try:
                await guild.system_channel.send(embed=embed)
            except Exception as e:
                log.console(e)

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, channel_id, *, new_message):
        """Send a message to a text channel."""
        try:
            channel = await ex.client.fetch_channel(channel_id)  # 403 forbidden on tests.
            await channel.send(new_message)
            await ctx.send("> **Message Sent.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **ERROR: {e}**")

    @commands.command()
    async def servercount(self, ctx):
        """Shows how many servers the bot has [Format: %servercount]"""
        await ctx.send(f"> **I am connected to {ex.u_miscellaneous.get_server_count()} servers.**")

    @commands.command()
    async def serverinfo(self, ctx):
        """View information about the current guild. [Format: %serverinfo]"""
        try:
            guild = ctx.guild
            embed = discord.Embed(title=f"{guild.name} ({guild.id})", color=0xffb6c1, url=f"{guild.icon_url}")
            embed.set_author(name="Irene", url=keys.bot_website,
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
            await ctx.send("> This server has not yet been loaded into my cache (takes about an hour from restart).")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """Displays which servers Irene is in."""
        guilds = ex.client.guilds
        count = 1
        page_number = 1
        embed = discord.Embed(title=f"{len(guilds)} Servers - Page {page_number}", color=0xffb6c1)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for using Irene.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        guilds_ordered = [[guild.id, guild.member_count] for guild in guilds]
        guilds_ordered.sort(key=lambda server_info: server_info[1])
        guild_ids_sorted = [guild[0] for guild in guilds_ordered]
        embed_list = []
        try:
            for main_guild_id in guild_ids_sorted:
                # need to do a nested loop due to fetch_guild not containing attributes needed.
                for guild in guilds:
                    if guild.id != main_guild_id:
                        continue
                    member_count = f"Member Count: {guild.member_count}\n"
                    owner = f"Guild Owner: {guild.owner} ({guild.owner.id})\n"
                    desc = member_count + owner
                    embed.add_field(name=f"{guild.name} ({guild.id})", value=desc, inline=False)
                    if count == 25:
                        count = 0
                        embed_list.append(embed)
                        page_number += 1
                        embed = discord.Embed(title=f"{len(guilds)} Servers - Page {page_number}", color=0xffb6c1)
                        embed.set_author(name="Irene", url=keys.bot_website,
                                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
                        embed.set_footer(text="Thanks for using Irene.",
                                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
                    count += 1
        except Exception as e:
            log.console(e)
        if count:
            embed_list.append(embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command(name="8ball", aliases=['8'])
    async def _8ball(self, ctx, *, question=None):
        """Asks the 8ball a question. [Format: %8ball Question]"""
        if question:
            await ctx.send(f">>> **Question: {question} \nAnswer: {choice(ex.cache.eight_ball_responses)}**")
        else:
            await ctx.send("> **Please enter an 8ball prompt.**")

    @commands.command()
    @commands.is_owner()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(f">>> {message}", tts=True, delete_after=10)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """Shows Latency to Discord [Format: %ping]"""
        await ctx.send(f"> **My ping is currently {ex.get_ping()}ms.**")


