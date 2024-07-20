import random

import disnake
from IreneAPIWrapper.models import Channel, User, Interaction
from ..helper import (
    get_channel_model,
    create_guild_model,
    get_discord_channel,
    send_message,
    get_message,
    add_embed_footer_and_author,
)
from keys import get_keys


async def process_interaction(
    interaction_type,
    past_tense_interaction,
    attacker: disnake.Member,
    victim: disnake.Member,
    ctx=None,
    inter=None,
    allowed_mentions=None,
):
    user = await User.get(attacker.id)
    image_url = None
    desc = None

    interaction = random.choice(
        [
            interaction
            for interaction in list(await Interaction.get_all())
            if interaction.type.name.lower() == interaction_type
        ]
    )
    title = f"**{attacker.display_name}** {past_tense_interaction} **{victim.display_name}**"
    image_url = interaction.url
    if not interaction:
        return await send_message(
            key="interaction_no_results",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    embed = disnake.Embed(
        color=disnake.Color.random(), title=title, description=desc or None
    )
    if image_url:
        embed.set_image(url=image_url)
    embed = await add_embed_footer_and_author(embed)
    return await send_message(
        user=user, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions, embed=embed
    )
