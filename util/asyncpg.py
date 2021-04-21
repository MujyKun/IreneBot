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

    async def get_profile_xp(self, user_id: int):
        return (await self.conn.fetchrow("SELECT profilexp FROM currency.levels WHERE userid = $1", user_id))[0]

    async def check_twitch_already_posted(self, twitch_username, channel_id) -> bool:
        return ((await self.conn.fetchrow("SELECT COUNT(*) FROM twitch.alreadyposted WHERE username = $1 AND "
                                          "channelid = $2", twitch_username, channel_id))[0]) >= 1

    async def set_twitch_posted(self, twitch_username, channel_id):
        await self.conn.execute("INSERT INTO twitch.alreadyposted(username, channelid) VALUES ($1, $2)",
                                twitch_username, channel_id)

    async def delete_twitch_posted(self, twitch_username):
        await self.conn.execute("DELETE FROM twitch.alreadyposted WHERE username = $1", twitch_username)

    async def fetch_languages(self):
        return await self.conn.fetch("SELECT userid, language FROM general.languages")

    async def fetch_levels(self):
        return await self.conn.fetch("SELECT userid, rob, daily, beg, profile FROM currency.levels")

    async def fetch_currency(self):
        return await self.conn.fetch("SELECT userid, money FROM currency.currency")

    async def fetch_filter_enabled(self):
        return await self.conn.fetch("SELECT userid from gg.filterenabled")

    async def fetch_filtered_groups(self):
        return await self.conn.fetch("SELECT userid, groupid FROM gg.filteredgroups")

    async def fetch_twitch_guilds(self):
        return await self.conn.fetch("SELECT guildid, channelid, roleid FROM twitch.guilds")

    async def fetch_twitch_notifications(self):
        return await self.conn.fetch("SELECT username, guildid FROM twitch.channels")

    async def fetch_gg_stats(self):
        return await self.conn.fetch("SELECT userid, easy, medium, hard FROM stats.guessinggame")

    async def fetch_reminders(self):
        return await self.conn.fetch("SELECT id, userid, reason, timestamp FROM reminders.reminders")

    async def fetch_timezones(self):
        return await self.conn.fetch("SELECT userid, timezone FROM reminders.timezones")

    async def fetch_all_self_assign_roles(self):
        return await self.conn.fetch("SELECT roleid, rolename, serverid FROM selfassignroles.roles")

    async def fetch_all_self_assign_channels(self):
        return await self.conn.fetch("SELECT channelid, serverid FROM selfassignroles.channels")

    async def fetch_weverse(self):
        return await self.conn.fetch("SELECT channelid, communityname, roleid, commentsdisabled FROM weverse.channels")

    async def fetch_command(self, session_id):
        return await self.conn.fetch("SELECT commandname, count FROM stats.commands WHERE sessionid = $1", session_id)

    async def fetch_session_usage(self, date):
        return await self.conn.fetchrow("SELECT session FROM stats.sessions WHERE date = $1", date)

    async def fetch_restricted_channels(self):
        return await self.conn.fetch("SELECT channelid, serverid, sendhere FROM groupmembers.restricted")

    async def fetch_custom_commands(self):
        return await self.conn.fetch("SELECT serverid, commandname, message FROM general.customcommands")

    async def fetch_bot_statuses(self):
        return await self.conn.fetch("SELECT status FROM general.botstatus")

    async def fetch_dead_links(self):
        return await self.conn.fetch("SELECT deadlink, userid, messageid, idolid, guessinggame FROM "
                                     "groupmembers.deadlinkfromuser")

    async def fetch_all_idols(self):
        return await self.conn.fetch("""SELECT id, fullname, stagename, formerfullname, formerstagename, birthdate,
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify,
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags, difficulty
            FROM groupmembers.Member ORDER BY id""")

    async def fetch_all_groups(self):
        return await self.conn.fetch("""SELECT groupid, groupname, debutdate, disbanddate, description, twitter, 
            youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company,
            website, thumbnail, banner, gender, tags FROM groupmembers.groups 
            ORDER BY groupname""")

    async def fetch_aliases(self, object_id, group=False):
        return await self.conn.fetch("SELECT alias, serverid FROM groupmembers.aliases "
                                     "WHERE objectid = $1 AND isgroup = $2", object_id, int(group))

    async def fetch_members_in_group(self, group_id):
        return await self.conn.fetch("SELECT idolid FROM groupmembers.idoltogroup WHERE groupid = $1", group_id)

    async def fetch_total_session_usage(self):
        return await self.conn.fetchrow("SELECT totalused FROM stats.sessions ORDER BY totalused DESC")

    async def add_new_session(self, total_used, session_commands, date):
        await self.conn.execute("INSERT INTO stats.sessions(totalused, session, date) VALUES ($1, $2, $3)",
                                total_used, session_commands, date)

    async def fetch_session_id(self, date):
        return await self.conn.fetchrow("SELECT sessionid FROM stats.sessions WHERE date = $1", date)

    async def fetch_n_word(self):
        return await self.conn.fetch("SELECT userid, nword FROM general.nword")

    async def fetch_temp_channels(self):
        return await self.conn.fetch("SELECT chanid, delay FROM general.tempchannels")

    async def fetch_welcome_messages(self):
        return await self.conn.fetch("SELECT channelid, serverid, message, enabled FROM general.welcome")

    async def fetch_server_prefixes(self):
        return await self.conn.fetch("SELECT serverid, prefix FROM general.serverprefix")

    async def fetch_logged_servers(self):
        return await self.conn.fetch("SELECT id, serverid, channelid, sendall FROM logging.servers WHERE "
                                     "status = $1", 1)

    async def fetch_logged_channels(self, primay_key):
        return await self.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1", primay_key)

    async def fetch_bot_bans(self):
        return await self.conn.fetch("SELECT userid FROM general.blacklisted")

    async def fetch_mod_mail(self):
        return await self.conn.fetch("SELECT userid, channelid FROM general.modmail")

    async def fetch_cached_patrons(self):
        return await self.conn.fetch("SELECT userid, super FROM patreon.cache")

    async def delete_patron(self, user_id):
        await self.conn.execute("DELETE FROM patreon.cache WHERE userid = $1", user_id)

    async def update_patron(self, user_id, super_patron: int):
        await self.conn.execute("UPDATE patreon.cache SET super = $1 WHERE userid = $2", super_patron, user_id)

    async def add_patron(self, user_id, super_patron: int):
        await self.conn.execute("INSERT INTO patreon.cache(userid, super) VALUES($1, $2)", user_id, super_patron)
