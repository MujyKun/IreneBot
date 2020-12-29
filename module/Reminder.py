from module.keys import reminder_limit
from discord.ext import commands, tasks
from Utility import resources as ex
import datetime
import pytz
import discord


# noinspection PyBroadException,PyPep8
class Reminder(commands.Cog):
    def __init__(self):
        self.set_timezone_format = "settimezone (timezone abbreviation) (country code)"

    # TODO: add remindlater command or reacts to the reminder

    @commands.command(aliases=["listreminds", "reminders", "reminds"])
    async def listreminders(self, ctx):
        """Lists out all of your reminders.
        [Format: %listreminders]"""
        remind_list = await ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await ex.u_reminder.get_user_timezone(ctx.author.id)

        if not remind_list:
            return await ctx.send(f"> {ctx.author.display_name}, you have no reminders.")

        m_embed = await ex.create_embed(title="Reminders List")
        embed_list = []
        remind_number = 1
        index_number = 1
        for remind_id, remind_reason, remind_time in remind_list:
            if user_timezone:
                remind_time = remind_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
            m_embed.add_field(name=f"{index_number}) {remind_reason}",
                              value=f"{await ex.u_reminder.get_locale_time(remind_time,user_timezone)}",
                              inline=False)
            remind_number += 1
            index_number += 1
            if remind_number == 11:
                embed_list.append(m_embed)
                m_embed = await ex.create_embed(title="Reminders List")
                remind_number = 1
        if remind_number:
            embed_list.append(m_embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command(aliases=["removeremind"])
    async def removereminder(self, ctx, reminder_index: int):
        """Remove one of your reminders.
        [Format: %removereminder (reminder index)]"""
        reminders = ex.cache.reminders.get(ctx.author.id)
        user_timezone = await ex.u_reminder.get_user_timezone(ctx.author.id)
        if not reminders:
            return await ctx.send(f"> {ctx.author.display_name}, you have no reminders.")
        else:
            try:
                remind_id, remind_reason, remind_time = reminders[reminder_index-1]
                remind_time = remind_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
                await ctx.send(f"> {ctx.author.display_name}, I will not remind you to **{remind_reason}**"
                               f" on `{await ex.u_reminder.get_locale_time(remind_time,user_timezone)}`.")
                await ex.u_reminder.remove_user_reminder(ctx.author.id, remind_id)
            except:
                return await ctx.send(f"> {ctx.author.display_name}, I could not find index {reminder_index}.")

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        """Create a reminder to do a task at a certain time.
        [Format: %remindme to ______ at 9PM
        or
        %remindme to ____ in 6hrs 30mins]"""
        reminders = ex.cache.reminders.get(ctx.author.id)
        user_timezone = await ex.u_reminder.get_user_timezone(ctx.author.id)
        if reminders:
            if len(reminders) >= reminder_limit:
                return await ctx.send(f"> {ctx.author.display_name}, You have reached the maximum limit "
                                      f"({reminder_limit}) for reminders you can have.")
        server_prefix = await ex.get_server_prefix_by_context(ctx)
        try:
            is_relative_time, type_index = await ex.u_reminder.determine_time_type(user_input)
        except ex.exceptions.ImproperFormat:
            return await ctx.send(
                f"> {ctx.author.display_name}, that is not a proper reminder format. Use `{server_prefix}help remindme`"
                f" for help with the acceptable format.")

        if is_relative_time is None:
            return await ctx.send(
                f"> {ctx.author.display_name}, that is not a proper reminder format. Use `{server_prefix}help remindme`"
                f" for help with the acceptable format.")
        remind_reason = await ex.u_reminder.process_reminder_reason(user_input, type_index)
        try:
            remind_time = await ex.u_reminder.process_reminder_time(user_input, type_index, is_relative_time, ctx.author.id)
        except ex.exceptions.ImproperFormat:
            return await ctx.send(f"{ctx.author.display_name}, you did not enter the correct time format.")
        except ex.exceptions.TooLarge:
            return await ctx.send(
                f"> {ctx.author.display_name}, the time for a reminder can not be greater than 2 years.")
        except ex.exceptions.NoTimeZone:
            return await ctx.send(f"> {ctx.author.display_name}, you do not have a timezone set. Please use "
                                  f"`{server_prefix}{self.set_timezone_format}`")

        await ex.u_reminder.set_reminder(remind_reason, remind_time, ctx.author.id)
        return await ctx.send(
            f"> {ctx.author.display_name}, I will remind you to **{remind_reason}** on "
            f"`{await ex.u_reminder.get_locale_time(remind_time,user_timezone)}`")

    @commands.command(aliases=['gettz', 'time'])
    async def gettimezone(self, ctx, user: discord.Member = None):
        """Get your current set timezone.
        [Format: %gettimezone]"""
        server_prefix = await ex.get_server_prefix_by_context(ctx)

        if not user:
            user = ctx.author
        user_timezone = await ex.u_reminder.get_user_timezone(user.id)
        help_message = f" Please use `{server_prefix}{self.set_timezone_format}`."
        if not user_timezone:
            return await ctx.send(f"> {user.display_name}{', you do' if user==ctx.author else ' does'}"
                                  f" not have a timezone set." + (help_message if user == ctx.author else ""))

        current_time = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%I:%M:%S %p')
        timezone_abbrev = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('UTC%z')
        return await ctx.send(
            f"> {user.display_name}{', your' if user==ctx.author else chr(39)+'s'} current time is "
            f"`{current_time}` in the timezone `{user_timezone} {timezone_abbrev}`")

    @commands.command(aliases=['settz'])
    async def settimezone(self, ctx, timezone_name=None, country_code=None):
        """Set your local timezone with a timezone abbreviation and country code.
        [Format: %settimezone (timezone name) (country code)]"""
        if not timezone_name and not country_code:
            await ex.u_reminder.remove_user_timezone(ctx.author.id)
            return await ctx.send(f"> {ctx.author.display_name}, if your timezone was set, it was removed.")

        server_prefix = await ex.get_server_prefix_by_context(ctx)
        user_timezone = await ex.u_reminder.process_timezone_input(timezone_name, country_code)
        if not user_timezone:
            return await ctx.send(f"> {ctx.author.display_name}, that is not a valid timezone. "
                                  f"Please use {server_prefix}settimezone (timezone name) (country code).")

        timezone_utc = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('UTC%z')
        native_time = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%c')
        await ex.u_reminder.set_user_timezone(ctx.author.id, user_timezone)
        return await ctx.send(f"> {ctx.author.display_name}, your timezone has been set to `{user_timezone} "
                              f"{timezone_utc}`, where it is currently `{native_time}`")

    @tasks.loop(seconds=5, minutes=0, hours=0, reconnect=True)
    async def reminder_loop(self):
        """Process for checking for reminders and sending them out if they are past overdue."""
        for user_id in ex.cache.reminders:
            reminders = ex.cache.reminders.get(user_id)
            if not reminders:
                return
            for remind_id, remind_reason, remind_time in reminders:
                try:
                    current_time = datetime.datetime.now(remind_time.tzinfo)
                    if current_time < remind_time:
                        return
                    dm_channel = await ex.get_dm_channel(user_id=user_id)
                    if dm_channel:
                        title_desc = f"This is a reminder to **{remind_reason}**."
                        embed = await ex.create_embed(title="Reminder", title_desc=title_desc)
                        await dm_channel.send(embed=embed)
                        await ex.u_reminder.remove_user_reminder(user_id, remind_id)
                except:
                    pass  # likely forbidden error -> do not have access to dm user

