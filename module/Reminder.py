from module.keys import reminder_limit
from discord.ext import commands, tasks
from Utility import resources as ex
import datetime
import pytz
import discord
import typing


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
            msg = await ex.get_msg(ctx, "reminder", "no_reminders")
            msg = await ex.replace(msg, ['name', ctx.author.display_name])
            return await ctx.send(msg)

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
        reminders = await ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await ex.u_reminder.get_user_timezone(ctx.author.id)
        if not reminders:
            msg = await ex.get_msg(ctx, "reminder", "no_reminders")
            msg = await ex.replace(msg, ['name', ctx.author.display_name])
            return await ctx.send(msg)
        else:
            try:
                remind_id, remind_reason, remind_time = reminders[reminder_index-1]
                if user_timezone:
                    remind_time = remind_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
                msg = await ex.get_msg(ctx, "reminder", "remove_reminder")
                msg = await ex.replace(msg, [['name', ctx.author.display_name],
                                             ['reason', remind_reason],
                                             ['time', await ex.u_reminder.get_locale_time(remind_time,user_timezone)]])
                await ctx.send(msg)
                await ex.u_reminder.remove_user_reminder(ctx.author.id, remind_id)
            except:
                msg = await ex.get_msg(ctx, "reminder", "index_not_found")
                msg = await ex.replace(msg, [['name', ctx.author.display_name], ['index', reminder_index]])
                return await ctx.send(msg)

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        """Create a reminder to do a task at a certain time.
        [Format: %remindme to ______ at 9PM
        or
        %remindme to ____ in 6hrs 30mins]"""
        reminders = await ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await ex.u_reminder.get_user_timezone(ctx.author.id)
        if reminders:
            if len(reminders) >= reminder_limit:
                msg = await ex.get_msg(ctx, "reminder", "max_reminders")
                msg = await ex.replace(msg, [["name", ctx.author.display_name], ["reminder_limit", reminder_limit]])
                return await ctx.send(msg)
        server_prefix = await ex.get_server_prefix(ctx)
        # msgs are repeated numerous times. setting the values beforehand.
        incorrect_format_msg = await ex.get_msg(ctx, "reminder", "incorrect_format")
        incorrect_format_msg = await ex.replace(incorrect_format_msg, [["name", ctx.author.display_name],
                                                                       ["server_prefix", server_prefix]])
        try:
            is_relative_time, type_index = await ex.u_reminder.determine_time_type(user_input)
        except ex.exceptions.ImproperFormat:
            return await ctx.send(incorrect_format_msg)

        if is_relative_time is None:
            return await ctx.send(incorrect_format_msg)
        remind_reason = await ex.u_reminder.process_reminder_reason(user_input, type_index)
        try:
            remind_time = await ex.u_reminder.process_reminder_time(user_input, type_index, is_relative_time, ctx.author.id)
        except ex.exceptions.ImproperFormat:
            msg = await ex.get_msg(ctx, "reminder", "incorrect_time_format")
            msg = await ex.replace(msg, ["name", ctx.author.display_name])
            return await ctx.send(msg)
        except ex.exceptions.TooLarge:
            msg = await ex.get_msg(ctx, "reminder", "too_long")
            msg = await ex.replace(msg, ['name', ctx.author.display_name])
            return await ctx.send(msg)
        except ex.exceptions.NoTimeZone:
            msg = await ex.get_msg(ctx, "reminder", "no_timezone")
            msg = await ex.replace(msg, [['name', ctx.author.display_name], ['server_prefix', server_prefix],
                                         ['format', self.set_timezone_format]])
            return await ctx.send(msg)

        await ex.u_reminder.set_reminder(remind_reason, remind_time, ctx.author.id)
        msg = await ex.get_msg(ctx, "reminder", "will_remind")
        msg = await ex.replace(msg, [['name', ctx.author.display_name], ['reason', remind_reason],
                                     ['time', await ex.u_reminder.get_locale_time(remind_time, user_timezone)]])
        return await ctx.send(msg)

    @commands.command(aliases=['gettz', 'time'])
    async def gettimezone(self, ctx, user_input: typing.Union[discord.Member, str] = None):
        """Get your current set timezone.
        [Format: %gettimezone]"""
        server_prefix = await ex.get_server_prefix(ctx)

        if isinstance(user_input, str):
            try:
                timezone_input = await ex.u_reminder.process_timezone_input(user_input)
                current_time = await ex.u_reminder.format_time('%I:%M:%S %p', timezone_input)
                msg = await ex.get_msg(ctx, "reminder", "current_time")
                msg = await ex.replace(msg, [["name", ctx.author.display_name], ["tz", timezone_input],
                                             ["time", current_time]])
                return await ctx.send(msg)
            except:
                msg = await ex.get_msg(ctx, "reminder", "incorrect_tz_input")
                return await ctx.send(msg)
        elif isinstance(user_input, discord.Member):
            user = user_input
        elif not user_input:
            user = None
        else:
            msg = await ex.get_msg(ctx, "reminder", "incorrect_tz_input")
            return await ctx.send(msg)

        if not user:
            user = ctx.author
        user_timezone = await ex.u_reminder.get_user_timezone(user.id)
        if not user_timezone:
            msg = await ex.get_msg(ctx, "reminder", "no_timezone")
            msg = await ex.replace(msg, [['name', user.display_name], ['server_prefix', server_prefix],
                                         ['format', self.set_timezone_format]])
            return await ctx.send(msg)

        current_time = await ex.u_reminder.format_time('%I:%M:%S %p', user_timezone)
        timezone_abbrev = await ex.u_reminder.format_time('UTC%z', user_timezone)
        msg = await ex.get_msg(ctx, "reminder", "user_time")
        msg = await ex.replace(msg, [["name", user.display_name], ["time", current_time],
                                     ["tz", f"{user_timezone} {timezone_abbrev}"]])
        return await ctx.send(msg)

    @commands.command(aliases=['settz'])
    async def settimezone(self, ctx, timezone_name=None, country_code=None):
        """Set your local timezone with a timezone abbreviation and country code.
        [Format: %settimezone (timezone name) (country code)]"""
        if not timezone_name and not country_code:
            await ex.u_reminder.remove_user_timezone(ctx.author.id)
            msg = await ex.get_msg(ctx, "reminder", "remove_tz")
            msg = await ex.replace(msg, ["name", ctx.author.display_name])
            return await ctx.send(msg)

        server_prefix = await ex.get_server_prefix(ctx)
        user_timezone = await ex.u_reminder.process_timezone_input(timezone_name, country_code)
        if not user_timezone:
            msg = await ex.get_msg(ctx, "reminder", "invalid_tz")
            msg = await ex.replace(msg, [["name", ctx.author.display_name], ["server_prefix", server_prefix],
                                         ["format", self.set_timezone_format]])
            return await ctx.send(msg)

        timezone_utc = await ex.u_reminder.format_time('UTC%z', user_timezone)
        native_time = await ex.u_reminder.format_time('%c', user_timezone)
        await ex.u_reminder.set_user_timezone(ctx.author.id, user_timezone)
        msg = await ex.get_msg(ctx, "reminder", "add_tz")
        msg = await ex.replace(msg, [["name", ctx.author.display_name], ["tz", f"{user_timezone} {timezone_utc}"],
                                     ["time", native_time]])
        return await ctx.send(msg)

    @tasks.loop(seconds=5, minutes=0, hours=0, reconnect=True)
    async def reminder_loop(self):
        """Process for checking for reminders and sending them out if they are past overdue."""
        try:
            for user in ex.cache.users.values():
                if not user.reminders:
                    continue
                for remind_id, remind_reason, remind_time in user.reminders:
                    try:
                        current_time = datetime.datetime.now(remind_time.tzinfo)
                        if current_time < remind_time:
                            continue
                        dm_channel = await ex.get_dm_channel(user_id=user.id)
                        if dm_channel:
                            title_desc = await ex.get_msg(user, "reminder", "remind_dm")
                            title_desc = await ex.replace(title_desc, ["reason", remind_reason])
                            embed = await ex.create_embed(title="Reminder", title_desc=title_desc)
                            await dm_channel.send(embed=embed)
                            await ex.u_reminder.remove_user_reminder(user.id, remind_id)
                    except:
                        pass  # likely forbidden error -> do not have access to dm user
        except:
            pass  # dictionary changed size during iteration -> Next Loop instance will take care of this loop.

