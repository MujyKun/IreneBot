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

    @commands.guild_only()
    @commands.group(name="noti")
    async def regular_noti(self, ctx):
        ...

    @regular_noti.command(name="add", description="Add a phrase/word to be notified for.")
    async def regular_add(self, ctx: commands.Context, *, phrase: str):
        await helper.process_add(
            phrase=phrase,
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_noti.command(name="remove", description="Remove a phrase/word to no longer be notified for.")
    async def regular_remove(self, ctx: commands.Context, *, phrase: str):
        await helper.process_remove(
            phrase=phrase,
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_noti.command(name="list", description="List all your user notifications in this server.")
    async def regular_list(self, ctx: commands.Context):
        await helper.process_list(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============
    @commands.guild_only()
    @commands.slash_command(
        name="noti", description="Commands related to User Notifications."
    )
    async def noti(self, inter: AppCmdInter):
        ...

    @noti.sub_command(name="add", description="Add a phrase/word to be notified for.")
    async def add(self, inter: AppCmdInter, phrase: str):
        await helper.process_add(
            phrase=phrase,
            guild_id=inter.guild.id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @noti.sub_command(
        name="remove", description="Remove a phrase/word to no longer be notified for."
    )
    async def remove(
        self,
        inter: AppCmdInter,
        phrase: str = commands.Param(autocomplete=helper.auto_complete_phrases),
    ):
        await helper.process_remove(
            phrase=phrase,
            guild_id=inter.guild.id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @noti.sub_command(
        name="list", description="List all your user notifications in this server."
    )
    async def list(self, inter: AppCmdInter):  # add auto complete
        await helper.process_list(
            guild_id=inter.guild.id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: Bot):
    bot.add_cog(UserNotificationsCog(bot))
