import discord
import os
from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
import aiofiles
import sqlite3
import asyncio
import random

client = 0
path = 'module\currency.db'
DBconn = sqlite3.connect(path, check_same_thread = False)
#DBconn = sqlite3.connect(path)
c = DBconn.cursor()


def setup(client1):
    client1.add_cog(DreamCatcher(client1))
    global client
    client = client1


class DreamCatcher(commands.Cog):
    def __init__(self, client):
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
    async def createlinks(self, ctx, number=18144):
        """Create HD links and store them in the database.[Format: %createlinks (post number)]"""
        self.create_links_number = number

        @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
        async def paste_all_links(ctx):
            try:
                self.create_links_number += 1
                number = self.create_links_number
                # if number >= latest post
                if number >= (c.execute("SELECT PostID FROM DCPost").fetchone()[0]):
                    paste_all_links.cancel()
                else:
                    my_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(number)
                    async with aiohttp.ClientSession() as session:
                        async with session.get('{}'.format(my_url)) as r:
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
                                            c.execute("INSERT INTO DCHDLinks VALUES (NULL,?)", (HD_Link,))
                                            DBconn.commit()
                                            print(f"DC Link posted on DB for post {number}")
                                            number += 1
                                    else:
                                        print("LINK Passing Post from POST #{}".format(number))
                            elif r.status == 304:
                                print("> **Access Denied - {}**".format(number))
                            elif r.status == 404:
                                print("LINK Error 404. {} was not Found.".format(number))
                                pass
                            else:
                                print("LINK Other Error")
            except:
                pass
        paste_all_links.start(ctx)

    @commands.command(aliases=["%"])
    async def dcrandom(self, ctx):
        """Pull Random Photo from DC APP[Format: %dcrandom or %%]"""
        try:
            amount_of_links = c.execute("SELECT COUNT(*) FROM DCHDLinks").fetchone()[0]
            if amount_of_links == 0:
                await ctx.send("> **There are no links saved.**")
            if amount_of_links != 0:
                random_choice = random.randint(1,amount_of_links)
                link = c.execute("SELECT Link FROM DCHDLinks WHERE ID = ?", (random_choice,)).fetchone()[0]
                await ctx.send(link)
        except Exception as e:
            await ctx.send(e)


    @commands.command()
    @commands.is_owner()
    async def dcstop(self, ctx):
        """Stops DC Loop [Format: %dcstop]"""
        DCAPP().new_task4.stop()
        await ctx.send("> **If there was a loop, it stopped.**")

    @commands.command()
    @commands.is_owner()
    async def dcstart(self, ctx):
        """Starts DC Loop [Format: %dcstart]"""
        try:
            DCAPP().new_task4.start()
            await ctx.send("> **Loop started.**")
        except:
            await ctx.send("> **A loop is already running.**")
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updates(self, ctx,*, solution=""):
        """Send DC Updates to your current text channel [Format: %updates] | To Stop : [Format: %updates stop]"""
        channel = ctx.channel.id
        if solution == "stop":
            counter = c.execute("SELECT COUNT(*) From DreamCatcher WHERE ServerID = ?",(channel,)).fetchone()[0]
            if counter == 1:
                await ctx.send ("> **This channel will no longer receive updates.**")
                c.execute("DELETE FROM DreamCatcher WHERE ServerID = ?",(channel,))
                DBconn.commit()
            if counter == 0:
                await ctx.send("> **This channel does not currently receive updates.**")
        if solution != "stop":
            counter = c.execute("SELECT COUNT(*) From DreamCatcher WHERE ServerID = ?", (channel,)).fetchone()[0]
            if counter == 1:
                await ctx.send ("> **This channel already receives DC Updates**")
            if counter == 0:
                channel_name = client.get_channel(channel)
                await ctx.send("> **I Will Post All DC Updates In {}**".format(channel_name))
                c.execute("INSERT INTO DreamCatcher VALUES (?)",(channel,))
                DBconn.commit()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def latest(self, ctx):
        """Grabs the highest resolution possible from MOST RECENT DC Post [Format: %latest]"""
        my_url = c.execute("SELECT URL FROM DCUrl").fetchone()[0]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('{}'.format(my_url)) as r:
                    url_list = []
                    if r.status == 200:
                        page_html = await r.text()
                        page_soup = soup(page_html, "html.parser")
                        image_url = (page_soup.findAll("div", {"class": "imgSize width"}))
                        for image in image_url:
                            new_image_url = image.img["src"]
                            DC_Date = new_image_url[41:49]
                            unique_id = new_image_url[55:87]
                            file_format = new_image_url[93:]
                            HD_Link = f'https://file.candlemystar.com/post/{DC_Date}{unique_id}{file_format}'
                            url_list.append(HD_Link)
                        await ctx.send(f"> **Here are the Original Photos for <{my_url}>**:")
                        for link in url_list:
                            await ctx.send(f"<{link}>")
                    else:
                        await ctx.send(f"> **Error {r.status}: Unable to retrieve latest photos.**")
        except:
            await ctx.send(f"> **Unable to retrieve latest photos.** ")

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
            if number >= (c.execute("SELECT PostID FROM DCPost").fetchone()[0]):
                download_all_task.cancel()
            else:
                my_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(number)
                async with aiohttp.ClientSession() as session:
                    async with session.get('{}'.format(my_url)) as r:
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
                                            print(f"Downloaded {unique_id[:8]}{file_format} on {number}")
                                            number += 1
                                else:
                                    print("DOWNLOAD Passing Post from POST #{}".format(number))
                        elif r.status == 304:
                            print("> **Access Denied - {}**".format(number))
                        elif r.status == 404:
                            print("DOWNLOAD Error 404. {} was not Found.".format(number))
                            pass
                        else:
                            print("DOWNLOAD Other Error")
        download_all_task.start(ctx)


