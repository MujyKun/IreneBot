import random
import disnake
from models import Bot
from IreneAPIWrapper.models import Media, Person, Group, User
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper
from typing import Literal, List, Optional


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
    @commands.guild_only()
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.group(
        name="autoaff",
        description="Automatically send affiliation photos every 12 hours.",
    )
    async def regular_autoaff(self, ctx):
        """Automatically send affiliation photos to a channel every 12 hours.

        The time can be set manually using a slash command."""
        ...

    @regular_autoaff.command(
        name="add", description="Add an affiliation to send media every 12 hours."
    )
    async def regular_auto_aff_add(
        self, ctx, affiliation_id: int, text_channel: disnake.TextChannel = None
    ):
        """Add an affiliation to send media every 12 hours.

        The time can be set manually using a slash command.
        """
        if not text_channel:
            text_channel = ctx.channel
        await helper.process_auto_aff(
            channel_id=text_channel.id,
            aff_id=affiliation_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            guild_id=ctx.guild.id,
        )

    @regular_autoaff.command(
        name="remove", description="Delete an affiliation that sends media."
    )
    async def regular_auto_aff_remove(
        self, ctx, affiliation_id: int, text_channel: disnake.TextChannel = None
    ):
        """Delete an affiliation that sends media."""
        if not text_channel:
            text_channel = ctx.channel
        await helper.process_auto_aff(
            channel_id=text_channel.id,
            aff_id=affiliation_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            remove=True,
        )

    @regular_autoaff.command(
        name="list", description="List the affiliations that automatically send media."
    )
    async def regular_automatic_list(
        self, ctx, text_channel: disnake.TextChannel = None
    ):
        """List the affiliations that automatically send media."""
        if not text_channel:
            text_channel = ctx.channel
        await helper.process_list_auto_aff(
            channel_id=text_channel.id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
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
    async def regular_call_media(
        self,
        ctx: commands.Context,
        item_type: Literal["person", "group", "affiliation"],
        item_id: int,
        file_type: str = None,
    ):
        await helper.process_call(
            item_type,
            item_id,
            ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
            file_type=file_type,
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
    @commands.slash_command(
        name="autoaff",
        description="Automatically send affiliation photos to a channel.",
    )
    @commands.has_guild_permissions(**{"manage_messages": True})
    @commands.guild_only()
    async def autoaff(self, inter: AppCmdInter):
        ...

    @autoaff.sub_command(
        name="add", description="Automatically send affiliation photos every 12 hours.",
        extras={"permissions": "Manage Messages",
                "syntax": "/autoaff add (selection) [text channel] [hours to send after]"}
    )
    async def autoaff_add(
        self,
        inter: AppCmdInter,
        selection: str = commands.Param(autocomplete=helper.auto_complete_affiliation),
        text_channel: Optional[disnake.TextChannel] = None,
        hours_to_send_after: int = 12,
    ):
        if not text_channel:
            text_channel = inter.channel
        affiliation_id = int(selection.split(")")[0])
        await helper.process_auto_aff(
            channel_id=text_channel.id,
            aff_id=affiliation_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
            hours_to_send_after=hours_to_send_after,
            guild_id=inter.guild_id,
        )

    @autoaff.sub_command(
        name="remove", description="Delete an affiliation that sends media.",
        extras={"permissions": "Manage Messages",
                "syntax": "/autoaff remove (selection) [text channel]"}
    )
    async def autoaff_remove(
        self,
        inter: AppCmdInter,
        selection: str = commands.Param(autocomplete=helper.auto_complete_affiliation),
        text_channel: Optional[disnake.TextChannel] = None,
    ):
        if not text_channel:
            text_channel = inter.channel
        affiliation_id = int(selection.split(")")[0])
        await helper.process_auto_aff(
            channel_id=text_channel.id,
            aff_id=affiliation_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
            remove=True,
        )

    @autoaff.sub_command(
        name="list", description="List the affiliations that automatically send media."
    )
    async def autoaff_list(
        self, inter: AppCmdInter, text_channel: Optional[disnake.TextChannel] = None
    ):
        if not text_channel:
            text_channel = inter.channel
        await helper.process_list_auto_aff(
            channel_id=text_channel.id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="whois", description="Figure out who a media object belongs to."
    )
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
        file_type: Optional[str] = commands.Param(
            default=None, autocomplete=helper.auto_complete_file_type
        ),
        count: int = commands.Param(
            default=1, autocomplete=helper.auto_complete_call_count
        ),
    ):
        """Display the media for a specific Person, Group, or Affiliation."""
        object_id = int(selection.split(")")[0])
        await helper.process_call(
            item_type,
            object_id,
            inter.user.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
            file_type=file_type,
            count=count,
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

    @tasks.loop(minutes=5, seconds=0, reconnect=True)
    async def loop_auto_aff(self):
        """
        Send automatic affiliation photos
        """
        try:
            await helper.process_loop_auto_aff(self.bot)
        except Exception as e:
            self.bot.logger.error(f"Auto Affiliation Loop Error -> {e}")


def setup(bot: Bot):
    cog = GroupMembersCog(bot)
    bot.add_cog(cog)
    cog.loop_auto_aff.start()
