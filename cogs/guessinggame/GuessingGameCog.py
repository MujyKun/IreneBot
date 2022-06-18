from typing import Literal

from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot, GuessingGame


class GuessingGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(name="guessinggame", description="Play a guessing game with Persons.")
    async def guessinggame(self, inter: AppCmdInter,
                           max_rounds: commands.Range[3, 60] = 20,
                           timeout: commands.Range[5, 60] = 20,
                           gender: Literal["male", "female", "mixed"] = "mixed",
                           difficulty: Literal["easy", "medium", "hard"] = "medium",
                           contains_nsfw: Literal["Yes", "No"] = "No"):
        """Send a photo of a random person."""

        contains_nsfw = True if contains_nsfw == "Yes" else False

        gg = GuessingGame(inter, self.bot, max_rounds, timeout, gender, difficulty, contains_nsfw)

        await inter.send("Starting guessing game")
        await gg.start()


def setup(bot: Bot):
    bot.add_cog(GuessingGameCog(bot))
