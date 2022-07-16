import disnake
from models import Bot
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from cogs.moderator import helper


class ModeratorCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.group(name="prefix", description="Commands related to Guild Prefixes.")
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    async def regular_prefix(self, ctx: commands.Context):
        ...

    @regular_prefix.command(name="add", description="Add a guild prefix.")
    async def regular_prefix_add(self, ctx: commands.Context, prefix: str):
        await helper.process_prefix_add_remove(
            ctx=ctx,
            guild=ctx.guild,
            prefix=prefix,
            add=True,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_prefix.command(
        name="list", description="List all the current guild prefixes."
    )
    async def regular_prefix_list(self, ctx: commands.Context):
        await helper.process_prefix_list(
            ctx=ctx, guild=ctx.guild, allowed_mentions=self.allowed_mentions
        )

    @regular_prefix.command(name="remove", description="Delete a guild prefix.")
    async def regular_prefix_remove(self, ctx: commands.Context, prefix: str):
        await helper.process_prefix_add_remove(
            ctx=ctx,
            guild=ctx.guild,
            prefix=prefix,
            add=False,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(
        name="prefix", description="Commands related to Guild Prefixes."
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def prefix(self, inter: AppCmdInter):
        ...

    @prefix.sub_command(name="add", description="Add a guild prefix.")
    async def add(
        self,
        inter: AppCmdInter,
        prefix: str,
    ):
        await helper.process_prefix_add_remove(
            inter=inter,
            guild=inter.guild,
            prefix=prefix,
            add=True,
            allowed_mentions=self.allowed_mentions,
        )

    @prefix.sub_command(name="remove", description="Delete a guild prefix.")
    async def remove(
        self,
        inter: AppCmdInter,
        prefix: str = commands.Param(
            autocomplete=helper.auto_complete_type_guild_prefixes
        ),
    ):
        await helper.process_prefix_add_remove(
            inter=inter,
            guild=inter.guild,
            prefix=prefix,
            add=False,
            allowed_mentions=self.allowed_mentions,
        )

    @prefix.sub_command(
        name="list",
        description="List all the current guild prefixes.",
    )
    async def list(self, inter: AppCmdInter):
        await helper.process_prefix_list(
            inter=inter, guild=inter.guild, allowed_mentions=self.allowed_mentions
        )


def setup(bot: Bot):
    cog = ModeratorCog(bot)
    bot.add_cog(cog)
