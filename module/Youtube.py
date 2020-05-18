from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup as soup
from datetime import *
import asyncio
from module import logger as log
from Utility import fetch_all, fetch_one, DBconn, c


class Youtube(commands.Cog):
    def __init__(self, client):
        self.client = client
        pass

    @commands.command()
    @commands.is_owner()
    async def addurl(self, ctx, link):
        """Add url to youtube videos [Format: %addurl (link)]"""
        if 'youtube.com' in link or 'youtu.be' in link:
            try:
                c.execute("INSERT INTO currency.Links VALUES(%s)", (link,))
                DBconn.commit()
                await ctx.send("> **That video is now being traced**")
            except Exception as e:
                log.console (e)
                await ctx.send("> **That video is already being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def removeurl(self, ctx, link):
        """Remove url from youtube videos [Format: %removeurl (link)]"""
        try:
            c.execute("DELETE FROM currency.Links WHERE Link = %s", (link,))
            DBconn.commit()
            await ctx.send("> **That video has been deleted**")
        except:
            await ctx.send("> **That video is not being tracked.**")

    @commands.command()
    @commands.is_owner()
    async def scrapeyoutube(self, ctx):
        """Scrape Youtube Video"""
        c.execute("SELECT link FROM currency.links")
        links = fetch_all()
        for link in links:
            c.execute("SELECT LinkID FROM currency.links WHERE Link = %s", (link,))
            id = fetch_one()
            async with aiohttp.ClientSession() as session:
                async with session.get('{}'.format(link[0])) as r:
                    if r.status == 200:
                        page_html = await r.text()
                        log.console(page_html)
                        page_soup = soup(page_html, "html.parser")
                        view_count = (page_soup.find("div", {"class": "watch-view-count"})).text
                        # c.execute("INSERT INTO currency.ViewCount VALUES (%s,%s)", (id,datetime.now()))
                        # DBconn.commit()
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
        self.view_count = []
        self.now = []
        pass

    @tasks.loop(seconds=0, minutes=30, hours=0, reconnect=True)
    async def new_task5(self):
        check = True
        try:
            c.execute("SELECT link FROM currency.links")
            links = fetch_all()
        except Exception as e:
            check = False
            pass
        if check:
            try:
                for link in links:
                    c.execute("SELECT LinkID FROM currency.links WHERE Link = %s", link)
                    link_id = fetch_one()
                    async with aiohttp.ClientSession() as session:
                        async with session.get('{}'.format(link[0])) as r:
                            if r.status == 200:
                                page_html = await r.text()
                                # log.console(page_html)
                                page_soup = soup(page_html, "html.parser")
                                view_count = (page_soup.find("div", {"class": "watch-view-count"})).text
                                now = datetime.now()
                                c.execute("INSERT INTO currency.ViewCount VALUES (%s,%s,%s)", (link_id, view_count, now))
                                self.view_count.append(view_count)
                                self.now.append(now)
                                DBconn.commit()
                # log.console("Updated Video Views Tracker")
            except Exception as e:
                log.console(e)
        self.view_count = []
        self.now = []
