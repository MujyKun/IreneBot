from IreneAPIWrapper.models import Channel, Guild, User, Language, PackMessage
from IreneAPIWrapper.exceptions import IncorrectNumberOfItems
from typing import Optional, Union, List

from disnake import Embed
from disnake.ext import commands
from util import logger
import disnake
from keys import get_keys
from models import Trackable, StatsTracker
from tracemalloc import get_traced_memory

LIMIT_ROUNDS = [3, 60]
LIMIT_TIMEOUT = [5, 60]
BRACKET_SIZE_OPTIONS = [8, 16, 32, 64]
DIFFICULTY_OPTIONS = ["easy", "medium", "hard"]
GENDER_OPTIONS = ["male", "female", "mixed"]
NSFW_OPTIONS = ["yes", "no"]


async def set_trackable(name, value, frequency=None):
    """Set a trackable to a new value."""
    trackable = await get_trackable(name)
    trackable.value = value
    if frequency and trackable.frequency != frequency:
        trackable.frequency = frequency


async def get_trackable(name) -> Trackable:
    """Get a trackable."""
    stats_tracker = await get_tracker()
    trackable: Optional[Trackable] = stats_tracker.trackables.get(name, None)
    if not trackable:
        trackable = Trackable(name)
        stats_tracker.trackables[name] = trackable
    return trackable


async def increment_trackable(name, frequency=None):
    """Increment a trackable by 1."""
    trackable = await get_trackable(name)
    trackable.value += 1

    if frequency and trackable.frequency != frequency:
        trackable.frequency = frequency


async def get_tracker() -> StatsTracker:
    """Get the available tracker."""
    return _trackable


_trackable = StatsTracker()


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
            icon=None if not guild.icon else guild.icon.url,
            owner_id=guild.owner_id,
            banner=None if not guild.banner else guild.banner.url,
            description=guild.description,
            mfa_level=guild.mfa_level,
            splash=None if not guild.splash else guild.splash.url,
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


