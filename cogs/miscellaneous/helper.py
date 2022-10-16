from typing import Union

from IreneAPIWrapper.models import User, EightBallResponse
import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice
from re import findall
from disnake.ext import commands
from ..helper import send_message
from models import all as all_games
from keys import get_keys


async def process_ping(
    latency, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    user = await User.get(user_id)
    return await send_message(
        latency,
        key="ping",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def process_stop_games(
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    user = await User.get(user_id)
    if not user:
        return

    games = [
        game for game in all_games if game.host_user == user and not game.is_complete
    ]
    for game in games:
        await game.stop()

    await send_message(
        key="stop_games",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def process_choose(
    choices: str,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the choose command.
    """
    user = await User.get(user_id)
    possible_choices = await get_possible_choices(choices)

    await send_message(
        ",".join(possible_choices),
        choice(possible_choices),
        key="choose_options",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def send_bot_invite(
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    user = await User.get(user_id=user_id)
    await send_message(
        msg=f"{get_keys().bot_invite_url}",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def process_8ball(
    prompt: str,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the 8ball command.
    """
    user = await User.get(user_id=user_id)
    answer = await EightBallResponse.get_random_response(fetch=False)

    await send_message(
        prompt,
        answer.response,
        key="8ball_response",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def get_possible_choices(choices: str):
    """Get the choices possible in a user's input string."""
    modified_choices = choices.replace(",", "|")
    possible_choices = modified_choices.split("|")

    possible_choices = [
        f"`{m_choice.replace('_', ' ')}`"
        for m_choice in possible_choices
        if m_choice not in [" ", ""]
    ]
    return possible_choices


async def process_display_emoji(
    message: Union[disnake.Message, str],
    invoker_user_id,
    inter=None,
    ctx=None,
    allowed_mentions=None,
):
    user = await User.get(invoker_user_id)
    urls = []
    if isinstance(message, disnake.Message):
        if message.stickers:
            urls.append(message.stickers[0].url)
        content = message.content
    else:
        content = message
    if content:
        emojis = findall(r"<a?:?\w+:[0-9]{18}>", content)
        urls += [disnake.PartialEmoji.from_str(emoji_info).url for emoji_info in emojis]
    if not urls:
        return await send_message(
            key="no_emojis_found",
            user=user,
            inter=inter,
            ctx=ctx,
            allowed_mentions=allowed_mentions,
            ephemeral=True,
        )
    return await send_message(
        msg="\n".join(urls),
        user=user,
        inter=inter,
        ctx=ctx,
        allowed_mentions=allowed_mentions,
    )
