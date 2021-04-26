import util.s_sql as self


async def fetch_filter_enabled():
    """Fetches the users with a guessing game filter enabled."""
    return await self.conn.fetch("SELECT userid from gg.filterenabled")


async def fetch_filtered_groups():
    """Fetches all the users and the groups they have filtered."""
    return await self.conn.fetch("SELECT userid, groupid FROM gg.filteredgroups")


async def fetch_gg_stats():
    """Fetch the user's id, easy, medium, and hard guessing game stats"""
    return await self.conn.fetch("SELECT userid, easy, medium, hard FROM stats.guessinggame")