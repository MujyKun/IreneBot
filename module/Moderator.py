import discord
from discord.ext import commands
import aiohttp
import aiofiles
import os
from module import logger as log
from module.keys import client, bot_prefix
from Utility import resources as ex


class Moderator(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def setprefix(self, ctx, *, prefix=bot_prefix):
        """Set the server prefix. If prefix was forgotten, type this command with the default prefix.[Format: %setprefix %]"""
        prefix = prefix.lower()
        current_server_prefix = await ex.get_server_prefix(ctx.guild.id)
        if len(prefix) > 8:
            await ctx.send("> **Your prefix can not be more than 8 characters.**")
        else:
            # Default prefix '%' should never be in DB.
            if current_server_prefix == "%":
                if prefix != "%":
                    ex.c.execute("INSERT INTO general.serverprefix VALUES (%s,%s)", (ctx.guild.id, prefix))
            else:
                if prefix != "%":
                    ex.c.execute("UPDATE general.serverprefix SET prefix = %s WHERE serverid = %s", (prefix, ctx.guild.id))
                else:
                    ex.c.execute("DELETE FROM general.serverprefix WHERE serverid = %s", (ctx.guild.id,))
            ex.DBconn.commit()
            await ctx.send(f"> **This server's prefix has been set to {prefix}.**")

    @commands.command(aliases=['prune', 'purge'])
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, user: discord.Member = discord.Member):
        """Prune Messages [Format: %clear (amount)][Aliases: prune]"""
        amount = int(amount)
        original = amount

        def clearx(m):
            return m.author == user
        if user == discord.Member:
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
                    await ctx.channel.purge(limit=100, check=clearx, bulk=True)
                elif checker == 1:
                    await ctx.channel.purge(limit=100, bulk=True)
                log.console("Pruned 100 messages")
            await ctx.send("> **{}** messages have been pruned.".format(original))

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = discord.Member, *, reason="No Reason"):
        """Ban A User [Format: %ban @user]"""
        check = True
        if user == discord.Member:
            await ctx.send("> **Please choose a person to ban.**")
        else:
            if user.id == ctx.author.id:
                await ctx.send("> **You can not ban yourself!**")
                check = False
            try:
                if check:
                    await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
                    embed = discord.Embed(title="User Banned!", description=f">**<@{user.id}> was banned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
                    await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> was not able to be banned by <@{ctx.author.id}> successfully. \n {e}**!", color=0xff00f6)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = discord.User, *, reason="No Reason"):
        """Unban A User [Format: %unban @user]"""
        if user == discord.User:
            await ctx.send("> **Please choose a person to unban.**")
        else:
            try:
                if user.id == ctx.author.id:
                    await ctx.send("> **You can not unban yourself!**")
                await ctx.guild.unban(user=user, reason=reason)
                embed = discord.Embed(title="User Unbanned!", description=f"> **<@{user.id}> was unbanned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> could not be unbanned by <@{ctx.author.id}> \n {e}**!", color=0xff00f6)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = discord.Member, reason="No Reason"):
        """Kick A User [Format: %kick @user]"""
        if user == discord.Member:
            await ctx.send("> **Please choose a person to kick.**")
        else:
            try:
                if user.id == ctx.author.id:
                    await ctx.send("> **You can not kick yourself!**")
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
    @commands.has_guild_permissions(manage_messages=True)
    async def tempchannel(self, ctx, delay=-1):
        """Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel. [Format: %temp (delay)]"""
        channel_id = ctx.channel.id
        try:
            if delay == -1:
                    ex.c.execute("DELETE FROM currency.TempChannels WHERE chanID = %s", (channel_id,))
                    ex.DBconn.commit()
                    await ctx.send ("> **If this channel was a temporary channel, it has been removed.**")
            if delay >= 60:
                new_delay = f"{(delay/60)} minutes"
            if 0 <= delay < 60:
                new_delay = f"{delay} seconds"
            if delay < -1:
                await ctx.send("> **The delay cannot be negative.**")
            if delay >= 0:
                channel_id = ctx.channel.id
                ex.c.execute("SELECT COUNT(*) FROM currency.TempChannels WHERE chanID = %s", (channel_id,))
                counter = ex.fetch_one()
                if counter == 1:
                    ex.c.execute("SELECT delay FROM currency.TempChannels WHERE chanID = %s", (channel_id,))
                    old_delay = ex.fetch_one()
                    if old_delay == delay:
                        await ctx.send(f"> **This channel is already a temp channel that deletes messages every {new_delay}.**")
                    else:
                        ex.c.execute("UPDATE currency.TempChannels SET delay = %s WHERE chanID = %s", (delay, channel_id))
                        ex.DBconn.commit()
                        await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                if counter == 0:
                    await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                    ex.c.execute("INSERT INTO currency.TempChannels VALUES (%s, %s)", (channel_id, delay))
                    ex.DBconn.commit()
        except Exception as e:
            log.console(e)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True, manage_emojis=True)
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
