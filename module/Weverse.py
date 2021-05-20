import discord
import asyncio
from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


# noinspection PyPep8
class Weverse(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex
        self.current_notification_id = 0
        self.notifications_already_posted = {}  # channel_id : [notification ids]
        self.available_choices = "[TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI," \
                                 " HENRY, Dreamcatcher, CherryBullet, MIRAE, TREASURE]"

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def updates(self, ctx, community_name, role: discord.Role = None):
        """
        Receive Weverse Updates of a specific Weverse community in the current text channel.

        Use again to disable for a specific community.
        Available Communities ->
        [TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI, HENRY, Dreamcatcher,
        CherryBullet, MIRAE, TREASURE]
        [Format: %updates <community name> [role to notify]]
        """
        try:
            if not self.ex.weverse_client.cache_loaded:
                return await ctx.send(f"> {ctx.author.display_name}, "
                                      f"Weverse cache is being updated. Please try again in a minute or two.")

            channel_id = ctx.channel.id
            community_name = community_name.lower()
            if community_name in ['cherry_bullet', 'cherrybullet']:
                community_name = "cherry bullet"
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
    async def disablecomments(self, ctx, community_name):
        """Disable updates for comments on a community."""
        channel_id = ctx.channel.id
        if not await self.ex.u_weverse.check_weverse_channel(channel_id, community_name):
            return await ctx.send(f"This channel is not subscribed to weverse updates from {community_name}.")
        for channel in await self.ex.u_weverse.get_weverse_channels(community_name):
            await asyncio.sleep(0)
            if channel[0] != channel_id:
                continue
            await self.ex.u_weverse.change_weverse_comment_status(channel_id, community_name, not channel[2],
                                                                  updated=True)
            if channel[2]:
                return await ctx.send(f"> This channel will no longer receive comments from {community_name}.")
            return await ctx.send(f"> This channel will now receive comments from {community_name}.")

    # testing with the amount of seconds to avoid duplicates (checks have been put in place).
    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def weverse_updates(self):
        """Process for checking for Weverse updates and sending to discord channels."""
        if not self.ex.weverse_client.cache_loaded:
            return

        if not await self.ex.weverse_client.check_new_user_notifications():
            return

        user_notifications = self.ex.weverse_client.user_notifications
        if not user_notifications:
            return
        is_comment = False
        latest_notification = user_notifications[0]

        community_name = latest_notification.community_name or latest_notification.bold_element
        if not community_name:
            return
        channels = await self.ex.u_weverse.get_weverse_channels(community_name.lower())
        if not channels:
            log.console("WARNING: There were no channels to post the Weverse notification to.")
            return

        noti_type = self.ex.weverse_client.determine_notification_type(latest_notification.message)
        embed_title = f"New {community_name} Notification!"
        message_text = None
        if noti_type == 'comment':
            is_comment = True
            embed = await self.ex.u_weverse.set_comment_embed(latest_notification, embed_title)
        elif noti_type == 'post':
            embed, message_text = await self.ex.u_weverse.set_post_embed(latest_notification, embed_title)
        elif noti_type == 'media':
            embed, message_text = await self.ex.u_weverse.set_media_embed(latest_notification, embed_title)
        elif noti_type == 'announcement':
            return None  # not keeping track of announcements ATM
        else:
            return None

        if not embed:
            log.console(f"WARNING: Could not receive Weverse information for {community_name}. "
                        f"Noti ID:{latest_notification.id} - "
                        f"Contents ID: {latest_notification.contents_id} - "
                        f"Noti Type: {latest_notification.contents_type}")
            return  # we do not want constant attempts to send a message.

        for channel_info in channels:
            # sleeping for 2 seconds before every channel post. still needs to be properly tested
            # for rate-limits
            await asyncio.sleep(2)
            channel_id = channel_info[0]
            notification_ids = self.notifications_already_posted.get(channel_id)
            if not notification_ids:
                await self.ex.u_weverse.send_weverse_to_channel(channel_info, message_text, embed, is_comment,
                                                                community_name)
                self.notifications_already_posted[channel_id] = [latest_notification.id]
            else:
                if latest_notification.id not in notification_ids:
                    self.notifications_already_posted[channel_id].append(latest_notification.id)
                    await self.ex.u_weverse.send_weverse_to_channel(channel_info, message_text, embed,
                                                                    is_comment, community_name)
