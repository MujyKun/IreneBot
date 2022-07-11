import random
from typing import List, Union

import disnake
from IreneAPIWrapper.models.twitchaccount import TwitchAccount
from IreneAPIWrapper.models import Person, Group, Channel, Guild
from disnake.ext import commands


async def _subscribe(twitch_username, guild: disnake.Guild, channel_id, role_id=None):
    """Internal subscribe."""
    channel_model = await get_channel_model(channel_id)
    channel_model.guild_id = guild.id
    await create_guild_model(guild)

    twitch_account = await TwitchAccount.get(twitch_username)
    if not twitch_account:
        await TwitchAccount.insert(
            twitch_username, guild_id=guild.id, channel_id=channel_id, role_id=role_id
        )
        return
    else:
        await twitch_account.subscribe(channel=channel_model, role_id=role_id)


async def _unsubscribe(twitch_username, channel_id):
    """Internal unsubscribe."""
    twitch_account = await TwitchAccount.get(twitch_username)
    channel_model = await get_channel_model(channel_id)

    if not twitch_account or not channel_model:
        return

    await twitch_account.unsubscribe(channel_model)


async def get_subscribed(guild):
    """Get all the twitch accounts subbed to in a guild."""
    await create_guild_model(guild)
    return await TwitchAccount.subbed_in(guild_id=guild.id)


async def get_subbed_msg(guild: disnake.Guild):
    """Get a message containing a list of subscriptions belonging to the guild."""
    accounts: List[TwitchAccount] = await get_subscribed(guild)
    channels = [
        await get_channel_model(t_channel.id) for t_channel in guild.text_channels
    ]
    msg = f"These are the twitch subscriptions in {guild.name}:\n\n"

    for account in accounts:
        subbed_channels = account.check_subscribed(channels)
        display_channels = ", ".join(
            ["<#{}>".format(_ch.id) for _ch in subbed_channels]
        )
        msg += f"{account.name} is subscribed in: {display_channels}\n"

    return msg


async def get_channel_model(channel_id) -> Channel:
    """Get a channel model."""
    channel_model = await Channel.get(channel_id)
    if not channel_model:
        await Channel.insert(channel_id)
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


async def process_add(
    channel_to_notify: disnake.TextChannel,
    guild: disnake.Guild,
    twitch_username: str,
    role_id: int = None,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Subscribe to a twitch account."""
    twitch_username = twitch_username.lower()
    if not await TwitchAccount.check_user_exists(twitch_username):
        msg = "That username does not exist on Twitch."
        if ctx:
            await ctx.send(msg)
        if inter:
            await inter.send(msg)
        return

    await _subscribe(
        twitch_username,
        channel_id=channel_to_notify.id,
        guild=guild,
        role_id=role_id,
    )

    msg = f"{channel_to_notify.mention} is now subscribed to {twitch_username}."
    if ctx:
        await ctx.send(msg, allowed_mentions=allowed_mentions)
    if inter:
        await inter.send(msg, allowed_mentions=allowed_mentions)


async def process_remove(
    channel_to_notify: disnake.TextChannel,
    twitch_username: str,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Unsubscribe from a twitch account."""
    twitch_username = twitch_username.lower()
    await _unsubscribe(twitch_username, channel_id=channel_to_notify.id)
    msg = f"{channel_to_notify.mention} is no longer subscribed to {twitch_username}."
    if ctx:
        await ctx.reply(msg, allowed_mentions=allowed_mentions)
    if inter:
        await inter.send(msg, allowed_mentions=allowed_mentions)


async def auto_complete_type_subbed_guild(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the twitch accounts subscribed to in a guild."""
    accounts: List[TwitchAccount] = await get_subscribed(inter.guild)
    return [account.name for account in accounts]
