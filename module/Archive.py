import discord
import os
from discord.ext import commands
import aiofiles
import asyncio
from random import *
from module.keys import owner_id, bot_website
from datetime import datetime
from IreneUtility.util import u_logger as log


# noinspection PyBroadException,PyPep8
class Archive(commands.Cog):
    def __init__(self, ex):
        self.ex = ex

    async def on_message(self, message, is_owner=False):
        if message.author.bot:
            return
        if is_owner:
            try:
                def check(m):
                    return m.channel == message.channel and m.author.id == owner_id

                msg = await self.ex.client.wait_for('message', timeout=60, check=check)
                if msg.content.lower() == "confirm" or msg.content.lower() == "confirmed":
                    return True
            except asyncio.TimeoutError:
                return False
        try:
            all_channels = await self.ex.conn.fetch("SELECT id, channelid, guildid, driveid, name FROM archive.channellist")
            for p_id, channel_id, guild_id, drive_id, name in all_channels:
                if message.channel.id != channel_id:
                    return
                if len(message.attachments):
                    for file in message.attachments:
                        url = file.url
                        if "%27%3E" in url:
                            pos = url.find("%27%3E")
                            url = url[0:pos - 1]
                        if ":large" in url:
                            pos = url.find(":large")
                            url = url[0:pos]
                        await Archive.download_url(url, drive_id, message.channel.id)
                    # quickstart.Drive.checker()
                if len(message.embeds):
                    for embed in message.embeds:
                        if str(embed.url) == "Embed.Empty":
                            pass
                        else:
                            url = embed.url
                            if "%27%3E" in url:
                                pos = url.find("%27%3E")
                                url = url[0:pos-1]
                            if ":large" in url:
                                pos = url.find(":large")
                                url = url[0:pos]
                            await Archive.download_url(url, drive_id, message.channel.id)
                        # quickstart.Drive.checker()
                await Archive.deletephotos()
        except Exception as e:
            log.useless(f"{e} - Archive.on_message")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def addchannel(self, ctx, drive_folder_id, name="NULL", owner_present=0):
        """REQUIRES BOT OWNER PRESENCE -- Make the current channel start archiving images to google drive [Format: %addchannel <drive folder id> <optional - name>]"""
        user = await self.ex.get_user(ctx.author.id)
        try:
            if not owner_present:
                return await ctx.send(await self.ex.replace(
                    await self.ex.get_msg(user, 'archive', 'talk_to_owner'), [['name', ctx.author.display_name],
                                                                         ['owner_id', self.ex.keys.owner_id]]))

            await ctx.send(await self.ex.get_msg(user, 'archive', 'waiting_confirmation'))
            if not await self.on_message(ctx, is_owner=True):

                return await ctx.send(await self.ex.get_msg(user, 'archive', 'no_confirmation'))

            drive_id_in_db = self.ex.first_result(await self.ex.conn.fetchrow("SELECT COUNT(*) FROM archive.channellist WHERE driveid = $1", drive_folder_id))
            if not drive_id_in_db:
                url = f"https://drive.google.com/drive/folders/{drive_folder_id}"
                return await ctx.send(await self.ex.replace(
                    await self.ex.get_msg(user, 'archive', 'url_being_used'), ['g_drive_url', url]))

            channel_id_in_db = self.ex.first_result(await self.ex.conn.fetchrow("SELECT COUNT(*) FROM archive.channellist WHERE channelid = $1", ctx.channel.id))
            if not channel_id_in_db:
                await ctx.send(await self.ex.get_msg(user, 'archive', 'being_archived'))

            url = f"https://drive.google.com/drive/folders/{drive_folder_id}"
            async with self.ex.session.get(url) as r:
                if r.status == 200:
                    await self.ex.conn.execute("INSERT INTO archive.ChannelList VALUES($1,$2,$3,$4)", ctx.channel.id, ctx.guild.id, drive_folder_id, name)
                    msg = await self.ex.get_msg(user, 'archive', 'archive_success')
                elif r.status == 404:
                    msg = await self.ex.get_msg(user, 'archive', 'not_found')
                elif r.status == 403:
                    msg = await self.ex.get_msg(user, 'archive', 'no_access')
                else:
                    msg = await self.ex.get_msg(user, 'archive', 'unknown_issue')
                await ctx.send(await self.ex.replace(msg, ["g_drive_url", url]))

        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(user, 'archive', 'main_error'))

    # noinspection PyBroadException
    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def listchannels(self, ctx):
        """List the channels in your server that are being archived. [Format: %listchannels]"""
        user = await self.ex.get_user(ctx.author.id)
        all_channels = await self.ex.conn.fetch("SELECT id, channelid, guildid, driveid, name FROM archive.ChannelList")
        guild_name = ctx.guild.name
        embed = discord.Embed(title=f"Archived {guild_name} Channels", color=0x87CEEB)
        embed.set_author(name="Irene", url=bot_website, icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for using Irene.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        check = False
        for p_id, channel_id, guild_id, drive_id, name in all_channels:
            # noinspection PyBroadException,PyBroadException,PyBroadException
            try:
                list_channel = (self.ex.client.get_channel(channel_id)).name
                if ctx.guild.id == guild_id:
                    check = True
                    embed.insert_field_at(0, name=list_channel, value=f"https://drive.google.com/drive/folders/{drive_id} | {name}", inline=False)
            except Exception as e:
                # Error would occur on test bot if the client does not have access to a certain channel id
                # this try-except will also be useful if a server removed the bot.
                log.useless(f"{e} - Archive.listchannels")
        if check:
            await ctx.send(embed=embed)
        else:
            await ctx.send(await self.ex.get_msg(user, 'archive', 'no_channels'))

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def deletechannel(self, ctx):
        """Stop the current channel from being archived [Format: %deletechannel]"""
        user = await self.ex.get_user(ctx.author.id)
        try:
            channel_id_in_db = self.ex.first_result(await self.ex.conn.fetchrow("SELECT COUNT(*) FROM archive.ChannelList WHERE ChannelID = $1", ctx.channel.id))
            if not channel_id_in_db:
                return await ctx.send(await self.ex.get_msg(user, 'archive', 'not_archived'))
            else:
                await self.ex.conn.execute("DELETE FROM archive.channellist WHERE ChannelID = $1", ctx.channel.id)
                await ctx.send(await self.ex.get_msg(user, 'archive', 'removed_archive'))
        except Exception as e:
            log.console(e)
            await ctx.send(await self.ex.get_msg(user, 'archive', 'main_error'))

    async def download_url(self, url, drive_id, channel_id):
        try:
            async with self.ex.session.get(url) as r:
                if r.status != 200:
                    return

                check = False
                unique_id = randint(0, 1000000000000)
                unique_id2 = randint(0, 1000)
                unique_id3 = randint(0, 500)
                src = url[len(url)-4:len(url)]
                checker_x = url.find(":large")
                if checker_x != -1:
                    src = url[len(url)-10:len(url)-6]
                    url = f"{url[0:checker_x-1]}:orig"

                src2 = url.find('?format=')
                if src2 != -1:
                    check = True
                    src = f".{url[src2+8:src2+11]}"
                    # url = f"{url[0:src2-1]}{src}:orig"
                if src == ".jpg" or src == ".gif" or src == '.png' or check:
                    file_name = f"1_{unique_id}_{unique_id2}_{unique_id3}{src}"
                    fd = await aiofiles.open(
                        'Photos/{}'.format(file_name), mode='wb')
                    await fd.write(await r.read())
                    await fd.close()
                    await self.ex.conn.execute("INSERT INTO archive.ArchivedChannels VALUES($1,$2,$3,$4)", file_name, src, drive_id, channel_id)
                    # quickstart.Drive.checker()
        except Exception as e:
            log.console(e)

    async def deletephotos(self):
        """Delete photos that are not needed."""
        all_files = await self.ex.conn.fetch("SELECT filename from archive.ArchivedChannels")
        file_list = [file[0] for file in all_files]
        all_photos = os.listdir('Photos')
        for photo in all_photos:
            if photo != "placeholder.txt" and photo not in file_list:
                try:
                    os.unlink('Photos/{}'.format(photo))
                except Exception as e:
                    log.useless(f"{e} - Failed to unlink photo - Archive.deletephotos")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def addhistory(self, ctx, year: int = None, month: int = None, day: int = None):
        """Add all of the previous images from a text channel to google drive."""
        user = await self.ex.get_user(ctx.author.id)
        if year and month and day:
            after = datetime(year, month, day)
        else:
            after = None

        async def history():
            try:
                async for message in ctx.channel.history(limit=None, after=after):
                    if len(message.attachments):
                        for file in message.attachments:
                            url = file.url
                            if "%27%3E" in url:
                                pos = url.find("%27%3E")
                                url = url[0:pos - 1]
                            if ":large" in url:
                                pos = url.find(":large")
                                url = url[0:pos - 1]
                            await self.download_url(url, drive_id, ctx.channel.id)

                    if len(message.embeds):
                        for embed in message.embeds:
                            if str(embed.url) == "Embed.Empty":
                                pass
                            else:
                                url = embed.url
                                if "%27%3E" in url:
                                    pos = url.find("%27%3E")
                                    url = url[0:pos-1]
                                if ":large" in url:
                                    pos = url.find(":large")
                                    url = url[0:pos-1]
                                await self.download_url(url, drive_id, ctx.channel.id)

            except Exception as e:
                log.console(e)
        check = False
        channels = await self.ex.conn.fetch("SELECT channelid, guildid, driveid FROM archive.ChannelList")
        for channel_id, guild_id, drive_id in channels:
            if ctx.channel.id == channel_id:
                check = True
                await ctx.send(await self.ex.get_msg(user, 'archive', 'history_start'))
                await history()
                await self.deletephotos()
                await ctx.send(await self.ex.get_msg(user, 'archive', 'history_success'))
        if not check:
            await self.ex.get_msg(user, 'archive', 'not_archived')
            await ctx.send(await self.ex.get_msg(user, 'archive', 'not_archived'))
