from typing import Literal

from disnake import AppCmdInter
from disnake.ext import commands
from models import Bot, GuessingGame, GroupGuessingGame
from cogs.groupmembers import helper as gm_helper
from IreneAPIWrapper.models import User, Group, Person


# TODO:
# When accrediting a user, upsert to the database.
# When a game finishes, make an update to the stats in the database.

class GuessingGameCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(name="guessinggame", description="Play a guessing game with Persons.")
    async def guessinggame(self, inter: AppCmdInter,
                           max_rounds: commands.Range[3, 60] = 20,
                           timeout: commands.Range[5, 60] = 20,
                           gender: Literal["male", "female", "mixed"] = "mixed",
                           difficulty: Literal["easy", "medium", "hard"] = "medium",
                           contains_nsfw: Literal["Yes", "No"] = "No"):
        """Plays a guessing game."""

        contains_nsfw = True if contains_nsfw == "Yes" else False
        user = await User.get(inter.user.id)
        gg = GuessingGame(inter, self.bot, max_rounds, timeout, gender, difficulty, contains_nsfw, user=user)

        await inter.send("Starting guessing game")
        await gg.start()

    @commands.slash_command(name="groupguessinggame", description="Play a guessing game with Groups.")
    async def groupguessinggame(self, inter: AppCmdInter,
                           max_rounds: commands.Range[3, 60] = 20,
                           timeout: commands.Range[5, 60] = 20,
                           gender: Literal["male", "female", "mixed"] = "mixed",
                           difficulty: Literal["easy", "medium", "hard"] = "medium",
                           contains_nsfw: Literal["Yes", "No"] = "No"):
        """Plays a group guessing game."""

        contains_nsfw = True if contains_nsfw == "Yes" else False
        user = await User.get(inter.user.id)

        gg = GroupGuessingGame(inter, self.bot, max_rounds, timeout, gender, difficulty, contains_nsfw, user=user)

        await inter.send("Starting group guessing game")
        await gg.start()

    @commands.slash_command(name="toggleggfilter", description="Toggle the filter for guessing game.")
    async def toggleggfilter(self, inter: AppCmdInter):
        """Toggle the GG Filter."""
        user = await User.get(inter.user.id)
        await user.toggle_gg_filter()
        await inter.send(f"Your guessing game filter (including groups) is now {'enabled' if user.gg_filter_active else 'disabled'}.")

    @commands.slash_command(name="ggfilter", description="Filter the guessing game.")
    async def ggfilter(self, inter: AppCmdInter, selection: str = commands.Param(autocomplete=gm_helper.auto_complete_person)):
        user = await User.get(inter.user.id)
        person_id = int(selection.split(')')[0])
        if not user.gg_filter_person_ids and not user.gg_filter_active:
            await self.toggleggfilter.invoke(inter)

        if person_id not in user.gg_filter_person_ids:
            user.gg_filter_person_ids.append(person_id)
        else:
            user.gg_filter_person_ids.remove(person_id)

        await user.upsert_filter_persons(tuple(user.gg_filter_person_ids))
        inter.item_type = "person"
        await self.view_gg_filter.invoke(inter)

    @commands.slash_command(name="gggfilter", description="Filter the group guessing game.")
    async def gggfilter(self, inter: AppCmdInter, selection: str = commands.Param(autocomplete=gm_helper.auto_complete_group)):
        user = await User.get(inter.user.id)
        group_id = int(selection.split(')')[0])
        if not user.gg_filter_group_ids and not user.gg_filter_active:
            await self.toggleggfilter.invoke(inter)

        if group_id not in user.gg_filter_group_ids:
            user.gg_filter_group_ids.append(group_id)
        else:
            user.gg_filter_group_ids.remove(group_id)

        await user.upsert_filter_groups(tuple(user.gg_filter_group_ids))
        inter.item_type = "group"
        await self.view_gg_filter.invoke(inter)

    @commands.slash_command(name="viewggfilter", description="View the GG Filter for Persons and Groups.")
    async def view_gg_filter(self, inter, item_type: Literal["person", "group"] = None):
        """View the GG filter for Persons and Groups."""
        if not item_type:
            item_type = "person" if not hasattr(inter, "item_type") else inter.item_type

        user = await User.get(inter.user.id)
        if item_type == "person":
            objects = [await Person.get(person_id) for person_id in user.gg_filter_person_ids]
            names = "\n".join([f"{person.id}) {str(person.name)}" for person in objects])
        elif item_type == "group":
            objects = [await Group.get(group_id) for group_id in user.gg_filter_group_ids]
            names = "\n".join([f"{group.id}) {group.name}" for group in objects])
        else:
            raise NotImplementedError("Item type aside from Person & Group is not supported.")
        await inter.send(f"Your GG Filter for {item_type} is now:\n{names if names else 'Empty.'}")


def setup(bot: Bot):
    bot.add_cog(GuessingGameCog(bot))
