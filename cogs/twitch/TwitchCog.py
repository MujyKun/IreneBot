import random
import disnake
from IreneAPIWrapper.models.twitchaccount import TwitchAccount

from models import Bot
from IreneAPIWrapper.models import Media, Person, Group, Channel
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal, List, Optional
from disnake import Permissions


class TwitchCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.group(
        name="twitch", description="Commands related to Twitch Subscriptions."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    async def regular_twitch(self, ctx: commands.Context):
        ...

    @regular_twitch.command(name="add", description="Subscribe to a twitch account.")
    async def regular_add(
        self,
        ctx: commands.Context,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            guild=ctx.guild,
            twitch_username=twitch_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_twitch.command(
        name="list", description="List the Twitch accounts subscribed to."
    )
    async def regular_list(self, ctx: commands.Context):
        await ctx.send(await helper.get_subbed_msg(ctx.guild))

    @regular_twitch.command(
        name="remove", description="Unsubscribe from a twitch account."
    )
    async def regular_remove(
        self,
        ctx: commands.Context,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            ctx=ctx,
            channel_to_notify=channel if channel else ctx.channel,
            twitch_username=twitch_username,
            allowed_mentions=self.allowed_mentions,
        )

    # ==============
    # SLASH COMMANDS
    # ==============

    @commands.slash_command(
        name="twitch", description="Commands related to Twitch Subscriptions."
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def twitch(self, inter: AppCmdInter):
        ...

    @twitch.sub_command(name="add", description="Add a Twitch channel to subscribe to.")
    async def add(
        self,
        inter: AppCmdInter,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        await helper.process_add(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            guild=inter.guild,
            twitch_username=twitch_username,
            role_id=role.id if role else None,
            allowed_mentions=self.allowed_mentions,
        )

    @twitch.sub_command(name="remove", description="Unsubscribe from a Twitch channel.")
    async def remove(
        self,
        inter: AppCmdInter,
        twitch_username: str = commands.Param(
            autocomplete=helper.auto_complete_type_subbed_guild
        ),
        channel: Optional[disnake.TextChannel] = None,
    ):
        await helper.process_remove(
            inter=inter,
            channel_to_notify=channel if channel else inter.channel,
            twitch_username=twitch_username,
            allowed_mentions=self.allowed_mentions,
        )

    @twitch.sub_command(
        name="list",
        description="List all Twitch channels being followed in this guild.",
    )
    async def list(self, inter: AppCmdInter):
        await inter.send(await helper.get_subbed_msg(inter.guild))


def setup(bot: Bot):
    bot.add_cog(TwitchCog(bot))
