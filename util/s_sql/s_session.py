import util.s_sql as self


async def fetch_command(session_id):
    """Fetch the command name and its usage amount for a certain session."""
    return await self.conn.fetch("SELECT commandname, count FROM stats.commands WHERE sessionid = $1", session_id)


async def fetch_session_usage(date):
    """Fetch the session command usage of a date."""
    return await self.conn.fetchrow("SELECT session FROM stats.sessions WHERE date = $1", date)


async def fetch_total_session_usage():
    """Fetches the total amount of commands used."""
    return await self.conn.fetchrow("SELECT totalused FROM stats.sessions ORDER BY totalused DESC")


async def add_new_session(total_used, session_commands, date):
    """Insert a new session.

    :param total_used: Total commands used for all sessions.
    :param session_commands: The amount of commands to give the session (usually 0)
    :param date: Usually datetime.date.today()
    """
    await self.conn.execute("INSERT INTO stats.sessions(totalused, session, date) VALUES ($1, $2, $3)",
                            total_used, session_commands, date)


async def fetch_session_id(date):
    """Fetch a session id with a date.

    :param date: Usually datetime.date.today()
    """
    return await self.conn.fetchrow("SELECT sessionid FROM stats.sessions WHERE date = $1", date)