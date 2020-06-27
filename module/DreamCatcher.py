from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
import aiofiles
import asyncio
from module import logger as log
from module.keys import client
from Utility import DBconn, c, fetch_one, fetch_all,get_video_and_bat_list, get_dc_channels, get_videos, get_photos, get_embed, send_content, delete_content, get_member_name_and_id, add_post_to_db, send_new_post, open_bat_file, get_image_list, download_dc_photos


class DreamCatcher(commands.Cog):
    def __init__(self):
        self.list = ['\n DC_GAHYEON                ', '\n DC_SIYEON                ', '\n DC_YOOHYEON                ', '\n DC_JIU                ', '\n DC_SUA                ', '\n DREAMCATCHER                ', '\n DC_DAMI                ', '\n DC_HANDONG                ']
        # 1 Means True
        self.download_all_number = 0
        self.error_status = 1
        self.first_run = 1
        self.number = 0
        self.original_number = 0
        self.tries = 0
        self.post_list = []
        self.latest_DC = ''
        self.create_links_number = 0
        pass

    @commands.command()
    @commands.is_owner()
    async def dcstop(self, ctx):
        """Stops DC Loop [Format: %dcstop]"""
        DcApp().new_task4.stop()
        await ctx.send("> **If there was a loop, it stopped.**")

    @commands.command()
    @commands.is_owner()
    async def dcstart(self, ctx):
        """Starts DC Loop [Format: %dcstart]"""
        try:
            DcApp().new_task4.start()
            await ctx.send("> **Loop started.**")
        except:
            await ctx.send("> **A loop is already running.**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def updates(self, ctx, *, solution=""):
        """Send DC Updates to your current text channel [Format: %updates] | To Stop : [Format: %updates stop]"""
        channel = ctx.channel.id
        if solution == "stop":
            c.execute("SELECT COUNT(*) From dreamcatcher.DreamCatcher WHERE ServerID = %s",(channel,))
            counter = fetch_one()
            if counter == 1:
                await ctx.send ("> **This channel will no longer receive updates.**")
                c.execute("DELETE FROM dreamcatcher.DreamCatcher WHERE ServerID = %s",(channel,))
                DBconn.commit()
            if counter == 0:
                await ctx.send("> **This channel does not currently receive updates.**")
        if solution != "stop":
            c.execute("SELECT COUNT(*) From dreamcatcher.DreamCatcher WHERE ServerID = %s", (channel,))
            counter = fetch_one()
            if counter == 1:
                await ctx.send ("> **This channel already receives DC Updates**")
            if counter == 0:
                channel_name = client.get_channel(channel)
                await ctx.send("> **I Will Post All DC Updates In {}**".format(channel_name))
                c.execute("INSERT INTO dreamcatcher.DreamCatcher VALUES (%s)",(channel,))
                DBconn.commit()

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def latest(self, ctx, member=None):
        """Grabs the highest resolution possible from MOST RECENT DC Posts [Format: %latest (member)] [Member Options: jiu, sua, siyeon, handong, yoohyeon, dami, gahyeon, dc]"""
        member_list = ["jiu", "sua", "siyeon", "handong", "yoohyeon", "dami", "gahyeon", "dc"]
        if member is not None:
            member = member.lower()
        if member not in member_list and member is not None:
            await ctx.send("> **That member does not exist. The available member options are jiu, sua, siyeon, handong, yoohyeon, dami, gahyeon, dc**")
        else:
            original_post_number = 0
            hd_photos = ""
            if member is not None:
                c.execute("SELECT postnumber, link from dreamcatcher.dchdlinks WHERE member = %s ORDER BY postnumber DESC", (member,))
                all_links = fetch_all()
            else:
                c.execute("SELECT postnumber, link from dreamcatcher.dchdlinks ORDER BY postnumber DESC")
                all_links = fetch_all()
            for link in all_links:
                post_number = link[0]
                if original_post_number == post_number or original_post_number == 0:
                    original_post_number = post_number
                    url = link[1]
                    hd_photos += f"\n{url}"
            base_url = f"https://dreamcatcher.candlemystar.com/post/{original_post_number}"
            original_msg = f"> **Here are the Original Photos for <{base_url}>**:"
            await ctx.send(original_msg + hd_photos)

    @commands.command()
    @commands.is_owner()
    async def download_all(self, ctx, *, number=18144):
        """Download All DC Photos from DC APP [Format: %download_all]"""
        self.download_all_number = number
        @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
        async def download_all_task(ctx):
            self.download_all_number += 1
            number = self.download_all_number
            # if number >= latest post
            # last run on 40830
            c.execute("SELECT PostID FROM dreamcatcher.DCPost")
            if number >= fetch_one():
                download_all_task.cancel()
            else:
                post_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(number)
                async with aiohttp.ClientSession() as session:
                    async with session.get('{}'.format(post_url)) as r:
                        if r.status == 200:
                                page_html = await r.text()
                                page_soup = soup(page_html, "html.parser")
                                username = (page_soup.find("div", {"class": "card-name"})).text
                                if username in self.list:
                                    image_url = (page_soup.findAll("div", {"class": "imgSize width"}))
                                    for image in image_url:
                                        new_image_url = image.img["src"]
                                        DC_Date = new_image_url[41:49]
                                        unique_id = new_image_url[55:87]
                                        file_format = new_image_url[93:]
                                        HD_Link = f'https://file.candlemystar.com/post/{DC_Date}{unique_id}{file_format}'
                                        async with session.get(HD_Link) as resp:
                                            fd = await aiofiles.open('DCAppDownloaded/{}'.format(f"{unique_id[:8]}{file_format}"), mode='wb')
                                            await fd.write(await resp.read())
                                            await fd.close()
                                            log.console(f"Downloaded {unique_id[:8]}{file_format} on {number}")
                                            number += 1
                                else:
                                    log.console("DOWNLOAD Passing Post from POST #{}".format(number))
                        elif r.status == 304:
                            log.console("> **Access Denied - {}**".format(number))
                        elif r.status == 404:
                            log.console("DOWNLOAD Error 404. {} was not Found.".format(number))
                            pass
                        else:
                            log.console("DOWNLOAD Other Error")
        download_all_task.start(ctx)


class DcApp:
    def __init__(self):
        self.list = ['\n DC_GAHYEON                ', '\n DC_SIYEON                ', '\n DC_YOOHYEON                ', '\n DC_JIU                ', '\n DC_SUA                ', '\n DREAMCATCHER                ', '\n DC_DAMI                ', '\n DC_HANDONG                ']
        # 1 Means True
        self.error_status = 1
        self.first_run = 1
        self.number = 0
        self.original_number = 0
        self.tries = 0
        self.post_list = []
        self.count_loop = 0
        self.already_added = 0

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def new_task4(self):
        try:
            self.count_loop += 1
            if self.first_run == 1:
                c.execute("SELECT PostID FROM dreamcatcher.DCPost")
                number = fetch_one()
                self.first_run = 0
                self.number = number
                self.post_list.append(number)
            if self.error_status == 1:
                if 5 > self.tries >= 2:
                    self.number += 1
                if self.tries >= 5:
                    count_list = (len(self.post_list))
                    self.number = self.post_list[count_list - 1]
                    self.tries = 0
            if self.error_status == 0:
                self.tries = 0
                self.number += 1
                pass
            post_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(self.number)
            async with aiohttp.ClientSession() as session:
                async with session.get('{}'.format(post_url)) as r:
                    if r.status == 200:
                        c.execute("DELETE FROM dreamcatcher.DCPost")
                        c.execute("INSERT INTO dreamcatcher.DCPost VALUES(%s)", (self.number,))
                        DBconn.commit()
                        self.error_status = 0
                        if self.number not in self.post_list:
                            page_html = await r.text()
                            page_soup = soup(page_html, "html.parser")
                            username = (page_soup.find("div", {"class": "card-name"})).text
                            status_message = page_soup.find("div", {"class": "card-text"}).text
                            # Getting rid of unnecessary space
                            status_message = status_message.replace('                        ', '')
                            status_message = status_message.replace('                    ', '')
                            if username in self.list:
                                image_url = (page_soup.findAll("div", {"class": "imgSize width"}))
                                image_links = await download_dc_photos(image_url)
                                video_list, bat_list = get_video_and_bat_list(page_soup)
                                if bat_list is not None:
                                    await open_bat_file(bat_list)
                                    # Videos were attempting to being sent but were not found. Needs time to render.
                                    await asyncio.sleep(5)
                                channels = get_dc_channels()
                                member_name, member_id = get_member_name_and_id(username, self.list)
                                dc_photos_embed = await get_embed(image_links, member_name)
                                add_post_to_db(image_links, member_id, member_name, self.number, post_url)
                                for channel in channels:
                                    try:
                                        channel_id = channel[0]
                                        channel = client.get_channel(channel_id)
                                        # This part is repeated due to closed file IO error.
                                        dc_videos = get_videos(video_list)
                                        await send_new_post(channel_id, channel, member_name, status_message, post_url)
                                        await send_content(channel, dc_photos_embed, dc_videos)
                                    except Exception as e:
                                        # This try except was added due to errors with specific channels resulting
                                        # in an infinite loop
                                        pass
                                delete_content()
                            else:
                                log.console(f"Passing Post from POST #{self.number}")
                        self.post_list.append(self.number)

                    elif r.status == 304:
                        log.console(f"> **Access Denied - {self.number}**")
                    elif r.status == 404:
                        self.tries += 1
                        if self.count_loop % 500 == 0:
                            log.console(f"Error 404. {self.number} was not Found.")
                        self.error_status = 1
                        pass
                    else:
                        log.console(r.status)
        except Exception as e:
            log.console(e)
