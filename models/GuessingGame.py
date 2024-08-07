import datetime
from typing import List, Optional, Union

import disnake.ext.commands
from IreneAPIWrapper.models import (
    User,
    Affiliation,
    Media,
    Person,
    GuessingGame as GuessingGameModel,
)
from IreneAPIWrapper.exceptions import Empty

from random import sample
from . import BaseScoreGame


class GuessingGame(BaseScoreGame):
    def __init__(
        self,
        bot,
        max_rounds,
        timeout,
        gender,
        difficulty,
        is_nsfw,
        user: User,
        ctx=None,
        inter=None,
    ):
        super(GuessingGame, self).__init__(
            bot, user, max_rounds, difficulty, gender, timeout, ctx=ctx, inter=inter
        )
        self.current_affiliation: Optional[Affiliation] = None
        self.current_media: Optional[Media] = None
        self.is_nsfw = is_nsfw
        self.__played_media_ids: List[int] = []
        self.__gg: Optional[GuessingGameModel] = None

        self.pool: List[Media] = []

    async def _determine_filter_pool(self):
        """Determine the filtered media pool for a user."""
        person_ids = self.host_user.gg_filter_person_ids
        persons = [await Person.get(person_id) for person_id in person_ids]

        affiliations_ = set()

        for person in persons:
            affiliations_.update(person.affiliations)

        affiliations = list(affiliations_)

        media_pool = await Media.get_all(affiliations, limit=1000)

        if not media_pool:
            raise Empty

        self.pool = media_pool

    async def _determine_pool(
        self,
    ):
        """Determine the media pool for a user."""
        aff_pool = []

        if self.host_user.gg_filter_active:
            return await self._determine_filter_pool()

        _affs = await Affiliation.get_all()

        for aff in _affs:
            # check gender
            if self.gender != "mixed":
                if aff.person.gender.lower() != self.gender[0]:
                    continue
            aff_pool.append(aff)

        media_pool: List[Media] = []
        medias: List[Media] = await Media.get_all(affiliations=aff_pool, limit=1000)

        for media in medias:
            if (media.is_nsfw and not self.is_nsfw) and media.faces > 2:
                continue

            difficulty = media.difficulty

            # hard will contain easy & medium as well.
            if not difficulty or (difficulty >= self.easy) or (
                    difficulty >= self.medium and self.difficulty.name in ["hard", "medium"]) or (
                    difficulty >= self.hard and self.difficulty.name == "hard"):
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
                return await self.send_message(key="no_media_results")
        self.rounds += 1

        media = sample(self.pool, 1)[0]
        self.current_media = media
        self.current_affiliation = media.affiliation
        self.__played_media_ids.append(media.id)
        self.pool.remove(media)

        if not self.pool:
            self._complete = True

        await self._generate_correct_answers()
        media_url = await media.fetch_image_host_url()
        await self.send_message(msg=media_url, delete_after=self.timeout + 3)
        await self._wait_for_answer()

    async def _generate_correct_answers(self):
        possible_names = [
            str(self.current_affiliation.person.name).lower(),
            self.current_affiliation.stage_name.lower(),
        ] + await self.current_affiliation.person.get_aliases_as_strings()

        if self.current_media.affiliation.person.former_name:
            possible_names.append(
                str(self.current_media.affiliation.person.former_name).lower()
            )

        self.correct_answers = list(set(possible_names))  # remove dupes

    async def _send_results(self, winner: disnake.User = None):
        """Send the results of a round and continue/finish the game.

        :param winner: Optional[:ref:`disnake.User`]
            The winner of the round if there is one.
        """
        await self.current_media.upsert_guesses(correct=bool(winner))

        win_msg = (
            await self.get_message("incorrect_answer_gg")
            if not winner
            else await self.get_message("winner_gg_msg", f"{winner.display_name}")
        )
        correct_answer_msg = await self.get_message(
            "correct_answer_gg",
            f"{self.current_affiliation.stage_name}",
            f"{self.current_affiliation.group.name}",
        )
        possible_answer_msg = await self.get_message(
            "all_answers_gg", f"{self.correct_answers}"
        )
        result_message = (
            win_msg + "\n" + correct_answer_msg + "\n" + possible_answer_msg
        )
        await self.send_message(msg=result_message, delete_after=self.timeout + 3)

        if not self.is_complete:
            await self._generate_new_question()
        else:
            await self._print_final_winners()
            self._complete = True

    async def _update_game_in_db(self, finished=False, media_and_status=True):
        """
        Update the game in the database.

        :param finished: bool
            Whether the game is finished.
        :param media_and_status: bool
            Whether to update the media and status IDs to the database.
        """
        if not self.__gg:
            gg_id = await GuessingGameModel.insert(
                start_date=datetime.datetime.utcnow(),
                media_ids=self.__played_media_ids,
                status_ids=[],
                mode_id=self._mode.id,
                difficulty_id=self.difficulty.id,
                is_nsfw=self.is_nsfw,
            )
            self.__gg = await GuessingGameModel.get(gg_id)

        if media_and_status and self.__gg:
            status_ids = [player.status.id for player in self.players.values()]
            media_ids = self.__played_media_ids
            await self.__gg.update_media_and_status(media_ids, status_ids)

        if finished:
            self.end_time = datetime.datetime.utcnow()
            await self.__gg.update_end_date(end_time=self.end_time)
