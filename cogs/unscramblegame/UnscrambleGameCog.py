from typing import Literal

from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot, UnscrambleGame
from IreneAPIWrapper.models import User


class UnscrambleGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(name="unscramblegame", description="Play an unscramble game.")
    async def unscramblegame(self, inter: AppCmdInter,
                           max_rounds: commands.Range[3, 60] = 20,
                           timeout: commands.Range[5, 60] = 20,
                           gender: Literal["male", "female", "mixed"] = "mixed",
                           difficulty: Literal["easy", "medium", "hard"] = "medium"):
        """Plays a guessing game."""
        user = await User.get(inter.user.id)
        us = UnscrambleGame(inter, self.bot, max_rounds, timeout, gender, difficulty, user=user)

        await inter.send("Starting unscramble game")
        await us.start()


def setup(bot: Bot):
    bot.add_cog(UnscrambleGameCog(bot))
