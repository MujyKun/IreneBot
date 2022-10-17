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
        self.invalid_selection = "item_type returned something other than 'person', 'group', or 'affiliation'."

    ###################
    # MESSAGE COMMANDS
    ###################
    @commands.message_command(
        name="Who Is This?",
        extras={"description": "Figure out who a media object belongs to."},
    )
    async def message_whois(self, inter: AppCmdInter, message: disnake.Message):
        """Figure out who a media object belongs to."""
        media_id = 0  # Cause the search to not find a result by default.
        if message.content:
            media_id = int("".join(filter(str.isdigit, message.content)) or 0)
        await helper.process_who_is(
            media_id=media_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    ###################
    # REGULAR COMMANDS
    ###################
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
    async def regular_call_media(
        self,
        ctx: commands.Context,
        item_type: Literal["person", "group", "affiliation"],
        item_id: int,
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
        description="Display a profile card for either a Person, Group, or Affiliation.",
    )
    async def regular_card(
        self, ctx, item_type: Literal["person", "group", "affiliation"], item_id: int
    ):
        await helper.process_card(
            item_type=item_type,
            item_id=item_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.command(
        name="randomperson", description="Display random media for a random Person."
    )
    async def regular_random_person(self, ctx):
        """Send a photo of a random person."""
        await helper.process_random_person(user_id=ctx.author.id, ctx=ctx)

    @commands.command(
        name="distance", description="Get the Similarity Distance of two words."
    )
    async def regular_distance(self, ctx, search_word, target_word):
        await helper.process_distance(
            search_phrase=search_word,
            target_phrase=target_word,
            user_id=ctx.author.id,
            ctx=ctx,
        )

    ################
    # SLASH COMMANDS
    ################
    @commands.slash_command(description="Figure out who a media object belongs to.")
    async def whois(
        self,
        inter: AppCmdInter,
        media_id: int,
    ):
        """Figure out who a media object belongs to."""
        await helper.process_who_is(
            media_id=media_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        description="Display a profile card for either a Person, Group, or Affiliation."
    )
    async def card(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group", "affiliation"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        """Display a profile card for either a Person, Group, or Affiliation."""
        object_id = int(selection.split(")")[0])
        await helper.process_card(
            item_type=item_type,
            item_id=object_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(name="call", description="Call Media for an Idol/Group.")
    async def call_media(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group", "affiliation"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        """Display the media for a specific Person, Group, or Affiliation."""
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
        await helper.process_random_person(user_id=inter.author.id, inter=inter)

    @commands.slash_command(
        name="count",
        description="Get count for the media a person, group, or affiliation has.",
    )
    async def count(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group", "affiliation"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        object_id = int(selection.split(")")[0])
        await helper.process_count(
            item_type=item_type, item_id=object_id, inter=inter, user_id=inter.author.id
        )

    @commands.slash_command(
        name="aliases", description="Get the aliases of persons or groups."
    )
    async def aliases(
        self,
        inter: AppCmdInter,
        item_type: Literal["person", "group"],
        selection: str = commands.Param(autocomplete=helper.auto_complete_type),
    ):
        object_id = int(selection.split(")")[0])
        await helper.process_aliases(
            item_type=item_type, item_id=object_id, inter=inter, user_id=inter.author.id
        )

    @commands.slash_command(
        name="distance", description="Get the Similarity Distance of two words."
    )
    async def distance(
        self, inter: AppCmdInter, search_phrase: str, target_phrase: str
    ):
        await helper.process_distance(
            search_phrase=search_phrase,
            target_phrase=target_phrase,
            user_id=inter.author.id,
            inter=inter,
        )

    #
    # @commands.slash_command(
    #     name="countleaderboard",
    #     description="Shows leaderboards for how many times a Person or Group has been called.",
    #     aliases=["clb", "cb", "highestcount"],
    # )
    # async def countleaderboard(
    #     self, inter: AppCmdInter, item_type: Literal["Persons", "Groups"]
    # ):
    #     if item_type == "Persons":
    #         objects = await Person.get_all()
    #     elif item_type == "Groups":
    #         objects = await Group.get_all()
    #     else:
    #         raise NotImplementedError(
    #             f"An entity aside from a person or object has not been implemented. {item_type}"
    #         )
    #     sorted_leaderboard = await helper.get_call_count_leaderboard(objects)
    #     if not sorted_leaderboard:
    #         desc = "No Results."
    #     else:
    #         desc = ""
    #         for count, content in enumerate(sorted_leaderboard, 1):
    #             model = content[0]
    #             call_count = content[1]
    #             desc += f"**{count})** **{str(model.name)}** [{model.id}] -> Called **{call_count}** times.\n"
    #
    #     embed = disnake.Embed(
    #         title=f"{item_type} Leaderboard",
    #         color=helper.get_random_color(),
    #         description=desc,
    #     )
    #     await inter.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(GroupMembersCog(bot))
