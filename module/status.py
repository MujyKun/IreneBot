import discord
from discord.ext import tasks
from module.keys import bot_prefix
import random
from Utility import resources as ex


# noinspection PyBroadException,PyPep8
class Status:
    """Change the bot's playing status in a loop"""
    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def change_bot_status_loop(self):
        try:
            if not ex.client.loop.is_running():
                raise Exception

            random_statuses = [
                f'{ex.u_miscellaneous.get_server_count()} servers.',
                f'{ex.u_miscellaneous.get_channel_count()} channels.',
                f'{bot_prefix}help',
                f'{ex.u_miscellaneous.get_user_count()} users.'
            ]
            if ex.cache.bot_statuses:
                final_statuses = []
                status = random.choice(ex.cache.bot_statuses)
                final_statuses.append(random.choice(random_statuses))
                final_statuses.append(status)
                final_status = random.choice(final_statuses)
            else:
                final_status = f"{bot_prefix}help"
            activity = discord.Activity(name=final_status, type=discord.ActivityType.listening)
            await ex.client.change_presence(status=discord.Status.online, activity=activity)
        except:
            pass