async def get_discord_channel(bot, channel: Channel) -> Optional[disnake.TextChannel]:
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
    view: disnake.ui.View = None,
    delete_after: int = None,
    embed: Optional[disnake.Embed] = None,
    embeds: Optional[List[Embed]] = None,
    response_deferred: bool = False,
    ephemeral: bool = False,
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
    :param view: disnake.ui.View
        The view for the message.
    :param delete_after: int
        Howmany seconds to delete the message after.
    :param embed: disnake.Embed
        Embedded message to send.
    :param embeds: List[disnake.Embed]
        Embedded messages to send.
    :param response_deferred: bool
        Whether a response was deferred (a pre-message was sent as an acknowledgement).
    :param ephemeral: bool
        Whether a message should only be visible to the user. Only possible with interaction commands.
    """
    if (user and key) and not msg:
        msg = await get_message(user, key, *custom_args)

    if not msg and not embed and not embeds:
        logger.error(
            f"No message to send -> "
            f"Custom Args: {custom_args}, "
            f"Message: {msg}, "
            f"CTX: {ctx}, "
            f"INTER: {inter}, "
            f"EMBED: {embed},"
            f"EMBEDS: {embeds},"
            f"Allowed Mentions: {allowed_mentions}, "
            f"Key: {key}"
        )
        return

    if msg:
        msg = msg.replace("\\n", "\n")

    final_msgs = []
    if ctx:
        final_msgs.append(
            await ctx.send(
                msg,
                allowed_mentions=allowed_mentions,
                view=view,
                delete_after=delete_after,
                embed=embed,
                embeds=embeds,
            )
        )  # ignore warning caused by embeds.
    if channel:
        final_msgs.append(
            await channel.send(
                msg,
                allowed_mentions=allowed_mentions,
                view=view,
                delete_after=delete_after,
                embed=embed,
                embeds=embeds,
            )
        )  # ignore warning caused by embeds.
    if inter:
        if not view:
            view = disnake.utils.MISSING
        if not allowed_mentions:
            allowed_mentions = disnake.utils.MISSING
        if not delete_after:
            delete_after = disnake.utils.MISSING
        if not embed:
            embed = disnake.utils.MISSING
        if not embeds:
            embeds = disnake.utils.MISSING
        if not response_deferred:
            final_msgs.append(
                await inter.send(
                    msg,
                    allowed_mentions=allowed_mentions,
                    view=view,
                    delete_after=delete_after,
                    embed=embed,
                    embeds=embeds,
                    ephemeral=ephemeral,
                )
            )
        else:
            try:
                final_msgs.append(
                    await inter.edit_original_response(
                        msg,
                        allowed_mentions=allowed_mentions,
                        view=view,
                        embed=embed,
                        embeds=embeds,
                    )
                )
            except Exception as e:
                print(e)

    return final_msgs


async def check_game_input(
    user,
    bracket_size=None,
    max_rounds=None,
    timeout=None,
    difficulty=None,
    gender=None,
    contains_nsfw=None,
) -> Union[str, bool]:
    """Check the inputs for a guessing game and return a string with all errors."""
    input_err_msgs = [await get_message(user, "error_invalid_input")]

    if bracket_size and bracket_size not in BRACKET_SIZE_OPTIONS:
        input_err_msgs.append(
            await get_message(user, "error_bracket_size", BRACKET_SIZE_OPTIONS)
        )
    if max_rounds and not LIMIT_ROUNDS[0] <= max_rounds <= LIMIT_ROUNDS[1]:
        input_err_msgs.append(
            await get_message(
                user, "error_limit_rounds", LIMIT_ROUNDS[0], LIMIT_ROUNDS[1]
            )
        )
    if difficulty and difficulty.lower() not in DIFFICULTY_OPTIONS:
        input_err_msgs.append(
            await get_message(
                user, "error_difficulty_options", ", ".join(DIFFICULTY_OPTIONS)
            )
        )
    if gender and gender.lower() not in GENDER_OPTIONS:
        input_err_msgs.append(
            await get_message(user, "error_gender_options", ", ".join(GENDER_OPTIONS))
        )
    if timeout and not LIMIT_TIMEOUT[0] <= timeout <= LIMIT_TIMEOUT[1]:
        input_err_msgs.append(
            await get_message(
                user, "error_timeout_options", LIMIT_TIMEOUT[0], LIMIT_TIMEOUT[1]
            )
        )
    if contains_nsfw and contains_nsfw.lower() not in NSFW_OPTIONS:
        input_err_msgs.append(
            await get_message(
                user, "error_nsfw_options", NSFW_OPTIONS[0], NSFW_OPTIONS[1]
            )
        )

    if len(input_err_msgs) > 1:
        return "\n".join(input_err_msgs)
    return True


async def in_game(user: User, must_be_host=True) -> bool:
    """Check if a user is in a game.

    :param user: IreneAPIWrapper.models.User
        The user object.
    :param must_be_host: bool
        Whether the user needs to be the host of the game.
    """
    from models import all_games as all_games

    in_game_not_host = False

    if not must_be_host:
        in_game_not_host = any(
            [
                game
                for game in all_games
                if game.players.get(user.id) and not game.is_complete
            ]
        )

    in_game_host = any(
        [game for game in all_games if game.host_user == user and not game.is_complete]
    )

    return in_game_host or in_game_not_host


async def add_embed_footer_and_author(embed: disnake.Embed) -> disnake.Embed:
    """Add a footer and author to an embed."""
    _keys = get_keys()
    if _keys.embed_icon_url:
        embed.set_author(
            name="Irene",
            url=_keys.bot_website_url,
            icon_url=_keys.embed_icon_url,
        )
    if _keys.embed_footer_url:
        embed.set_footer(
            text="Thanks for using Irene!", icon_url=_keys.embed_footer_url
        )
    return embed


async def defer_inter(inter, ephemeral=False):
    """Defer an interaction."""
    response_deferred = False
    if inter:
        response_deferred = await inter.response.defer(
            with_message=True, ephemeral=ephemeral
        )
    return response_deferred


async def get_memory_usage():
    current, peak = get_traced_memory()
    return current, peak  # bytes -> Divide by 1048576 for MiB
