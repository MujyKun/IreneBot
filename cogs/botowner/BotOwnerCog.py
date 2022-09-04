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

    @commands.is_owner()
    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the right owner."""
        return await ctx.bot.is_owner(ctx.author)

    async def cog_slash_command_check(self, inter: AppCmdInter):
        """A local cog check to confirm the right owner."""
        if not await inter.bot.is_owner(inter.author):
            raise commands.NotOwner

    @commands.group(name="8ballresponse", description="Modify 8ball responses.")
    async def regular_eight_ball_response(self, ctx: commands.Context):
        ...

    @regular_eight_ball_response.command(
        name="add", description="Add an 8ball response."
    )
    async def regular_add_eight_ball_response(
        self, ctx: commands.Context, *, response: str
    ):
        await helper.process_add_eight_ball_response(
            response=response,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_eight_ball_response.command(
        name="list", description="List all 8ball responses."
    )
    async def regular_list_eight_ball_response(self, ctx: commands.Context):
        await helper.process_list_eight_ball_responses(
            user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    @regular_eight_ball_response.command(
        name="delete", description="Delete an 8ball response."
    )
    async def regular_delete_eight_ball_response(
        self, ctx: commands.Context, response_id: int
    ):
        await helper.process_delete_eight_ball_response(
            response_id=response_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.group(name="interaction", description="Interaction commands")
    async def regular_interaction(self, ctx: commands.Context):
        ...

    @regular_interaction.command(name="add", description="Add an interaction")
    async def regular_interaction_add(
        self, ctx: commands.Context, type_name: str, url: str
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction.command(name="delete", description="Delete an interaction")
    async def regular_interaction_delete(
        self, ctx: commands.Context, type_name: str, url: str
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction.group(name="type")
    async def regular_interaction_type(self, ctx: commands.Context):
        ...

    @regular_interaction_type.command(name="add", description="Add an interaction type")
    async def regular_interaction_add(self, ctx: commands.Context, type_name: str):
        await helper.process_interaction_type_add(
            type_name=type_name,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction_type.command(
        name="delete", description="Delete an interaction type"
    )
    async def regular_interaction_delete(self, ctx: commands.Context, type_name):
        await helper.process_interaction_type_delete(
            type_name=type_name,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    ################
    # SLASH COMMANDS
    ################

    @commands.slash_command(name="8ballresponse", description="Modify 8ball responses.")
    async def eight_ball_response(self, inter: AppCmdInter):
        ...

    @eight_ball_response.sub_command(name="add", description="Add an 8ball response.")
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
        name="list", description="List all 8ball responses."
    )
    async def list_eight_ball_response(self, inter: AppCmdInter):
        await helper.process_list_eight_ball_responses(
            user_id=inter.author.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @eight_ball_response.sub_command(
        name="delete", description="Delete an 8ball response."
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

    @commands.slash_command(name="interaction", description="Interaction Commands")
    async def interaction(self, inter: AppCmdInter):
        ...

    @interaction.sub_command(name="add", description="Add an interaction")
    async def interaction_add(
        self,
        inter: AppCmdInter,
        url: str,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction.sub_command(name="delete", description="Delete an interaction")
    async def interaction_delete(
        self,
        inter: AppCmdInter,
        url: str,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction.sub_command_group(name="type")
    async def interaction_type(self, inter: AppCmdInter):
        ...

    @interaction_type.sub_command(name="add", description="Add an interaction type")
    async def interaction_type_add(self, inter: AppCmdInter, type_name):
        await helper.process_interaction_type_add(
            type_name=type_name,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction_type.sub_command(
        name="delete", description="Delete an interaction type"
    )
    async def interaction_type_delete(
        self,
        inter: AppCmdInter,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_type_delete(
            type_name=type_name,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(BotOwnerCog(bot))
