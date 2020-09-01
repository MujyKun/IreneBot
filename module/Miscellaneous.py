import discord
from random import *
from discord.ext import commands
from module import keys
from module import logger as log
from Utility import resources as ex
import json
client = keys.client


class Miscellaneous(commands.Cog):
    @staticmethod
    async def on_message_notifications(message):
        try:
            message_sender = message.author
            message_guild_id = message.guild.id
            message_content = message.content
            notifications = await ex.conn.fetch("SELECT guildid,userid,phrase FROM general.notifications")
            if not message_sender.bot:
                for notification in notifications:
                    guild_id = notification[0]
                    user_id = notification[1]
                    phrase = notification[2]
                    message_split = message_content.lower().split(" ")
                    if phrase in message_split and guild_id == message_guild_id and message_sender.id != user_id:
                        dm_channel = await ex.get_dm_channel(user_id)
                        start_loc = (message_content.lower()).find(phrase)
                        end_loc = start_loc + len(phrase)
                        new_message_content = f"{message_content[0:start_loc]}`{message_content[start_loc:end_loc]}`{message_content[end_loc:len(message_content)]}"
                        title_desc = f"""
    Phrase: {phrase}
    Message Author: {message_sender}
    
    **Message:** {new_message_content}
    [Click to go to the Message]({message.jump_url})
    """
                        embed = await ex.create_embed(title="Phrase Found", color=ex.get_random_color(), title_desc=title_desc)
                        await dm_channel.send(embed=embed)
        except Exception as e:
            pass

    @commands.command()
    async def addnoti(self, ctx, *, phrase):
        """Receive a DM whenever a phrase or word is said in the current server. [Format: %addnoti (phrase/word)]"""
        try:
            check_exists = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM general.notifications WHERE guildid = $1 AND userid = $2 AND phrase = $3", ctx.guild.id, ctx.author.id, phrase.lower()))
            # will return 0 or 1
            if check_exists:
                raise Exception
            await ex.conn.execute("INSERT INTO general.notifications(guildid,userid,phrase) VALUES($1, $2, $3)", ctx.guild.id, ctx.author.id, phrase.lower())
            await ctx.send(f"> **{ctx.author.display_name}, I added `{phrase}` to your notifications.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{ctx.author.display_name}, You are already receiving notifications for `{phrase}`**")
        pass

    @commands.command(aliases=["deletenoti"])
    async def removenoti(self, ctx, *, phrase):
        """Remove a phrase/word when it said in the current server. [Format: %removenoti (phrase/word)]"""
        try:
            await ex.conn.execute("DELETE FROM general.notifications WHERE guildid=$1 AND userid=$2 AND phrase=$3", ctx.guild.id, ctx.author.id, phrase.lower())
            await ctx.send(f"> **{ctx.author.display_name}, if you were receiving notifications for that phrase, it has been removed.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something Went Wrong, please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command()
    async def listnoti(self, ctx):
        """list all your notification phrases that exist in the current server. [Format: %listnoti]"""
        try:
            phrases = await ex.conn.fetch("SELECT phrase FROM general.notifications WHERE guildid = $1 AND userid = $2", ctx.guild.id, ctx.author.id)
            if len(phrases) == 0:
                return await ctx.send(f"> **{ctx.author.display_name}, You do not have any notification phrases on this server.**")
            final_list = ""
            counter = 1
            for phrase in phrases:
                if counter != len(phrases):
                    final_list += f"**{phrase[0]}**,"
                else:
                    final_list += f"**{phrase[0]}**"
                counter += 1
            await ctx.send(final_list)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something Went Wrong, please {await ex.get_server_prefix_by_context(ctx)}report it.**")


    @commands.command()
    async def patreon(self, ctx):
        """Displays Patreon Information. [Format: %patreon]"""
        await ctx.send(f"**Please support <@{keys.bot_id}>'s development at {keys.patreon_link}.**")

    @commands.command()
    @commands.is_owner()
    async def addpatreon(self, ctx, *, users):
        """Adds a patreon. [Format: %addpatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.add_to_patreon(user)
        await ctx.send(f">>> **Added {users} to Patreon.**")

    @commands.command()
    @commands.is_owner()
    async def removepatreon(self, ctx, *, users):
        """Removes a patreon. [Format: %removepatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.remove_from_patreon(user)
        await ctx.send(f">>> **Removed {users} from Patreon.**")

    @commands.command()
    async def botinfo(self, ctx):
        """Get information about the bot."""
        try:
            current_server_prefix = await ex.get_server_prefix(ctx.guild.id)
        except Exception as e:
            current_server_prefix = await client.get_prefix(ctx.message)
        app = await client.application_info()
        app_id = app.id
        app_name = app.name
        app_owner = app.owner
        app_icon_url = app.icon_url
        patreon_url = keys.patreon_link
        bot_uptime = await ex.get_cooldown_time((keys.datetime.now() - keys.startup_time).total_seconds())
        commands_used = await ex.get_command_count()
        total_commands = commands_used[0]
        current_session_commands = commands_used[1]
        bot_server_links = """
[Top.gg](https://top.gg/bot/520369375325454371)
[Discord Bots](https://discord.bots.gg/bots/520369375325454371)
[Bots on Discord](https://bots.ondiscord.xyz/bots/520369375325454371)
[Discord Boats](https://discord.boats/bot/520369375325454371)
        """
        mods = ""
        for bot_mod in keys.mods_list:
            mods += f"<@{bot_mod}> | "
        embed = await ex.create_embed(title=f"I am {app_name}! ({app_id})", title_desc="I was made with Python using the discord.py wrapper.")
        embed.set_thumbnail(url=app_icon_url)
        embed.add_field(name=f"Servers Connected", value=f"{ex.get_server_count()} Servers", inline=True)
        embed.add_field(name=f"Text/Voice Channels Watched", value=f"{ex.get_text_channel_count()}/{ex.get_voice_channel_count()} Channels", inline=True)
        embed.add_field(name=f"Servers/Channels Logged", value=f"{len(await ex.get_servers_logged())}/{len(await ex.get_channels_logged())} Logged", inline=True)
        embed.add_field(name=f"DC Updates Sent to", value=f"{len(await ex.get_dc_channels())} Channels", inline=True)
        embed.add_field(name=f"Bot Uptime", value=bot_uptime, inline=True)
        embed.add_field(name=f"Total Commands Used", value=f"{total_commands} Commands", inline=True)
        embed.add_field(name=f"This Session", value=f"{current_session_commands} Commands", inline=True)
        embed.add_field(name=f"Playing Music", value=f"{len(client.voice_clients)} Voice Clients", inline=True)
        embed.add_field(name=f"Ping", value=f"{ex.get_ping()} ms", inline=True)
        embed.add_field(name=f"Bot Owner", value=f"<@{app_owner.id}>", inline=False)
        if len(mods) != 0:
            embed.add_field(name=f"Bot Mods", value=mods, inline=True)
        embed.add_field(name=f"Support Server", value=f"[Invite to Server]({keys.bot_support_server_link})", inline=False)
        embed.add_field(name=f"Website", value=keys.bot_website, inline=False)
        embed.add_field(name=f"Github", value=f"https://github.com/MujyKun/IreneBot", inline=False)
        embed.add_field(name=f"Discord Invite", value=keys.bot_invite_link, inline=False)
        embed.add_field(name=f"Bot Server Links", value=bot_server_links, inline=False)
        embed.add_field(name=f"Suggest", value=f"Suggest a feature using `{current_server_prefix}suggest`.", inline=False)
        if len(patreon_url) != 0:
            embed.add_field(name=f"Patreon", value=f"[Please Support <@{keys.bot_id}> here.]({patreon_url})", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def checkprefix(self, ctx):
        """Check the current prefix using the default prefix."""
        try:
            await ctx.send(f"> **Your current server prefix is {await ex.get_server_prefix(ctx.guild.id)}**")
        except Exception as e:
            await ctx.send(f"> **Your current prefix is {await client.get_prefix(ctx.message)}")

    @commands.command(aliases=['trans', 't'])
    async def translate(self, ctx, from_language, to_language, *, message):
        """Translate between languages using Papago [Format: %translate English Korean this is a test phrase.]"""
        try:
            response = await ex.translate(message, from_language, to_language)
            if response is not None:
                code = response['code']
                if code == 0:
                    text = response['text']
                    target_lang = response['source']
                    msg = f"Original ({target_lang}): {message} \nTranslated ({to_language}): {text} "
                    return await ctx.send(msg)
                else:
                    return await ctx.send("> **Something went wrong and I did not receive a proper response from Papago.**")
            else:
                return await ctx.send(f"**My Papago Translation Service is currently turned off and cannot process requests or you did not enter the right format.**")
        except Exception as e:
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
            channel = await client.fetch_channel(keys.report_channel_id)  # 403 error on testing
            msg = await channel.send(embed=embed)
            await ctx.send("> **Your bug report has been sent.**")
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except Exception as e:
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
            channel = await client.fetch_channel(keys.suggest_channel_id)  # 403 error on testing
            msg = await channel.send(embed=embed)
            await ctx.send("> **Your suggestion has been sent.**")
            await msg.add_reaction("\U0001f44d")  # thumbs up
            await msg.add_reaction("\U0001f44e")  # thumbs down
        except Exception as e:
            log.console(e)
            await ctx.send("Could not fetch channel to suggest to.")

    @commands.command()
    async def nword(self, ctx, user: discord.Member = discord.Member):
        """Checks how many times a user has said the N Word [Format: %nword @user]"""
        if user == discord.Member:
            user = ctx.author
        checker = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.Counter WHERE UserID = $1", user.id))
        if checker > 0:
            current_count = ex.first_result(await ex.conn.fetchrow("SELECT NWord FROM currency.Counter WHERE UserID = $1", user.id))
            await ctx.send(f"> **<@{user.id}> has said the N-Word {current_count} time(s)!**")
        if checker == 0:
            await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")

    @commands.is_owner()
    @commands.command()
    async def clearnword(self, ctx, user: discord.Member = "@user"):
        """Clear A User's Nword Counter [Format: %clearnword @user]"""
        if user == "@user":
            await ctx.send("> **Please @ a user**")
        if user != "@user":
            checker = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.Counter WHERE UserID = $1", user.id))
            if checker > 0:
                await ex.conn.execute("DELETE FROM currency.Counter where UserID = $1", user.id)
                await ctx.send("**> Cleared.**")
            if checker == 0:
                await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")

    @commands.command(aliases=["nwl"])
    async def nwordleaderboard(self, ctx):
        """Shows leaderboards for how many times the nword has been said. [Format: %nwl]"""
        embed = discord.Embed(title=f"NWord Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url=keys.bot_website, icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %nword (user) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        all_members = await ex.conn.fetch("SELECT UserID, NWord FROM currency.Counter ORDER BY NWord DESC")
        count_loop = 0
        for mem in all_members:
            count_loop += 1
            if count_loop <= 10:
                user_name = (await client.fetch_user(mem[0])).name
                embed.add_field(name=f"{count_loop}) {user_name} ({mem[0]})", value=mem[1])
        await ctx.send(embed=embed)


    @commands.command(aliases=['rand', 'randint', 'r'])
    async def random(self, ctx, a: int, b: int):
        """Choose a random number from a range (a,b). """
        try:
            # await ctx.send("> **You need a range of two numbers [Format: %random a b][Ex: %random 1 100]**")
            await ctx.send(f"> **Your random number is {randint(a, b)}.**")
        except Exception as e:
            await ctx.send(f"> **{e}**")

    @commands.command(aliases=['coinflip', 'f'])
    async def flip(self, ctx):
        """Flips a coin [Format: %flip][Aliases: coinflip, f]"""
        flip_choice = ["Heads", "Tails"]
        random_number = randint(0, 1)
        await ctx.send(f"> **You flipped {flip_choice[random_number]}**")

    @commands.command(aliases=['define', 'u'])
    async def urban(self, ctx, term="none", number=1, override=0):
        """Search a term through UrbanDictionary. [Format: %urban (term) (definition number)][Aliases: define,u]"""
        if ctx.channel.is_nsfw() or override == 1:
            if term == "none":
                await ctx.send("> **Please enter a word for me to define**")
            if term != "none":
                term = term.replace("_", " ")
                url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
                querystring = {"term": f"{term}"}
                async with ex.session.get(url, headers=keys.X_RapidAPI_headers, params=querystring) as r:
                    if r.status == 200:
                        result = await r.json()
                        try:
                            first_result = (result['list'])[number-1]
                        except:
                            await ctx.send (f"> **It is not possible to find definition number `{number}` for the word: `{term}`.**")
                        await ctx.send(f">>> **`Word: {term}`\n`Definition Number: {number}`\n{first_result['definition']}**")
                    else:
                        log.console(r.status)
                        await ctx.send("> **The connection to the UrbanDictionary API failed.**")
                pass
            pass
        else:
            server_prefix = await ex.get_server_prefix_by_context(ctx)
            await ctx.send(f">>> **This text channel must be NSFW to use {server_prefix}"
                           f"urban (Guidelines set by top.gg).**\nTo override this, You may add a **1** after the "
                           f"definition number.\nExample: {server_prefix}urban hello (definition number) **1**.")

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
        """Sends a bot message to certain text channels"""
        desc = f"{new_message}"
        embed = discord.Embed(title=f"Announcement from {ctx.author} ({ctx.author.id})", description=desc, color=0xff00f6)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %support for an invite to Irene's discord server.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        # embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)

        guilds = client.guilds
        for guild in guilds:
            try:
                await guild.system_channel.send(embed=embed)
            except Exception as e:
                log.console(e)
                pass

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, channel_id, *, new_message):
        """Send a message to a text channel."""
        try:
            channel = await client.fetch_channel(channel_id)  # 403 forbidden on tests.
            await channel.send(new_message)
            await ctx.send("> **Message Sent.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **ERROR: {e}**")

    @commands.command()
    async def servercount(self, ctx):
        """Shows how many servers the bot has [Format: %servercount]"""
        await ctx.send(f"> **I am connected to {ex.get_server_count()} servers.**")

    @commands.command()
    async def serverinfo(self, ctx):
        """View information about the current guild. [Format: %serverinfo]"""
        try:
            guild = ctx.guild
            embed = discord.Embed(title= f"{guild.name} ({guild.id})", color=0xffb6c1, url=f"{guild.icon_url}")
            embed.set_author(name="Irene", url=keys.bot_website,
                             icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
            embed.set_footer(text="Thanks for using Irene.",
                             icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner.id})", inline=True)
            embed.add_field(name="Region", value=guild.region , inline=True)
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
            await ctx.send("> **Something went wrong.. Please %report the issue.**")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """Displays which servers Irene is in."""
        guilds = client.guilds
        count = 1
        page_number = 1
        embed = discord.Embed(title=f"{len(guilds)} Servers - Page {page_number}", color=0xffb6c1)
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for using Irene.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        guilds_ordered = []
        for guild in guilds:
            guild_info = [guild.id, guild.member_count]
            guilds_ordered.append(guild_info)
        guilds_ordered.sort(key=lambda server_info: server_info[1])
        guild_ids_sorted = []
        for guild in guilds_ordered:
            guild_ids_sorted.append(guild[0])
        embed_list = []
        try:
            for main_guild_id in guild_ids_sorted:
                # need to do a nested loop due to fetch_guild not containing attributes needed.
                for guild in guilds:
                    if guild.id == main_guild_id:
                        guild_id = guild.id
                        guild_member_count = guild.member_count
                        guild_owner = guild.owner
                        guild_name = guild.name
                        guild_icon = guild.icon
                        guild_banner = guild.banner
                        guild_channels = guild.text_channels
                        member_count = f"Member Count: {guild_member_count}\n"
                        owner = f"Guild Owner: {guild_owner} ({guild_owner.id})\n"
                        desc = member_count + owner
                        embed.add_field(name=f"{guild_name} ({guild_id})", value=desc, inline=False)
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
        if count != 0:
            embed_list.append(embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command(aliases=['8ball', '8'])
    async def _8ball(self, ctx, *, question=None):
        """Asks the 8ball a question. [Format: %8ball Question]"""
        if question is not None:
            responses = [
                # Positive 13
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                ":thumbsup:",
                "Well, duh",
                "Of course, that was a stupid question.",


                # Neutral 7
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Why the fuck are you asking me you dumb rat.",
                "You should already know this you 바보.",

                # Negative 10
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful.",
                ":thumbsdown:",
                "Are you kidding?",
                "Don't bet on it.",
                "Forget about it.",
                "It's just not meant to be."




]
            await ctx.send(">>> **Question: {} \nAnswer: {}**".format(question, choice(responses)))
        else:
            await ctx.send("> **Please enter a prompt.**")

    @commands.command()
    @commands.is_owner()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(">>> {}".format(message), tts=True, delete_after=5)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """Shows Latency to Discord [Format: %ping]"""
        await ctx.send(f"> **My ping is currently {ex.get_ping()}ms.**")


