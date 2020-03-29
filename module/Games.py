from discord.ext import commands
from module import logger as log


client = 0


def setup(client1):
    client1.add_cog(Games(client1))
    global client
    client = client1


class Games(commands.Cog):
    def __init__(self, client):
        pass
