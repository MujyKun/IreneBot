from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from random import *
import discord
from module import logger as log
from module.keys import bot_website
from Utility import resources as ex


# noinspection PyBroadException,PyPep8
class Currency(commands.Cog):
    @commands.command()
    @commands.cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        """Gives a certain amount of money every 24 hours [Format: %daily]"""
        user = await ex.get_user(ctx.author.id)
        daily_amount = await user.get_daily_amount()
        await user.update_balance(add=daily_amount)
        msg_str = ex.cache.languages[user.user_language]['currency']['daily_msg']
        msg_str = msg_str.replace("{name}", ctx.author.display_name)
        msg_str = msg_str.replace("{daily_amount}", daily_amount)

        return await ctx.send(msg_str)

    @commands.command(aliases=['b', 'bal', '$'])
    async def balance(self, ctx, *, member: discord.Member = None):
        """View your balance [Format: %balance (@user)][Aliases: b,bal,$]"""
        if not member:
            member = ctx.author

        user = await ex.get_user(member.id)
        await user.register_currency()

        msg_str = ex.cache.languages[user.user_language]['currency']['balance_msg']
        msg_str = msg_str.replace("{name}", member.display_name)
        msg_str = msg_str.replace("{balance}", await user.get_shortened_balance())

        return await ctx.send(msg_str)

    @commands.command()
    async def bet(self, ctx, *, balance="1"):
        """Bet your money [Format: %bet (amount)]"""
        pass

    @commands.command(aliases=['leaderboards', 'lb'])
    async def leaderboard(self, ctx, mode="server"):
        """Shows Top 10 Users server/global wide [Format: %leaderboard (global/server)][Aliases: leaderboards, lb]"""
        pass

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def beg(self, ctx):
        """Beg a homeless man for money [Format: %beg]"""
        pass

    @commands.command(aliases=["levelup"])
    @commands.cooldown(1, 61, BucketType.user)
    async def upgrade(self, ctx, command=""):
        """Upgrade a command to the next level with your money. [Format: %upgrade rob/daily/beg]"""
        pass

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, *, user: discord.Member = discord.Member):
        """Rob a user [Format: %rob @user]"""
        pass

    @commands.command()
    async def give(self, ctx, mentioned_user: discord.Member = discord.Member, amount="0"):
        """Give a user money [Format: %give (@user) (amount)]"""
        pass

    @commands.command(aliases=['rockpaperscissors'])
    async def rps(self, ctx, rps_choice='', amount="0"):
        """Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]"""
        pass
