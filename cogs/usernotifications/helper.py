from IreneAPIWrapper.models import User, Group, Person, Notification
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import send_message, check_game_input, in_game


async def auto_complete_phrases(inter: AppCmdInter, user_input: str):
    """Auto complete typing phrases"""
    notifications = await Notification.get_all(
        guild_id=inter.guild_id, user_id=inter.author.id
    )
    return [noti.phrase for noti in notifications][:24]


async def process_add(
    phrase: str,
    guild_id: int,
    user_id: int,
    ctx=None,
    inter=None,
    allowed_mentions=None,
):
    """Add a phrase"""
    user = await User.get(user_id)
    notifications = await Notification.get_all(guild_id=guild_id, user_id=user_id)
    phrase = phrase.lower()
    if any([phrase == noti.phrase.lower() for noti in notifications]):
        return await send_message(
            key="noti_already_exists",
            ctx=ctx,
            inter=inter,
            user=user,
            allowed_mentions=allowed_mentions,
        )

    await Notification.insert(guild_id, user_id, phrase)
    return await send_message(
        key="noti_added",
        ctx=ctx,
        inter=inter,
        user=user,
        allowed_mentions=allowed_mentions,
    )


async def process_list(
    guild_id: int, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """List phrases."""
    user = await User.get(user_id)
    notifications = await Notification.get_all(guild_id=guild_id, user_id=user_id)
    return await send_message(
        "\n".join([noti.phrase for noti in notifications]),
        key="noti_list",
        ctx=ctx,
        inter=inter,
        user=user,
        allowed_mentions=allowed_mentions,
    )


async def process_remove(
    phrase: str,
    guild_id: int,
    user_id: int,
    ctx=None,
    inter=None,
    allowed_mentions=None,
):
    """Remove a phrase"""
    notifications = await Notification.get_all(guild_id=guild_id, user_id=user_id)
    user = await User.get(user_id)
    # should only produce 0 or 1 match(es)
    matches = [noti for noti in notifications if noti.phrase.lower() == phrase]
    if not matches:
        return await send_message(
            key="noti_does_not_exist",
            ctx=ctx,
            inter=inter,
            user=user,
            allowed_mentions=allowed_mentions,
        )

    await matches[0].delete()
    return await send_message(
        key="noti_removed",
        ctx=ctx,
        inter=inter,
        user=user,
        allowed_mentions=allowed_mentions,
    )
