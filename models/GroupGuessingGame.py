from . import GuessingGame, User
import disnake.ext.commands
from IreneAPIWrapper.models import User, Media, Group, GROUP, Mode
from IreneAPIWrapper.exceptions import Empty


class GroupGuessingGame(GuessingGame):
    """
    A GuessingGame, but instead of guessing Persons, you guess a Group name.
    """
    def __init__(self, ctx, bot, max_rounds, timeout, gender, difficulty, is_nsfw, user: User):
        super(GroupGuessingGame, self).__init__(ctx, bot, max_rounds, timeout, gender, difficulty, is_nsfw, user)
        self._mode: Mode = GROUP
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