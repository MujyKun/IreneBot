import random

import disnake
from IreneAPIWrapper.models.twitchaccount import TwitchAccount
from IreneAPIWrapper.models import Person, Group, Channel, Guild


async def subscribe(twitch_username, guild: disnake.Guild, channel_id, role_id=None):
    channel_model = await Channel.get(channel_id)
    if not channel_model:
        await Channel.insert(channel_id)
        channel_model = await Channel.get(channel_id)
        channel_model.guild_id = guild.id

    guild_model = await Guild.get(guild.id)
    if not guild_model:
        await Guild.insert(
            guild_id=guild.id,
            name=guild.name,
            emoji_count=len(guild.emojis),
            afk_timeout=guild.afk_timeout,
            icon=guild.icon.url,
            owner_id=guild.owner_id,
            banner=guild.banner,
            description=guild.description,
            mfa_level=guild.mfa_level,
            splash=guild.splash,
            nitro_level=guild.premium_tier,
            boosts=guild.premium_subscription_count,
            text_channel_count=len(guild.text_channels),
            voice_channel_count=len(guild.voice_channels),
            category_count=len(guild.categories),
            emoji_limit=guild.emoji_limit,
            member_count=guild.member_count,
            role_count=len(guild.roles),
            shard_id=guild.shard_id,
            create_date=guild.created_at,
            has_bot=True,
        )

    twitch_account = await TwitchAccount.get(twitch_username)
    if not twitch_account:
        await TwitchAccount.insert(twitch_username, guild_id=guild.id,
                                   channel_id=channel_id,
                                   role_id=role_id)
        return
    else:
        await twitch_account.subscribe(channel=channel_model, role_id=role_id)
