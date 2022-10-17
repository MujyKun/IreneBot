import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter, ButtonStyle
from disnake.ui import Button
from random import randint
from keys import get_keys
from typing import List, Dict
from main import Bot


async def create_bot_author_embed(**kwargs) -> disnake.Embed:
    """Create a bot specific discord Embed with bot author and footer."""
    embed = disnake.Embed(**kwargs)
    if not embed.color:
        embed.colour = _get_random_color()
    embed = await set_embed_bot_author_and_footer(
        embed, f"Thanks for using {get_keys().bot_name}."
    )
    return embed


async def set_embed_bot_author_and_footer(embed, footer_message) -> disnake.Embed:
    """Sets the bot author and footer of an embed."""
    bot_keys = get_keys()
    embed.set_author(
        name=bot_keys.bot_name,
        url=bot_keys.bot_website_url,
        icon_url=bot_keys.embed_icon_url,
    )
    embed.set_footer(text=footer_message, icon_url=bot_keys.embed_icon_url)
    return embed


async def create_user_embed(user: disnake.User, **kwargs) -> disnake.Embed:
    """Create a bot specific discord Embed with bot author and footer."""
    embed = disnake.Embed(**kwargs)
    if not embed.color:
        embed.colour = _get_random_color()
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)
    return embed


def _get_random_color():
    """Retrieves a random hex color."""
    r = lambda: randint(0, 255)
    return int(
        ("%02X%02X%02X" % (r(), r(), r())), 16
    )  # must be specified to base 16 since 0x is not present


async def add_embed_inline_fields(
    embed: disnake.Embed, fields: Dict[str, str]
) -> disnake.Embed:
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be inline"""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value)
    return embed


async def add_embed_listed_fields(
    embed: disnake.Embed, fields: Dict[str, str]
) -> disnake.Embed:
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be not be inline."""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value, inline=False)
    return embed


async def create_embeds_from_list(
    items: List[str], groupings: int = 10, title: str = None
) -> List[disnake.Embed]:
    numbered_items = [f"{i + 1}) {items[i]}" for i in range(0, len(items))]
    grouped_items = [
        "\n".join(numbered_items[i : i + groupings])
        for i in range(0, len(numbered_items), groupings)
    ]
    embeds = [
        disnake.Embed(title=title, description=grouped_items[i])
        for i in range(0, len(grouped_items))
    ]
    return embeds
