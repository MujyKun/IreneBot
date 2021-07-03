import discord
from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
from IreneUtility.models import VliveChannel
import asyncio


class Vlive(commands.Cog):
    def __init__(self, t_ex):
        self.ex: Utility = t_ex

    @commands.group(aliases=["vlive"])
    @commands.has_guild_permissions(manage_messages=True)
    async def vliveupdates(self, ctx):
        """Follow a Vlive Channel and get announcements.

        [Format: %vliveupdates (idol/group/code) (idol id/group id/vlive code)]
        """
        ...

    @vliveupdates.command()
    async def idol(self, ctx, idol_id: int, role: discord.Role = None):
        """Follow a VLIVE channel belonging to an Idol ID If they have one."""
        role_id = None if not role else role.id
        idol = await self.ex.u_group_members.get_member(idol_id)
        if not idol:
            msg = await self.ex.get_msg(ctx, "groupmembers", "invalid_id")
            return await ctx.send(msg)

        if not isinstance(idol.vlive, VliveChannel):
            msg = await self.ex.get_msg(ctx, "vlive", "unknown_code", ["result", "idol"])
            return await ctx.send(msg)

        await self.ex.u_vlive.follow_or_unfollow(ctx, ctx.channel, idol.vlive.id, role_id=role_id)

    @vliveupdates.command()
    async def group(self, ctx, group_id: int, role: discord.Role = None):
        """Follow a VLIVE channel belonging to a Group ID If they have one."""
        role_id = None if not role else role.id
        group = await self.ex.u_group_members.get_group(group_id)
        if not group:
            msg = await self.ex.get_msg(ctx, "groupmembers", "invalid_id")
            return await ctx.send(msg)

        if not isinstance(group.vlive, VliveChannel):
            msg = await self.ex.get_msg(ctx, "vlive", "unknown_code", ["result", "group"])
            return await ctx.send(msg)

        await self.ex.u_vlive.follow_or_unfollow(ctx, ctx.channel, group.vlive.id, role_id=role_id)

    @vliveupdates.command()
    async def code(self, ctx, channel_code: str, role: discord.Role = None):
        """Follow a VLIVE channel based on the channel code."""
        role_id = None if not role else role.id
        channel_code = channel_code.lower()
        vlive_obj = self.ex.cache.vlive_channels.get(channel_code)
        if not vlive_obj:
            vlive_obj = VliveChannel(channel_code)

            # check if the code works
            if not await vlive_obj.check_channel_code():
                # code does not work
                msg = await self.ex.get_msg(ctx, "vlive", "invalid_code")
                return await ctx.send(msg)

            # add new object to the cache
            self.ex.cache.vlive_channels[vlive_obj.id] = vlive_obj

        await self.ex.u_vlive.follow_or_unfollow(ctx, ctx.channel, channel_code, role_id=role_id)

    @vliveupdates.command()
    async def list(self, ctx):
        """Lists the VLIVE channels currently being followed in the text channel."""
        channel_codes = []
        vlive_channels_copied = self.ex.cache.vlive_channels.copy()
        for vlive_obj in vlive_channels_copied.values():
            if vlive_obj.check_channel_followed(ctx.channel):
                channel_codes.append(vlive_obj.id)
        msg = await self.ex.get_msg(ctx, "vlive", "list_channel_codes", ["result", ", ".join(channel_codes)])
        return await ctx.send(msg)

    # notification loop
    @tasks.loop(seconds=0, minutes=1, hours=0, reconnect=True)
    async def vlive_notification_updates(self):
        """Send vlive announcements for live channels."""
        if not self.ex.irene_cache_loaded:
            return

        for vlive_channel in self.ex.cache.vlive_channels.values():
            await asyncio.sleep(0)  # bare yield

            if not vlive_channel:  # no channels are following the channel.
                continue

            try:
                if await vlive_channel.check_live() and not vlive_channel.already_posted:
                    channels_to_remove = await vlive_channel.send_live_to_followers()
                    for text_channel in channels_to_remove:
                        await self.ex.u_vlive.unfollow_vlive(text_channel, vlive_channel.id)
            except Exception as e:
                log.console(f"{e} (Exception)", method=self.vlive_notification_updates)
