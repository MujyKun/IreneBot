from Utility import resources as ex
from util import logger as log
# from util.asyncpg import Asyncpg
from discord.ext import tasks
from concurrent.futures import ThreadPoolExecutor
import util.s_sql
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
                # to avoid circular import, set the Utility objects here.
                from util import objects
                ex.u_objects = objects

                ex.conn = await self.get_db_connection()
                # Delete all active blackjack games
                await ex.u_blackjack.delete_all_games()
                ex.running_loop = asyncio.get_running_loop()
                await self.create_thread_pool()
                sys.setrecursionlimit(ex.recursion_limit)
                # ex.sql = Asyncpg(ex.conn)
                ex.sql = util.s_sql
                util.s_sql.conn = ex.conn
            except Exception as e:
                log.console(e)
            self.set_start_up_connection.stop()

    @staticmethod
    async def create_thread_pool():
        ex.thread_pool = ThreadPoolExecutor()

    @tasks.loop(seconds=0, minutes=1, reconnect=True)
    async def show_irene_alive(self):
        """Looped every minute to send a connection to localhost:5123 to show bot is working well."""
        source_link = "http://127.0.0.1:5123/restartBot"
        async with ex.session.get(source_link):
            pass

    @staticmethod
    async def get_db_connection():
        """Retrieve Database Connection"""
        return await ex.keys.connect_to_db()


ex.u_database = DataBase()
# all active blackjack games are also deleted on db start, current session stats refreshed.
# cache is reset in the on_ready event.
ex.u_database.set_start_up_connection.start()



