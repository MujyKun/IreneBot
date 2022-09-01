from typing import Literal

import disnake
from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot
from . import helper
from IreneAPIWrapper.models import Person, BiasGame as BiasGameModel


class UserNotificationsCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    # ==============
    # SLASH COMMANDS
    # ==============


def setup(bot: Bot):
    bot.add_cog(UserNotificationsCog(bot))
