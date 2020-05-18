import discord
from random import *
from discord.ext import commands
from module import keys
from module import logger as log
import aiohttp
from Utility import DBconn, c, fetch_one, fetch_all


class Miscellaneous(commands.Cog):
    def __init__(self, client):
        self.client = client
        pass

    @commands.command()
    @commands.is_owner()
    async def changestatus(self, ctx, *, status):
        """Change the playing status of Irene."""
        await self.client.change_presence(status=discord.Status.online, activity=discord.Game(status))


    @commands.command()
    async def report(self, ctx, *, issue):
        """Report an issue with Irene. Format: [%report (issue)]"""
        desc = f"**{issue}**"
        embed = discord.Embed(title="Bug Report", color=0xff00f6)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a report.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        channel = await self.client.fetch_channel(703833469620453396)
        msg = await channel.send(embed=embed)
        await ctx.send("> **Your bug report has been sent.**")
        await msg.add_reaction("\U0001f44d")  # thumbs up
        await msg.add_reaction("\U0001f44e")  # thumbs down

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        """Suggest a feature for Irene. Format: [%suggest (suggestion)]"""
        desc = f"**{suggestion}**"
        embed = discord.Embed(title="Suggestion", color=0xff00f6)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for leaving a suggestion.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)
        channel = await self.client.fetch_channel(703549964181307413)
        msg = await channel.send(embed=embed)
        await ctx.send("> **Your suggestion has been sent.**")
        await msg.add_reaction("\U0001f44d")  # thumbs up
        await msg.add_reaction("\U0001f44e")  # thumbs down

    @commands.command()
    async def nword(self, ctx, user: discord.Member = "@user"):
        """Checks how many times a user has said the N Word [Format: %nword @user]"""
        if user == "@user":
            await ctx.send("> **Please @ a user**")
        if user != "@user":
            c.execute("SELECT COUNT(*) FROM currency.Counter WHERE UserID = %s", (user.id,))
            checker = fetch_one()
            if checker > 0:
                c.execute("SELECT NWord FROM currency.Counter WHERE UserID = %s", (user.id,))
                current_count = fetch_one()
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
            c.execute("SELECT COUNT(*) FROM currency.Counter WHERE UserID = %s", (user.id,))
            checker = fetch_one()
            if checker > 0:
                c.execute("DELETE FROM currency.Counter where UserID = %s", (user.id,))
                await ctx.send("**> Cleared.**")
                DBconn.commit()
            if checker == 0:
                await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")

    @commands.command(aliases=["nwl"])
    async def nwordleaderboard(self, ctx):
        """Shows leaderboards for how many times the nword has been said. [Format: %nwl]"""
        embed = discord.Embed(title=f"NWord Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %nword (user) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        c.execute("SELECT UserID, NWord FROM currency.Counter ORDER BY NWord DESC")
        all_members = fetch_all()
        count_loop = 0
        for mem in all_members:
            count_loop += 1
            if count_loop <= 10:
                user_name = (await self.client.fetch_user(mem[0])).name
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
                async with aiohttp.request('GET', url, headers=keys.X_RapidAPI_headers, params=querystring) as r:
                    if r.status == 200:
                        result = await r.json()
                        try:
                            first_result = (result['list'])[number-1]
                        except:
                            await ctx.send (f"> **It is not possible to find definition number `{number}` for the word: `{term}`.**")
                        await ctx.send(f">>> **`Word: {term}`\n`Definition Number: {number}`\n{first_result['definition']}**")
                    else:
                        await ctx.send("> **The connection to the UrbanDictionary API failed.**")
                pass
            pass
        else:
            await ctx.send("> **This text channel must be NSFW to use %urban (Guidelines set by top.gg).** ")

    @commands.command()
    async def invite(self, ctx):
        """Invite Link to add Irene to a server."""
        await ctx.send("> **Invite Link:** https://bit.ly/2Y5dIrd")

    @commands.command()
    async def support(self, ctx):
        """Invite Link to Irene's Discord Server"""
        await ctx.send("> **Support Server:** https://discord.gg/bEXm85V")

    @commands.command()
    @commands.is_owner()
    async def announce(self, ctx, *, new_message):
        """Sends a bot message to certain text channels"""
        desc = f"{new_message}"
        embed = discord.Embed(title=f"Announcement from {ctx.author} ({ctx.author.id})", description=desc, color=0xff00f6)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %support for an invite to Irene's discord server.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        # embed.add_field(name=f"{ctx.author.name} ({ctx.author.id})", value=desc)

        guilds = self.client.guilds
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
            channel = await self.client.fetch_channel(channel_id)
            await channel.send(new_message)
            await ctx.send("> **Message Sent.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **ERROR: {e}**")

    @commands.command()
    async def servercount(self, ctx):
        """Shows how many servers the bot has [Format: %servercount]"""
        guilds = self.client.guilds
        await ctx.send(f"> **I am connecetd to {len(guilds)} servers.**")

    @commands.command()
    async def serverinfo(self, ctx):
        """View information about the current guild. [Format: %serverinfo]"""
        try:
            guild = ctx.guild
            embed = discord.Embed(title= f"{guild.name} ({guild.id})", color=0xffb6c1, url=f"{guild.icon_url}")
            embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
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
        guilds = self.client.guilds
        count = 1
        embed = discord.Embed(title=f"Servers {len(guilds)}", color=0xffb6c1)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for using Irene.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        for guild in guilds:
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
                await ctx.send(embed=embed)
                embed = discord.Embed(title=f"Servers", color=0xffb6c1)
                embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                                 icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
                embed.set_footer(text="Thanks for using Irene.",
                                 icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
            count += 1
        await ctx.send(embed=embed)


    @commands.command(aliases=['8ball', '8'])
    async def _8ball(self, ctx, *, question):
        """Asks the 8ball a question. [Format: %8ball Question]"""
        responses = [
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
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
            "Why the fuck are you asking me you dumb rat.",
            "You should already know this you babo.",
            "Try Asking Lance.", ]
        await ctx.send(">>> **Question: {} \nAnswer: {}**".format(question, choice(responses)))

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, message):
        """Owner to Bot Message"""
        await ctx.send(">>> {}".format(message))

    @commands.command()
    @commands.is_owner()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(">>> {}".format(message), tts=True, delete_after=5)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """Shows Latency to Discord [Format: %ping]"""
        await ctx.send("> My ping is currently {}ms.".format(int(self.client.latency * 1000)))

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        """Kills the bot [Format: %kill]"""
        await ctx.send("> **The bot is now offline.**")
        await self.client.logout()