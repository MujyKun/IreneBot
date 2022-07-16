from typing import Literal

import disnake
from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot, GuessingGame, GroupGuessingGame
from cogs.groupmembers import helper as gm_helper
from cogs.guessinggame import helper
from IreneAPIWrapper.models import User, Group, Person


class GuessingGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.command(
        name="guessinggame",
        description="Play a guessing game with Persons.",
        aliases=["gg"],
    )
    async def regular_guessinggame(
        self,
        ctx,
        max_rounds: int = 20,
        timeout: int = 20,
        gender="mixed",
        difficulty="medium",
        contains_nsfw="No",
    ):
        await helper.process_gg(
            self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            user_id=ctx.author.id,
            difficulty=difficulty,
            contains_nsfw=contains_nsfw,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(
        name="groupguessinggame",
        description="Play a guessing game with Groups.",
        aliases=["ggg"],
    )
    async def regular_group_guessinggame(
        self,
        ctx,
        max_rounds: int = 20,
        timeout: int = 20,
        gender="mixed",
        difficulty="medium",
        contains_nsfw="No",
    ):
        await helper.process_gg(
            self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            user_id=ctx.author.id,
            difficulty=difficulty,
            contains_nsfw=contains_nsfw,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            group_mode=True,
        )

    @commands.command(
        name="toggleggfilter", description="Toggle the filter for guessing game."
    )
    async def regular_toggleggfilter(self, ctx):
        await helper.process_toggle_gg_filter(
            user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    @commands.command(name="ggfilter", description="Filter the guessing game.")
    async def regular_gg_filter(self, ctx, person_id: int):
        await helper.process_gg_filter(
            user_id=ctx.author.id,
            selection_id=person_id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="gggfilter", description="Filter the group guessing game.")
    async def regular_ggg_filter(self, ctx, group_id: int):
        await helper.process_gg_filter(
            user_id=ctx.author.id,
            selection_id=group_id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            group_mode=True,
        )

    @commands.command(
        name="viewggfilter",
        description="View the GG Filter for Persons and Groups.",
        aliases=["viewgggfilter"],
    )
    async def regular_view_gg_filter(self, ctx, item_type: str = "person"):
        await helper.process_view_gg_filter(
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            group_mode=True if item_type.lower() in ["group", "groups"] else False,
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(
        name="guessinggame", description="Play a guessing game with Persons."
    )
    async def guessinggame(
        self,
        inter: AppCmdInter,
        max_rounds: commands.Range[3, 60] = 20,
        timeout: commands.Range[5, 60] = 20,
        gender: Literal["male", "female", "mixed"] = "mixed",
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        contains_nsfw: Literal["Yes", "No"] = "No",
    ):
        """Plays a guessing game."""
        await helper.process_gg(
            self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            user_id=inter.user.id,
            difficulty=difficulty,
            contains_nsfw=contains_nsfw,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="groupguessinggame", description="Play a guessing game with Groups."
    )
    async def groupguessinggame(
        self,
        inter: AppCmdInter,
        max_rounds: commands.Range[3, 60] = 20,
        timeout: commands.Range[5, 60] = 20,
        gender: Literal["male", "female", "mixed"] = "mixed",
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        contains_nsfw: Literal["Yes", "No"] = "No",
    ):
        """Plays a group guessing game."""
        await helper.process_gg(
            self.bot,
            max_rounds=max_rounds,
            timeout=timeout,
            gender=gender,
            user_id=inter.user.id,
            difficulty=difficulty,
            contains_nsfw=contains_nsfw,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
            group_mode=True,
        )

    @commands.slash_command(
        name="toggleggfilter", description="Toggle the filter for guessing game."
    )
    async def toggleggfilter(self, inter: AppCmdInter):
        """Toggle the GG Filter."""
        await helper.process_toggle_gg_filter(
            user_id=inter.user.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @commands.slash_command(name="ggfilter", description="Filter the guessing game.")
    async def ggfilter(
        self,
        inter: AppCmdInter,
        selection: str = commands.Param(autocomplete=gm_helper.auto_complete_person),
    ):
        person_id = int(selection.split(")")[0])
        await helper.process_gg_filter(
            user_id=inter.user.id,
            selection_id=person_id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="gggfilter", description="Filter the group guessing game."
    )
    async def gggfilter(
        self,
        inter: AppCmdInter,
        selection: str = commands.Param(autocomplete=gm_helper.auto_complete_group),
    ):
        group_id = int(selection.split(")")[0])
        await helper.process_gg_filter(
            user_id=inter.user.id,
            selection_id=group_id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="viewggfilter", description="View the GG Filter for Persons and Groups."
    )
    async def view_gg_filter(self, inter, item_type: Literal["person", "group"] = None):
        """View the GG filter for Persons and Groups."""
        await helper.process_view_gg_filter(
            user_id=inter.user.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
            group_mode=True if item_type == "group" else False,
        )


def setup(bot: Bot):
    bot.add_cog(GuessingGameCog(bot))
