from util.sql import SQL

"""
asyncpg.py (Concrete Class)


DESIGN FLAW:
This file will end up incredibly large and not spread across many files, but it will be the sacrifice for easier
swapping of DB libraries as a child of the SQL class.
"""

sql: SQL = None  # set to the same instance the Utility is working with ( but set to the abstract type )


class Asyncpg(SQL):
    def __init__(self, conn):
        self.conn = conn

        global sql
        sql = self

    """
    Method Descriptions may be found in the abstract class.
    The linter will take care of it.
    """

    async def create_level_row(self, user_id: int):
        await self.conn.execute("INSERT INTO currency.levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)

    async def update_level(self, user_id: int, column_name: str, level: int):
        await self.conn.execute(f"UPDATE currency.levels SET {column_name} = $1 WHERE userid = $2", level, user_id)

    async def register_currency(self, user_id: int, starting_balance: int):
        await self.conn.execute("INSERT INTO currency.currency (userid, money) VALUES ($1, $2)",
                                user_id, starting_balance)

    async def set_user_language(self, user_id: int, language: str):
        await self.conn.execute("INSERT INTO general.languages(userid, language) VALUES ($1, $2)", user_id, language)

    async def delete_user_language(self, user_id: int):
        await self.conn.execute("DELETE FROM general.languages WHERE userid = $1", user_id)

    async def update_user_balance(self, user_id: int, money: str):
        await self.conn.execute("UPDATE currency.currency SET money = $1::text WHERE userid = $2", money, user_id)












