from disnake.ext import commands

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @slash_command(description="Display user avatar")
    # async def avatar(self, inter: SlashInteraction,
    #                  user: disMember = OptionParam(lambda inter: inter.author)):
    #     embed = await create_bot_author_embed(self.bot.keys, title=f"{user.display_name}'s Avatar ({user.id})")
    #     embed.set_image(url=user.avatar_url)
    #     await inter.respond(embed=embed)
    #
    # @slash_command(description="View a user's profile information.")
    # async def profile(self, inter: SlashInteraction,
    #                   user: disMember = OptionParam(lambda inter: inter.author)):
    #     embed = await create_bot_author_embed(self.bot.keys, title=f"{user.name} ({user.id})")
    #     # TODO: Implement all profile fields


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(ProfileCog(bot))
