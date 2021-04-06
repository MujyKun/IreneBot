from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
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
        msg_str = await ex.get_msg(user, 'currency', 'daily_msg')
        msg_str = await ex.replace(msg_str, [["name", ctx.author.display_name], ["daily_amount", daily_amount]])

        return await ctx.send(msg_str)

    @commands.command(aliases=['b', 'bal', '$'])
    async def balance(self, ctx, *, member: discord.Member = None):
        """View your balance [Format: %balance (@user)][Aliases: b,bal,$]"""
        if not member:
            member = ctx.author

        user = await ex.get_user(member.id)
        await user.register_currency()

        msg_str = await ex.get_msg(user, 'currency', 'balance_msg')
        msg_str = await ex.replace(msg_str, [["name", member.display_name],
                                             ["balance", await user.get_shortened_balance()]])

        return await ctx.send(msg_str)

    @commands.command()
    async def bet(self, ctx, *, amount_to_bet: str):
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
    async def upgrade(self, ctx, command=None):
        """Upgrade a command to the next level with your money. [Format: %upgrade rob/daily/beg]"""
        pass

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, *, person_to_rob: discord.Member):
        """Rob a user [Format: %rob @user]"""
        pass

    @commands.command()
    async def give(self, ctx, person_to_give: discord.Member, amount_to_give: int):
        """Give a user money [Format: %give (@user) (amount)]"""
        pass

    @commands.command(aliases=['rockpaperscissors'])
    async def rps(self, ctx, rps_choice='', amount="0"):
        """Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]"""
        pass
