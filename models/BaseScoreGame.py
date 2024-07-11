from . import PlayerScore, Game, User, BaseRoundGame
from typing import List, Optional
from IreneAPIWrapper.models import UserStatus, get_difficulty, Mode, NORMAL
import asyncio
import disnake


class BaseScoreGame(BaseRoundGame):
    """
    Is an abstract model for a game with a competition & point system
    """

    def __init__(
        self, bot, user, max_rounds, difficulty, gender, timeout, ctx=None, inter=None
    ):
        super(BaseScoreGame, self).__init__(bot, user, max_rounds, ctx=ctx, inter=inter)
        self.difficulty = get_difficulty(difficulty)  # easy / medium / hard
        self.gender = gender  # male / female / mixed
        self.timeout = timeout
        self.correct_answers: List[str] = []
        self._mode: Mode = NORMAL
        self._end_keywords = ["stop", "end"]
        self._skip_keywords = ["skip"]

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
        sorted_user_ids = sorted(
            self.players,
            key=lambda user_id: (self.players[user_id]).status.score,
            reverse=True,
        )
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
            scores = "\n".join(
                [f"{str(player_score)}" for player_score in player_scores]
            )
            msg = await self.get_message("final_scores_games", scores)
        else:
            msg = await self.get_message("game_finished_no_scores")
        await self.send_message(msg=msg)

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """

    async def _wait_for_answer(self):
        """Wait for the correct guessing game answer."""

        def check_for_answer(message):
            """Check if a message contains the correct answer."""
            context = self.ctx if self.ctx else self.inter
            same_channel = message.channel == context.channel
            correct_answer = message.content.lower() in self.correct_answers + self._skip_keywords + self._end_keywords
            return same_channel and correct_answer

        try:
            msg = await self.bot.wait_for(
                "message", check=check_for_answer, timeout=self.timeout
            )
            await msg.add_reaction("👍")
            if msg.content.lower() in self._skip_keywords:
                return await self._send_results()
            elif msg.content.lower() in self._end_keywords:
                self.rounds = self.max_rounds + 1
                return await self._send_results()
            else:
                await self._accredit_player(msg.author.id)
                return await self._send_results(msg.author)
        except asyncio.TimeoutError:
            await self._send_results()
