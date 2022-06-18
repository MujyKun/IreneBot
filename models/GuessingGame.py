import asyncio
from typing import List, Dict, Optional, Union

import disnake.ext.commands
from IreneAPIWrapper.models import User, Affiliation, Media, Person, Group
from IreneAPIWrapper.exceptions import Empty
from dataclasses import dataclass

from random import choice

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


@dataclass
class PlayerScore:
    user: User
    disnake_user: disnake.User
    points: int = 0

    def __str__(self):
        return f"{self.disnake_user.display_name} -> {self.points}."


class GuessingGame:
    def __init__(self, ctx, bot, max_rounds, timeout, gender, difficulty, is_nsfw, user: User):
        self.ctx: disnake.ext.commands.Context = ctx
        self.host_user = user
        self.bot: Bot = bot
        self.max_rounds = max_rounds
        self.players: Dict[int, PlayerScore] = {}
        self.difficulty = difficulty  # easy / medium / hard
        self.gender = gender  # male / female / mixed
        self.rounds = 0
        self.timeout = timeout
        self.correct_answers: List[str] = []
        self.current_affiliation: Optional[Affiliation] = None
        self.current_media: Optional[Media] = None
        self.is_nsfw = is_nsfw

        self.pool: List[Media] = []

        self._complete = False

    @property
    def is_complete(self):
        return self._complete or self.rounds >= self.max_rounds

    async def start(self):
        """Start a guessing game."""
        await self._generate_new_question()

    async def _determine_filter_pool(self):
        """Determine the filtered media pool for a user."""
        person_ids = self.host_user.gg_filter_person_ids
        persons = [await Person.get(person_id) for person_id in person_ids]
        affiliations_ = []
        for person in persons:
            affiliations_ += person.affiliations

        affiliations = []
        [affiliations.append(aff) for aff in affiliations if aff not in affiliations]

        media_pool = await Media.get_all(affiliations)

        if not media_pool:
            raise Empty

        self.pool = media_pool

    async def _determine_pool(self):
        """Determine the media pool for a user."""
        aff_pool = []

        if self.host_user.gg_filter_active:
            return await self._determine_filter_pool()

        for aff in await Affiliation.get_all():
            # check gender
            if self.gender != "mixed":
                if aff.person.gender.lower() != self.gender[0]:
                    continue
            aff_pool.append(aff)

        # check difficulty
        easy = 0.8
        medium = 0.5
        hard = 0

        media_pool: List[Media] = []

        medias: List[Media] = await Media.get_all(affiliations=aff_pool)
        for media in medias:
            if media.is_nsfw and not self.is_nsfw:
                continue

            difficulty = media.difficulty
            if not difficulty:
                media_pool.append(media)
                continue

            # hard will contain easy & medium as well.
            if difficulty >= easy:
                media_pool.append(media)
                continue

            if difficulty >= medium and self.difficulty in ["hard", "medium"]:
                media_pool.append(media)
                continue

            if difficulty >= hard and self.difficulty == "hard":
                media_pool.append(media)

        if not media_pool:
            raise Empty

        self.pool = media_pool

    async def _generate_new_question(self):
        """Generate a new question for the game."""
        if not self.pool:
            try:
                await self._determine_pool()
            except Empty:
                self._complete = True
                await self.ctx.send("There is no media available for your guessing game. Try changing your selections.")
                return

        media = choice(self.pool)
        self.current_media = media
        self.current_affiliation = media.affiliation
        self.pool.remove(media)

        if not self.pool:
            self._complete = True

        await self._generate_correct_answers()
        await self.ctx.send(media.source.url)
        await self._wait_for_answer()

    async def _generate_correct_answers(self):
        possible_names = [str(self.current_affiliation.person.name).lower(), self.current_affiliation.stage_name.lower()] + \
                         await self.current_affiliation.person.get_aliases_as_strings()

        if self.current_media.affiliation.person.former_name:
            possible_names.append(str(self.current_media.affiliation.person.former_name).lower())

        possible_names_no_dupes = []
        [possible_names_no_dupes.append(name) for name in possible_names if name not in possible_names_no_dupes]

        self.correct_answers = possible_names_no_dupes

    def _get_sorted_player_scores(self) -> List[PlayerScore]:
        """
        Get the sorted player scores in descending order.

        :returns: List[:ref:`PlayerScore`]
            A list of PlayerScores.
        """
        sorted_user_ids = sorted(self.players, key=lambda user_id: (self.players[user_id]).points, reverse=True)
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
            player_score = PlayerScore(user, disnake_user)
            self.players[user_id] = player_score
        player_score.points += 1

    async def _print_final_winners(self):
        """Print the final winners of the game"""
        player_scores = self._get_sorted_player_scores()
        if player_scores:
            scores = '\n'.join([f"{str(player_score)}" for player_score in player_scores])
            msg = f"The final scores are:\n\n{scores}"
        else:
            msg = "The Guessing Game has finished! No one has received a point in the Guessing Game. "
        await self.ctx.send(msg)

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """
        await self.current_media.upsert_guesses(correct=bool(winner))

        win_msg = "No one guessed correctly." if not winner else f"{winner.display_name} won the round."
        correct_answer_msg = f"The correct answer was {self.current_affiliation.stage_name} from " \
                             f"{self.current_affiliation.group.name}"
        possible_answer_msg = f"Possible answers: {self.correct_answers}"
        result_message = win_msg + "\n" + correct_answer_msg + "\n" + possible_answer_msg
        await self.ctx.send(result_message)

        if self.rounds < self.max_rounds and not self._complete:
            await self._generate_new_question()
        else:
            await self._print_final_winners()
            self._complete = True

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


class GroupGuessingGame(GuessingGame):
    """
    A GuessingGame, but instead of guessing Persons, you guess a Group name.
    """
    def __init__(self, ctx, bot, max_rounds, timeout, gender, difficulty, is_nsfw, user: User):
        super(GroupGuessingGame, self).__init__(ctx, bot, max_rounds, timeout, gender, difficulty, is_nsfw, user)
        ...

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """
        await self.current_media.upsert_guesses(correct=bool(winner))

        win_msg = "No one guessed correctly." if not winner else f"{winner.display_name} won the round."
        correct_answer_msg = f"The correct answer was {self.current_affiliation.group.name}."
        possible_answer_msg = f"Possible answers: {self.correct_answers}"
        result_message = win_msg + "\n" + correct_answer_msg + "\n" + possible_answer_msg
        await self.ctx.send(result_message)

        if self.rounds < self.max_rounds and not self._complete:
            await self._generate_new_question()
        else:
            await self._print_final_winners()
            self._complete = True

    async def _generate_correct_answers(self):
        possible_names = [str(self.current_affiliation.group.name)] + \
                         await self.current_affiliation.group.get_aliases_as_strings()

        possible_names_no_dupes = []
        [possible_names_no_dupes.append(name.lower()) for name in possible_names if name.lower()
            not in possible_names_no_dupes]

        self.correct_answers = possible_names_no_dupes

    async def _determine_filter_pool(self):
        """Determine the filtered media pool for a user."""
        group_ids = self.host_user.gg_filter_group_ids
        groups = [await Group.get(group_id) for group_id in group_ids]
        affiliations_ = []
        for group in groups:
            affiliations_ += group.affiliations

        affiliations = []
        [affiliations.append(aff) for aff in affiliations if aff not in affiliations]

        media_pool = await Media.get_all(affiliations)

        if not media_pool:
            raise Empty

        self.pool = media_pool
