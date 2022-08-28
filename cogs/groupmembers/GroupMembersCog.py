import random
import disnake
from models import Bot
from IreneAPIWrapper.models import Media, Person, Group, User
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal, List


class GroupMembersCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)
        self.invalid_selection = (
            "item_type returned something other than 'person' or 'group'"
        )

    @commands.command(
        name="whois", description="Figure out who a media object belongs to."
    )
    async def regular_whois(
        self,
        ctx: commands.Context,
        media_id: int,
    ):
        """Figure out who a media object belongs to."""
        await helper.process_who_is(
            media_id=media_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(name="call", description="Call Media for an Idol/Group")
    async def regular_call_person_or_group(
        self, ctx: commands.Context, item_type: Literal["person", "group"], item_id: int
    ):
        await helper.process_call(
            item_type,
            item_id,
            ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(
        name="card",
        description="Display a profile card for either a Person or a Group.",
    )
    async def regular_card(
        self, ctx, item_type: Literal["person", "group"], item_id: int
    ):
        await helper.process_card(
            item_type=item_type,
            item_id=item_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    ################
    # SLASH COMMANDS
    ################
    @commands.slash_command(description="Figure out who a media object belongs to.")
    async def whois(
        self,
        inter: AppCmdInter,
        media_id: int = commands.Param("Media ID"),
    ):
        """Figure out who a media object belongs to."""
        await helper.process_who_is(
            media_id=media_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        description="Display a profile card for either a Person or a Group."
    )
    async def card(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        """Display a profile card for either a Person or a Group."""
        object_id = int(selection.split(")")[0])
        await helper.process_card(
            item_type=item_type,
            item_id=object_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="call", description="Call Media for an Idol/Group.")
    async def call_person_or_group(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        """Display the media for a specific Person or Group."""
        object_id = int(selection.split(")")[0])
        await helper.process_call(
            item_type,
            object_id,
            inter.user.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="randomperson", description="Display random media for a random Person."
    )
    async def random_person(self, inter: AppCmdInter):
        """Send a photo of a random person."""
        media: Media = random.choice(list(await Media.get_all()))
        await inter.send(media.source.url)

    @commands.slash_command(
        name="count", description="Get count for the media a person or group has."
    )
    async def count(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        object_id = int(selection.split(")")[0])
        if item_type == "person":
            person = await Person.get(object_id)
            medias: List[Media] = await Media.get_all(person.affiliations)
        elif item_type == "group":
            group = await Group.get(object_id)
            medias: List[Media] = await Media.get_all(group.affiliations)
        else:
            raise NotImplementedError(
                f"An entity aside from a person or object has not been implemented. {item_type}"
            )
        await inter.send(
            f"There is **{len(medias)}** known media for that {item_type}."
        )

    @commands.slash_command(
        name="aliases", description="Get the aliases of persons or groups."
    )
    async def aliases(self, inter: AppCmdInter, name):
        name = name.lower()
        persons = await helper.search_for_obj(name)
        groups = await helper.search_for_obj(name, False)

        persons_aliases = []
        for person in persons:
            aliases_as_strings = await person.get_aliases_as_strings()
            if not aliases_as_strings:
                continue
            persons_aliases.append(
                f"{str(person.name)} [{person.id}] - {' | '.join(aliases_as_strings)}"
            )

        groups_aliases = []
        for group in groups:
            aliases_as_strings = await group.get_aliases_as_strings()
            if not aliases_as_strings:
                continue
            groups_aliases.append(
                f"{group.name} [{group.id}] - {' | '.join(aliases_as_strings)}"
            )
        persons_aliases_as_str = "\n".join(persons_aliases)
        groups_aliases_as_str = "\n".join(groups_aliases)

        description = (
            f"**Person(s):**\n{persons_aliases_as_str}\n\n" if persons_aliases else ""
        )
        description += (
            f"**Group(s):**\n{groups_aliases_as_str}" if groups_aliases else ""
        )
        description = description if description else "**No Results.**"

        embed = disnake.Embed(
            title=f"Aliases for {name}",
            color=helper.get_random_color(),
            description=description,
        )
        await inter.send(embed=embed)

    @commands.slash_command(
        name="distance", description="Get the Levenshtein Distance of two words."
    )
    async def distance(self, inter: AppCmdInter, search_word: str, target_word: str):
        if len(search_word) * len(target_word) > 2000000:
            return await inter.send("You cannot compare words of that length.")

        await inter.send(
            f"The search word has **{await helper.unblock_levenshtein_distance(search_word, target_word) * 100:.2f}%** "
            f"similarity with the target word."
        )

    @commands.slash_command(
        name="countleaderboard",
        description="Shows leaderboards for how many times a Person or Group has been called.",
        aliases=["clb", "cb", "highestcount"],
    )
    async def countleaderboard(
        self, inter: AppCmdInter, item_type: Literal["Persons", "Groups"]
    ):
        if item_type == "Persons":
            objects = await Person.get_all()
        elif item_type == "Groups":
            objects = await Group.get_all()
        else:
            raise NotImplementedError(
                f"An entity aside from a person or object has not been implemented. {item_type}"
            )
        sorted_leaderboard = await helper.get_call_count_leaderboard(objects)
        if not sorted_leaderboard:
            desc = "No Results."
        else:
            desc = ""
            for count, content in enumerate(sorted_leaderboard, 1):
                model = content[0]
                call_count = content[1]
                desc += f"**{count})** **{str(model.name)}** [{model.id}] -> Called **{call_count}** times.\n"

        embed = disnake.Embed(
            title=f"{item_type} Leaderboard",
            color=helper.get_random_color(),
            description=desc,
        )
        await inter.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(GroupMembersCog(bot))
