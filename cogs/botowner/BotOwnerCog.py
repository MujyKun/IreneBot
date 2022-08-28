from . import helper
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from util import botembed, botinfo


class BotOwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the right owner."""
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(name="addeightballresponse", description="Add an 8ball response.")
    async def regular_add_eight_ball_response(
        self, ctx: commands.Context, *, response: str
    ):
        await helper.process_add_eight_ball_response(
            response=response,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    ################
    # SLASH COMMANDS
    ################

    @commands.slash_command(
        name="addeightballresponse", description="Add an 8ball response."
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

    @commands.slash_command(
        name="listeightballresponses", description="List all 8ball responses."
    )
    async def list_eight_ball_response(self, inter: AppCmdInter):
        await helper.process_list_eight_ball_responses(
            user_id=inter.author.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @commands.slash_command(
        name="deleteeightballresponse", description="Delete an 8ball response."
    )
    async def delete_eight_ball_response(
        self,
        inter: AppCmdInter,
        response_id: int = commands.Param("ID of 8ball response."),
    ):
        await helper.process_delete_eight_ball_response(
            response_id=response_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(BotOwnerCog(bot))
