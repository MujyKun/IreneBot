import util.s_sql as self


async def set_user_language(user_id: int, language: str):
    """
    Set the user's client language.

    :param user_id:
    :param language:
    """
    await self.conn.execute("INSERT INTO general.languages(userid, language) VALUES ($1, $2)", user_id, language)


async def delete_user_language(user_id: int):
    """
    Deletes the user from the language table.
    Default is en_us [Which should not exist in the language table]

    :param user_id:
    """
    await self.conn.execute("DELETE FROM general.languages WHERE userid = $1", user_id)


async def fetch_languages():
    """Fetches all user ids and their language preference."""
    return await self.conn.fetch("SELECT userid, language FROM general.languages")


async def fetch_timezones():
    """Fetch all timezones. (user id, timezone)"""
    return await self.conn.fetch("SELECT userid, timezone FROM reminders.timezones")
