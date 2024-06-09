from . import helper
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##################
    # REGULAR COMMANDS
    ##################
    @commands.command(name="avatar", description="Display user avatar")
    async def regular_avatar(self, ctx, user: disnake.Member = None):
        await helper.display_avatar(user=user or ctx.author, ctx=ctx)

    @commands.command(name="banner", description="Display user's profile banner.")
    async def regular_banner(self, ctx, user: disnake.Member = None):
        await helper.display_banner(
            self.bot, invoker_user_id=ctx.author.id, user=user or ctx.author, ctx=ctx
        )

    ################
    # SLASH COMMANDS
    ################
    @commands.slash_command(name="avatar", description="Display user avatar")
    async def slash_avatar(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the avatars of."
        ),
    ):
        await helper.display_avatar(inter=inter, user=user)

    @commands.slash_command(name="banner", description="Display user's profile banner.")
    async def slash_banner(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the banner of."
        ),
    ):
        await helper.display_banner(
            bot=self.bot, invoker_user_id=inter.user.id, user=user, inter=inter
        )

    ###############
    # USER COMMANDS
    ###############
    @commands.user_command(
        name="Avatar", extras={"description": "Display a User's Avatar"}
    )
    async def user_avatar(self, inter: AppCmdInter, user):
        """User Avatar Shi"""
        await helper.display_avatar(inter=inter, user=user)

    @commands.user_command(
        name="User Banner", description="Display a User's profile banner."
    )
    async def user_banner(self, inter: AppCmdInter, user):
        await helper.display_banner(
            bot=self.bot, invoker_user_id=inter.user.id, inter=inter, user=user
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(ProfileCog(bot))
