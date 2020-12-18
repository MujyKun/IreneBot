import discord
from discord.ext import commands, tasks
from module import logger as log
from Utility import resources as ex


class Weverse(commands.Cog):
    def __init__(self):
        self.notifications_already_posted = []
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
    @tasks.loop(seconds=20, minutes=0, hours=0, reconnect=True)
    async def weverse_updates(self):
        """Process for checking for Weverse updates and sending to discord channels."""
        if ex.weverse_client.cache_loaded:
            if await ex.weverse_client.check_new_user_notifications():
                user_notifications = ex.weverse_client.user_notifications
                if user_notifications:
                    is_comment = False
                    latest_notification = user_notifications[0]
                    if latest_notification not in self.notifications_already_posted:
                        self.notifications_already_posted.append(latest_notification.id)
                        community_name = latest_notification.community_name or latest_notification.bold_element
                        if not community_name:
                            return
                        channels = await ex.get_weverse_channels(community_name.lower())
                        noti_type = ex.weverse_client.determine_notification_type(latest_notification.message)
                        embed_title = f"New {community_name} Notification!"
                        message = None
                        if noti_type == 'comment':
                            is_comment = True
                            embed = await ex.set_comment_embed(latest_notification, embed_title)
                        elif noti_type == 'post':
                            embed, message = await ex.set_post_embed(latest_notification, embed_title)
                        elif noti_type == 'media':
                            embed, message = await ex.set_media_embed(latest_notification, embed_title)
                        elif noti_type == 'announcement':
                            return  # not keeping track of announcements ATM
                        else:
                            return
                        # check again if it was already posted in the case 2 loops are running concurrently.
                        if latest_notification not in self.notifications_already_posted:
                            for channel_info in channels:
                                channel_id = channel_info[0]
                                role_id = channel_info[1]
                                comments_disabled = channel_info[2]
                                if not (is_comment and comments_disabled):
                                    try:
                                        channel = ex.client.get_channel(channel_id)
                                        if not channel:
                                            # fetch channel instead (assuming discord.py cache did not load)
                                            channel = await ex.client.fetch_channel(channel_id)
                                    except Exception as e:
                                        # remove the channel from future updates as it cannot be found.
                                        return await ex.delete_weverse_channel(channel_id, community_name.lower())
                                    try:
                                        await channel.send(embed=embed)
                                        if message:
                                            # Since an embed already exists, any individual content will not load
                                            # as an embed -> Make it it's own message.
                                            if role_id:
                                                message = f"<@&{role_id}>\n{message}"
                                            await channel.send(message)
                                    except Exception as e:
                                        # no permission to post
                                        return



