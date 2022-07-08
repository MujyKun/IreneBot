import asyncio
import random
from typing import List, Dict, Optional, Union

import disnake.ext.commands
from IreneAPIWrapper.models import User, Affiliation, Media, Person, Group
from IreneAPIWrapper.exceptions import Empty

from random import choice
from . import PlayerScore, BaseScoreGame

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


class UnscrambleGame(BaseScoreGame):
    def __init__(self, ctx, bot, max_rounds, timeout, gender, difficulty, user: User):
        super(UnscrambleGame, self).__init__(ctx, bot, user, max_rounds, difficulty, gender, timeout)
        self.current_question: Optional[str] = None  # scrambled
        self.current_affiliation: Optional[Affiliation] = None

        self.pool: List[Affiliation] = []
        self.__pool_was_set = False  # confirm if we've already set the initial pool.

    async def _generate_new_question(self):
        if not self.pool:
            try:
                await self._determine_pool()
            except Empty:
                self._complete = True
                await self.ctx.send("There are no available affiliations for your unscramble game.")
                if self.players:
                    await self._print_final_winners()
                return
        aff = choice(self.pool)
        self.current_affiliation = aff
        self.pool.remove(aff)  # an affiliation will only be used once.
        try:
            await self._generate_correct_answers()
        except Empty:
            return await self._generate_new_question()  # recursion until we run out of questions.

        await self.ctx.send(f"The name I want you to unscramble is {self.current_question}.")
        await self._wait_for_answer()

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """
        win_msg = "No one guessed correctly." if not winner else f"{winner.display_name} won the round."
        correct_answer_msg = f"The correct answer was {self.correct_answers[0]}."
        result_message = win_msg + "\n" + correct_answer_msg
        await self.ctx.send(result_message)

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
                possible_questions.append(str(self.current_affiliation.person.former_name))
            if self.current_affiliation.person.aliases:
                possible_questions += [alias.name for alias in self.current_affiliation.person.aliases]

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

    async def _update_game_in_db(self):
        ...
