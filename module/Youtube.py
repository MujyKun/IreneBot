from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
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
                await ex.conn.execute("INSERT INTO currency.Links VALUES($1)", link)
                await ctx.send("> **That video is now being traced**")
            except Exception as e:
                log.console (e)
                await ctx.send("> **That video is already being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def removeurl(self, ctx, link):
        """Remove url from youtube videos [Format: %removeurl (link)]"""
        try:
            await ex.conn.execute("DELETE FROM currency.Links WHERE Link = $1", link)
            await ctx.send("> **That video has been deleted**")
        except:
            await ctx.send("> **That video is not being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def scrapeyoutube(self, ctx):
        """Scrape Youtube Video"""
        links = await ex.conn.fetch("SELECT link FROM currency.links")
        for link in links:
            id = ex.first_result(await ex.conn.fetchrow("SELECT LinkID FROM currency.links WHERE Link = $1", link))
            async with ex.session.get('{}'.format(link[0])) as r:
                if r.status == 200:
                    page_html = await r.text()
                    log.console(page_html)
                    page_soup = soup(page_html, "html.parser")
                    view_count = (page_soup.find("div", {"class": "watch-view-count"})).text
                    # await ex.conn.execute("INSERT INTO currency.ViewCount VALUES ($1,$1)", id,datetime.now())
                    await ctx.send(f"> **Managed to scrape DC SCREAM -- {view_count} -- {datetime.now()}**")

    @commands.command()
    @commands.is_owner()
    async def stoploop(self, ctx):
        """Stops scraping youtube videos [Format: %stoploop]"""
        YoutubeLoop().new_task5.stop()
        await ctx.send("> **If there was a loop, it stopped.**")

    @commands.command()
    @commands.is_owner()
    async def startloop(self, ctx, seconds=0):
        """Starts scraping youtube videos [Format: %startloop (seconds)]"""
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
        self.view_count = []
        self.now = []
        pass

    @tasks.loop(seconds=0, minutes=30, hours=0, reconnect=True)
    async def new_task5(self):
        if ex.client.loop.is_running():
            if self.first_loop:
                await asyncio.sleep(10) # sleeping to stabilize connection to DB
                self.first_loop = False
            check = True
            try:
                links = await ex.conn.fetch("SELECT link FROM currency.links")
            except Exception as e:
                check = False
                pass
            if check:
                try:
                    for link in links:
                        link_id = ex.first_result(await ex.conn.fetchrow("SELECT LinkID FROM currency.links WHERE Link = $1", link))
                        async with ex.session.get('{}'.format(link[0])) as r:
                            if r.status == 200:
                                page_html = await r.text()
                                # log.console(page_html)
                                page_soup = soup(page_html, "html.parser")
                                view_count = (page_soup.find("div", {"class": "watch-view-count"})).text
                                now = datetime.now()
                                await ex.conn.execute("INSERT INTO currency.ViewCount VALUES ($1,$2,$3)", link_id, view_count, now)
                                self.view_count.append(view_count)
                                self.now.append(now)
                    # log.console("Updated Video Views Tracker")
                except Exception as e:
                    log.console(e)
            self.view_count = []
            self.now = []
