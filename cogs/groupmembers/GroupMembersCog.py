import random
import disnake
from disnake.ext import commands
from models import Bot
from IreneAPIWrapper.models import Media, Person, Group, AbstractModel
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal, List, Union, Dict, Tuple, Optional


class GroupMembersCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.invalid_selection = "item_type returned something other than 'person' or 'group'"

    @commands.slash_command(
        description="Display a profile card for either a Person or a Group.")
    async def card(self, inter: AppCmdInter, item_type: Literal["person", "group"],
                   selection: str = commands.Param(autocomplete=helper.auto_complete_type)):
        """Display a profile card for either a Person or a Group."""
        object_id = int(selection.split(')')[0])
        if item_type == "person":
            person = await Person.get(object_id)
            await inter.send(str(person.name))
        elif item_type == "group":
            group = await Group.get(object_id)
            await inter.send(str(group.name))
        else:
            raise RuntimeError(self.invalid_selection)

    @commands.slash_command(name="call", description="Call Media for an Idol/Group.")
    async def call_person_or_group(self, inter: AppCmdInter, item_type: Literal["person", "group"],
                                   selection: str = commands.Param(autocomplete=helper.auto_complete_type)):
        """Display the media for a specific Person or Group."""
        object_id = int(selection.split(')')[0])
        if item_type == "person":
            person = await Person.get(object_id)
            medias: List[Media] = await Media.get_all(person.affiliations)
        elif item_type == "group":
            group = await Group.get(object_id)
            medias: List[Media] = await Media.get_all(group.affiliations)
        else:
            raise RuntimeError(self.invalid_selection)
        await inter.send((random.choice(medias)).source.url)

    @commands.slash_command(name="randomperson", description="Display random media for a random Person.")
    async def random_person(self, inter: AppCmdInter):
        """Send a photo of a random person."""
        media: Media = random.choice(list(await Media.get_all()))
        await inter.send(media.source.url)

    @commands.slash_command(name="count", description="Get count for the media a person or group has.")
    async def count(self, inter: AppCmdInter, item_type: Literal["person", "group"],
                    selection: str = commands.Param(autocomplete=helper.auto_complete_type)):
        object_id = int(selection.split(')')[0])
        if item_type == "person":
            person = await Person.get(object_id)
            medias: List[Media] = await Media.get_all(person.affiliations)
        elif item_type == "group":
            group = await Group.get(object_id)
            medias: List[Media] = await Media.get_all()
        else:
            raise NotImplementedError(f"An entity aside from a person or object has not been implemented. {item_type}")
        await inter.send(f"{len(medias)}")

    @commands.slash_command(name="aliases", description="Get the aliases of persons or groups.")
    async def aliases(self, inter: AppCmdInter, name):
        name = name.lower()
        persons = await self.search_for_obj_by_alias(name)
        groups = await self.search_for_obj_by_alias(name, False)

        persons_aliases = []
        for person in persons:
            aliases_as_strings = await person.get_aliases_as_strings()
            if not aliases_as_strings:
                continue
            persons_aliases.append(f"{str(person.name)} [{person.id}] - {' | '.join(aliases_as_strings)}")

        groups_aliases = []
        for group in groups:
            aliases_as_strings = await group.get_aliases_as_strings()
            if not aliases_as_strings:
                continue
            groups_aliases.append(f"{group.name} [{group.id}] - {' | '.join(aliases_as_strings)}")
        persons_aliases_as_str = '\n'.join(persons_aliases)
        groups_aliases_as_str = '\n'.join(groups_aliases)

        description = f"**Person(s):**\n{persons_aliases_as_str}\n\n" if persons_aliases else ''
        description += f"**Group(s):**\n{groups_aliases_as_str}" if groups_aliases else ''
        description = description if description else "**No Results.**"

        embed = disnake.Embed(title=f"Aliases for {name}", color=self.get_random_color(), description=description)
        await inter.send(embed=embed)

    @commands.slash_command(name="distance", description="Get the Levenshtein Distance of two words.")
    async def distance(self, inter: AppCmdInter, search_word: str, target_word: str):
        if len(search_word) * len(target_word) > 2000000:
            return await inter.send("You cannot compare words of that length.")

        await inter.send(f"The search word has **{self.levenshtein_distance(search_word, target_word) * 100:.2f}%** "
                         f"similarity with the target word.")

    @commands.slash_command(name="countleaderboard",
                            description="Shows leaderboards for how many times a Person or Group has been called.",
                            aliases=['clb', 'cb', 'highestcount'])
    async def countleaderboard(self, inter: AppCmdInter, item_type: Literal["Persons", "Groups"]):
        if item_type == "Persons":
            objects = await Person.get_all()
        elif item_type == "Groups":
            objects = await Group.get_all()
        else:
            raise NotImplementedError(f"An entity aside from a person or object has not been implemented. {item_type}")
        leaderboard = await self.get_leaderboard(objects)

        embed = disnake.Embed(title=f"{item_type} Leaderboard", color=self.get_random_color(), description=leaderboard)

    async def get_leaderboard(self, objects: Union[List[Person], List[Group]]) -> Optional[
        List[Tuple[AbstractModel, int]]]:
        if not objects:
            return None
        objects = list(objects)

        if isinstance(objects[0], Person):
            objects.sort(key=lambda x: x.call_count)
            person_called_amounts_final = []
            for obj in objects:
                person_called_amounts_final.append((obj, obj.call_count))
            return person_called_amounts_final

        elif isinstance(objects[0], Group):
            group_called_amounts = {}
            group_called_amounts_final = []
            for obj in objects:
                persons = [affiliation.person for affiliation in obj.affiliations]
                group_called_amounts[obj] = sum(person.call_count for person in persons)
            group_called_amounts_sorted = sorted(group_called_amounts, key=lambda x: group_called_amounts[x])
            for obj in group_called_amounts_sorted:
                group_called_amounts_final.append((obj, group_called_amounts[obj]))
            return group_called_amounts_final
        else:
            raise NotImplementedError(f"An entity aside from a person or object has not been implemented.")

    async def search_for_obj_by_alias(self, search_name, persons=True) -> Union[List[Person], List[Group]]:
        """
        Check if a name matches with an alias or a Person/Group's full name.

        :param search_name: str
            The name to search for.
        :param persons: bool
            Whether to search for Persons [Otherwise will search for Groups]

        :returns: Union[List[:ref:`Person`], List[:ref:`Group`]]
            A list of persons or groups that match the search filter.
        """
        if persons:
            persons: List[Person] = await Person.get_all()
            filtered = [item for item in persons if await self._filter_by_name(item, search_name)]
        else:
            groups: List[Group] = await Group.get_all()
            filtered = [item for item in groups if await self._filter_by_name(item, search_name)]
        return filtered

    async def _filter_by_name(self, obj: Union[Person, Group], name: str):
        """
        Uses levenshtein distance against person/group aliases.
        Any aliases/names with an 80% or greater similarity will count as a result.

        :returns: bool
            Whether the Person or Group object is included in the filter.

        """
        aliases = await obj.get_aliases_as_strings()
        name = name.lower()

        if any([self.levenshtein_distance(name, alias.lower()) >= 0.8 for alias in aliases]):
            return True

        if self.levenshtein_distance(name, str(obj).lower()) >= 0.8:
            return True

        return False

    def get_random_color(self):
        """Retrieves a random hex color."""
        r = lambda: random.randint(0, 255)
        return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present

    def levenshtein_distance(self, search_word: str, target_word: str) -> float:
        """
        Compute levenshtein's distance and get the percentage back.

        :param search_word: str
            The word being searched for.
        :param target_word: str
            The target word to compare to.

        :returns: float
            How similar the words are to each other (Ratio from 0 to 1 where 1 is 100% similarity)
        """
        import time
        start = time.time()
        edits: Dict[Tuple[int, int], int] = {}
        max_i = len(search_word)
        max_j = len(target_word)

        if not max_i or not max_j:  # if any of the words are blank strings
            return 0

        for j in range(0, max_j + 1):
            edits[(0, j)] = j

        for i in range(0, max_i + 1):
            edits[(i, 0)] = i

        for i, i_char in enumerate(search_word, start=1):
            for j, j_char in enumerate(target_word, start=1):
                if i_char == j_char:
                    edit_cost = 0

                else:
                    edit_cost = 1
                edits[(i, j)] = min(edits[(i - 1, j)] + 1,
                                    edits[(i, j - 1)] + 1,
                                    edits[(i - 1, j - 1)] + edit_cost)

        min_edits_needed = edits[(max_i, max_j)]
        end = time.time()
        print(end - start)
        return 1 - min_edits_needed / max(max_i, max_j)

    # # Example of a slash command in a cog
    # @slash_command(description="Says Hello from Gowon")
    # async def hello(self, inter: SlashInteraction):
    #     # await inter.respond("Annyeong")
    #     pass
    #
    # @hello.sub_command()
    # async def goodmorning(self, inter: SlashInteraction):
    #     await inter.respond("good morning!")
    #
    # @hello.sub_command()
    # async def goodnight(self, inter: SlashInteraction):
    #     await inter.respond("good night!")
    #
    # @hello.sub_command()
    # async def test(self, inter: SlashInteraction):
    #     row_of_buttons = ActionRow(
    #         Button(
    #             style=ButtonStyle.green,
    #             label="Green button",
    #             custom_id="green"
    #         ),
    #         Button(
    #             style=ButtonStyle.red,
    #             label="Red button",
    #             custom_id="red"
    #         )
    #     )
    #     await inter.respond("hi", components=[row_of_buttons])
    #
    # # Buttons in cogs (no changes basically)
    # @commands.command()
    # async def test(self, ctx):
    #     row_of_buttons = ActionRow(
    #         Button(
    #             style=ButtonStyle.green,
    #             label="Green button",
    #             custom_id="green"
    #         ),
    #         Button(
    #             style=ButtonStyle.red,
    #             label="Red button",
    #             custom_id="red"
    #         )
    #     )
    #     msg = await ctx.send("This message has buttons", components=[row_of_buttons])
    #
    #     # Wait for a button click
    #     def check(inter):
    #         return inter.author == ctx.author
    #
    #     inter = await msg.wait_for_button_click(check=check)
    #     # Process the button click
    #     await inter.reply(f"Button: {inter.button.label}", type=ResponseType.UpdateMessage)

    ...


def setup(bot: Bot):
    bot.add_cog(GroupMembersCog(bot))
