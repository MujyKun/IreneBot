import util.s_sql as self


async def register_currency(user_id: int, starting_balance: int):
    """
    Adds the user to the currency table.

    :param user_id: Discord User ID
    :param starting_balance: Amount of money a user should start with.
    """
    await self.conn.execute("INSERT INTO currency.currency (userid, money) VALUES ($1, $2)",
                            user_id, starting_balance)


async def update_user_balance(user_id: int, money: str):
    """
    Update a user's balance.

    :param user_id: Discord User ID
    :param money: Balance to update to
    """
    await self.conn.execute("UPDATE currency.currency SET money = $1::text WHERE userid = $2", money, user_id)


async def fetch_currency():
    """Fetches all user ids with their balance."""
    return await self.conn.fetch("SELECT userid, money FROM currency.currency")
