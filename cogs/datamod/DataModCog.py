from typing import Optional, Literal

from . import helper
from .. import helper as main_helper
from ..groupmembers import helper as gm_helper
import disnake
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter, Option
from keys import get_keys
from IreneAPIWrapper.models import (
    User,
)


class NotDataMod(commands.CheckFailure):
    """Exception raised when the message author is not a Data Moderator.

    This inherits from :exc:`CheckFailure`
    """
    pass


class DataModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the user is a Data Mod."""
        return (await User.get(ctx.author.id)).is_data_mod

    async def cog_slash_command_check(self, inter: AppCmdInter):
        """A local cog check to confirm the user is a Data Mod."""
        if not (await User.get(inter.author.id)).is_data_mod:
            raise NotDataMod
        return True

    ################
    # SLASH COMMANDS
    ################

    # add social
    # twitter: Optional[str] = None,
    # youtube: Optional[str] = None,
    # melon: Optional[str] = None,
    # instagram: Optional[str] = None,
    # vlive: Optional[str] = None,
    # spotify: Optional[str] = None,
    # fancafe: Optional[str] = None,
    # facebook: Optional[str] = None,
    # tiktok: Optional[str] = None,

    @commands.slash_command(
        name="person",
        description="Manage a Person.",
        guild_ids=get_keys().bot_owner_only_servers,
        extras={"permissions": "Data Mod"},
    )
    async def person(self, inter: AppCmdInter):
        ...

    @person.sub_command(
        name="add",
        description="Add a Person.",
        extras={"permissions": "Data Mod", "syntax": "/person add (response)"},
    )
    async def add_person(
        self,
        inter: AppCmdInter,
        gender: Literal['m', 'f'],
        date_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        former_name_id: Optional[int] = None,
        former_first_name: Optional[str] = None,
        former_last_name: Optional[str] = None,
        description: Optional[str] = None,
        height: Optional[int] = None,
        display_id: Optional[int] = None,
        avatar: Optional[str] = None,
        banner: Optional[str] = None,
        social_id: Optional[int] = None,
        location_id: Optional[int] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        blood_id: Optional[int] = None
    ):
        ...

    @person.sub_command(
        name="remove",
        description="Remove a Person.",
        extras={"permissions": "Data Mod", "syntax": "/person remove (person)"},
    )
    async def remove_person(
        self,
        inter: AppCmdInter,
        person: str = commands.Param(autocomplete=gm_helper.auto_complete_person)
    ):
        ...


def setup(bot: commands.AutoShardedBot):
    cog = DataModCog(bot)
    bot.add_cog(cog)
