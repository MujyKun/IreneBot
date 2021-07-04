import discord
import asyncio
from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


# noinspection PyPep8
class Weverse(commands.Cog):
    def __init__(self, ex):
        self.running = False
        self.ex: Utility = ex
        self.available_choices = "[TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI," \
                                 " HENRY, Dreamcatcher, CherryBullet, MIRAE, TREASURE, LETTEAMOR, EVERGLOW, FTISLAND," \
                                 " woo!ah!, IKON, JUST_B, BlackPink]"

    @commands.command(aliases=["weverse"])
    @commands.has_guild_permissions(manage_messages=True)
    async def weverseupdates(self, ctx, community_name, role: discord.Role = None):
        """
        Receive Weverse Updates of a specific Weverse community in the current text channel.

        Use again to disable for a specific community.
        Available Communities ->
        [TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI, HENRY, Dreamcatcher,
        Cherry_Bullet, MIRAE, TREASURE, LETTEAMOR, EVERGLOW, FTISLAND, woo!ah!, IKON, JUST_B, BLACKPINK]
        [Format: %updates <community name> [role to notify]]
        """
        try:
            if not self.ex.weverse_client.cache_loaded:
                return await ctx.send(f"> {ctx.author.display_name}, "
                                      f"Weverse cache is being updated. Please try again in a minute or two.")

            if self.ex.weverse_announcements:
                if ctx.author.id != self.ex.keys.owner_id:
                    msg = await self.ex.get_msg(ctx.author.id, "weverse", "bot_owner_only",
                                                ["support_server_link", self.ex.keys.bot_support_server_link])
                    return await ctx.send(msg)

            channel_id = ctx.channel.id
            community_name = community_name.lower()
            community_name = community_name.replace("_", " ")
            if await self.ex.u_weverse.check_weverse_channel(channel_id, community_name):
                if not role:
                    await self.ex.u_weverse.delete_weverse_channel(channel_id, community_name)
                    return await ctx.send(f"> {ctx.author.display_name}, You will no longer receive updates for "
                                          f"{community_name}.")
            for community in self.ex.weverse_client.all_communities.values():
                await asyncio.sleep(0)
                if community.name.lower() == community_name:
                    # delete any existing before adding a new one.
                    await self.ex.u_weverse.delete_weverse_channel(channel_id, community_name)
                    await self.ex.u_weverse.add_weverse_channel(channel_id, community_name)
                    # add role to weverse subscription after channel is added to db.
                    if role:
                        await self.ex.u_weverse.add_weverse_role(channel_id, community_name, role.id)
                    return await ctx.send(f"> {ctx.author.display_name}, You will now receive weverse updates for"
                                          f" {community.name} in this channel.")
            return await ctx.send(f"> {ctx.author.display_name},I could not find {community_name}. "
                                  f"Available choices are:\n{self.available_choices}")
        except Exception as e:
            msg = "An error has occurred trying to subscribe to a weverse community."
            log.console(f"{msg} - {e}")
            return await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def disablecomments(self, ctx, *, community_name):
        """Disable updates for comments on a community."""
        await self.ex.u_weverse.disable_type(ctx, community_name.replace("_", " "))

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def disablemedia(self, ctx, *, community_name):
        """Disable updates for media on a community."""
        await self.ex.u_weverse.disable_type(ctx, community_name.replace("_", " "), media=True)

    @commands.command()
    @commands.is_owner()
    async def testweverse(self, ctx, amount=20):
        """Attempt to post the notifications in Weverse to the channel.

        [Format: %testweverse [amount=20]
        """
        for count, noti in enumerate(self.ex.weverse_client.user_notifications):
            await self.ex.u_weverse.send_notification(noti, ctx=ctx)
            if count == amount:
                return

# testing with the amount of seconds to avoid duplicates (checks have been put in place).
    @tasks.loop(seconds=45, minutes=0, hours=0, reconnect=True)
    async def weverse_updates(self):
        """Process for checking for Weverse updates and sending to discord channels."""
        if not self.ex.weverse_client.cache_loaded:
            return

        if not await self.ex.weverse_client.check_new_user_notifications():
            return

        user_notifications = self.ex.weverse_client.user_notifications
        if not user_notifications:
            return

        latest_notification = user_notifications[0]

        await self.ex.u_weverse.send_notification(latest_notification)


