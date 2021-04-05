from util.sql import SQL

"""
asyncpg.py (Concrete Class)
"""

sql: SQL = None  # set to the same instance the Utility is working with ( but the concrete type )


class Asyncpg(SQL):
    def __init__(self, conn):
        self.conn = conn

        global sql
        sql = self

    async def create_level_row(self, user_id: int):
        """
        Create a row in currency.levels for the user.

        :param user_id: Discord User ID
        """
        await self.conn.execute("INSERT INTO currency.levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)

    async def update_level(self, user_id: int, column_name: str, level: int):
        """
        Update the level of a user.

        :param user_id: Discord User ID
        :param column_name: Column name of the currency.levels table
        :param level: Level to set column to.
        """
        await self.conn.execute(f"UPDATE currency.levels SET {column_name} = $1 WHERE userid = $2", level, user_id)

    async def register_currency(self, user_id: int, starting_balance: int):
        """
        Adds the user to the currency table.

        :param user_id: Discord User ID
        :param starting_balance: Amount of money a user should start with.
        """
        await self.conn.execute("INSERT INTO currency.currency (userid, money) VALUES ($1, $2)",
                                user_id, starting_balance)

    async def set_user_language(self, user_id: int, language: str):
        """
        Set the user's client language.

        :param user_id:
        :param language:
        """
        await self.conn.execute("INSERT INTO general.languages(userid, language) VALUES ($1, $2)", user_id, language)

    async def delete_user_language(self, user_id: int):
        """
        Deletes the user from the language table.
        Default is en_us [Which should not exist in the language table]

        :param user_id:
        """
        await self.conn.execute("DELETE FROM general.languages WHERE userid = $1", user_id)

    async def update_user_balance(self, user_id: int, money: str):
        """
        Update a user's balance.

        :param user_id: Discord User ID
        :param money: Balance to update to
        """
        await self.conn.execute("UPDATE currency.currency SET money = $1::text WHERE userid = $2", money, user_id)








