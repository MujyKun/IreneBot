import util.s_sql as self


async def fetch_cached_patrons():
    """Fetch the cached patrons."""
    return await self.conn.fetch("SELECT userid, super FROM patreon.cache")


async def delete_patron(user_id):
    """Delete a patron.

    :param user_id: Discord User ID
    """
    await self.conn.execute("DELETE FROM patreon.cache WHERE userid = $1", user_id)


async def update_patron(user_id, super_patron: int):
    """Updates a patron's status

    :param user_id: Discord User ID
    :param super_patron: 1 for the user becoming a super patron, or 0 if they are a normal patron.
    """
    await self.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", super_patron, user_id)


async def add_patron(user_id, super_patron: int):
    """Add a patron

    :param user_id: Discord User ID
    :param super_patron: 1 for the user becoming a super patron, or 0 if they are a normal patron.
    """
    await self.conn.execute("INSERT INTO patreon.cache(userid, super) VALUES($1, $2)", user_id, super_patron)