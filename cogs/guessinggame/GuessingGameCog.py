from disnake.ext import commands
from models import Bot


class GuessingGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


def setup(bot: Bot):
    bot.add_cog(GuessingGameCog(bot))
