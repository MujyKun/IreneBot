from typing import Union, Dict

import IreneAPIWrapper.models
from IreneAPIWrapper.models import User, EightBallResponse, Urban
import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice, randint
from re import findall
from disnake.ext import commands
from ..helper import send_message
from models import all_games as all_games
from keys import get_keys
from util import botembed, botinfo


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
    """Process Display Emoji"""
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


async def process_bot_info(bot, ctx=None, inter=None):
    """Process Bot Info"""
    embed = await botembed.create_bot_author_embed(
        bot.keys, title=f"I am {bot.keys.bot_name}"
    )
    active_games = [
        len(botinfo.get_gg(finished=False)),
        len(botinfo.get_ggg(finished=False)),
        len(botinfo.get_bg(finished=False)),
        len(botinfo.get_us(finished=False)),
        len(botinfo.get_other_games(finished=False)),
    ]

    inactive_games = [
        len(botinfo.get_gg()),
        len(botinfo.get_ggg()),
        len(botinfo.get_bg()),
        len(botinfo.get_us()),
        len(botinfo.get_other_games()),
    ]

    inline_fields = {
        "Servers Connected": f"{botinfo.get_server_count(bot)}",
        "Active GG/GGG/BG/US/Others": "/".join(
            [str(game_count) for game_count in active_games]
        ),
        "Inactive GG/GGG/BG/US/Others": "/".join(
            [str(game_count) for game_count in inactive_games]
        ),
        "Ping": botinfo.get_bot_ping(bot),
        "Shards": bot.shard_count,
        "Bot Owner": f"<@{bot.keys.bot_owner_id}>",
        "Connected to API": f"{bot.api.connected}",
        "Users": f"{botinfo.get_user_count(bot)}"
    }

    embed = await botembed.add_embed_inline_fields(embed, inline_fields)
    return await send_message(ctx=ctx, inter=inter, embed=embed)


async def process_server_info(bot, guild: disnake.Guild, inter=None, ctx=None):
    """Process Server Info"""
    embed = await botembed.create_bot_author_embed(
        bot.keys, title=f"{guild.name} ({guild.id})", url=f"{guild.icon.url}"
    )
    embed.set_thumbnail(url=guild.icon.url)
    fields = {
        "Owner": f"{guild.owner} ({guild.owner.id})",
        "Users": guild.member_count,
        "Roles": f"{len(guild.roles)}",
        "Emojis": f"{len(guild.emojis)}",
        "Description": guild.description,
        "Channels": f"{len(guild.channels)}",
        "AFK Timeout": f"{guild.afk_timeout / 60} minutes",
        "Since": guild.created_at
    }
    embed = await botembed.add_embed_inline_fields(embed, fields)
    return await send_message(ctx=ctx, inter=inter, embed=embed)


async def process_random(start_number, end_number, invoker_user_id, ctx=None, inter=None):
    """Process a random number."""
    user = await User.get(invoker_user_id)
    if start_number > end_number:
        return await send_message(key="invalid_range", user=user, ctx=ctx, inter=inter, ephemeral=True)
    return await send_message(start_number, end_number, randint(start_number, end_number), key="random_number",
                              user=user, ctx=ctx, inter=inter)


async def process_urban(phrase, definition_number, invoker_user_id, ctx=None, inter=None, allowed_mentions=None,
                        response_deferred=False):
    user = await User.get(invoker_user_id)
    results = _urban.get(phrase.lower())
    if not results:
        results = await Urban.query(phrase) or {}
        _urban[phrase.lower()] = results

    definition_list = results.get('list') or []
    definition_data = {}
    try:
        definition_data = definition_list[definition_number - 1]
    except IndexError:
        ...

    if not results or not definition_data:
        return await send_message(key="no_urban_result", user=user, ctx=ctx, inter=inter,
                                  ephemeral=True, allowed_mentions=allowed_mentions,
                                  response_deferred=response_deferred)

    definition = f"{definition_data.get('definition')}\n<{definition_data.get('permalink')}> -> " \
                 f"{definition_data.get('thumbs_up')} Upvotes"

    return await send_message(phrase.lower(), definition_number, definition, key="urban_result", user=user, ctx=ctx,
                              inter=inter, allowed_mentions=allowed_mentions, response_deferred=response_deferred)


_urban: Dict[str, dict] = dict()
