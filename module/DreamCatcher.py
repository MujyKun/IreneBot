from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
import aiofiles
import discord
import asyncio
from module import logger as log
from module.keys import client, dc_app_test_channel_id
from Utility import resources as ex


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
        self.current_dc_loop_instance = None

    @commands.command()
    @commands.is_owner()
    async def dcstop(self, ctx):
        """Stops DC Loop [Format: %dcstop]"""
        if self.current_dc_loop_instance is not None:
            self.current_dc_loop_instance.new_task4.stop()
            self.current_dc_loop_instance = None
            return await ctx.send("> **The loop was stopped.**")
        return await ctx.send("> **Could not detect another loop.**")

    @commands.command()
    @commands.is_owner()
    async def dcstart(self, ctx):
        """Starts another instance of the DC Loop [Format: %dcstart]"""
        try:
            self.current_dc_loop_instance = DcApp()
            self.current_dc_loop_instance.new_task4.start()
            await ctx.send("> **Loop started.**")
        except:
            await ctx.send("> **A loop is already running.**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def dcnotify(self, ctx, role: discord.Role = None):
        """Mention a role when there is a new DC post.
        [Format: %dcnotify @role]"""
        channel_id = ctx.channel.id
        counter = await ex.get_dc_channel_exists(channel_id)
        server_prefix = await ex.get_server_prefix_by_context(ctx)
        if counter == 0:
            return await ctx.send(f"> {ctx.author.display_name}, This channel does not currently receive DCAPP Updates. Turn it on with {server_prefix}updates.")
        if role is None:
            await ex.conn.execute("UPDATE dreamcatcher.dreamcatcher SET roleid = NULL WHERE channelid = $1", channel_id)
            ex.cache.dc_app_channels[channel_id] = None
            return await ctx.send(f"> **{ctx.author.display_name}, no roles will be notified on a new DCAPP post. In order to notify a role, use {server_prefix}dcnotify @role.**")
        if counter == 1:
            await ex.conn.execute("UPDATE dreamcatcher.dreamcatcher SET roleid = $1 WHERE channelid = $2", role.id, channel_id)
            ex.cache.dc_app_channels[channel_id] = role.id
            return await ctx.send(f"> **{role} will now be pinged for the DCAPP updates.**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def updates(self, ctx, *, solution=""):
        """Send DC Updates to your current text channel [Format: %updates] | To Stop : [Format: %updates stop]"""
        channel_id = ctx.channel.id
        counter = await ex.get_dc_channel_exists(channel_id)
        if solution == "stop":
            if counter == 1:
                await ctx.send ("> **This channel will no longer receive updates.**")
                ex.cache.dc_app_channels.pop(channel_id, None)
                await ex.conn.execute("DELETE FROM dreamcatcher.DreamCatcher WHERE channelid = $1", channel_id)
            if counter == 0:
                await ctx.send("> **This channel does not currently receive updates.**")
        if solution != "stop":
            if counter == 1:
                await ctx.send("> **This channel already receives DC Updates**")
            if counter == 0:
                channel_name = client.get_channel(channel_id)
                await ctx.send("> **I Will Post All DC Updates In {}**".format(channel_name))
                ex.cache.dc_app_channels[channel_id] = None
                await ex.conn.execute("INSERT INTO dreamcatcher.DreamCatcher(channelid) VALUES ($1)", channel_id)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def latest(self, ctx, member=None):
        """Grabs the highest resolution possible from MOST RECENT DC Posts [Format: %latest (member)] [Member Options: jiu, sua, siyeon, handong, yoohyeon, dami, gahyeon, dc]"""
        if member is not None:
            member = member.lower()
        if member not in ex.cache.dc_member_list and member is not None:
            await ctx.send("> **That member does not exist. The available member options are jiu, sua, siyeon, handong, yoohyeon, dami, gahyeon, dc**")
        else:
            original_post_number = 0
            hd_photos = ""
            if member is not None:
                all_links = await ex.conn.fetch("SELECT postnumber, link from dreamcatcher.dchdlinks WHERE member = $1 ORDER BY postnumber DESC", member)
            else:
                all_links = await ex.conn.fetch("SELECT postnumber, link from dreamcatcher.dchdlinks ORDER BY postnumber DESC")
            for link in all_links:
                post_number = link[0]
                if original_post_number == post_number or original_post_number == 0:
                    original_post_number = post_number
                    url = link[1]
                    hd_photos += f"\n{url}"
            base_url = f"https://dreamcatcher.candlemystar.com/post/{original_post_number}"
            original_msg = f"> **Here are the Original Photos for <{base_url}>**:"
            await ctx.send(original_msg + hd_photos)

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
        self.last_updated_number = 0

    async def check_dc_post(self, dc_number, test=False, repost=False):
        post_url = 'https://dreamcatcher.candlemystar.com/post/{}'.format(dc_number)
        async with ex.session.get('{}'.format(post_url)) as r:
            if r.status == 200:
                if not repost:
                    try:
                        # There should only be one row in dreamcatcher.dcpost
                        post_exists = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM dreamcatcher.DCPost"))
                        if post_exists == 0:
                            await ex.conn.execute("INSERT INTO dreamcatcher.DCPost VALUES($1)", dc_number)
                        elif post_exists == 1:
                            if self.last_updated_number != dc_number:
                                await ex.conn.execute("UPDATE dreamcatcher.DCPost SET postid = $1", dc_number)
                                self.last_updated_number = dc_number
                        else:
                            await ex.conn.execute("DELETE FROM dreamcatcher.DCPost")  # just in case
                            await ex.conn.execute("INSERT INTO dreamcatcher.DCPost VALUES($1)", dc_number)
                    except Exception as e:
                            pass
                    self.error_status = 0
                if dc_number not in self.post_list:
                    page_html = await r.text()
                    page_soup = soup(page_html, "html.parser")
                    username = (page_soup.find("div", {"class": "card-name"})).text
                    if username in self.list:
                        image_url = (page_soup.findAll("div", {"class": "imgSize width"}))
                        image_links = await ex.download_dc_photos(image_url)
                        video_list, bat_list = await ex.get_video_and_bat_list(page_soup)
                        """
                        This is no longer necessary as it does it straight from the terminal now.
                        
                        if bat_list is not None:
                            await ex.open_bat_file(bat_list)
                            # Videos were attempting to being sent but were not found. Needs time to render.
                            await asyncio.sleep(5)
                        """
                        channels = ex.cache.dc_app_channels
                        if test:
                            channels = {dc_app_test_channel_id: None}
                        member_name, member_id = ex.get_member_name_and_id(username, self.list)
                        dc_photos_embed = await ex.get_embed(image_links, member_name)
                        if not repost:
                            await ex.add_post_to_db(image_links, member_id, member_name, dc_number, post_url)
                        status_message = page_soup.find("div", {"class": "card-text"}).text
                        # Getting rid of unnecessary spaces in the status message
                        status_message = status_message.replace('                        ', '')
                        status_message = status_message.replace('                    ', '')
                        # translate before iterating the channels.
                        translated_message = await ex.translate(status_message, 'ko', 'en')
                        for channel_id in channels:
                            try:
                                role_id = channels.get(channel_id)
                                channel = client.get_channel(channel_id)
                                # This part is repeated due to closed file IO error.
                                dc_videos = ex.get_videos(video_list)
                                await ex.send_new_post(channel_id, role_id, channel, member_name, status_message,
                                                       post_url, translated_message)
                                await ex.send_content(channel, dc_photos_embed, dc_videos)
                                if repost:
                                    await channel.send(f"> **Requested a repost from the server.**")
                            except Exception as e:
                                # This try except was added due to errors with specific channels resulting
                                # in an infinite loop
                                pass
                        ex.delete_content()
                    else:
                        log.console(f"Passing Post from POST #{dc_number}")
                self.post_list.append(dc_number)

            elif r.status == 304:
                log.console(f"> **Access Denied - {dc_number}**")
            elif r.status == 404:
                self.tries += 1
                if self.count_loop % 500 == 0:
                    log.console(f"Error 404. {dc_number} was not Found.")
                self.error_status = 1
                pass
            else:
                log.console(r.status)

    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def new_task4(self):
        try:
            if ex.client.loop.is_running():
                if self.first_run == 1:
                    await asyncio.sleep(10)  # sleeping to stabilize connection to DB
                self.count_loop += 1
                if self.first_run == 1:
                    number = ex.first_result(await ex.conn.fetchrow("SELECT PostID FROM dreamcatcher.DCPost"))
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
                await self.check_dc_post(self.number)
        except Exception as e:
            log.console(e)
