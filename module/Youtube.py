from discord.ext import commands, tasks
from datetime import *
import asyncio
from module import logger as log
from Utility import resources as ex


class Youtube(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    @commands.is_owner()
    async def addurl(self, ctx, link):
        """Add url to youtube videos [Format: %addurl (link)]"""
        if 'youtube.com' in link or 'youtu.be' in link:
            try:
                await ex.conn.execute("INSERT INTO youtube.links(link, channelid) VALUES($1, $2)", link, ctx.channel.id)
                await ctx.send(f"> **<{link}> is now being tracked.**")
            except Exception as e:
                log.console(e)
                await ctx.send(f"> **<{link}> is already being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def removeurl(self, ctx, link):
        """Remove url from youtube videos [Format: %removeurl (link)]"""
        try:
            await ex.conn.execute("DELETE FROM youtube.links WHERE link = $1", link)
            await ctx.send(f"> **<{link}> has been deleted**")
        except:
            await ctx.send(f"> **<{link}> is not being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def scrapeyoutube(self, ctx):
        """Scrape View Count From Youtube Video"""
        await YoutubeLoop.scrape_videos()

    @commands.command()
    @commands.is_owner()
    async def stoploop(self, ctx):
        """Stops scraping youtube videos [Format: %stoploop]"""
        YoutubeLoop().new_task5.stop()
        await ctx.send("> **If there was a loop, it stopped.**")

    @commands.command()
    @commands.is_owner()
    async def startloop(self, ctx, seconds=0):
        """Starts scraping youtube videos [Format: %startloop (seconds to start)]"""
        try:
            if seconds >= 0:
                await asyncio.sleep(seconds)
                YoutubeLoop().new_task5.start()
                await ctx.send("> **Loop started.**")
        except:
            await ctx.send("> **A loop is already running.**")


class YoutubeLoop:
    def __init__(self):
        self.first_loop = True

    @staticmethod
    async def send_channel(channel_id, data):
        try:
            channel = ex.client.get_channel(channel_id)
            await channel.send(data)
        except Exception as e:
            log.console(f"{e} - Failed to send data to {channel_id}")

    @staticmethod
    async def scrape_videos(check=True):
        try:
            links = await ex.conn.fetch("SELECT link, channelid FROM youtube.links")
            check = True
        except Exception as e:
            pass
        if check:
            try:
                for link in links:
                    link_id = ex.first_result(
                        await ex.conn.fetchrow("SELECT id FROM youtube.links WHERE link = $1", link[0]))
                    async with ex.session.get(link[0]) as r:
                        if r.status == 200:
                            page_html = await r.text()
                            start_pos = page_html.find("viewCount") + 14
                            end_loc = start_pos
                            while page_html[end_loc] != '\\':
                                end_loc += 1
                            view_count = f"{int(page_html[start_pos:end_loc]):,} views"
                            current_date = datetime.now()
                            await ex.conn.execute("INSERT INTO youtube.views(linkid, views, date) VALUES ($1,$2,$3)",
                                                  link_id, view_count, str(current_date))
                            await YoutubeLoop.send_channel(link[1],
                                                    f"> **UPDATE FOR <{link[0]}>: {view_count} -- {current_date}**")
                log.console("Updated Video Views Tracker")
            except Exception as e:
                log.console(e)

    @tasks.loop(seconds=0, minutes=30, hours=0, reconnect=True)
    async def new_task5(self):
        if ex.client.loop.is_running():
            if self.first_loop:
                await asyncio.sleep(10)  # sleeping to stabilize connection to DB
                self.first_loop = False
            check = False
            await self.scrape_videos(check)

