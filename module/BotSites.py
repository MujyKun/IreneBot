from discord.ext import commands
from module.keys import client, discord_boats, bot_id
from module import logger as log
from Utility import resources as ex


class BotSites(commands.Cog):
    """Discord Bot Sites API"""
    def __init__(self):
        pass


@client.event
async def on_guild_post():
    log.console("Server Count Updated on Top.GG")
    try:
        # discord.boats
        if ex.get_server_count() != 0:
            await discord_boats.post_stats(botid=bot_id, server_count=ex.get_server_count())
            log.console("Server Count Updated on discord.boats")
    except Exception as e:
        log.console(f"Server Count Update FAILED on discord.boats - {e}")
