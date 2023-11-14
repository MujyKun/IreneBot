from typing import Literal

import disnake
from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot
from . import helper


class UnscrambleGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.command(
        name="unscramblegame", description="Play an unscramble game.", aliases=["us"]
    )
    @commands.guild_only()
    async def regular_unscramblegame(
        self, ctx, max_rounds=20, timeout=20, gender="mixed", difficulty="medium"
    ):
        await helper.process_us(
            bot=self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            difficulty=difficulty,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="unscramblegame", description="Play an unscramble game."
    )
    @commands.guild_only()
    async def unscramblegame(
        self,
        inter: AppCmdInter,
        max_rounds: commands.Range[int, 3, 60] = 20,
        timeout: commands.Range[int, 5, 60] = 20,
        gender: Literal["male", "female", "mixed"] = "mixed",
        difficulty: Literal["easy", "medium", "hard"] = "medium",
    ):
        """Plays a guessing game."""
        await helper.process_us(
            bot=self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            difficulty=difficulty,
            user_id=inter.user.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: Bot):
    bot.add_cog(UnscrambleGameCog(bot))
