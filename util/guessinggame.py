from Utility import resources as ex
from module import logger as log


class GuessingGame:
    async def update_user_guessing_game_score(self, difficulty, user_id, score):
        """Update a user's guessing game score."""
        try:
            difficulty_as_string = await self.convert_difficulty_to_string(difficulty)
            user_scores = ex.cache.guessing_game_counter.get(user_id)
            # if the user does not exist, create them in the db
            if not user_scores:
                await self.create_user_in_guessing_game_db(user_id)
                user_scores = {}  # set to default so getting current user score does not error.
            difficulty_score = user_scores.get(difficulty_as_string) or 0
            # difficulty score will always exist, no need to have a condition.
            user_scores[difficulty_as_string] = difficulty_score + score
            await self.update_user_score_in_db(difficulty_as_string, difficulty_score, user_id)
        except Exception as e:
            log.console(f"{e} -> update_user_guessing_game_score")

    @staticmethod
    async def convert_difficulty_to_string(difficulty_level: int):
        return ex.cache.difficulty_levels[difficulty_level - 1]

    @staticmethod
    async def create_user_in_guessing_game_db(user_id):
        """Inserts a user into the guessing game db with no scores. This allows for updating scores easier."""
        return await ex.conn.execute("INSERT INTO stats.guessinggame(userid) VALUES ($1)", user_id)

    @staticmethod
    async def update_user_score_in_db(difficulty, score, user_id):
        return await ex.conn.execute(f"UPDATE stats.guessinggame SET {difficulty} = $1 WHERE userid = $2", score,
                                     user_id)

    @staticmethod
    async def get_guessing_game_top_ten(difficulty, members=None):
        """Get the top ten of a certain guessing game difficulty"""
        # make sure it is actually a difficulty in case of sql-injection. (condition created in case of future changes)
        if difficulty.lower() in ex.cache.difficulty_levels:
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
