import discord
from discord.ext import tasks
from module.keys import bot_prefix
import random
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


# noinspection PyBroadException,PyPep8
class Status:
    def __init__(self, ex):
        """

        :param ex: Utility object.
        """
        self.ex: Utility = ex

    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def change_bot_status_loop(self):
        """Change the bot's playing status in a loop"""
        try:
            if not self.ex.client.loop.is_running():
                raise Exception

            random_statuses = [
                f'{self.ex.u_miscellaneous.get_server_count()} servers.',
                f'{self.ex.u_miscellaneous.get_channel_count()} channels.',
                f'{bot_prefix}help',
                f'{self.ex.u_miscellaneous.get_user_count()} users.'
            ]
            if self.ex.cache.bot_statuses:
                final_statuses = []
                status = random.choice(self.ex.cache.bot_statuses)
                final_statuses.append(random.choice(random_statuses))
                final_statuses.append(status)
                final_status = random.choice(final_statuses)
            else:
                final_status = f"{bot_prefix}help"
            activity = discord.Activity(name=final_status, type=discord.ActivityType.listening)
            await self.ex.client.change_presence(status=discord.Status.online, activity=activity)
        except Exception as e:
            log.useless(f"{e} (Exception) - Failed to change status presence of bot. - Status.change_bot_status_loop")
