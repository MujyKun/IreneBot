import discord
from discord.ext import commands, tasks
from module.keys import client, bot_prefix
import random
from Utility import resources as ex


class Status:
    """Change the bot's playing status in a loop"""
    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def change_bot_status_loop(self):
        if ex.client.loop.is_running():
            try:
                random_statuses = [
                    f'{ex.get_server_count()} servers.',
                    f'{ex.get_channel_count()} channels.',
                    f'{bot_prefix}help',
                    f'{ex.get_user_count()} users.'
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
                await client.change_presence(status=discord.Status.online, activity=activity)
            except Exception as e:
                pass
