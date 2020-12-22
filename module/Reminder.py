import discord
from discord.ext import commands
from module import logger as log, events
import random
from Utility import resources as ex
import datetime

class Reminder(commands.Cog):

    @commands.command(aliases=["listreminders","reminders","reminds"])
    async def listreminds(self, ctx):
        """List out all currently set reminders"""
        remind_list = await ex.get_reminders(ctx.author.id)

        if not remind_list:
            return await ctx.send(f"> {ctx.author.display_name}, you have no reminders.")

        m_embed = await ex.create_embed(title="Reminders List")
        embed_list = []
        remind_number = 0
        for remind in remind_list:
            remind_number += 1
            m_embed.add_field(name= f"{remind[1].strftime('%m/%d/%Y, %H:%M:%S')}", value= f"to {remind[0]}", inline=False)
            if remind_number == 25:
                embed_list.append(m_embed)
                m_embed = await ex.create_embed(title="Reminders List")
                remind_number = 0
        if remind_number:
            embed_list.append(m_embed)
        msg = await ctx.send(embed = m_embed[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)


    @commands.command(aliases=["removereminder"])
    async def removeremind(self, ctx):
        """Remove a reminder from your set reminders.
        [Format: %removeremind (remind index)]"""
        pass

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        """Create a reminder to do a task at a certain time.
        [Format: %remindme to ______ at 9PM
        or
        %remindme to ____ in 6hrs 30mins]"""
        is_relative_time, type_index = await ex.determine_time_type(user_input)
        if is_relative_time is None:
            # Error
        remind_reason = await ex.process_remind_reason(user_input, type_index)
        remind_time = await ex.process_remind_time(user_input, type_index, is_relative_time, ctx.author.id)


    @commands.command()
    async def gettimezone(self, ctx):
        """Get your current set timezone.
        [Format: %gettimezone]"""
        pass

    @commands.command()
    async def settimezone(self, ctx, timezone_name, country_code):
        """Set your local timezone with the timezone name and country code.
        [Format: %settimezone (timezone name) (country code)]"""
        user_timezone = await ex.get_time_zone_name(timezone_name, country_code)