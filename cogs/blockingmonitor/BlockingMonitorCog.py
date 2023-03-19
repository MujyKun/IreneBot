from models import Bot
from disnake.ext import commands
import sys
import time
import threading
import traceback
import concurrent.futures
import asyncio
from util import logger
from disnake import ApplicationCommandInteraction as AppCmdInter


class BlockingMonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitor_thread = StackMonitor(self.bot)
        self.monitor_thread.start()

    def cog_unload(self):
        self.monitor_thread.stop()

    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the right owner."""
        return await ctx.bot.is_owner(ctx.author)

    async def cog_slash_command_check(self, inter: AppCmdInter) -> bool:
        """A local cog check to confirm the right owner."""
        return await inter.bot.is_owner(inter.author)

    @commands.group(invoke_without_command=True)
    async def bmon(self, ctx):
        ...

    @bmon.command()
    async def stop(self, ctx):
        """Stop BlockingMonitor"""
        if not self.monitor_thread:
            print("Blocking Monitor already stopped.")
            return

        self.monitor_thread.stop()
        self.monitor_thread = None
        print("Blocking Monitor Stopped.")

    @bmon.command()
    async def start(self, ctx):
        """Start BlockingMonitor"""
        if self.monitor_thread:
            print("Blocking Monitor Already Running")
            return

        self.monitor_thread = StackMonitor(self.bot)
        self.monitor_thread.start()
        print("Started Blocking Monitor")


class StackMonitor(threading.Thread):
    def __init__(self, bot, block_threshold=1, check_freq=2):
        super().__init__(
            name=f"{type(self).__name__}-{threading._counter()}", daemon=True
        )
        self.bot = bot
        self._do_run = threading.Event()
        self._do_run.set()

        self.block_threshold = block_threshold
        self.check_frequency = check_freq

        self.last_stack = None
        self.still_blocked = False
        self._last_frame = None

    @staticmethod
    async def dummy_coro():
        return True

    def test_loop_availability(self):
        t0 = time.perf_counter()
        fut = asyncio.run_coroutine_threadsafe(self.dummy_coro(), self.bot.loop)
        t1 = time.perf_counter()

        try:
            fut.result(self.block_threshold)
            t2 = time.perf_counter()
        except (asyncio.TimeoutError, concurrent.futures.TimeoutError):
            t2 = time.perf_counter()

            frame = sys._current_frames()[self.bot.loop._thread_id]
            stack = traceback.format_stack(frame)

            if (
                stack == self.last_stack
                and frame is self._last_frame
                and frame.f_lasti == self._last_frame.f_lasti
            ):

                self.still_blocked = True
                logger.info("Still Blocked...")
                # log.console("Still blocked...", method=self.test_loop_availability, event_loop=self.ex.client.loop)
                return
            else:
                self.still_blocked = False

            logger.warn(
                f"Future took longer than {self.block_threshold}s to return\n"
                + "".join(stack)
            )

            self.last_stack = stack
            self._last_frame = frame

        else:
            if self.still_blocked:
                logger.info("No longer blocked.")
                self.still_blocked = False

            self.last_stack = None
            return t2 - t1

    def run(self):
        while self._do_run.is_set():
            if self.bot.loop.is_running():
                self.test_loop_availability()
            time.sleep(self.check_frequency)

    def stop(self):
        self._do_run.clear()


def setup(bot: Bot):
    bot.add_cog(BlockingMonitorCog(bot))
