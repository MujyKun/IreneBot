from Utility import resources as ex
from util import logger as log


class GuessingGame:
    async def update_user_guessing_game_score(self, difficulty, user_id, score):
        """Update a user's guessing game score."""
        try:
            user_scores = ex.cache.guessing_game_counter.get(user_id)
            # if the user does not exist, create them in the db & cache
            if not user_scores:
                await self.create_user_in_guessing_game(user_id)
                user_scores = {}  # set to default so getting current user score does not error.
            difficulty_score = user_scores.get(difficulty) or 0
            # difficulty score will always exist, no need to have a condition.
            user_scores[difficulty] = difficulty_score + score
            await self.update_user_score_in_db(difficulty, user_scores[difficulty], user_id)
        except Exception as e:
            log.console(f"{e} -> update_user_guessing_game_score")

    @staticmethod
    async def create_user_in_guessing_game(user_id):
        """Inserts a user into the guessing game db with no scores. This allows for updating scores easier."""
        ex.cache.guessing_game_counter[user_id] = {"easy": 0, "medium": 0, "hard": 0}
        return await ex.conn.execute("INSERT INTO stats.guessinggame(userid) VALUES ($1)", user_id)

    @staticmethod
    async def update_user_score_in_db(difficulty, score, user_id):
        return await ex.conn.execute(f"UPDATE stats.guessinggame SET {difficulty} = $1 WHERE userid = $2", score,
                                     user_id)

    @staticmethod
    async def get_guessing_game_top_ten(difficulty, members=None):
        """Get the top ten of a certain guessing game difficulty"""
        # make sure it is actually a difficulty in case of s_sql-injection. (condition created in case of future changes)
        if difficulty.lower() not in ex.cache.difficulty_levels:
            raise ValueError("invalid difficulty given to get_guessing_game_top_ten()")
        if members:
            return await ex.conn.fetch(f"SELECT userid, {difficulty} FROM stats.guessinggame WHERE {difficulty} "
                                       f"is not null AND userid IN {members} ORDER BY {difficulty} DESC LIMIT 10")
        return await ex.conn.fetch(f"SELECT userid, {difficulty} FROM stats.guessinggame WHERE {difficulty} "
                                   f"is not null ORDER BY {difficulty} DESC LIMIT 10")

    @staticmethod
    async def get_user_score(difficulty: str, user_id):
        user_scores = ex.cache.guessing_game_counter.get(user_id)
        if not user_scores:
            return 0
        difficulty_score = user_scores.get(difficulty) or 0
        return difficulty_score

    @staticmethod
    async def toggle_filter(user_id):
        """Enables/Disables the group filter for the guessing game on a user."""
        user = await ex.get_user(user_id)
        user.gg_filter = not user.gg_filter
        if user.gg_filter:
            await ex.conn.execute("INSERT INTO gg.filterenabled(userid) VALUES ($1)", user.id)
        else:
            await ex.conn.execute("DELETE FROM gg.filterenabled WHERE userid = $1", user.id)

    async def filter_auto_add_remove_group(self, user_or_id, group_or_id):  # can also pass in a user or group.
        """Automatically Add/Remove a group from a user's filtered group list based on the current list.

        :returns False if group was removed.
        :returns True if group was added.
        :exception ex.exceptions.InvalidParamsPassed if invalid group id."""

        # check if a user was passed in instead of a user id
        if isinstance(user_or_id, ex.u_objects.User):
            user = user_or_id
        else:
            user = await ex.get_user(user_or_id)

        # check if a group was passed in instead of a group id
        if isinstance(group_or_id, ex.u_objects.Group):
            group = group_or_id
        else:
            group = await ex.u_group_members.get_group(group_or_id)

        # raise an exception if we have an invalid group id.
        if not group:
            raise ex.exceptions.InvalidParamsPassed(f"Invalid Group ID ({group_or_id}) was passed in...")

        # add group if not already filtered.
        if group not in user.gg_groups:
            await self.filter_add_group(user, group)
            return True  # signifies that a group was added.

        # remove group if already filtered.
        else:
            await self.filter_remove_group(user, group)
            return False  # signifies that a group was removed.

    @staticmethod
    async def filter_add_group(user, group):
        """Adds a filtered group to a user."""
        user.gg_groups.append(group)
        await ex.conn.execute("INSERT INTO gg.filteredgroups(userid, groupid) VALUES($1, $2)",
                              user.id, group.id)

    @staticmethod
    async def filter_remove_group(user, group):
        """Remove a filtered group from a user."""
        user.gg_groups.remove(group)
        await ex.conn.execute("DELETE FROM gg.filteredgroups WHERE userid = $1 AND groupid = $2",
                              user.id, group.id)


ex.u_guessinggame = GuessingGame()
