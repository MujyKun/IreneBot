from . import PlayerScore, Game, User
from typing import List
from IreneAPIWrapper.models import UserStatus, get_difficulty
import asyncio
import disnake


class BaseScoreGame(Game):
    """
    Is an abstract model for a game with a competition & point system
    """
    def __init__(self, ctx, bot, user, max_rounds, difficulty, gender, timeout):
        super(BaseScoreGame, self).__init__(ctx, bot, user, max_rounds)
        self.difficulty = get_difficulty(difficulty)  # easy / medium / hard
        self.gender = gender  # male / female / mixed
        self.timeout = timeout
        self.correct_answers: List[str] = []

        # default difficulty - May differ in concrete objects.
        self.easy = 0.8
        self.medium = 0.5
        self.hard = 0

    async def start(self):
        """Start a game."""
        await self._update_game_in_db()
        await self._generate_new_question()
        await self._update_game_in_db(finished=True)

    async def _generate_new_question(self):
        """Generate a new question."""

    def _get_sorted_player_scores(self) -> List[PlayerScore]:
        """
        Get the sorted player scores in descending order.

        :returns: List[:ref:`PlayerScore`]
            A list of PlayerScores.
        """
        sorted_user_ids = sorted(self.players, key=lambda user_id: (self.players[user_id]).status.score, reverse=True)
        return [self.players[user_id] for user_id in sorted_user_ids]

    async def _accredit_player(self, user_id: int):
        """
        Give a player a point.

        :param user_id: int
            The user's ID to accredit.
        """
        player_score = self.players.get(user_id)
        if not player_score:
            user = await User.get(user_id)
            disnake_user = self.bot.get_user(user_id)
            status_id = await UserStatus.insert(user_id, 0)
            status = await UserStatus.get(status_id)
            player_score = PlayerScore(user, disnake_user, status)
            self.players[user_id] = player_score

        await player_score.status.increment(by=1)

    async def _update_game_in_db(self, finished=False):
        """
        Update the game in the database.

        :param finished: bool
            Whether the game is finished.
        """

    async def _print_final_winners(self):
        """Print the final winners of the game"""
        player_scores = self._get_sorted_player_scores()
        if player_scores:
            scores = '\n'.join([f"{str(player_score)}" for player_score in player_scores])
            msg = f"The final scores are:\n\n{scores}"
        else:
            msg = "The Game has finished! No one has received a point in the Game. "
        await self.ctx.send(msg)

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """

    async def _wait_for_answer(self):
        """Wait for the correct guessing game answer."""
        def check_for_answer(message):
            """Check if a message contains the correct answer."""
            same_channel = message.channel == self.ctx.channel
            correct_answer = message.content.lower() in self.correct_answers
            return same_channel and correct_answer
        try:
            msg = await self.bot.wait_for('message', check=check_for_answer, timeout=self.timeout)
            await self._accredit_player(msg.author.id)
            await self._send_results(msg.author)
        except asyncio.TimeoutError:
            await self._send_results()
