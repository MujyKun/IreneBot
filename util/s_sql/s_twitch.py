import util.s_sql as self


async def set_twitch_posted(twitch_username, channel_id):
    """
    Set a discord text channel to have already been sent a message from twitch announcements.
    :param twitch_username: Twitch username
    :param channel_id: Text Channel ID
    """
    await self.conn.execute("INSERT INTO twitch.alreadyposted(username, channelid) VALUES ($1, $2)",
                            twitch_username, channel_id)


async def delete_twitch_posted(twitch_username):
    """
    Delete the text channels from a table that have received messages for a twitch username.
    :param twitch_username: Twitch username
    """
    await self.conn.execute("DELETE FROM twitch.alreadyposted WHERE username = $1", twitch_username)


async def check_twitch_already_posted(twitch_username, channel_id) -> bool:
    """
    Check if a twitch channel being live was already posted to a text cahnnel.

    :param twitch_username: Twitch username
    :param channel_id: Text Channel ID
    :return: True if the live announcement was already posted.
    """
    return ((await self.conn.fetchrow("SELECT COUNT(*) FROM twitch.alreadyposted WHERE username = $1 AND "
                                      "channelid = $2", twitch_username, channel_id))[0]) >= 1


async def fetch_twitch_guilds():
    """Fetch all guild ids, channel ids, and role ids"""
    return await self.conn.fetch("SELECT guildid, channelid, roleid FROM twitch.guilds")


async def fetch_twitch_notifications():
    """Fetch all twitch username and guild ids that announcements should be sent to."""
    return await self.conn.fetch("SELECT username, guildid FROM twitch.channels")