"""
sql.py

Abstract Class (Do Not Create An Instance)

Useful for different sql libraries.
"""


class SQL:
    async def create_level_row(self, user_id: int):
        """
        Create a row in currency.levels for the user.

        :param user_id: Discord User ID
        """

    async def update_level(self, user_id: int, column_name: str, level: int):
        """
        Update the level of a user.

        :param user_id: Discord User ID
        :param column_name: Column name of the currency.levels table
        :param level: Level to set column to.
        """

    async def register_currency(self, user_id: int, starting_balance: int):
        """
        Adds the user to the currency table.

        :param user_id: Discord User ID
        :param starting_balance: Amount of money a user should start with.
        """

    async def set_user_language(self, user_id: int, language: str):
        """
        Set the user's client language.

        :param user_id:
        :param language:
        """

    async def delete_user_language(self, user_id: int):
        """
        Deletes the user from the language table.
        Default is en_us [Which should not exist in the language table]

        :param user_id:
        """

    async def update_user_balance(self, user_id: int, money: str):
        """
        Update a user's balance.

        :param user_id: Discord User ID
        :param money: Balance to update to
        """

