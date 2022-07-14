from IreneAPIWrapper.models import Channel, Guild
from models import Bot
from typing import Optional
import disnake


async def get_channel_model(channel_id, guild_id) -> Channel:
    """Get a channel model."""
    channel_model = await Channel.get(channel_id)
    if not channel_model:
        await Channel.insert(channel_id, guild_id)
        channel_model = await Channel.get(channel_id)
    return channel_model


async def create_guild_model(guild):
    """Create a guild model if it does not already exist."""
    guild_model = await Guild.get(guild.id)
    if not guild_model:
        await Guild.insert(
            guild_id=guild.id,
            name=guild.name,
            emoji_count=len(guild.emojis),
            afk_timeout=guild.afk_timeout,
            icon=guild.icon.url,
            owner_id=guild.owner_id,
            banner=guild.banner.url,
            description=guild.description,
            mfa_level=guild.mfa_level,
            splash=guild.splash.url,
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


async def get_discord_channel(
    bot: Bot, channel: Channel
) -> Optional[disnake.TextChannel]:
    """Get a discord channel without worrying about errors."""
    discord_channel = bot.get_channel(channel.id)
    try:
        if not discord_channel:
            discord_channel = await bot.fetch_channel(channel.id)
    except Exception as e:
        print(f"Failed to fetch channel {channel.id} - {e}")
    return discord_channel
