from Utility import resources as ex
from module import logger as log
from discord.ext import tasks
from concurrent.futures import ThreadPoolExecutor
from module.keys import connect_to_db
import sys
import asyncio


class DataBase:
    @tasks.loop(seconds=0, minutes=0, hours=0, reconnect=True)
    async def set_start_up_connection(self):
        """Looping Until A Stable Connection to DB is formed. This is to confirm Irene starts before the DB connects.
        Also creates thread pool and increases recursion limit.
        """
        if ex.client.loop.is_running():
            try:
                ex.conn = await self.get_db_connection()
                # Delete all active blackjack games
                await ex.u_database.delete_all_games()
                ex.running_loop = asyncio.get_running_loop()
                await self.create_thread_pool()
                sys.setrecursionlimit(ex.recursion_limit)
            except Exception as e:
                log.console(e)
            self.set_start_up_connection.stop()

    async def create_thread_pool(self):
        ex.thread_pool = ThreadPoolExecutor()

    @tasks.loop(seconds=0, minutes=1, reconnect=True)
    async def show_irene_alive(self):
        """Looped every minute to send a connection to localhost:5123 to show bot is working well."""
        source_link = "http://127.0.0.1:5123/restartBot"
        async with ex.session.get(source_link) as resp:
            pass

    @staticmethod
    async def get_db_connection():
        """Retrieve Database Connection"""
        return await connect_to_db()
