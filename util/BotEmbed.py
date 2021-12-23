from discord import Embed as disEmbed, User as disUser
from random import randint
from keys import Keys


async def create_bot_author_embed(botkeys: Keys, **kwargs) -> disEmbed:
    """Create a bot specific discord Embed with bot author and footer."""
    embed = disEmbed(**kwargs)
    if not embed.color:
        embed.colour = _get_random_color()
    embed.set_author(name=botkeys.bot_name, url=botkeys.bot_website_url,
                     icon_url=botkeys.embed_icon_url)
    embed.set_footer(text=f"Thanks for using {botkeys.bot_name}", icon_url=botkeys.embed_footer_url)
    return embed


async def create_user_embed(user: disUser, **kwargs) -> disEmbed:
    """Create a bot specific discord Embed with bot author and footer."""
    embed = disEmbed(**kwargs)
    if not embed.color:
        embed.colour = _get_random_color()
    embed.set_author(name=user.display_name,
                     icon_url=user.avatar_url)
    return embed


def _get_random_color():
    """Retrieves a random hex color."""
    r = lambda: randint(0, 255)
    return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present


async def add_embed_inline_fields(embed: disEmbed, fields: dict):
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be inline"""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value)
    return embed


async def add_embed_listed_fields(embed: disEmbed, fields: dict):
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be not be inline."""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value, inline=False)
    return embed


async def set_embed_author_and_footer(botkeys: Keys, embed, footer_message):
    """Sets the bot author and footer of an embed."""
    embed.set_author(name=botkeys.bot_name, url=botkeys.bot_website_url,
                     icon_url=botkeys.embed_icon_url)
    embed.set_footer(text=footer_message,
                     icon_url=botkeys.embed_icon_url)
    return embed
