from . import helper
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="avatar", description="Display user avatar")
    async def slash_avatar(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the avatars of."
        ),
    ):
        await helper.display_avatar(inter, user)

    @commands.user_command(name="Avatar", description="Display user avatar")
    async def user_avatar(self, inter: AppCmdInter, user: disnake.Member):
        await helper.display_avatar(inter, user)

    @commands.slash_command(name="banner", description="Display user's profile banner.")
    async def slash_banner(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the banner of."
        ),
    ):
        await helper.display_banner(self.bot, inter, user)

    @commands.user_command(
        name="User Banner", description="Display user's profile banner."
    )
    async def user_banner(self, inter: AppCmdInter, user: disnake.Member):
        await helper.display_banner(self.bot, inter, user)

    # @slash_command(description="View a user's profile information.")
    # async def profile(self, inter: SlashInteraction,
    #                   user: disMember = OptionParam(lambda inter: inter.author)):
    #     embed = await create_bot_author_embed(self.bot.keys, title=f"{user.name} ({user.id})")
    #     # TODO: Implement all profile fields


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(ProfileCog(bot))
