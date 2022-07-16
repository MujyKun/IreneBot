from IreneAPIWrapper.models import Channel, Guild, User, Language, PackMessage
from IreneAPIWrapper.exceptions import IncorrectNumberOfItems
from models import Bot
from typing import Optional
from disnake.ext import commands
from util import logger
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


async def get_message(user, key, *custom_args):
    """Get a message from a user's language pack.

    :param user: IreneAPIWrapper.models.User
        A IreneAPIWrapper User Object
    :param key: str
        The PackMessage label/key for modification.
    :param custom_args:
        All custom args to replace
    """
    lang = Language.get_lang(user.language)
    pack_message = None
    if lang:
        pack_message: Optional[PackMessage] = lang[key.lower()]

    if not lang or not pack_message:
        lang = Language.get_english()
        pack_message: Optional[PackMessage] = lang[key.lower()]

    if pack_message:
        try:
            msg = pack_message.get(*custom_args)
        except IncorrectNumberOfItems as e:
            logger.error(f"ERROR: {e} -- ARGS: {custom_args}")
            # we will send the message without custom inputs filled in.
            msg = pack_message.message
        return msg


async def send_message(
    *custom_args,
    msg: str = None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
    channel: disnake.TextChannel = None,
    allowed_mentions: disnake.AllowedMentions = None,
    user: User = None,
    key: str = None,
):
    """Send a message to a discord channel/interaction.
    :param custom_args:
        All custom args to replace
    :param msg: str
        The message to send.
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param channel: disnake.TextChannel
        A discord Channel.
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    :param user: IreneAPIWrapper.models.User
        A IreneAPIWrapper User Object
    :param key: str
        The PackMessage label/key for modification.
    """
    if (user and key) and not msg:
        msg = await get_message(user, key, *custom_args)

    if not msg:
        logger.error(
            f"No message to send -> "
            f"Custom Args: {custom_args}, "
            f"Message: {msg}, "
            f"CTX: {ctx}, "
            f"INTER: {inter}, "
            f"Allowed Mentions: {allowed_mentions}, "
            f"Key: {key}"
        )
        return

    if ctx:
        await ctx.send(msg, allowed_mentions=allowed_mentions)
    if inter:
        await inter.send(msg, allowed_mentions=allowed_mentions)
    if channel:
        await channel.send(msg, allowed_mentions=allowed_mentions)
