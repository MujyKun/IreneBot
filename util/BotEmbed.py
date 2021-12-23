from discord import Embed as disEmbed, User as disUser
from random import randint
from keys import Keys
from dislash import ActionRow, Button, ButtonStyle, SlashInteraction
from main import Bot

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


async def add_embed_inline_fields(embed: disEmbed, fields: dict) -> disEmbed:
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be inline"""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value)
    return embed


async def add_embed_listed_fields(embed: disEmbed, fields: dict) -> disEmbed:
    """Easily add fields to an embed through a dictionary of the field names and values. {name : value}
    All fields will be not be inline."""
    for f_name, f_value in fields.items():
        embed.add_field(name=f_name, value=f_value, inline=False)
    return embed


async def set_embed_author_and_footer(botkeys: Keys, embed, footer_message) -> disEmbed:
    """Sets the bot author and footer of an embed."""
    embed.set_author(name=botkeys.bot_name, url=botkeys.bot_website_url,
                     icon_url=botkeys.embed_icon_url)
    embed.set_footer(text=footer_message,
                     icon_url=botkeys.embed_icon_url)
    return embed


async def get_page_buttons(num_pages: int, current_page: int) -> list[ActionRow]:
    """Returns the 'Next' and 'Previous' buttons given the number of pages and the current page. The button will be
    disabled if you can no longer go back or forward in pages. If there are 6 or more pages, a 'First' and 'Last'
    button will be included."""
    is_first = (current_page == 0)
    is_end = (current_page == num_pages - 1)

    many_page_buttons = ActionRow(
        Button(
            style=ButtonStyle.gray,
            label="First",
            custom_id="first",
            disabled=is_first
        ),
        Button(
            style=ButtonStyle.gray,
            label="Previous",
            custom_id="prev",
            disabled=is_first
        ),
        Button(
            style=ButtonStyle.gray,
            label="Next",
            custom_id="next",
            disabled=is_end
        ),
        Button(
            style=ButtonStyle.gray,
            label="Last",
            custom_id="last",
            disabled=is_end
        )
    )

    few_page_buttons = ActionRow(
        Button(
            style=ButtonStyle.gray,
            label="Previous",
            custom_id="prev",
            disabled=is_first
        ),
        Button(
            style=ButtonStyle.gray,
            label="Next",
            custom_id="next",
            disabled=is_end
        )
    )
    if num_pages >= 6:
        return [many_page_buttons]
    else:
        return [few_page_buttons]


async def get_bot_info_buttons(bot: Bot) -> list[ActionRow]:
    """Generate bot link buttons for the support server, patreon link, website, and invite link."""
    info_buttons = ActionRow(
        Button(
            style=ButtonStyle.link,
            label="Get Help",
            url=bot.keys.support_server_invite_url,
            emoji="🤝"
        ),
        Button(
            style=ButtonStyle.link,
            label="Become a Patron",
            url=bot.keys.patreon_link,
            emoji="💰"
        ),
        Button(
            style=ButtonStyle.link,
            label="Bot Website",
            url=bot.keys.bot_website_url,
            emoji="🌐"
        ),
        Button(
            style=ButtonStyle.link,
            label="Bot Invite",
            url=bot.keys.bot_invite_url,
            emoji="🤖"
        ),
    )
    return [info_buttons]


async def create_paginated_embed(inter: SlashInteraction, embeds: list[disEmbed]) -> disEmbed:
    """Create a paginated embed with Previous/Next buttons to navigate through the different pages."""
    page_buttons = await get_page_buttons(len(embeds), 0)

    embed_idx = 0
    msg = await inter.reply(embed=embeds[embed_idx], components=page_buttons)
    on_click = msg.create_click_listener(timeout=60)

    @on_click.matching_id("first")
    async def first_button(inter: SlashInteraction):
        nonlocal embed_idx, msg, embeds
        embed_idx = 0

        new_page_buttons = await get_page_buttons(len(embeds), embed_idx)
        await msg.edit(embed=embeds[embed_idx], components=new_page_buttons)
        await inter.acknowledge()

    @on_click.matching_id("prev")
    async def prev_button(inter: SlashInteraction):
        nonlocal embed_idx, msg, embeds
        embed_idx -= 1

        new_page_buttons = await get_page_buttons(len(embeds), embed_idx)
        await msg.edit(embed=embeds[embed_idx], components=new_page_buttons)
        await inter.acknowledge()

    @on_click.matching_id("next")
    async def next_button(inter: SlashInteraction):
        nonlocal embed_idx, msg, embeds
        embed_idx += 1

        new_page_buttons = await get_page_buttons(len(embeds), embed_idx)
        await msg.edit(embed=embeds[embed_idx], components=new_page_buttons)
        await inter.acknowledge()

    @on_click.matching_id("last")
    async def last_button(inter: SlashInteraction):
        nonlocal embed_idx, msg, embeds
        embed_idx = len(embeds) - 1

        new_page_buttons = await get_page_buttons(len(embeds), embed_idx)
        await msg.edit(embed=embeds[embed_idx], components=new_page_buttons)
        await inter.acknowledge()

    @on_click.timeout
    async def on_timeout():
        nonlocal msg
        await msg.edit(components=[])

