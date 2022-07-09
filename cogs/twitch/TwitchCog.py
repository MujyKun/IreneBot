import random
import disnake
from models import Bot
from IreneAPIWrapper.models import Media, Person, Group
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal, List


class TwitchCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


def setup(bot: Bot):
    bot.add_cog(TwitchCog(bot))
