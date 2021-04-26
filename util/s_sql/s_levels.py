import util.s_sql as self


async def create_level_row(user_id: int):
    """
    Create a row in currency.levels for the user.

    :param user_id: Discord User ID
    """
    await self.conn.execute("INSERT INTO currency.levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)


async def update_level(user_id: int, column_name: str, level: int):
    """
    Update the level of a user.

    :param user_id: Discord User ID
    :param column_name: Column name of the currency.levels table
    :param level: Level to set column to.
    """
    await self.conn.execute(f"UPDATE currency.levels SET {column_name} = $1 WHERE userid = $2", level, user_id)


async def get_profile_xp(user_id: int):
    """
    Get a user's profile xp.

    :param user_id: Discord User ID
    """
    return (await self.conn.fetchrow("SELECT profilexp FROM currency.levels WHERE userid = $1", user_id))[0]


async def fetch_levels():
    """Fetches all user ids and their rob, daily, beg, and profile level."""
    return await self.conn.fetch("SELECT userid, rob, daily, beg, profile FROM currency.levels")

