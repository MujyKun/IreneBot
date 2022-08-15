from typing import List

import disnake
from IreneAPIWrapper.models import TwitchAccount
from IreneAPIWrapper.models import Channel, User
from disnake.ext import commands
from models import Bot
from ..helper import (
    get_channel_model,
    create_guild_model,
    get_discord_channel,
    send_message,
    get_message,
)
from util import logger


async def _subscribe(twitch_username, guild: disnake.Guild, channel_id, role_id=None):
    """Internal subscribe."""
    channel_model = await get_channel_model(channel_id, guild_id=guild.id)
    channel_model.guild_id = guild.id
    await create_guild_model(guild)

    twitch_account = await TwitchAccount.get(twitch_username)
    if not twitch_account:
        await TwitchAccount.insert(
            twitch_username, channel_id=channel_id, role_id=role_id)
        return
    else:
        await twitch_account.subscribe(channel=channel_model, role_id=role_id)


async def _unsubscribe(twitch_username, channel_id, guild_id):
    """Internal unsubscribe."""
    twitch_account = await TwitchAccount.get(twitch_username)
    channel_model = await get_channel_model(channel_id, guild_id=guild_id)

    if not twitch_account or not channel_model:
        return

    await twitch_account.unsubscribe(channel_model)


async def get_subscribed(guild):
    """Get all the twitch accounts subbed to in a guild."""
    await create_guild_model(guild)
    return await TwitchAccount.subbed_in(guild_id=guild.id)


async def get_subbed_msg(guild: disnake.Guild, user_id: int):
    """Get a message containing a list of subscriptions belonging to the guild."""
    user = await User.get(user_id)
    accounts: List[TwitchAccount] = await get_subscribed(guild)
    channels = [
        await get_channel_model(t_channel.id, guild_id=guild.id)
        for t_channel in guild.text_channels
    ]
    sub_msg = ""

    for account in accounts:
        subbed_channels = account.check_subscribed(channels)
        display_channels = ", ".join(
            ["<#{}>".format(_ch.id) for _ch in subbed_channels]
        )
        sub_msg += f"{account.name} is subscribed in: {display_channels}\n"

    return await get_message(user, "twitch_list", guild.name, sub_msg)


async def process_add(
    channel_to_notify: disnake.TextChannel,
    guild: disnake.Guild,
    twitch_username: str,
    user_id: int,
    role_id: int = None,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Subscribe to a twitch account."""
    user = await User.get(user_id)

    twitch_username = twitch_username.lower()
    if not await TwitchAccount.check_user_exists(twitch_username):
        return await send_message(
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            key="error_twitch_username",
        )

    await _subscribe(
        twitch_username,
        channel_id=channel_to_notify.id,
        guild=guild,
        role_id=role_id,
    )

    return await send_message(
        channel_to_notify.mention,
        twitch_username,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        key="twitch_subscribed",
    )


async def process_remove(
    channel_to_notify: disnake.TextChannel,
    twitch_username: str,
    user_id: int,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Unsubscribe from a twitch account."""
    user = await User.get(user_id)
    twitch_username = twitch_username.lower()
    await _unsubscribe(
        twitch_username,
        channel_id=channel_to_notify.id,
        guild_id=channel_to_notify.guild.id,
    )
    return await send_message(
        channel_to_notify.mention,
        twitch_username,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        key="twitch_unsubscribed",
    )


async def auto_complete_type_subbed_guild(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the twitch accounts subscribed to in a guild."""
    accounts: List[TwitchAccount] = await get_subscribed(inter.guild)
    return [account.name for account in accounts]


async def send_twitch_notifications(
    bot: Bot, channels: List[Channel], twitch_account: TwitchAccount
):
    """Send twitch notifications to discord channels that need it."""
    failed_channels = []
    success_channels = []

    for channel in channels:
        role_id = await twitch_account.get_role_id(channel)
        role_msg = "Hey " + "@everyone" if not role_id else f"<@&{role_id}>"
        msg = (
            role_msg
            + f", {twitch_account.id} is now live on https://www.twitch.tv/{twitch_account.id} ! "
            f"Make sure to go check it out!"
        )
        discord_channel = await get_discord_channel(bot, channel)
        if discord_channel is None:
            failed_channels.append(channel)
            continue
        try:
            await discord_channel.send(msg)
            success_channels.append(channel)
        except Exception as e:
            failed_channels.append(channel)
            logger.error(f"send_twitch_notifications - {discord_channel.id} - {e}")

    for channel in failed_channels:
        # getting and fetching the channel did not work.
        # or failed to send a message.
        # remove it from our subscriptions.
        await twitch_account.unsubscribe(channel)
        logger.info(
            f"Unsubscribed Channel {channel.id} from Twitch Account {twitch_account.id} "
            f"due to a fetching or message send failure."
        )

    return success_channels
