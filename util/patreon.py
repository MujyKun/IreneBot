from Utility import resources as ex
from module.keys import bot_support_server_id, patreon_role_id, patreon_super_role_id


class Patreon:
    async def get_patreon_users(self):
        """Get the permanent patron users"""
        return await ex.conn.fetch("SELECT userid from patreon.users")

    async def get_patreon_role_members(self, super_patron=False):
        """Get the members in the patreon roles."""
        support_guild = ex.client.get_guild(int(bot_support_server_id))
        # API call will not show role.members
        if not super_patron:
            patreon_role = support_guild.get_role(int(patreon_role_id))
        else:
            patreon_role = support_guild.get_role(int(patreon_super_role_id))
        return patreon_role.members

    async def check_if_patreon(self, user_id, super_patron=False):
        """Check if the user is a patreon.
        There are two ways to check if a user ia a patreon.
        The first way is getting the members in the Patreon/Super Patreon Role.
        The second way is a table to check for permanent patreon users that are directly added by the bot owner.
        -- After modifying -> We take it straight from cache now.
        """
        if user_id in ex.cache.patrons:
            if super_patron:
                return ex.cache.patrons.get(user_id) == super_patron
            return True

    async def add_to_patreon(self, user_id):
        """Add user as a permanent patron."""
        try:
            user_id = int(user_id)
            await ex.conn.execute("INSERT INTO patreon.users(userid) VALUES($1)", user_id)
            ex.cache.patrons[user_id] = True
        except Exception as e:
            pass

    async def remove_from_patreon(self, user_id):
        """Remove user from being a permanent patron."""
        try:
            user_id = int(user_id)
            await ex.conn.execute("DELETE FROM patreon.users WHERE userid = $1", user_id)
            ex.cache.patrons.pop(user_id, None)
        except Exception as e:
            pass

    async def reset_patreon_cooldown(self, ctx):
        """Checks if the user is a patreon and resets their cooldown."""
        # Super Patrons also have the normal Patron role.
        if await self.check_if_patreon(ctx.author.id):
            ctx.command.reset_cooldown(ctx)
