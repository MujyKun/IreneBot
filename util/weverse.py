from Utility import resources as ex
import aiofiles
from util import logger as log


# noinspection PyBroadException,PyPep8
class Weverse:
    async def add_weverse_channel(self, channel_id, community_name):
        """Add a channel to get updates for a community"""
        community_name = community_name.lower()
        await ex.conn.execute("INSERT INTO weverse.channels(channelid, communityname) VALUES($1, $2)", channel_id,
                              community_name)
        await self.add_weverse_channel_to_cache(channel_id, community_name)

    @staticmethod
    async def add_weverse_channel_to_cache(channel_id, community_name):
        """Add a weverse channel to cache."""
        community_name = community_name.lower()
        channels = ex.cache.weverse_channels.get(community_name)
        if channels:
            channels.append([channel_id, None, False])
        else:
            ex.cache.weverse_channels[community_name] = [[channel_id, None, False]]

    @staticmethod
    async def check_weverse_channel(channel_id, community_name):
        """Check if a channel is already getting updates for a community"""
        channels = ex.cache.weverse_channels.get(community_name.lower())
        if channels:
            for channel in channels:
                if channel_id == channel[0]:
                    return True
        return False

    @staticmethod
    async def get_weverse_channels(community_name):
        """Get all of the channel ids for a specific community name"""
        return ex.cache.weverse_channels.get(community_name.lower())

    async def delete_weverse_channel(self, channel_id, community_name):
        """Delete a community from a channel's updates."""
        community_name = community_name.lower()
        await ex.conn.execute("DELETE FROM weverse.channels WHERE channelid = $1 AND communityname = $2", channel_id,
                              community_name)
        channels = await self.get_weverse_channels(community_name)

        if not channels:
            return

        for channel in channels:
            if channel[0] == channel_id:
                if channels:
                    channels.remove(channel)
                else:
                    ex.cache.weverse_channels.pop(community_name)

    async def add_weverse_role(self, channel_id, community_name, role_id):
        """Add a weverse role to notify."""
        await ex.conn.execute("UPDATE weverse.channels SET roleid = $1 WHERE channelid = $2 AND communityname = $3",
                              role_id, channel_id, community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, role_id)

    async def delete_weverse_role(self, channel_id, community_name):
        """Remove a weverse role from a server (no longer notifies a role)."""
        await ex.conn.execute(
            "UPDATE weverse.channels SET roleid = NULL WHERE channel_id = $1 AND communityname = $2", channel_id,
            community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, None)

    @staticmethod
    async def replace_cache_role_id(channel_id, community_name, role_id):
        """Replace the server role that gets notified on Weverse Updates."""
        channels = ex.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[1] = role_id

    @staticmethod
    async def change_weverse_comment_status(channel_id, community_name, comments_disabled, updated=False):
        """Change a channel's subscription and whether or not they receive updates on comments."""
        comments_disabled = bool(comments_disabled)
        community_name = community_name.lower()
        if updated:
            await ex.conn.execute(
                "UPDATE weverse.channels SET commentsdisabled = $1 WHERE channelid = $2 AND communityname = $3",
                int(comments_disabled), channel_id, community_name)
        channels = ex.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[2] = comments_disabled

    @staticmethod
    async def set_comment_embed(notification, embed_title):
        """Set Comment Embed for Weverse."""
        comment_body = await ex.weverse_client.fetch_comment_body(notification.community_id, notification.contents_id)
        if not comment_body:
            artist_comments = await ex.weverse_client.fetch_artist_comments(notification.community_id,
                                                                            notification.contents_id)
            if artist_comments:
                comment_body = (artist_comments[0]).body
            else:
                return
        embed_description = f"**{notification.message}**\n\n" \
                            f"Content: **{comment_body}**\n" \
                            f"Translated Content: **{await ex.weverse_client.translate(notification.contents_id, is_comment=True, community_id=notification.community_id)}**"
        embed = await ex.create_embed(title=embed_title, title_desc=embed_description)
        return embed

    async def set_post_embed(self, notification, embed_title):
        """Set Post Embed for Weverse."""
        post = ex.weverse_client.get_post_by_id(notification.contents_id)
        if post:
            # artist = self.weverse_client.get_artist_by_id(notification.artist_id)
            embed_description = f"**{notification.message}**\n\n" \
                                f"Artist: **{post.artist.name} ({post.artist.list_name[0]})**\n" \
                                f"Content: **{post.body}**\n" \
                                f"Translated Content: **{await ex.weverse_client.translate(post.id, is_post=True, p_obj=post, community_id=notification.community_id)}**"
            embed = await ex.create_embed(title=embed_title, title_desc=embed_description)
            message = "\n".join(
                [await self.download_weverse_post(photo.original_img_url, photo.file_name) for photo in post.photos])
            return embed, message
        return None, None

    @staticmethod
    async def download_weverse_post(url, file_name):
        """Downloads an image url and returns image host url."""
        async with ex.session.get(url) as resp:
            fd = await aiofiles.open(ex.keys.weverse_image_folder + file_name, mode='wb')
            await fd.write(await resp.read())
        return f"https://images.irenebot.com/weverse/{file_name}"

    @staticmethod
    async def set_media_embed(notification, embed_title):
        """Set Media Embed for Weverse."""
        media = ex.weverse_client.get_media_by_id(notification.contents_id)
        if media:
            embed_description = f"**{notification.message}**\n\n" \
                                f"Title: **{media.title}**\n" \
                                f"Content: **{media.body}**\n"
            embed = await ex.create_embed(title=embed_title, title_desc=embed_description)
            message = media.video_link
            return embed, message
        return None, None

    async def send_weverse_to_channel(self, channel_info, message_text, embed, is_comment, community_name):
        channel_id = channel_info[0]
        role_id = channel_info[1]
        comments_disabled = channel_info[2]
        if not (is_comment and comments_disabled):
            try:
                channel = ex.client.get_channel(channel_id)
                if not channel:
                    # fetch channel instead (assuming discord.py cache did not load)
                    channel = await ex.client.fetch_channel(channel_id)
            except:
                # remove the channel from future updates as it cannot be found.
                return await self.delete_weverse_channel(channel_id, community_name.lower())
            try:
                await channel.send(embed=embed)
                if message_text:
                    # Since an embed already exists, any individual content will not load
                    # as an embed -> Make it it's own message.
                    if role_id:
                        message_text = f"<@&{role_id}>\n{message_text}"
                    await channel.send(message_text)
                    log.console(f"Weverse Post for {community_name} sent to {channel_id}.")
            except Exception as e:
                log.console(f"Weverse Post Failed to {channel_id} for {community_name} -> {e}")
                # no permission to post
                return


ex.u_weverse = Weverse()
