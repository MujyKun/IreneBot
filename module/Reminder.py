import discord
from discord.ext import commands
from module import logger as log, events
import random
from Utility import resources as ex
import datetime

class Reminder(commands.Cog):

    @commands.command()
    async def listreminds(self, ctx):
        pass

    @commands.command(aliases=["removereminder"])
    async def removeremind(self, ctx):
        pass

    @commands.command(aliases=["remind"])
    async def remindme(self, ctx, *, user_input):
        is_relative_time, type_index = await ex.determine_relative_time(user_input)
        if is_relative_time is None:
            # Error
        await ex.process_reminder_input(user_input, type_index, is_relative_time)



    @commands.command()
    async def settimezone(self, ctx, timezone_name, country_code):
        """Set your local timezone with the timezone name and country code.
        [Format: %settimezone (timezone name) (country code)]"""
        user_timezone = await ex.get_time_zone_name(timezone_name, country_code)