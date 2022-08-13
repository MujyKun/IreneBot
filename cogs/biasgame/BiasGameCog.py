from typing import Literal, Optional

import IreneAPIWrapper.models
import disnake
from disnake import AppCmdInter
from disnake.ext import commands
from models import BiasGame
from . import helper


class BiasGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.command(name="biasgame", description="Play a BiasGame")
    async def regular_biasgame(
        self, ctx: commands.Context, bracket_size: int = 8, gender: str = "mixed"
    ):
        """Play a Bias game."""
        await helper.process_bg(
            ctx=ctx,
            bot=self.bot,
            user_id=ctx.author.id,
            bracket_size=bracket_size,
            gender=gender,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(
        name="listbg", description="List a user's bias game leaderboards."
    )
    async def regular_listbg(self, ctx, user: Optional[disnake.User] = None):
        user = user if user else ctx.author
        await helper.process_list_bg(
            user_id=user.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(name="biasgame", description="Play a BiasGame")
    async def biasgame(
        self,
        inter: AppCmdInter,
        bracket_size: Literal[8, 16, 32, 64] = 8,
        gender: Literal["male", "female", "mixed"] = "mixed",
    ):
        """Play a Bias game."""
        await helper.process_bg(
            inter=inter,
            bot=self.bot,
            user_id=inter.user.id,
            bracket_size=bracket_size,
            gender=gender,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="listbg", description="List a user's bias game leaderboards."
    )
    async def listbg(self, inter, user: Optional[disnake.User] = None):
        user = user if user else inter.user
        await helper.process_list_bg(
            user_id=user.id, inter=inter, allowed_mentions=self.allowed_mentions
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(BiasGameCog(bot))
