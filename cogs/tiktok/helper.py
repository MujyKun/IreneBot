from typing import List

import disnake
from IreneAPIWrapper.models import TikTokAccount
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
from keys import get_keys
from util import logger


async def _subscribe(tiktok_username, user_id, guild: disnake.Guild, channel_id, role_id=None):
    """Internal subscribe."""
    channel_model = await get_channel_model(channel_id, guild_id=guild.id)
    channel_model.guild_id = guild.id
    await create_guild_model(guild)

    account = await TikTokAccount.get(tiktok_username)
    if not account:
        return await TikTokAccount.insert(
            tiktok_username, user_id=user_id, channel_id=channel_id, role_id=role_id
        )
    else:
        return await account.subscribe(channel=channel_model, role_id=role_id, user_id=user_id)


async def _unsubscribe(tiktok_username, channel_id, guild_id):
    """Internal unsubscribe."""
    account = await TikTokAccount.get(tiktok_username)
    channel_model = await get_channel_model(channel_id, guild_id=guild_id)

    if not account or not channel_model:
        return False

    await account.unsubscribe(channel_model)
    return True


async def get_subscribed(channel_id, guild_id):
    """Get all the TikTok accounts subbed to in a channel."""
    channel_model = await get_channel_model(channel_id, guild_id=guild_id)
    accounts = []
    account: TikTokAccount
    for account in await TikTokAccount.get_all():
        if account.check_subscribed([channel_model]):
            accounts.append(account)
    return accounts


async def get_subbed_msg(channel_id, guild: disnake.Guild, user_id: int):
    """Get a message containing a list of subscriptions belonging to the guild."""
    user = await User.get(user_id)
    accounts: List[TikTokAccount] = await get_subscribed(channel_id, guild)
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

    # return await get_message(user, "tiktok_list", guild.name, sub_msg)
    return await get_message(user, "tiktok_list", "this channel", sub_msg)


async def check_user_subscribe_limit(user_id: int) -> bool:
    """Check the user is within the limit of TikTok accounts to subscribe to."""
    num_of_users = sum([user_id in account.user_ids for account in await TikTokAccount.get_all()])
    return num_of_users < get_keys().tiktok_limit


async def process_add(
    channel_to_notify: disnake.TextChannel,
    guild: disnake.Guild,
    tiktok_username: str,
    user_id: int,
    role_id: int = None,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Subscribe to a TikTok account."""
    user = await User.get(user_id)

    if not user.is_considered_patron:
        return await send_message(
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            key="become_a_patron_limited",
        )

    if await check_user_subscribe_limit(user_id) is False:
        return await send_message(
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            key="limit_reached",
        )

    tiktok_username = tiktok_username.lower().replace("@", "")

    result = await _subscribe(
        tiktok_username,
        user_id=user_id,
        channel_id=channel_to_notify.id,
        guild=guild,
        role_id=role_id,
    )

    if result is False:
        return await send_message(
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            key="error_tiktok_username",
        )

    return await send_message(
        channel_to_notify.mention,
        tiktok_username,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        key="tiktok_subscribed",
    )


async def process_remove(
    channel_id: disnake.TextChannel,
    tiktok_username: str,
    user_id: int,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Unsubscribe from a TikTok account."""
    user = await User.get(user_id)
    tiktok_username = tiktok_username.lower()
    await _unsubscribe(
        tiktok_username,
        channel_id=channel_id.id,
        guild_id=channel_id.guild.id,
    )
    return await send_message(
        channel_id.mention,
        tiktok_username,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        key="tiktok_unsubscribed",
    )


async def auto_complete_type_subbed_channel(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the TikTok accounts subscribed to in a channel."""
    accounts: List[TikTokAccount] = await get_subscribed(inter.channel_id, inter.guild_id)
    return [account.name for account in accounts][:24]


async def send_tiktok_notifications(
    bot: Bot, channels: List[Channel], tiktok_account: TikTokAccount, video_id: int
):
    """Send TikTok notifications to discord channels that need it."""
    failed_channels = []
    success_channels = []

    for channel in channels:
        role_id = await tiktok_account.get_role_id(channel)
        role_msg = "Hey " + "@everyone" if not role_id else f"<@&{role_id}>"
        msg = (
            role_msg
            + f", {tiktok_account.id} has posted on TikTok at https://www.tiktok.com/@{tiktok_account.name}/video/{video_id} ! "
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
            logger.error(f"send_tiktok_notifications - {discord_channel.id} - {e}")

    for channel in failed_channels:
        # getting and fetching the channel did not work.
        # or failed to send a message.
        # remove it from our subscriptions.
        await tiktok_account.unsubscribe(channel)
        logger.info(
            f"Unsubscribed Channel {channel.id} from TikTok Account {tiktok_account.id} "
            f"due to a fetching or message send failure."
        )

    return success_channels
