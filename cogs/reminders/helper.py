import disnake
from IreneAPIWrapper.models import User, Date, Reminder
from datetime import datetime, timedelta
from ..helper import send_message, defer_inter, add_embed_footer_and_author, get_message
from typing import List


def get_periods(*args, **kwargs):
    """Get all time periods available for reminders."""
    return ["minute(s)", "hour(s)", "day(s)", "week(s)", "month(s)", "year(s)"]


def get_period_times(*args, **kwargs):
    """Get all period times in seconds."""
    return [60, 3600, 86400, 604800, 2629800, 31557600]


def get_matching_period_time(period):
    """Get the period time of a selection in seconds."""
    index = get_periods().index(period)
    return get_period_times()[index]


async def process_reminder_add(
    user_id: int,
    reason: str,
    _in: float,
    period: str,
    inter=None,
    allowed_mentions=None,
):
    """
    Process the addition of a reminder.

    :param user_id: int
        The user ID.
    :param reason: str
        The reason to be reminded for.
    :param _in: float
        When to be reminded.
    :param period: str
        "minute(s)", "hour(s)", "day(s)", "week(s)", "month(s)", "year(s)"
    :param inter: AppCmdInter
        Slash Command Context
    :param allowed_mentions:
        The mentions allowed.
    """
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)
    multiplier = get_matching_period_time(period)
    seconds_to_complete = multiplier * _in
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(seconds=seconds_to_complete)
    date_id = await Date.insert(start_time, end_time)
    date = await Date.get(date_id)
    remind_id = await Reminder.insert(user_id, reason, date)

    return await send_message(
        key="remind_success",
        user=user,
        inter=inter,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )


async def process_reminder_remove(
    user_id, remind_id: int, inter=None, allowed_mentions=None
):
    """
    Process the removal of a reminder.
    :param user_id: int
        The user's ID.
    :param remind_id: int
        The reminder ID.
    :param inter: AppCmdInter
        Slash Command Context
    :param allowed_mentions:
        The mentions allowed.
    """
    response_deferred = await defer_inter(inter)
    user = await User.get(user_id)
    reminder = await Reminder.get(remind_id)
    if reminder:
        await reminder.delete()

    return await send_message(
        key="reminder_deleted",
        user=user,
        inter=inter,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )


async def post_reminder(bot, reminder: Reminder):
    """Post a reminder to a user's DM."""
    try:
        user: disnake.User = bot.get_user(reminder.user_id) or await bot.fetch_user(
            reminder.user_id
        )
    except Exception as e:
        return bot.logger.warn(f"Failed to fetch user id: {reminder.user_id}")

    if not user:
        return

    desc = await get_message(
        await User.get(reminder.user_id), "reminder_description", f"{reminder.reason}"
    )

    embed = disnake.Embed(
        color=disnake.Color.random(), title="Reminder", description=desc
    )
    embed = await add_embed_footer_and_author(embed)

    try:
        await user.send(embed=embed)
    except Exception as e:
        return bot.logger.warn(
            f"Failed to send reminder id {reminder.id} to {reminder.user_id}"
        )


async def auto_complete_get_reminders(inter, user_input: str):
    """Auto complete get the reminders of a user."""
    user_id = inter.author.id
    await User.get(user_id)
    return [
        f"{reminder.id}) | Reason: {reminder.reason} | End Date: {str(reminder.date.end)}"
        for reminder in await Reminder.get_all()
        if user_id == reminder.user_id
    ]


async def process_reminder_loop(bot):
    """Process the reminder loop."""
    # we want to fetch all reminders from the api, not get from the cache
    # performance wise, there should be no noticeable difference
    # unless the database has millions of rows.
    # we can also get from the cache if needed be in the future.
    reminders: List[Reminder] = await Reminder.fetch_all()
    for reminder in reminders:
        date = reminder.date
        if not date.end:
            continue

        end_date = datetime.strptime(date.end, "%Y-%m-%d %H:%M:%S.%f")
        if datetime.utcnow() > end_date:
            try:
                await post_reminder(bot, reminder)
                await reminder.delete()
            except Exception as e:
                bot.logger.warn(
                    f"{e} -> Failed to post/delete Reminder ID: {reminder.id} -> DATE ID: {reminder.date.id} "
                    f"-> USER ID: {reminder.user_id} -> REASON: {reminder.reason}"
                )
