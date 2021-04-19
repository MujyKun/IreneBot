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

    async def fetch_languages(self):
        """Fetches all user ids and their language preference."""

    async def fetch_levels(self):
        """Fetches all user ids and their rob, daily, beg, and profile level."""

    async def fetch_currency(self):
        """Fetches all user ids with their balance."""

    async def fetch_filter_enabled(self):
        """Fetches the users with a guessing game filter enabled."""

    async def fetch_filtered_groups(self):
        """Fetches all the users and the groups they have filtered."""

    async def fetch_twitch_guilds(self):
        """Fetch all guild ids, channel ids, and role ids"""

    async def fetch_twitch_notifications(self):
        """Fetch all twitch username and guild ids that announcements should be sent to."""

    async def fetch_gg_stats(self):
        """Fetch the user's id, easy, medium, and hard guessing game stats"""

    async def fetch_reminders(self):
        """Fetch all reminders. (id, user id, reason, timestamp)"""

    async def fetch_timezones(self):
        """Fetch all timezones. (user id, timezone)"""

    async def fetch_all_self_assign_roles(self):
        """Fetch all role ids, role names, and server ids for self assignable roles."""

    async def fetch_all_self_assign_channels(self):
        """Fetch all channel ids and server ids for self assignable roles."""

    async def fetch_weverse(self):
        """Fetch all weverse subscriptions."""

    async def fetch_command(self, session_id):
        """Fetch the command name and its usage amount for a certain session."""

    async def fetch_session_usage(self, date):
        """Fetch the session command usage of a date."""

    async def fetch_restricted_channels(self):
        """Fetch all restricted idol photo channels."""

    async def fetch_custom_commands(self):
        """Fetches all custom commands."""

    async def fetch_bot_statuses(self):
        """Fetch all bot statuses."""

    async def fetch_dead_links(self):
        """Fetch all dead links."""

    async def fetch_all_idols(self):
        """Fetch all idols."""

    async def fetch_all_groups(self):
        """Fetch all groups."""

    async def fetch_aliases(self, object_id, group=False):
        """Fetch all global and server aliases of an idol or group.

        :param object_id: An Idol or Group id
        :param group: Whether the object is a group.
        """

    async def fetch_members_in_group(self, group_id):
        """Fetches the idol ids in a group.

        :param group_id: The group's id
        """

    async def fetch_total_session_usage(self):
        """Fetches the total amount of commands used."""

    async def add_new_session(self, total_used, session_commands, date):
        """Insert a new session.

        :param total_used: Total commands used for all sessions.
        :param session_commands: The amount of commands to give the session (usually 0)
        :param date: Usually datetime.date.today()
        """

    async def fetch_session_id(self, date):
        """Fetch a session id with a date.

        :param date: Usually datetime.date.today()
        """

    async def fetch_n_word(self):
        """Fetch all users N Word count."""

    async def fetch_temp_channels(self):
        """Fetch all temporary channels"""

    async def fetch_welcome_messages(self):
        """Fetch all welcome messages"""

    async def fetch_server_prefixes(self):
        """Fetch the server prefixes."""

    async def fetch_logged_servers(self):
        """Fetch the servers being logged."""

    async def fetch_logged_channels(self, primay_key):
        """Fetch the channels of a logged server.

        :param primay_key: The table key of the logged server.
        """

    async def fetch_bot_bans(self):
        """Fetch all bot bans."""

    async def fetch_mod_mail(self):
        """Fetch mod mail users and channels."""

    async def fetch_cached_patrons(self):
        """Fetch the cached patrons."""

    async def delete_patron(self, user_id):
        """Delete a patron.

        :param user_id: Discord User ID
        """

    async def update_patron(self, user_id, super_patron: int):
        """Updates a patron's status

        :param user_id: Discord User ID
        :param super_patron: 1 for the user becoming a super patron, or 0 if they are a normal patron.
        """

    async def add_patron(self, user_id, super_patron: int):
        """Add a patron

        :param user_id: Discord User ID
        :param super_patron: 1 for the user becoming a super patron, or 0 if they are a normal patron.
        """

