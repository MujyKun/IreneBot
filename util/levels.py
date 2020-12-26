from Utility import Utility


class Levels(Utility):
    async def get_level(self, user_id, command):
        """Get the level of a command (rob/beg/daily)."""
        count = self.first_result(
            await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1 AND {command} > $2",
                                     user_id, 1))
        if not count:
            level = 1
        else:
            level = self.first_result(
                await self.conn.fetchrow(f"SELECT {command} FROM currency.Levels WHERE UserID = $1", user_id))
        return int(level)

    async def set_level(self, user_id, level, command):
        """Set the level of a user for a specific command."""
        async def update_level():
            """Updates a user's level."""
            await self.conn.execute(f"UPDATE currency.Levels SET {command} = $1 WHERE UserID = $2", level, user_id)

        count = self.first_result(await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1", user_id))
        if not count:
            await self.conn.execute("INSERT INTO currency.Levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)
            await update_level()
        else:
            await update_level()

    @staticmethod
    async def get_xp(level, command):
        """Returns money/experience needed for a certain level."""
        if command == "profile":
            return 250 * level
        return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)

    @staticmethod
    async def get_rob_percentage(level):
        """Get the percentage of being able to rob. (Every 1 is 5%)"""
        chance = int(6 + (level // 10))  # first 10 levels is 6 for 30% chance
        if chance > 16:
            chance = 16
        return chance
