import discord
from random import *
from discord.ext import commands
from module import keys
import sqlite3
import aiohttp
import aiofiles
import os
import asyncio
from module import logger as log

client = 0
path = 'module\currency.db'
DBconn = sqlite3.connect(path, check_same_thread=False)
c = DBconn.cursor()


def setup(client1):
    client1.add_cog(Miscellaneous(client1))
    global client
    client = client1


class Miscellaneous(commands.Cog):
    def __init__(self, client):
        pass

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = "@user", *, reason="No Reason"):
        """Ban A User [Format: %ban @user]"""
        try:
            await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
            embed = discord.Embed(title="User Banned!", description=f">**<@{user.id}> was banned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"**<@{user.id}> was not able to be banned by <@{ctx.author.id}> successfully. \n {e}**!", color=0xff00f6)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = "@user", *, reason="No Reason"):
        """Unban A User [Format: %unban @user]"""
        log.console (type(user))
        try:
            await ctx.guild.unban(user=user, reason=reason)
            embed = discord.Embed(title="User Unbanned!", description=f"> **<@{user.id}> was unbanned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"**<@{user.id}> could not be unbanned by <@{ctx.author.id}> \n {e}**!", color=0xff00f6)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = "@user", reason="No Reason"):
        """Kick A User [Format: %kick @user]"""
        try:
            await ctx.guild.kick(user=user, reason=reason)
            embed = discord.Embed(title="User Kicked!",
                                  description=f"**<@{user.id}> was kicked by <@{ctx.author.id}> for {reason}**!",
                                  color=0xff00f6)
        except Exception as e:
            embed = discord.Embed(title="Error",
                                  description=f"**<@{user.id}> could not be kicked by <@{ctx.author.id}> \n {e}**!",
                                  color=0xff00f6)
        await ctx.send(embed=embed)

    @commands.command(aliases=['temp'])
    @commands.has_permissions(manage_messages=True)
    async def tempchannel(self, ctx, delay=-1):
        """Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel. [Format: %temp (delay)]"""
        channel_id = ctx.channel.id
        try:
            if delay == -1:
                    c.execute("DELETE FROM TempChannels WHERE chanID = ?", (channel_id,))
                    DBconn.commit()
                    await ctx.send ("> **If this channel was a temporary channel, it has been removed.**")
            if delay >= 60:
                new_delay = f"{(delay/60)} minutes"
            if 0 <= delay < 60:
                new_delay = f"{delay} seconds"
            if delay < -1:
                await ctx.send("> **The delay cannot be negative.**")
            if delay >= 0:
                channel_id = ctx.channel.id
                counter = c.execute("SELECT COUNT(*) FROM TempChannels WHERE chanID = ?", (channel_id,)).fetchone()[0]
                if counter == 1:
                    old_delay = c.execute("SELECT delay FROM TempChannels WHERE chanID = ?", (channel_id,)).fetchone()[0]
                    if old_delay == delay:
                        await ctx.send(f"> **This channel is already a temp channel that deletes messages every {new_delay}.**")
                    else:
                        c.execute("UPDATE TempChannels SET delay = ? WHERE chanID = ?", (delay, channel_id))
                        DBconn.commit()
                        await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                if counter == 0:
                    await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                    c.execute("INSERT INTO TempChannels VALUES (?, ?)", (channel_id, delay))
                    DBconn.commit()
        except Exception as e:
            log.console(e)

    @commands.command()
    @commands.has_permissions(manage_messages=True, manage_emojis=True)
    async def addemoji(self, ctx, url, emoji_name):
        """Adds an emoji to the server. [Format: %addemoji (url) (emoji name)]"""
        if "?v=1" in url or ".jpg" in url or ".png" in url or ".gif" in url:
            file_format = url[52:56]
        else:
            file_format = "None"
            await ctx.send(f">>> **Please use a url that ends in ?v=1 or a file format like .png or edit your emoji on \n <https://ezgif.com/resize?url={url}>**")
            log.console (f"Please use a url that ends in ?v=1 or a file format like .png or edit your emoji on https://ezgif.com/resize?url={url}")
        if len(emoji_name) < 2:
            file_format = "None"
            await ctx.send("> **Please enter an emoji name more than two letters.**")
        if file_format != "None":
            # await ctx.send(file_format)
            async with aiohttp.ClientSession() as session:
                async with session.get('{}'.format(url)) as r:
                    if r.status == 200:
                        # await ctx.send("Connection Successful")
                        fd = await aiofiles.open('Emoji/{}'.format(f"{emoji_name}{file_format}"), mode='wb')
                        await fd.write(await r.read())
                        await fd.close()
                        log.console(f"Downloaded {emoji_name}{file_format}")
                        full_file_name = emoji_name + file_format
                        file_size = (os.path.getsize(f'Emoji/{full_file_name}'))
                        if file_size > 262144:
                            await ctx.send(f">>> **File cannot be larger than 256.0 kb. Please resize the emoji here (for the resize method, use Gifsicle).**\n <https://ezgif.com/resize?url={url}>")
                            log.console(f"File cannot be larger than 256.0 kb. Please resize the emoji here. https://ezgif.com/resize?url={url}")
                        elif file_size <= 262144:
                            v = await aiofiles.open(f'Emoji/{full_file_name}', mode='rb')
                            # await ctx.guild.create_custom_emoji(name=emoji_name, image=f'Emoji/{full_file_name}')
                            await ctx.guild.create_custom_emoji(name=emoji_name, image=await v.read())
                            await v.close()
                            emojis = client.emojis
                            max_emoji_length = len(emojis)
                            if emoji_name in str(emojis[max_emoji_length-1]):
                                await ctx.send(emojis[max_emoji_length-1])
                            elif emoji_name in str(emojis[0]):
                                await ctx.send(emojis[0])
                            else:
                                await ctx.send(f"> **Added :{emoji_name}:**")
                        all_photos = os.listdir('Emoji')
                        for photo in all_photos:
                            try:
                                os.unlink('Emoji/{}'.format(photo))
                            except:
                                pass
                    elif r.status == 404:
                        await ctx.send("> **That URL was not Found.**")
                    elif r.status == 403:
                        await ctx.send("> **I do not have access to that site.**")
                    else:
                        await ctx.send("> **I was not able to connect to that url**")


    @commands.command()
    async def nword(self, ctx, user: discord.Member = "@user"):
        """Checks how many times a user has said the N Word [Format: @user]"""
        if user == "@user":
            await ctx.send("> **Please @ a user**")
        if user != "@user":
            checker = c.execute("SELECT COUNT(*) FROM Counter WHERE UserID = ?", (user.id,)).fetchone()[0]
            if checker > 0:
                current_count = c.execute("SELECT NWord FROM Counter WHERE UserID = ?", (user.id,)).fetchone()[0]
                await ctx.send(f"> **<@{user.id}> has said the N-Word {current_count} time(s)!**", delete_after=40)
            if checker == 0:
                await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**", delete_after=40)

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
    async def urban(self, ctx, term="none", number=1):
        """Search a term through UrbanDictionary. [Format: %urban (term) (definition number)][Aliases: define,u]"""
        if ctx.channel.is_nsfw():
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
    @commands.is_owner()
    async def announce(self, ctx,*, new_message):
        """Sends a bot message to certain text channels"""
        channel_list = [628049276446048256,356846361045368844,413508021088419846,588224699952005123]
        for channel in channel_list:
            channel = client.get_channel(channel)
            await channel.send(f"**ANNOUNCEMENT from {ctx.author}**\n> **{new_message}**")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """Extremely sloppy way of showing which servers the bot are in."""
        guilds = client.guilds
        for guild in guilds:
            guild_id = guild.id
            guild_member_count = guild.member_count
            guild_owner = guild.owner_id
            guild_name = guild.name
            guild_icon = guild.icon
            guild_banner = guild.banner
            guild_channels = guild.text_channels
            channel_info = ""
            for channel in guild_channels:
                channel_info += f"[{channel},{channel.id}]\n"

            await ctx.send(f">>> Guild ID: {guild_id}\nGuild Owner: {guild_owner}\nGuild Name: {guild_name}\nMember Count: {guild_member_count}\nGuild Icon: {guild_icon}\nGuild Banner: {guild_banner}\n **Channels:**\n{channel_info} ")


    @commands.command()
    @commands.is_owner()
    async def logging(self, ctx, *, keyword='add'):
        """ [Format: %logging (stop/add)"""
        if keyword == 'add':
            counter = c.execute("SELECT COUNT(*) FROM logging WHERE channelid = ?", (ctx.channel.id,)).fetchone()[0]
            if counter == 0:
                c.execute("INSERT INTO logging VALUES(?)", (ctx.channel.id,))
                DBconn.commit()
                await ctx.send("> **This channel is now being logged.**")
            if counter == 1:
                await ctx.send("> **This channel is already being logged.**")
        if keyword == 'stop':
            try:
                c.execute("DELETE FROM logging WHERE channelid = ?", (ctx.channel.id,))
                DBconn.commit()
                await ctx.send("> **This channel is no longer being logged**")
            except:
                await ctx.send("> **This channel isn't being logged.**")
            pass

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
        await ctx.send("> My ping is currently {}ms.".format(int(client.latency * 1000)))

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        """Kills the bot [Format: %kill]"""
        await ctx.send("> **The bot is now offline.**")
        await client.logout()

    @commands.command(aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, userid: discord.Member = "abc"):
        """Prune Messages [Format: %clear (amount)][Aliases: prune]"""
        amount = int(amount)
        original = amount
        def clearx(m):
            return m.author == userid
        if userid == "abc":
            checker = 1
        else:
            checker = 0
        amount = amount + 1
        if amount <= 101:
            if checker == 0:
                await ctx.channel.purge(limit=amount, check=clearx, bulk=True)
            elif checker == 1:
                await ctx.channel.purge(limit=amount, bulk=True)
            log.console("Pruned {} messages".format(amount))
        if amount >= 102:
            number = (amount // 100)
            await ctx.send(
                "> **{}** messages will be deleted in 5 seconds and will be split in intervals of 100.".format(
                    original))
            for i in range(number):
                if checker == 0:
                    await ctx.channel.purge(limit=100, check=userid, bulk=True)
                elif checker == 1:
                    await ctx.channel.purge(limit=100, bulk=True)
                log.console("Pruned 100 messages")
            await ctx.send("> **{}** messages have been pruned.".format(original))
