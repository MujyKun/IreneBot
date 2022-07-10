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

    @commands.command(name="test")
    async def test(
        self,
        ctx: commands.Context,
        twitch_username: str,
        channel: Optional[disnake.TextChannel] = None,
        role: Optional[disnake.Role] = None,
    ):
        role_id = role.id if role else None
        await helper.subscribe(
            twitch_username,
            channel_id=channel.id if channel else ctx.channel.id,
            guild=ctx.guild,
            role_id=role_id,
        )
        await ctx.send(f"You are now subscribed to {twitch_username}.")

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
        # make sure server is not already following the twitch account
        role_id = role.id if role else None
        await helper.subscribe(
            twitch_username,
            channel_id=channel.id if channel else inter.channel_id,
            guild=inter.guild,
            role_id=role_id,
        )

        await inter.send("Works.")

    @twitch.sub_command(name="remove", description="Unsubscribe from a Twitch channel.")
    async def remove(self, inter: AppCmdInter):
        await inter.send("Works.")

    @twitch.sub_command(
        name="list",
        description="List all Twitch channels being followed in this guild.",
    )
    async def list(self, inter: AppCmdInter):
        await inter.send("Works.")


def setup(bot: Bot):
    bot.add_cog(TwitchCog(bot))
