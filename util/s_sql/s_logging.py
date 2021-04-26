import util.s_sql as self


async def fetch_logged_servers():
    """Fetch the servers being logged."""
    return await self.conn.fetch("SELECT id, serverid, channelid, sendall FROM logging.servers WHERE "
                                 "status = $1", 1)


async def fetch_logged_channels(primay_key):
    """Fetch the channels of a logged server.

    :param primay_key: The table key of the logged server.
    """
    return await self.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1", primay_key)
