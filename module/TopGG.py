import dbl
from discord.ext import commands
from module import keys
from module import logger as log


class TopGG(commands.Cog):
    """top.gg API"""
    def __init__(self, client):
        self.client = client
        self.token = keys.top_gg_key
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    async def on_guild_post(self):
        log.console("Server count posted successfully")
