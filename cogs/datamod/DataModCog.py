from . import helper
from .. import helper as main_helper
import disnake
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
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
        self._loop_running = False

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

    @commands.slash_command(
        name="8ballresponse",
        description="Modify 8ball responses.",
        guild_ids=get_keys().bot_owner_only_servers,
        extras={"permissions": "Bot Owner"},
    )
    async def eight_ball_response(self, inter: AppCmdInter):
        ...

    @eight_ball_response.sub_command(
        name="add",
        description="Add an 8ball response.",
        extras={"permissions": "Bot Owner", "syntax": "/8ballresponse add (response)"},
    )
    async def add_eight_ball_response(
        self,
        inter: AppCmdInter,
        response: str = commands.Param("8ball Response to add."),
    ):
        await helper.process_add_eight_ball_response(
            response=response,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @eight_ball_response.sub_command(
        name="list",
        description="List all 8ball responses.",
        extras={"permissions": "Bot Owner", "syntax": "/8ballresponse list"},
    )
    async def list_eight_ball_response(self, inter: AppCmdInter):
        await helper.process_list_eight_ball_responses(
            user_id=inter.author.id, inter=inter, allowed_mentions=self.allowed_mentions
        )


def setup(bot: commands.AutoShardedBot):
    cog = DataModCog(bot)
    bot.add_cog(cog)
