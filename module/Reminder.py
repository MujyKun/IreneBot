import asyncio

from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
import datetime
import pytz
import discord
import typing
from IreneUtility.Utility import Utility


# noinspection PyBroadException,PyPep8
class Reminder(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex
        self.set_timezone_format = "settimezone (timezone abbreviation) (country code)"

    # TODO: add remindlater command or reacts to the reminder

    @commands.command(aliases=["listreminds", "reminders", "reminds"])
    async def listreminders(self, ctx):
        """
        Lists out all of your reminders.

        [Format: %listreminders]
        """
        remind_list = await self.ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await self.ex.u_reminder.get_user_timezone(ctx.author.id)

        if not remind_list:
            msg = await self.ex.get_msg(ctx, "reminder", "no_reminders", ['name', ctx.author.display_name])
            return await ctx.send(msg)

        m_embed = await self.ex.create_embed(title="Reminders List")
        embed_list = []
        remind_number = 1
        index_number = 1
        for remind_id, remind_reason, remind_time in remind_list:
            await asyncio.sleep(0)
            if user_timezone:
                remind_time = remind_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
            m_embed.add_field(name=f"{index_number}) {remind_reason}",
                              value=f"{await self.ex.u_reminder.get_locale_time(remind_time,user_timezone)}",
                              inline=False)
            remind_number += 1
            index_number += 1
            if remind_number == 11:
                embed_list.append(m_embed)
                m_embed = await self.ex.create_embed(title="Reminders List")
                remind_number = 1
        if remind_number:
            embed_list.append(m_embed)
        msg = await ctx.send(embed=embed_list[0])
        await self.ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command(aliases=["removeremind"])
    async def removereminder(self, ctx, reminder_index: int):
        """
        Remove one of your reminders.

        [Format: %removereminder (reminder index)]
        """
        reminders = await self.ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await self.ex.u_reminder.get_user_timezone(ctx.author.id)
        if not reminders:
            msg = await self.ex.get_msg(ctx, "reminder", "no_reminders", ['name', ctx.author.display_name])
            return await ctx.send(msg)
        else:
            try:
                remind_id, remind_reason, remind_time = reminders[reminder_index-1]
                if user_timezone:
                    remind_time = remind_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
                msg = await self.ex.get_msg(ctx, "reminder", "remove_reminder",
                                            [['name', ctx.author.display_name],
                                             ['reason', remind_reason],
                                             ['time', await self.ex.u_reminder.get_locale_time(remind_time,
                                                                                               user_timezone)]])
                await ctx.send(msg)
                await self.ex.u_reminder.remove_user_reminder(ctx.author.id, remind_id)
            except:
                msg = await self.ex.get_msg(ctx, "reminder", "index_not_found",
                                            [['name', ctx.author.display_name], ['index', reminder_index]])
                return await ctx.send(msg)

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        """
        Create a reminder to do a task at a certain time.

        [Format: %remindme to ______ at 9PM
        or
        %remindme to ____ in 6hrs 30mins]
        """
        reminders = await self.ex.u_reminder.get_reminders(ctx.author.id)
        user_timezone = await self.ex.u_reminder.get_user_timezone(ctx.author.id)
        if reminders:
            if len(reminders) >= self.ex.keys.reminder_limit:
                msg = await self.ex.get_msg(ctx, "reminder", "max_reminders", [["name", ctx.author.display_name],
                                                                               ["reminder_limit",
                                                                                self.ex.keys.reminder_limit]])
                return await ctx.send(msg)
        server_prefix = await self.ex.get_server_prefix(ctx)
        # msgs are repeated numerous times. setting the values beforehand.
        incorrect_format_msg = await self.ex.get_msg(ctx, "reminder", "incorrect_format",
                                                     [["name", ctx.author.display_name],
                                                      ["server_prefix", server_prefix]])
        try:
            is_relative_time, type_index = await self.ex.u_reminder.determine_time_type(user_input)
        except self.ex.exceptions.ImproperFormat:
            return await ctx.send(incorrect_format_msg)

        if is_relative_time is None:
            return await ctx.send(incorrect_format_msg)
        remind_reason = await self.ex.u_reminder.process_reminder_reason(user_input, type_index)
        try:
            remind_time = await self.ex.u_reminder.process_reminder_time(user_input, type_index, is_relative_time,
                                                                         ctx.author.id)
        except self.ex.exceptions.ImproperFormat:
            msg = await self.ex.get_msg(ctx, "reminder", "incorrect_time_format", ["name", ctx.author.display_name])
            return await ctx.send(msg)
        except self.ex.exceptions.TooLarge:
            msg = await self.ex.get_msg(ctx, "reminder", "too_long", ['name', ctx.author.display_name])
            return await ctx.send(msg)
        except self.ex.exceptions.NoTimeZone:
            msg = await self.ex.get_msg(ctx, "reminder", "no_timezone", [['name', ctx.author.display_name],
                                                                         ['server_prefix', server_prefix],
                                                                         ['format', self.set_timezone_format]])
            return await ctx.send(msg)

        await self.ex.u_reminder.set_reminder(remind_reason, remind_time, ctx.author.id)
        msg = await self.ex.get_msg(ctx, "reminder", "will_remind", [['name', ctx.author.display_name],
                                                                     ['reason', remind_reason],
                                                                     ['time', await self.ex.u_reminder.get_locale_time(
                                                                         remind_time, user_timezone)]])
        # we should put the msg in an embed to avoid custom inputing mentioning @everyone.
        embed = await self.ex.create_embed(title="Reminder", title_desc=msg)
        return await ctx.send(embed=embed)

    @commands.command(aliases=['gettz', 'time'])
    async def gettimezone(self, ctx, user_input: typing.Union[discord.Member, str] = None):
        """
        Get your current set timezone.

        [Format: %gettimezone]
        """
        server_prefix = await self.ex.get_server_prefix(ctx)

        if isinstance(user_input, str):
            try:
                timezone_input = await self.ex.u_reminder.process_timezone_input(user_input)
                current_time = await self.ex.u_reminder.format_time('%I:%M:%S %p', timezone_input)
                msg = await self.ex.get_msg(ctx, "reminder", "current_time", [["name", ctx.author.display_name],
                                                                              ["tz", timezone_input],
                                                                              ["time", current_time]])
                return await ctx.send(msg)
            except:
                msg = await self.ex.get_msg(ctx, "reminder", "incorrect_tz_input")
                return await ctx.send(msg)
        elif isinstance(user_input, discord.Member):
            user = user_input
        elif not user_input:
            user = None
        else:
            msg = await self.ex.get_msg(ctx, "reminder", "incorrect_tz_input")
            return await ctx.send(msg)

        if not user:
            user = ctx.author
        user_timezone = await self.ex.u_reminder.get_user_timezone(user.id)
        if not user_timezone:
            msg = await self.ex.get_msg(ctx, "reminder", "no_timezone", [['name', user.display_name],
                                                                         ['server_prefix', server_prefix],
                                                                         ['format', self.set_timezone_format]])
            return await ctx.send(msg)

        current_time = await self.ex.u_reminder.format_time('%I:%M:%S %p', user_timezone)
        timezone_abbrev = await self.ex.u_reminder.format_time('UTC%z', user_timezone)
        msg = await self.ex.get_msg(ctx, "reminder", "user_time", [["name", user.display_name], ["time", current_time],
                                                                   ["tz", f"{user_timezone} {timezone_abbrev}"]])
        return await ctx.send(msg)

    @commands.command(aliases=['settz'])
    async def settimezone(self, ctx, timezone_name=None, country_code=None):
        """
        Set your local timezone with a timezone abbreviation and country code.

        [Format: %settimezone (timezone name) (country code)]
        """
        if not timezone_name and not country_code:
            await self.ex.u_reminder.remove_user_timezone(ctx.author.id)
            msg = await self.ex.get_msg(ctx, "reminder", "remove_tz",  ["name", ctx.author.display_name])
            return await ctx.send(msg)

        server_prefix = await self.ex.get_server_prefix(ctx)
        user_timezone = await self.ex.u_reminder.process_timezone_input(timezone_name, country_code)
        if not user_timezone:
            msg = await self.ex.get_msg(ctx, "reminder", "invalid_tz", [["name", ctx.author.display_name],
                                                                        ["server_prefix", server_prefix],
                                                                        ["format", self.set_timezone_format]])
            return await ctx.send(msg)

        timezone_utc = await self.ex.u_reminder.format_time('UTC%z', user_timezone)
        native_time = await self.ex.u_reminder.format_time('%c', user_timezone)
        await self.ex.u_reminder.set_user_timezone(ctx.author.id, user_timezone)
        msg = await self.ex.get_msg(ctx, "reminder", "add_tz", [["name", ctx.author.display_name],
                                                                ["tz", f"{user_timezone} {timezone_utc}"],
                                                                ["time", native_time]])
        return await ctx.send(msg)

    @tasks.loop(seconds=5, minutes=0, hours=0, reconnect=True)
    async def reminder_loop(self):
        """Process for checking for reminders and sending them out if they are past overdue."""
        while not self.ex.irene_cache_loaded:
            await asyncio.sleep(1)
        try:
            # we do not want dictionary to change size during iteration, so we will make a copy.
            users_copy = self.ex.cache.users.copy()
            for user in users_copy.values():
                if not user.reminders:
                    continue
                for remind_id, remind_reason, remind_time in user.reminders:
                    try:
                        current_time = datetime.datetime.now(remind_time.tzinfo)
                        if current_time < remind_time:
                            continue
                        dm_channel = await self.ex.get_dm_channel(user_id=user.id)
                        if dm_channel:
                            title_desc = await self.ex.get_msg(user, "reminder", "remind_dm", ["reason", remind_reason])
                            embed = await self.ex.create_embed(title="Reminder", title_desc=title_desc)
                            await dm_channel.send(embed=embed)
                            await self.ex.u_reminder.remove_user_reminder(user.id, remind_id)
                    except discord.Forbidden as e:
                        # likely forbidden error -> do not have access to dm user
                        log.useless(f"{e} (discord.Forbidden) - Likely do not have access to dm user {user.id}",
                                    method=self.reminder_loop)
                        # remove the reminder since we do not want to try constantly reminding someone we cant.
                        await self.ex.u_reminder.remove_user_reminder(user.id, remind_id)
                    except Exception as e:
                        log.console(f"{e} - Reminder Loop")
        except Exception as e:
            log.useless(f"{e} (Exception) - Reminder.reminder_loop")
