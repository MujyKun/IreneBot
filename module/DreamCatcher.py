import discord
import os
from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
import aiofiles
import sqlite3
import asyncio

client = 0
path = 'module\currency.db'
DBconn = sqlite3.connect(path)
c = DBconn.cursor()


def setup(client1):
    client1.add_cog(DreamCatcher(client1))
    global client
    client = client1


class DreamCatcher(commands.Cog):
    def __init__(self, client):
        self.list = ['\n DC_GAHYEON                ', '\n DC_SIYEON                ', '\n DC_YOOHYEON                ', '\n DC_JIU                ', '\n DC_SUA                ', '\n DREAMCATCHER                ', '\n DC_DAMI                ', '\n DC_HANDONG                ']
        #1 Means True
        self.error_status = 1
        self.first_run = 1
        self.number = 0
        self.original_number = 0
        self.tries = 0
        self.post_list = []
        pass

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
    @commands.is_owner()
    async def scrape(self, ctx, *, number = 36666):
        """Starts Loop Searching For New DC Post [Format: %scrape (post number to start at)]"""
        @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
        async def new_task3(ctx, number):
            #print (self.number)
            if self.first_run == 1:
                self.first_run = 0
                self.number = number
                self.post_list.append(number)
            if self.error_status == 1:
                if self.tries >= 2 and self.tries < 25:
                    self.number += 1
                if self.tries >= 25:
                    count_list = (len(self.post_list))
                    #print (count_list)
                    #print (self.post_list)
                    self.number = self.post_list[count_list - 1]
                    #print (self.number)
                    self.tries = 0
            if self.error_status == 0:
                self.tries = 0
                self.number += 1
                pass
            #print (self.number)
            my_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(self.number)
            async with aiohttp.ClientSession() as session:
                async with session.get('{}'.format(my_url)) as r:
                    if r.status == 200:
                        self.error_status = 0
                        if self.number not in self.post_list:
                            #print("Connection Found")
                            page_html = await r.text()
                            #print(await r.text())
                            page_soup = soup(page_html, "html.parser")
                            username = (page_soup.find("div",{"class":"card-name"})).text
                            #await ctx.send(username)
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
                                another_list = []
                                for image in image_url:
                                    new_image_url = image.img["src"]
                                    file_name = new_image_url[82:]
                                    async with session.get(new_image_url) as resp:
                                        fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                                        await fd.write(await resp.read())
                                        await fd.close()
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
                                    info = 'ffmpeg -i "{}" -c:v libx264 -preset slow -crf 22 "Videos/{}"'.format(new_video_url, video_name)
                                    video_name_list.append(video_name)
                                    ab.write(info)
                                    ab.close()
                                for bat_name in bat_name_list:
                                    # open bat file
                                    check_bat = await asyncio.create_subprocess_exec("Videos\\{}".format(bat_name), stderr= asyncio.subprocess.PIPE)
                                    await check_bat.wait()
                                a1 = c.execute("SELECT ServerID FROM DreamCatcher").fetchall()
                                for channel in a1:
                                    channel = channel[0]
                                    DC_Videos = []
                                    try:
                                        if len(video_name_list) != 0:
                                            for video_name in video_name_list:
                                                dc_video = discord.File(fp='Videos/{}'.format(video_name), filename = video_name)
                                                DC_Videos.append(dc_video)
                                    except Exception as e:
                                        print (e)
                                    DC_Photos = []
                                    try:
                                        if len(another_list) != 0:
                                            for file_name in another_list:
                                                dc_photo = discord.File(fp='DCApp/{}'.format(file_name),
                                                                      filename= file_name)
                                                DC_Photos.append(dc_photo)
                                    except Exception as e:
                                        print(e)
                                    channel = client.get_channel(channel)
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
                                    try:
                                        if len(another_list) != 0:
                                            await channel.send(files=DC_Photos)
                                        if len(video_name_list) != 0:
                                            await channel.send(files=DC_Videos)
                                    except Exception as e:
                                        print(e)
                                        pass
                                all_videos = os.listdir('Videos')
                                for video in all_videos:
                                    try:
                                        os.unlink('Videos/{}'.format(video))
                                    except:
                                        pass
                                all_photos = os.listdir('DCApp')
                                for photo in all_photos:
                                    try:
                                        os.unlink('DCApp/{}'.format(photo))
                                    except:
                                        pass
                            else:
                                print("Passing Post from POST #{}".format(self.number))
                                #await ctx.send(">>> **Passing Post from {}, POST #{}**".format(username, self.number))
                        self.post_list.append(self.number)


                    elif r.status == 304:
                        print("> **Access Denied - {}**".format(self.number))
                    elif r.status == 404:
                        self.tries += 1
                        print("Error 404. {} was not Found.".format(self.number))
                        #await ctx.send('> **Error 404. {} was not Found.**'.format(self.number))
                        self.error_status = 1
                        pass
                    else:
                        print("Other Error")

        new_task3.start(ctx, number)
