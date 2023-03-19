from typing import Union

import disnake
from IreneAPIWrapper.models import User
from ..helper import send_message, defer_inter


async def display_avatar(
    user: Union[disnake.Member, disnake.User],
    ctx=None,
    inter=None,
    allowed_mentions=None,
):
    """Display the avatars of a user/member."""
    response_deferred = await defer_inter(inter)
    user_avatar = disnake.Embed(
        title=f"{user.display_name}'s Avatar ({user.id})", url=user.avatar.url
    )
    user_avatar.set_image(user.avatar.url)
    embeds = [user_avatar]

    if hasattr(user, "guild_avatar") and user.guild_avatar:
        member_avatar = disnake.Embed(
            title=f"{user.display_name}'s Guild Avatar " f"({user.id})",
            url=user.guild_avatar.url,
        )
        user_avatar.set_image(user.guild_avatar.url)
        embeds.append(member_avatar)

    await send_message(
        embeds=embeds,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )


async def display_banner(
    bot,
    invoker_user_id,
    user: Union[disnake.Member, disnake.User],
    ctx=None,
    inter=None,
    allowed_mentions=None,
):
    """Display the banners of a user/member."""
    response_deferred = await defer_inter(inter)
    banner = user.banner
    if not banner:
        fetched_user = await bot.fetch_user(user.id)
        if not fetched_user.banner:
            irene_user = await User.get(invoker_user_id)
            return await send_message(
                key="no_banner",
                user=irene_user,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
                response_deferred=response_deferred,
            )
        else:
            banner = fetched_user.banner

    embed = disnake.Embed(
        title=f"{user.display_name}'s Banner ({user.id})", url=banner.url
    )
    embed.set_image(banner.url)

    await send_message(
        embed=embed,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )
