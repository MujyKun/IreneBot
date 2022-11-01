import random
from datetime import datetime
from typing import List, Optional

import disnake.ext.commands
from IreneAPIWrapper.models import (
    User,
    Affiliation,
    Date,
    UnscrambleGame as UnscrambleGameModel,
)
from IreneAPIWrapper.exceptions import Empty

from random import choice
from . import BaseScoreGame

from typing import TYPE_CHECKING


class UnscrambleGame(BaseScoreGame):
    def __init__(
        self,
        bot,
        max_rounds,
        timeout,
        gender,
        difficulty,
        user: User,
        ctx=None,
        inter=None,
    ):
        super(UnscrambleGame, self).__init__(
            bot, user, max_rounds, difficulty, gender, timeout, ctx=ctx, inter=inter
        )
        self.current_question: Optional[str] = None  # scrambled
        self.current_affiliation: Optional[Affiliation] = None
        self.__us: Optional[UnscrambleGameModel] = None

        self.pool: List[Affiliation] = []
        self.__pool_was_set = False  # confirm if we've already set the initial pool.

    async def _generate_new_question(self):
        if not self.pool:
            try:
                await self._determine_pool()
            except Empty:
                self._complete = True
                await self.send_message(key="no_aff_results")
                if self.players:
                    await self._print_final_winners()
                return
        aff = choice(self.pool)
        self.current_affiliation = aff
        self.pool.remove(aff)  # an affiliation will only be used once.
        try:
            await self._generate_correct_answers()
        except Empty:
            return (
                await self._generate_new_question()
            )  # recursion until we run out of questions.

        await self.send_message(self.current_question, key="us_question", delete_after=self.timeout + 3)
        await self._wait_for_answer()

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """
        win_msg = (
            await self.get_message("incorrect_answer_gg")
            if not winner
            else await self.get_message("winner_gg_msg", f"{winner.display_name}")
        )

        correct_answer_msg = await self.get_message(
            "correct_answer_ggg", f"{self.correct_answers[0]}"
        )

        result_message = win_msg + "\n" + correct_answer_msg
        await self.send_message(msg=result_message, delete_after=self.timeout + 3)

        if not self.is_complete:
            await self._generate_new_question()
        else:
            await self._print_final_winners()
            self._complete = True

    async def _determine_pool(self):
        """Determine the pool for a user."""
        # Difficulty determines the type of questions that are given.
        # Therefore, we can add all Affiliations to the pool.
        if not self.__pool_was_set:
            self.pool = list(await Affiliation.get_all())
            self.__pool_was_set = True
        else:
            raise Empty

    async def _generate_correct_answers(self):
        # applies to all difficulties
        possible_questions = [self.current_affiliation.stage_name]

        if self.difficulty != "easy":
            possible_questions.append(self.current_affiliation.group.name)
            possible_questions.append(str(self.current_affiliation.person.name))

        if self.difficulty == "hard":
            if self.current_affiliation.person.former_name:
                possible_questions.append(
                    str(self.current_affiliation.person.former_name)
                )
            if self.current_affiliation.person.aliases:
                possible_questions += [
                    alias.name for alias in self.current_affiliation.person.aliases
                ]

        if not possible_questions:
            raise Empty

        question = choice(possible_questions)
        # we represent the unscrambled word as a list due to parent BaseScoreGame functionality
        self.correct_answers = [question.lower()]

        scrambled_words = []
        word_list = question.split()
        random.shuffle(word_list)
        for word in word_list:
            char_list = [char for char in word]  # put the characters into a list
            random.shuffle(char_list)
            scrambled_words.append("".join(char_list))

        scrambled_word = " ".join(scrambled_words)

        if self.difficulty == "hard":
            scrambled_word = scrambled_word.lower()

        self.current_question = scrambled_word

        if not self.current_question:
            raise Empty

    async def _update_game_in_db(self, finished=False, status=True):
        """
        Update the game in the database.

        :param finished: bool
            Whether the game is finished.
        :param status: bool
            Whether to update the status IDs to the database.
        """
        if not self._date or not self.__us:
            date_id = await Date.insert(self.start_time, self.end_time)
            self._date = await Date.get(date_id)

            us_id = await UnscrambleGameModel.insert(
                date_id=date_id,
                status_ids=[],
                mode_id=self._mode.id,
                difficulty_id=self.difficulty.id,
            )
            self.__us = await UnscrambleGameModel.get(us_id)

        if status and self.__us:
            status_ids = [player.status.id for player in self.players.values()]
            await self.__us.update_status(status_ids)

        if finished:
            self.end_time = datetime.now()

            if self._date:
                await self._date.update_end_date(end_date=self.end_time)
