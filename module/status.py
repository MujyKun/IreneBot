import discord
from discord.ext import commands, tasks
from module.keys import client, bot_prefix
import random
from Utility import get_bot_statuses, get_server_count, get_channel_count, get_user_count


class Status:
    def __init__(self):
        pass

    """Change the bot's playing status in a loop"""
    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def change_bot_status_loop(self):
        try:
            random_statuses = [
                f'{get_server_count()} servers.',
                f'{get_channel_count()} channels.',
                f'{bot_prefix}help',
                f'{get_user_count()} users.'
            ]
            statuses = await get_bot_statuses()
            if statuses is not None:
                final_statuses = []
                status = (random.choice(statuses))[0]
                final_statuses.append(random.choice(random_statuses))
                final_statuses.append(status)
                final_status = random.choice(final_statuses)
            else:
                final_status = f"{bot_prefix}help"
            activity = discord.Activity(name=final_status, type=discord.ActivityType.listening)
            await client.change_presence(status=discord.Status.online, activity=activity)
        except Exception as e:
            pass
