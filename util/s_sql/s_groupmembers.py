import util.s_sql as self


async def fetch_restricted_channels():
    """Fetch all restricted idol photo channels."""
    return await self.conn.fetch("SELECT channelid, serverid, sendhere FROM groupmembers.restricted")


async def fetch_dead_links():
    """Fetch all dead links."""
    return await self.conn.fetch("SELECT deadlink, userid, messageid, idolid, guessinggame FROM "
                                 "groupmembers.deadlinkfromuser")


async def fetch_all_idols():
    """Fetch all idols."""
    return await self.conn.fetch("""SELECT id, fullname, stagename, formerfullname, formerstagename, birthdate,
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify,
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags, difficulty
            FROM groupmembers.Member ORDER BY id""")


async def fetch_all_groups():
    """Fetch all groups."""
    return await self.conn.fetch("""SELECT groupid, groupname, debutdate, disbanddate, description, twitter, 
            youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company,
            website, thumbnail, banner, gender, tags FROM groupmembers.groups 
            ORDER BY groupname""")


async def fetch_aliases(object_id, group=False):
    """Fetch all global and server aliases of an idol or group.

    :param object_id: An Idol or Group id
    :param group: Whether the object is a group.
    """
    return await self.conn.fetch("SELECT alias, serverid FROM groupmembers.aliases "
                                 "WHERE objectid = $1 AND isgroup = $2", object_id, int(group))


async def fetch_members_in_group(group_id):
    """Fetches the idol ids in a group.

    :param group_id: The group's id
    """
    return await self.conn.fetch("SELECT idolid FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)