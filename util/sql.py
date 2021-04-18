"""
sql.py

Abstract Class (Do Not Create An Instance)

Useful for different sql libraries.

DESIGN FLAW:
This file will end up incredibly large and not spread across many files, but it will be the sacrifice for easier
swapping of DB libraries.
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

    async def get_profile_xp(self, user_id: int) -> int:
        """
        Get a user's profile xp.

        :param user_id: Discord User ID
        """

    async def set_twitch_posted(self, twitch_username, channel_id):
        """
        Set a discord text channel to have already been sent a message from twitch announcements.
        :param twitch_username: Twitch username
        :param channel_id: Text Channel ID
        """

    async def delete_twitch_posted(self, twitch_username):
        """
        Delete the text channels from a table that have received messages for a twitch username.
        :param twitch_username: Twitch username
        """

    async def check_twitch_already_posted(self, twitch_username, channel_id) -> bool:
        """
        Check if a twitch channel being live was already posted to a text cahnnel.

        :param twitch_username: Twitch username
        :param channel_id: Text Channel ID
        :return: True if the live announcement was already posted.
        """


