from discord.ext import commands, tasks
from Utility import resources as ex
import datetime
import pytz


class Reminder(commands.Cog):
    def __init__(self):
        self.set_timezone_format = "settimezone (timezone abbreviation) (country code)"

    @commands.command(aliases=["listreminds", "reminders", "reminds"])
    async def listreminders(self, ctx):
        """Lists out all of your reminders.
        [Format: %listreminders]"""
        remind_list = await ex.get_reminders(ctx.author.id)

        if not remind_list:
            return await ctx.send(f"> {ctx.author.display_name}, you have no reminders.")

        m_embed = await ex.create_embed(title="Reminders List")
        embed_list = []
        remind_number = 0
        for remind in remind_list:
            remind_number += 1
            m_embed.add_field(name=f"{remind[2].strftime('%m/%d/%Y, %H:%M:%S')}", value=f"to {remind[1]}", inline=False)
            if remind_number == 25:
                embed_list.append(m_embed)
                m_embed = await ex.create_embed(title="Reminders List")
                remind_number = 0
        if remind_number:
            embed_list.append(m_embed)
        msg = await ctx.send(embed=m_embed[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command(aliases=["removeremind"])
    async def removereminder(self, ctx, reminder_index):
        """Remove one of your reminders.
        [Format: %removereminder (reminder index)]"""
        reminders = ex.cache.reminders.get(ctx.author.id)
        if not reminders:
            return await ctx.send(f"> {ctx.author.display_name}, you have no reminders.")
        else:
            reminder = reminders.index(reminder_index+1)
            if not reminder:
                return await ctx.send(f"> {ctx.author.display_name}, I could not find index {reminder_index}.")
            await ex.remove_user_reminder(ctx.author.id, reminder[0])

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        """Create a reminder to do a task at a certain time.
        [Format: %remindme to ______ at 9PM
        or
        %remindme to ____ in 6hrs 30mins]"""
        try:
            is_relative_time, type_index = await ex.determine_time_type(user_input)
        except ex.exceptions.TooLarge:
            return await ctx.send(
                f"> {ctx.author.display_name}, the time for a reminder can not be greater than 2 years.")
        if is_relative_time is None:
            return await ctx.send(f"> {ctx.author.display_name}, please use 'in/at' to specify time.")
        remind_reason = await ex.process_reminder_reason(user_input, type_index)
        try:
            remind_time = await ex.process_reminder_time(user_input, type_index, is_relative_time, ctx.author.id)
        except ex.exceptions.ImproperFormat:
            return await ctx.send(f"{ctx.author.display_name}, you did not enter the correct time format.")
        except ex.exceptions.NoTimeZone:
            server_prefix = await ex.get_server_prefix_by_context(ctx)
            return await ctx.send(f"> {ctx.author.display_name}, you do not have a timezone set. Please use "
                                  f"`{server_prefix}{self.set_timezone_format}`")
        await ex.set_reminder(remind_reason, remind_time, ctx.author.id)
        return await ctx.send(
            f"> {ctx.author.display_name}, I will remind you to {remind_reason} on {remind_time.strftime('%m/%d/%Y, %H:%M:%S')}")

    @commands.command(aliases=['gettz'])
    async def gettimezone(self, ctx):
        """Get your current set timezone.
        [Format: %gettimezone]"""
        user_timezone = await ex.get_user_timezone(ctx.author.id)
        if not user_timezone:
            server_prefix = await ex.get_server_prefix_by_context(ctx)
            return await ctx.send(f"> {ctx.author.display_name}, you do not have a timezone set. Please use "
                                  f"`{server_prefix}{self.set_timezone_format}`")

        timezone_abbrev = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%Z%z')
        return await ctx.send(
            f"> {ctx.author.display_name}, your timezone is current set to {user_timezone} {timezone_abbrev}")

    @commands.command(aliases=['settz'])
    async def settimezone(self, ctx, timezone_name=None, country_code=None):
        """Set your local timezone with a timezone abbreviation and country code.
        [Format: %settimezone (timezone name) (country code)]"""
        if not timezone_name and not country_code:
            await ex.remove_user_timezone(ctx.author.id)
            return await ctx.send(f"> {ctx.author.display_name}, if your timezone was set, it was removed.")

        user_timezone = await ex.get_time_zone_name(timezone_name, country_code)
        if not user_timezone:
            return await ctx.send(f"> {ctx.author.display_name}, that is not a valid timezone.")

        timezone_utc = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%Z%z')
        native_time = datetime.datetime.now(pytz.timezone(user_timezone)).strftime('%c')
        await ex.set_user_timezone(ctx.author.id, user_timezone)
        return await ctx.send(f"> {ctx.author.display_name}, your timezone has been set to `{user_timezone} "
                              f"{timezone_utc}` where it is currently `{native_time}`")

    @tasks.loop(seconds=5, minutes=0, hours=0, reconnect=True)
    async def reminder_loop(self):
        """Process for checking for reminders and sending them out if they are past overdue."""
        for user_id in ex.cache.reminders:
            reminders = ex.cache.reminders.get(user_id)
            if reminders:
                for reminder in reminders:
                    try:
                        remind_id = reminder[0]
                        remind_reason = reminder[1]
                        remind_time = reminder[2]
                        current_time = datetime.datetime.now()
                        if current_time >= remind_time:
                            dm_channel = await ex.get_dm_channel(user_id=user_id)
                            if dm_channel:
                                title_desc = f"This is a reminder to **{remind_reason}**."
                                embed = ex.create_embed(title="Reminder", title_desc=title_desc)
                                await dm_channel.send(embed=embed)
                                await ex.remove_user_reminder(user_id, remind_id)
                    except:
                        # likely forbidden error -> do not have access to dm user
                        pass



