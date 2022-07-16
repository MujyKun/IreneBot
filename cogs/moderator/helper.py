from typing import List

import disnake
from IreneAPIWrapper.models import Guild
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import create_guild_model, send_message


async def process_prefix_add_remove(
    guild: disnake.Guild,
    prefix: str,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
    add=False,
):
    """Add a command prefix to a guild.

    :param guild: disnake.Guild
        Guild object
    :param prefix: str
        Prefix to add/remove
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    :param add: bool
        Whether to add a prefix. Defaults to removing.
    """
    await create_guild_model(guild)
    guild = await Guild.get(guild.id)

    if add:
        await guild.add_prefix(prefix)
        msg = f"{prefix.lower()} has been added as a command prefix for {guild.name}."
    else:
        await guild.delete_prefix(prefix)
        msg = (
            f"{prefix.lower()} has been removed as a command prefix from {guild.name}."
        )

    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def process_prefix_list(
    guild: disnake.Guild,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """Send the command prefixes of a guild.

    :param guild: disnake.Guild
        Guild object
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    """
    await create_guild_model(guild)
    guild = await Guild.get(guild.id)
    msg = f"The following are the custom prefixes for {guild.name}:\n" + ", ".join(
        guild.prefixes
    )
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def auto_complete_type_guild_prefixes(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the command prefixes in a guild."""
    await create_guild_model(inter.guild_id)
    guild = await Guild.get(inter.guild_id)
    return guild.prefixes
