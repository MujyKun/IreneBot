from typing import Union, List

import disnake
from models import Bot
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter, Permissions
from cogs.moderator import helper
from IreneAPIWrapper.models import ReactionRoleMessage


class ModeratorCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.guild_only()
    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the command is used in a guild and
        the user has manage messages permissions."""
        return ctx.author.guild_permissions.manage_messages

    async def cog_slash_command_check(self, inter: AppCmdInter):
        """A local cog check to confirm the command is used in a guild and
        the user has manage messages permissions."""
        if not inter.permissions.manage_permissions:
            raise commands.MissingPermissions(missing_permissions=["manage_messages"])
        if inter.guild is None:
            raise commands.NoPrivateMessage
        return True

    @commands.command(name="addemoji", aliases=["yoink"])
    @commands.has_guild_permissions(manage_emojis=True)
    async def regular_add_emoji(
        self, ctx, emoji: Union[disnake.PartialEmoji, str], emoji_name="EmojiName"
    ):
        if isinstance(emoji, disnake.PartialEmoji) and emoji_name == "EmojiName":
            emoji_name = emoji.name

        await helper.process_add_emoji(
            emoji=emoji, emoji_name=emoji_name, user_id=ctx.author.id, ctx=ctx
        )

    @commands.group(name="prefix", description="Commands related to Guild Prefixes.")
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

    @commands.command(
        name="clear",
        description="Clear messages in the text channel.",
        aliases=["prune"],
    )
    async def regular_clear_messages(self, ctx: commands.Context, amount: int = 1):
        await helper.process_prune(
            channel=ctx.channel,
            amount=amount + 1,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )  # + 1 for own message.

    # ==============
    # SLASH COMMANDS
    # ==============
    @commands.slash_command(
        name="clear",
        description="Clear messages in the text channel.",
        default_member_permissions=Permissions(manage_messages=True),
    )
    async def clear_messages(
        self, inter: AppCmdInter, amount: commands.Range[1, 100] = 1
    ):
        await helper.process_prune(
            channel=inter.channel,
            amount=amount,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="addemoji", description="Add an emoji to the server.")
    @commands.has_guild_permissions(manage_emojis=True)
    async def add_emoji(self, inter, emoji_url: str, emoji_name="EmojiName"):
        await helper.process_add_emoji(
            emoji=emoji_url, emoji_name=emoji_name, user_id=inter.author.id, inter=inter
        )

    @commands.slash_command(
        name="prefix",
        description="Commands related to Guild Prefixes.",
        default_member_permissions=Permissions(manage_messages=True),
    )
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

    @commands.slash_command(name="reactionroles", description="Add reaction roles.")
    async def slash_reaction_role(
        self, inter: AppCmdInter, description="Press a button to get the role you want!"
    ):
        await helper.process_add_reaction_role(
            inter.user.id,
            description=description,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: Bot):
    cog = ModeratorCog(bot)
    bot.add_listener(helper.handle_role_reaction_press, "on_button_click")
    bot.add_cog(cog)
