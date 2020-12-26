import discord
from discord.ext import commands, tasks
from module import logger as log
from Utility import resources as ex


class Weverse(commands.Cog):
    def __init__(self):
        self.current_notification_id = 0
        self.notifications_already_posted = {}  # channel_id : [notification ids]
        self.available_choices = "[TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI, HENRY, Dreamcatcher]"

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def updates(self, ctx, community_name, role: discord.Role = None):
        """Receive Weverse Updates of a specific Weverse community in the current text channel. Use again to disable for a specific community.
        Available Communities ->
        [TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI, HENRY, Dreamcatcher]
        [Format: %updates <community name> [role to notify]]
        """
        try:
            if not ex.weverse_client.cache_loaded:
                return await ctx.send(f"> {ctx.author.display_name}, Weverse cache is being updated. Please try again in a minute or two.")

            channel_id = ctx.channel.id
            community_name = community_name.lower()
            if await ex.check_weverse_channel(channel_id, community_name):
                if not role:
                    await ex.delete_weverse_channel(channel_id, community_name)
                    return await ctx.send(f"> {ctx.author.display_name}, You will no longer receive updates for {community_name}.")
                else:
                    # add role to weverse subscription.
                    await ex.add_weverse_role(channel_id, community_name, role.id)
            for community in ex.weverse_client.communities:
                if community.name.lower() == community_name:
                    await ex.add_weverse_channel(channel_id, community_name)
                    return await ctx.send(f"> {ctx.author.display_name}, You will now receive weverse updates for {community.name} in this channel.")
            return await ctx.send(f"> {ctx.author.display_name},I could not find {community_name}. Available choices are:\n{self.available_choices}")
        except Exception as e:
            msg = "An error has occurred trying to subscribe to a weverse community."
            log.console(f"{msg} - {e}")
            return await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def disablecomments(self, ctx, community_name):
        """Disable updates for comments on a community."""
        channel_id = ctx.channel.id
        if await ex.check_weverse_channel(channel_id, community_name):
            for channel in await ex.get_weverse_channels(community_name):
                if channel[0] == channel_id:
                    await ex.change_weverse_comment_status(channel_id, community_name, not channel[2], updated=True)
                    if channel[2]:
                        return await ctx.send(f"> This channel will no longer receive comments from {community_name}.")
                    return await ctx.send(f"> This channel will now receive comments from {community_name}.")
        else:
            return await ctx.send(f"This channel is not subscribed to weverse updates from {community_name}.")

    # testing with the amount of seconds to avoid duplicates (checks have been put in place).
    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def weverse_updates(self):
        """Process for checking for Weverse updates and sending to discord channels."""
        if ex.weverse_client.cache_loaded:
            if await ex.weverse_client.check_new_user_notifications():
                user_notifications = ex.weverse_client.user_notifications
                if user_notifications:
                    is_comment = False
                    latest_notification = user_notifications[0]
                    community_name = latest_notification.community_name or latest_notification.bold_element
                    if not community_name:
                        return
                    channels = await ex.get_weverse_channels(community_name.lower())
                    noti_type = ex.weverse_client.determine_notification_type(latest_notification.message)
                    embed_title = f"New {community_name} Notification!"
                    message_text = None
                    if noti_type == 'comment':
                        is_comment = True
                        embed = await ex.set_comment_embed(latest_notification, embed_title)
                    elif noti_type == 'post':
                        embed, message_text = await ex.set_post_embed(latest_notification, embed_title)
                    elif noti_type == 'media':
                        embed, message_text = await ex.set_media_embed(latest_notification, embed_title)
                    elif noti_type == 'announcement':
                        return  # not keeping track of announcements ATM
                    else:
                        return
                    for channel_info in channels:
                        channel_id = channel_info[0]
                        notification_ids = self.notifications_already_posted.get(channel_id)
                        if not notification_ids:
                            await ex.send_weverse_to_channel(channel_info, message_text, embed, is_comment, community_name)
                            self.notifications_already_posted[channel_id] = [latest_notification.id]
                        else:
                            if latest_notification.id not in notification_ids:
                                self.notifications_already_posted[channel_id].append(latest_notification.id)
                                await ex.send_weverse_to_channel(channel_info, message_text, embed, is_comment, community_name)