import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter


async def display_avatar(inter: AppCmdInter, user: disnake.Member):
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


async def display_banner(bot, inter: AppCmdInter, user: disnake.Member):
    # Due to API limitations, you must fetch the user from the client to get an object which contains the banner
    # attribute
    user_object = await bot.fetch_user(user.id)
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
