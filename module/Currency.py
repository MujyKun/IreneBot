from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
from Utility import resources as ex
from random import randint


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
                                             ["balance", (ex.add_commas(user.balance))],
                                             ["currency_name", ex.keys.currency_name]])

        return await ctx.send(msg_str)

    @commands.command()
    async def bet(self, ctx, *, bet_amount: str):
        """Bet your money [Format: %bet (amount)]"""
        user = await ex.get_user(ctx.author.id)
        bet_amount: int = ex.remove_commas(bet_amount)  # remove all commas from the input.
        server_prefix = await ex.get_server_prefix(ctx)
        await user.register_currency()  # confirm the user is registered.

        if user.in_currency_game:  # in a game that affects currency (such as blackjack).
            msg = await ex.get_msg(user, "currency", "in_game")
            msg = await ex.replace(msg, [["name", ctx.author.display_name],
                                         ["server_prefix", server_prefix]])
            return await ctx.send(msg)

        if bet_amount <= 0:  # input is wrong or they are trying to bet nothing.
            msg = await ex.get_msg(user, "currency", "nothing_to_bet")
            msg = await ex.replace(msg, [["name", ctx.author.display_name],
                                         ["currency_name", ex.keys.currency_name]])
            return await ctx.send(msg)

        if bet_amount > user.balance:  # user does not have enough.
            msg = await ex.get_msg(user, "currency", "not_enough")
            msg = await ex.replace(msg, [["name", ctx.author.display_name],
                                         ["currency_name", ex.keys.currency_name],
                                         ["balance", (ex.add_commas(user.balance))]])
            return await ctx.send(msg)

        user_random_number = randint(1, 100)  # served as comparator and is also the win percentage.
        comp_random_number = randint(1, 100)  # served as comparator and is also the loss percentage.

        # if the user and comp have an even number
        user_is_even = user_random_number % 2 == 0
        comp_is_even = comp_random_number % 2 == 0

        if (user_is_even and comp_is_even) or (not user_is_even and not comp_is_even):
            # if the user and comp random number are either both odd or both even -> win
            multiplier = (100 + user_random_number) / 100  # percentage converted to decimal
        else:
            # loss
            multiplier = (comp_random_number / 100)  # percentage converted to decimal

        bet_result = int((multiplier * bet_amount) - bet_amount)  # the amount to add or remove from the bet amount.
        result = "LOST" if bet_result < 0 else "WON"
        await user.update_balance(add=bet_result)
        msg = await ex.get_msg(user, "currency", "bet_result")
        msg = await ex.replace(msg, [["name", ctx.author.display_name],
                                     ["result", result],
                                     ["integer", -bet_result if bet_result < 0 else bet_result],
                                     ["balance", ex.add_commas(user.balance)]])
        await ctx.send(msg)

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
