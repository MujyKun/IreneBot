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
        self.current_notification_id = 0
        self.notifications_already_posted = {}  # channel_id : [notification ids]
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
        is_comment = False
        is_media = False
        images = None
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
            is_media = True
            embed, images, message_text = await self.ex.u_weverse.set_post_embed(latest_notification, embed_title)
        elif noti_type == 'media':
            is_media = True
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

        server_text_channel_ids = []  # text channels that belong to the support server

        try:
            support_server = self.ex.client.get_guild(self.ex.keys.bot_support_server_id) or self.ex.client.\
                fetch_guild(self.ex.keys.bot_support_server_id)

            server_text_channel_ids = [channel.id for channel in support_server.text_channels]
        except:
            warning_msg = "WARNING: Support Server could not be found for Weverse Cache to get the text channel IDs."
            log.console(warning_msg)
            log.useless(warning_msg)

        for channel_info in channels:
            channel_id = channel_info[0]
            if self.ex.weverse_announcements and channel_id not in server_text_channel_ids:
                # we do not want to remove the existing list of channels in the database, so we will use a filtering
                # method instead
                continue

            # sleeping for 2 seconds before every channel post. still needs to be properly tested
            # for rate-limits

            # after testing, Irene has been rate-limited too often, so we will introduce announcement
            # channels to the support server instead of constantly sending the same content to every channel.
            if not self.ex.weverse_announcements:
                await asyncio.sleep(2)

            notification_ids = self.notifications_already_posted.get(channel_id)
            if not notification_ids:
                await self.ex.u_weverse.send_weverse_to_channel(channel_info, message_text, embed, is_comment, is_media,
                                                                community_name, images=images)
                self.notifications_already_posted[channel_id] = [latest_notification.id]
            else:
                if latest_notification.id in notification_ids:
                    # it was already posted
                    continue

                self.notifications_already_posted[channel_id].append(latest_notification.id)
                await self.ex.u_weverse.send_weverse_to_channel(channel_info, message_text, embed,
                                                                is_comment, is_media, community_name, images=images)
