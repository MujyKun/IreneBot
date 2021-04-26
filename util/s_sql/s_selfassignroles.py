import util.s_sql as self


async def fetch_all_self_assign_roles():
    """Fetch all role ids, role names, and server ids for self assignable roles."""
    return await self.conn.fetch("SELECT roleid, rolename, serverid FROM selfassignroles.roles")


async def fetch_all_self_assign_channels():
    """Fetch all channel ids and server ids for self assignable roles."""
    return await self.conn.fetch("SELECT channelid, serverid FROM selfassignroles.channels")