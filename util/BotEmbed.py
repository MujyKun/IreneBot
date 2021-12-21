from discord import Embed as disEmbed
from random import randint
from keys import Keys


async def create_embed(botkeys: Keys, **kwargs) -> disEmbed:
    """Create a bot specific discord Embed with bot author and footer."""
    embed = disEmbed(**kwargs)
    if not embed.color:
        embed.colour = _get_random_color()
    embed.set_author(name=botkeys.bot_name, url=botkeys.bot_website_url,
                     icon_url=botkeys.embed_icon_url)
    embed.set_footer(text=f"Thanks for using {botkeys.bot_name}", icon_url=botkeys.embed_footer_url)
    return embed


def _get_random_color():
    """Retrieves a random hex color."""
    r = lambda: randint(0, 255)
    return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present


async def add_embed_fields(embed: disEmbed, fields: dict, all_inline: bool = True, inline_list: list[bool] = None):
    """Easily add fields to an embed through a dictionary of the field names and values. To set some of these fields to
    not be inline, define allInLine as False and pass a list of boolean values to set values as not inline."""
    if all_inline:
        for f_name, f_value in fields.items():
            embed.add_field(name=f_name, value=f_value)
    else:
        for f_name, f_value, f_inline in zip(fields.keys(), fields.values(), inline_list):
            embed.add_field(name=f_name, value=f_value, inline=f_inline)
    # TODO: Add error exception when there are not enough fields
    return embed


async def set_embed_author_and_footer(botkeys: Keys, embed, footer_message):
    """Sets the bot author and footer of an embed."""
    embed.set_author(name=botkeys.bot_name, url=botkeys.bot_website_url,
                     icon_url=botkeys.embed_icon_url)
    embed.set_footer(text=footer_message,
                     icon_url=botkeys.embed_icon_url)
    return embed