class DCAPP():
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
        # self.latest_DC = ''
        pass

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def new_task4(self):
        # print (self.number)
        self.count_loop += 1
        if self.first_run == 1:
            number = c.execute("SELECT PostID FROM DCPost").fetchone()[0]
            self.first_run = 0
            self.number = number
            self.post_list.append(number)
        if self.error_status == 1:
            if self.tries >= 2 and self.tries < 5:
                self.number += 1
            if self.tries >= 5:
                count_list = (len(self.post_list))
                # print (count_list)
                # print (self.post_list)
                self.number = self.post_list[count_list - 1]
                # print (self.number)
                self.tries = 0
        if self.error_status == 0:
            self.tries = 0
            self.number += 1
            pass
        # print (self.number)
        my_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(self.number)
        async with aiohttp.ClientSession() as session:
            async with session.get('{}'.format(my_url)) as r:
                if r.status == 200:
                    c.execute("DELETE FROM DCPost")
                    c.execute("INSERT INTO DCPost VALUES(?)", (self.number,))
                    DBconn.commit()
                    self.error_status = 0
                    if self.number not in self.post_list:
                        # print("Connection Found")
                        page_html = await r.text()
                        # print(await r.text())
                        page_soup = soup(page_html, "html.parser")
                        username = (page_soup.find("div", {"class": "card-name"})).text
                        # await ctx.send(username)
                        if username in self.list:
                            Gahyeon = self.list[0]
                            Siyeon = self.list[1]
                            Yoohyeon = self.list[2]
                            JiU = self.list[3]
                            SuA = self.list[4]
                            DC = self.list[5]
                            Dami = self.list[6]
                            Handong = self.list[7]
                            image_url = (page_soup.findAll("div", {"class": "imgSize width"}))
                            image_links = []
                            for image in image_url:
                                new_image_url = image.img["src"]
                                DC_Date = new_image_url[41:49]
                                unique_id = new_image_url[55:87]
                                file_format = new_image_url[93:]
                                HD_Link = f'https://file.candlemystar.com/post/{DC_Date}{unique_id}{file_format}'
                                image_links.append(HD_Link)
                                # automatically put HD links in database
                                try:
                                    c.execute("INSERT INTO DCHDLinks VALUES (NULL,?)", (HD_Link,))
                                    DBconn.commit()
                                except Exception as e:
                                    pass
                                async with session.get(HD_Link) as resp:
                                    fd = await aiofiles.open(
                                        'DreamHD/{}'.format(f"{unique_id[:8]}{file_format}"), mode='wb')
                                    await fd.write(await resp.read())
                                    await fd.close()
                            another_list = []
                            new_count = -1
                            final_image_list = []
                            for image in image_url:
                                new_count += 1
                                new_image_url = image.img["src"]
                                file_name = new_image_url[82:]
                                async with session.get(new_image_url) as resp:
                                    fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                                    await fd.write(await resp.read())
                                    await fd.close()
                                    file_size = (os.path.getsize(f'DCApp/{file_name}'))
                                    if file_size <= 20000:
                                        keep_going = True
                                        loop_count = 0
                                        while keep_going:
                                            print(f"Stuck in a loop {loop_count}")
                                            loop_count += 1
                                            try:
                                                os.unlink(f'DCApp/{file_name}')
                                            except Exception as e:
                                                print(e)
                                            fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                                            await fd.write(await resp.read())
                                            await fd.close()
                                            file_size = (os.path.getsize(f'DCApp/{file_name}'))
                                            if file_size > 20000:
                                                keep_going = False
                                            if loop_count == 30:
                                                try:
                                                    final_image_list.append(image_links[new_count])
                                                    os.unlink(f'DCApp/{file_name}')
                                                    keep_going = False
                                                except Exception as e:
                                                    print(e)
                                                    keep_going = False
                                    c.execute("DELETE FROM DCUrl")
                                    c.execute("INSERT INTO DCUrl VALUES(?)", (my_url,))
                                    DBconn.commit()
                                    another_list.append(file_name)
                            video_list = (page_soup.findAll("div", {"class": "swiper-slide img-box video-box width"}))
                            count_numbers = 0
                            video_name_list = []
                            bat_name_list = []
                            for video in video_list:
                                count_numbers += 1
                                new_video_url = video.source["src"]
                                bat_name = "{}DC.bat".format(count_numbers)
                                bat_name_list.append(bat_name)
                                ab = open("Videos\{}".format(bat_name), "a+")
                                video_name = "{}DCVideo.mp4".format(count_numbers)
                                info = 'ffmpeg -i "{}" -c:v libx264 -preset slow -crf 22 "Videos/{}"'.format(new_video_url,
                                                                                                             video_name)
                                video_name_list.append(video_name)
                                ab.write(info)
                                ab.close()
                            for bat_name in bat_name_list:
                                # open bat file
                                check_bat = await asyncio.create_subprocess_exec("Videos\\{}".format(bat_name),
                                                                                 stderr=asyncio.subprocess.PIPE)
                                await check_bat.wait()
                            a1 = c.execute("SELECT ServerID FROM DreamCatcher").fetchall()
                            for channel in a1:
                                channel = channel[0]
                                DC_Videos = []
                                try:
                                    if len(video_name_list) != 0:
                                        for video_name in video_name_list:
                                            dc_video = discord.File(fp='Videos/{}'.format(video_name), filename=video_name)
                                            DC_Videos.append(dc_video)
                                except Exception as e:
                                    print (e)
                                    pass
                                DC_Photos = []
                                try:
                                    if len(another_list) != 0:
                                        for file_name in another_list:
                                            dc_photo = discord.File(fp='DCApp/{}'.format(file_name),
                                                                    filename=file_name)
                                            DC_Photos.append(dc_photo)
                                except Exception as e:
                                    print (e)
                                    pass
                                channel = client.get_channel(channel)
                                # 'NoneType' object has no attribute 'send' -- Channel does not exist (catching error)
                                try:
                                    if username == Gahyeon:
                                        await channel.send(">>> **New Gahyeon Post\n<{}>**".format(my_url))
                                    if username == Siyeon:
                                        await channel.send(">>> **New Siyeon Post\n<{}>**".format(my_url))
                                    if username == Yoohyeon:
                                        await channel.send(">>> **New Yoohyeon Post\n<{}>**".format(my_url))
                                    if username == JiU:
                                        await channel.send(">>> **New JiU Post\n<{}>**".format(my_url))
                                    if username == SuA:
                                        await channel.send(">>> **New SuA Post\n<{}>**".format(my_url))
                                    if username == DC:
                                        await channel.send(">>> **New DreamCatcher Post\n<{}>**".format(my_url))
                                    if username == Dami:
                                        await channel.send(">>> **New Dami Post\n<{}>**".format(my_url))
                                    if username == Handong:
                                        await channel.send(">>> **New Handong Post\n<{}>**".format(my_url))
                                except Exception as e:
                                    print(e)
                                    pass
                                try:
                                    if len(another_list) != 0:
                                        await channel.send(files=DC_Photos)
                                    if len(video_name_list) != 0:
                                        await channel.send(files=DC_Videos)
                                    if len(final_image_list) != 0:
                                        for link in final_image_list:
                                            await channel.send(link)
                                except Exception as e:
                                    print (e)
                                    pass
                            all_videos = os.listdir('Videos')
                            for video in all_videos:
                                try:
                                    os.unlink('Videos/{}'.format(video))
                                except Exception as e:
                                    print(e)
                                    pass
                            all_photos = os.listdir('DCApp')
                            for photo in all_photos:
                                try:
                                    os.unlink('DCApp/{}'.format(photo))
                                except Exception as e:
                                    print (e)
                                    pass
                        else:
                            print("Passing Post from POST #{}".format(self.number))
                            # await ctx.send(">>> **Passing Post from {}, POST #{}**".format(username, self.number))
                    self.post_list.append(self.number)

                elif r.status == 304:
                    print("> **Access Denied - {}**".format(self.number))
                elif r.status == 404:
                    self.tries += 1
                    if self.count_loop % 100 == 0:
                        print("Error 404. {} was not Found.".format(self.number))
                    self.error_status = 1
                    pass
                else:
                    print(r.status)


# b = DCAPP()
# b.new_task4.start()
