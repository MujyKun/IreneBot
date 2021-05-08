from discord.ext import commands, tasks
from datetime import *
import asyncio
from IreneUtility.util import u_logger as log


# noinspection PyBroadException,PyPep8
class Youtube(commands.Cog):
    def __init__(self, ex):
        self.ex = ex
        self.current_yt_loop_instance = None

    @commands.command()
    @commands.is_owner()
    async def addurl(self, ctx, link):
        """Add url to youtube videos [Format: %addurl (link)]"""
        if 'youtube.com' in link or 'youtu.be' in link:
            try:
                await self.ex.conn.execute("INSERT INTO youtube.links(link, channelid) VALUES($1, $2)", link, ctx.channel.id)
                await ctx.send(f"> **<{link}> is now being tracked.**")
            except Exception as e:
                log.console(e)
                await ctx.send(f"> **<{link}> is already being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def removeurl(self, ctx, link):
        """Remove url from youtube videos [Format: %removeurl (link)]"""
        try:
            await self.ex.conn.execute("DELETE FROM youtube.links WHERE link = $1", link)
            await ctx.send(f"> **<{link}> has been deleted**")
        except:
            await ctx.send(f"> **<{link}> is not being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def scrapeyoutube(self, ctx):
        """Scrape view count from the youtube videos in the DB."""
        await YoutubeLoop(self.ex).scrape_videos()
        await ctx.send("> Scraped.")

    @commands.command()
    @commands.is_owner()
    async def stoploop(self, ctx):
        """Stops scraping youtube videos (Including main loop from start up)[Format: %stoploop]"""
        if self.ex.cache.main_youtube_instance:
            self.ex.cache.main_youtube_instance.loop_youtube_videos.stop()
        if self.current_yt_loop_instance:
            self.current_yt_loop_instance.loop_youtube_videos.stop()
            self.current_yt_loop_instance = None
            return await ctx.send("> **The loop was stopped.**")
        return await ctx.send("> **There is no new loop currently running.**")

    @commands.command()
    @commands.is_owner()
    async def startloop(self, ctx, seconds=0):
        """Starts scraping youtube videos with a new instance[Format: %startloop (seconds to start)]"""
        try:
            if seconds >= 0:
                self.current_yt_loop_instance = YoutubeLoop(self.ex)
                if seconds > 0:
                    await ctx.send(f"> Starting loop in {seconds} seconds.")
                await asyncio.sleep(seconds)
                self.current_yt_loop_instance.loop_youtube_videos.start()
                await ctx.send("> **Loop started.**")
        except:
            await ctx.send("> **A loop is already running.**")


# noinspection PyBroadException,PyPep8
class YoutubeLoop:
    def __init__(self, ex):
        self.ex = ex

    async def send_channel(self, channel_id, data):
        try:
            channel = self.ex.client.get_channel(channel_id)
            await channel.send(data)
        except Exception as e:
            log.console(f"{e} - Failed to send data to {channel_id}")

    async def scrape_videos(self):
        links = await self.ex.conn.fetch("SELECT link, channelid FROM youtube.links")
        for url, channel_id in links:
            try:
                link_id = self.ex.first_result(
                    await self.ex.conn.fetchrow("SELECT id FROM youtube.links WHERE link = $1", url))
                async with self.ex.session.get(url) as r:
                    if r.status != 200:
                        continue
                    page_html = await r.text()
                    start_pos = page_html.find("viewCount") + 12
                    end_loc = start_pos
                    while page_html[end_loc] != '"':
                        end_loc += 1
                    raw_view_count = page_html[start_pos:end_loc]
                    view_count = f"{int(raw_view_count):,} views"
                    current_date = datetime.now()
                    await self.ex.conn.execute("INSERT INTO youtube.views(linkid, views, date) VALUES ($1,$2,$3)",
                                          link_id, view_count, str(current_date))
                    await self.send_channel(channel_id,
                                                   f"> **UPDATE FOR <{url}>: {view_count} -- {current_date}**")
            except Exception as e:
                log.console(e)
        log.console("Updated Video Views Tracker")

    @tasks.loop(seconds=0, minutes=30, hours=0, reconnect=True)
    async def loop_youtube_videos(self):
        if self.ex.client.loop.is_running():
            if self.ex.conn:  # make sure a connection to the db exists.
                await self.scrape_videos()
