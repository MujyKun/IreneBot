from typing import List, Union, Optional

import disnake
from IreneAPIWrapper.models import TwitterAccount, Channel, Tweet
from disnake.ext import commands
from models import Bot
from ..helper import (
    get_channel_model,
    create_guild_model,
    get_discord_channel,
    send_message,
)


async def _subscribe(twitter_username, guild: disnake.Guild, channel_id, role_id=None):
    """Internal subscribe."""
    channel_model = await get_channel_model(channel_id, guild.id)
    if not channel_model.guild_id:
        channel_model.guild_id = guild.id
    await create_guild_model(guild)

    twitter_account = await TwitterAccount.get(twitter_username)
    if not twitter_account:
        await TwitterAccount.insert(
            twitter_username, guild_id=guild.id, channel_id=channel_id, role_id=role_id
        )
        return
    else:
        await twitter_account.subscribe(channel=channel_model, role_id=role_id)


async def _unsubscribe(twitter_username, channel_id, guild_id):
    """Internal unsubscribe."""
    twitter_account = await TwitterAccount.get(twitter_username)
    channel_model = await get_channel_model(channel_id, guild_id)

    if not twitter_account or not channel_model:
        return

    await twitter_account.unsubscribe(channel_model)


async def process_add(
    channel_to_notify: disnake.TextChannel,
    guild: disnake.Guild,
    twitter_username: str,
    role_id: int = None,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Subscribe to a twitch account."""
    twitter_username = twitter_username.lower()
    if not await TwitterAccount.check_user_exists(twitter_username):
        msg = "That username does not exist on Twitter."
        await send_message(
            msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )
        return

    await _subscribe(
        twitter_username,
        channel_id=channel_to_notify.id,
        guild=guild,
        role_id=role_id,
    )

    msg = f"{channel_to_notify.mention} is now subscribed to {twitter_username} on Twitter."
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def get_subscribed(guild):
    """Get all the Twitter accounts subbed to in a guild."""
    await create_guild_model(guild)
    return await TwitterAccount.subbed_in(guild_id=guild.id)


async def get_subbed_msg(guild: disnake.Guild):
    """Get a message containing a list of subscriptions belonging to the guild."""
    accounts: List[TwitterAccount] = await get_subscribed(guild)
    channels = [
        await get_channel_model(t_channel.id, guild_id=guild.id)
        for t_channel in guild.text_channels
    ]
    msg = f"These are the Twitter subscriptions in {guild.name}:\n\n"

    for account in accounts:
        subbed_channels = account.check_subscribed(channels)
        display_channels = ", ".join(
            ["<#{}>".format(_ch.id) for _ch in subbed_channels]
        )
        msg += f"{account.name} is subscribed in: {display_channels}\n"

    return msg


async def process_remove(
    channel_to_notify: disnake.TextChannel,
    twitter_username: str,
    allowed_mentions=None,
    ctx: commands.Context = None,
    inter: disnake.AppCmdInter = None,
):
    """Unsubscribe from a Twitter account."""
    twitter_username = twitter_username.lower()
    await _unsubscribe(
        twitter_username,
        channel_id=channel_to_notify.id,
        guild_id=channel_to_notify.guild.id,
    )
    msg = f"{channel_to_notify.mention} is no longer subscribed to {twitter_username}."
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def auto_complete_type_subbed_guild(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the twitch accounts subscribed to in a guild."""
    accounts: List[TwitterAccount] = await get_subscribed(inter.guild)
    return [account.name for account in accounts]


async def send_twitter_notifications(
    bot: Bot, twitter_account: TwitterAccount, tweets: List[Tweet]
):
    """Send twitter notifications to discord channels that need it."""
    failed_channels = []
    success_channels = []

    for tweet in tweets:
        twitter_link = f"https://twitter.com/{twitter_account.name}/status/{tweet.id}"
        for channel in twitter_account:
            role_id = await twitter_account.get_role_id(channel)
            role_msg = "Hey " + "@everyone" if not role_id else f"<@&{role_id}>"
            msg = (
                role_msg
                + f", A new tweet from {twitter_account.name} is available:\n {twitter_link}"
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
                print(f"send_twitter_notifications - {discord_channel.id} - {e}")

    for channel in failed_channels:
        # getting and fetching the channel did not work.
        # or failed to send a message.
        # remove it from our subscriptions.
        await twitter_account.unsubscribe(channel)
        print(
            f"Unsubscribed Channel {channel.id} from Twitter Account {twitter_account.id} - {twitter_account.name} "
            f"due to a fetching or message send failure."
        )

    return success_channels
