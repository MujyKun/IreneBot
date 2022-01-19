import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # AvatarSource = commands.option_enum({"Global": "global", "Server": "server", "Both": "both"})
    @commands.slash_command(description="Display user avatar")
    async def avatar(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the avatars of."
        ),
    ):
        avatar_embed = disnake.Embed(
            title=f"{user.display_name}'s Avatar ({user.id})", url=user.avatar.url
        )
        avatar_embed.set_image(url=user.avatar.url)
        if user.guild_avatar:
            guild_avatar_embed = disnake.Embed(
                title=f"{user.display_name}'s Avatar ({user.id})",
                url=user.guild_avatar.url,
            )
            guild_avatar_embed.set_image(url=user.guild_avatar.url)
            avatar_embeds = [avatar_embed, guild_avatar_embed]
            return await inter.response.send_message(embeds=avatar_embeds)
        await inter.response.send_message(embed=avatar_embed)
        # TODO: Add footer and add source option parameter
        # source: AvatarSource = commands.Param("both", description="User avatar sources.")

    @commands.user_command(name="Avatar", description="Display user avatar")
    async def user_avatar(
            self, inter: AppCmdInter):
        user = inter.author
        avatar_embed = disnake.Embed(
            title=f"{user.display_name}'s Avatar ({user.id})", url=user.avatar.url
        )
        avatar_embed.set_image(url=user.avatar.url)
        if user.guild_avatar:
            guild_avatar_embed = disnake.Embed(
                title=f"{user.display_name}'s Avatar ({user.id})",
                url=user.guild_avatar.url,
            )
            guild_avatar_embed.set_image(url=user.guild_avatar.url)
            avatar_embeds = [avatar_embed, guild_avatar_embed]
            return await inter.response.send_message(embeds=avatar_embeds)
        await inter.response.send_message(embed=avatar_embed)

    @commands.slash_command(description="Display user profile banner.")
    async def banner(
        self,
        inter: AppCmdInter,
        user: disnake.Member = commands.Param(
            lambda inter: inter.author, description="Member to display the banner of."
        ),
    ):
        # Due to API limitations, you must fetch the user from the client to get an object which contains the banner attribute
        user_object = await self.bot.fetch_user(user.id)
        if not user_object.banner:
            return await inter.response.send_message(
                f"{user.display_name} ({user.id}) does not have a profile banner.",
                ephemeral=True,
            )
        banner_embed = disnake.Embed(
            title=f"{user.display_name}'s Profile Banner ({user.id})",
            url=user_object.banner.url,
        )
        banner_embed.set_image(url=user_object.banner.url)
        await inter.response.send_message(embed=banner_embed)

    # @slash_command(description="View a user's profile information.")
    # async def profile(self, inter: SlashInteraction,
    #                   user: disMember = OptionParam(lambda inter: inter.author)):
    #     embed = await create_bot_author_embed(self.bot.keys, title=f"{user.name} ({user.id})")
    #     # TODO: Implement all profile fields


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(ProfileCog(bot))
