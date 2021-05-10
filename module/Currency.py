import random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord
from random import randint
from IreneUtility.Utility import Utility


# noinspection PyBroadException,PyPep8
class Currency(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex

    @commands.command()
    @commands.cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        """
        Gives a certain amount of money every 24 hours

        [Format: %daily]
        """
        user = await self.ex.get_user(ctx.author.id)
        daily_amount = await user.get_daily_amount()
        await user.update_balance(add=daily_amount)  # will auto register.
        msg_str = await self.ex.get_msg(user, 'currency', 'daily_msg')
        msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["daily_amount", daily_amount]])

        return await ctx.send(msg_str)

    @commands.command(aliases=['b', 'bal', '$'])
    async def balance(self, ctx, *, member: discord.Member = None):
        """
        View your balance

        [Format: %balance (@user)]
        [Aliases: b,bal,$]
        """
        if not member:
            member = ctx.author

        user = await self.ex.get_user(member.id)
        await user.register_currency()

        msg_str = await self.ex.get_msg(user, 'currency', 'balance_msg')
        msg_str = await self.ex.replace(msg_str, [["name", member.display_name],
                                                  ["balance", (self.ex.add_commas(user.balance))],
                                                  ["currency_name", self.ex.keys.currency_name]])

        return await ctx.send(msg_str)

    @commands.command()
    async def bet(self, ctx, *, bet_amount: str):
        """
        Bet your money

        [Format: %bet (amount)]
        """
        user = await self.ex.get_user(ctx.author.id)
        bet_amount: int = self.ex.remove_commas(bet_amount)  # remove all commas from the input.
        server_prefix = await self.ex.get_server_prefix(ctx)
        await user.register_currency()  # confirm the user is registered.

        if user.in_currency_game:  # in a game that affects currency (such as blackjack).
            msg = await self.ex.get_msg(user, "currency", "in_game")
            msg = await self.ex.replace(msg, [["name", ctx.author.display_name],
                                              ["server_prefix", server_prefix]])
            return await ctx.send(msg)

        if bet_amount <= 0:  # input is wrong or they are trying to bet nothing.
            msg = await self.ex.get_msg(user, "currency", "nothing_to_bet")
            msg = await self.ex.replace(msg, [["name", ctx.author.display_name],
                                              ["currency_name", self.ex.keys.currency_name]])
            return await ctx.send(msg)

        if bet_amount > user.balance:  # user does not have enough.
            msg = await self.ex.get_msg(user, "currency", "not_enough")
            msg = await self.ex.replace(msg, [["name", ctx.author.display_name],
                                              ["currency_name", self.ex.keys.currency_name],
                                              ["balance", (self.ex.add_commas(user.balance))]])
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
        msg = await self.ex.get_msg(user, "currency", "bet_result")
        msg = await self.ex.replace(msg, [["name", ctx.author.display_name],
                                          ["result", result],
                                          ["integer", -bet_result if bet_result < 0 else bet_result],
                                          ["balance", self.ex.add_commas(user.balance)]])
        await ctx.send(msg)

    @commands.command(aliases=['leaderboards', 'lb'])
    async def leaderboard(self, ctx, mode="server"):
        """
        Shows Top 10 Users server/global wide

        [Format: %leaderboard (global/server)]
        [Aliases: leaderboards, lb]
        """
        sorted_balance = []

        # user may be in DMs trying to access server currency list or misspelt the mode.
        if not ctx.guild or mode.lower() not in ["global", "server"]:
            mode = "global"
        elif mode.lower() == "server":
            # get member list of the server
            guild_member_list = [await self.ex.get_user(member.id) for member in ctx.guild.members]
            sorted_balance = [[t_user, t_user.balance] for t_user in guild_member_list]

        # global list
        if not sorted_balance:
            sorted_balance = [[t_user, t_user.balance] for t_user in self.ex.cache.users.values()]

        # sort by greatest value first
        sorted_balance.sort(key=lambda user_and_bal: user_and_bal[1], reverse=True)

        embed = await self.ex.create_embed(title=f"Currency Leaderboard ({mode.lower()})",
                                           footer_desc="Type %bal (user) to view their balance.")

        for count, user_info in enumerate(sorted_balance, 1):
            if count > 10:
                break
            user = user_info[0]
            embed.add_field(name=f"{count}) {self.ex.client.get_user(user.id)} ({user.id})",
                            value=await user.get_shortened_balance(), inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 300, BucketType.user)
    async def beg(self, ctx):
        """
        Beg a homeless man for money

        [Format: %beg]
        """
        user = await self.ex.get_user(ctx.author.id)
        beg_amount = (user.beg_level * 2) or random.randint(1, 25)  # randint > beg_amount until beg level 13
        await user.update_balance(add=beg_amount)  # will auto register
        msg_str = await self.ex.get_msg(user, 'currency', 'beg_msg')
        msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["integer", beg_amount],
                                                  ["currency_name", self.ex.keys.currency_name]])
        return await ctx.send(msg_str)

    @commands.command(aliases=["levelup"])
    @commands.cooldown(1, 61, BucketType.user)
    async def upgrade(self, ctx, command=None):
        """
        Upgrade a command to the next level with your money.

        [Format: %upgrade rob/daily/beg]
        """
        user = await self.ex.get_user(ctx.author.id)
        server_prefix = await self.ex.get_server_prefix(ctx)
        possible_options = ["rob", "daily", "beg"]

        # get rid of invalid input.
        if not command or command.lower() not in possible_options:
            msg_str = await self.ex.get_msg(user, 'general', 'invalid_input')
            msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name],
                                                      ["server_prefix", server_prefix],
                                                      ["command_name", "upgrade"]])
            return await ctx.send(msg_str)

        # set the current level of the user for the command we are trying to upgrade.
        elif command.lower() == possible_options[0]:  # rob
            level = user.rob_level
        elif command.lower() == possible_options[1]:  # daily
            level = user.daily_level
        elif command.lower() == possible_options[2]:  # beg
            level = user.beg_level

        # Level option has no condition for a new command.
        else:
            raise self.ex.exceptions.ShouldNotBeHere("Possible upgrade option has no logic added. "
                                                     "-> Currency.upgrade() ")

        # check howmuch money the user needs
        money_needed = await user.get_needed_for_level(level, command.lower())

        # if the user does not have enough money
        if user.balance < money_needed:
            msg_str = await self.ex.get_msg(user, 'currency', 'upgrade_not_enough')
            msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["integer", money_needed],
                                                      ["command_name", command.lower()], ["balance", user.balance]])
            return await ctx.send(msg_str)

        # confirm the user really wants to upgrade their level.
        msg_str = await self.ex.get_msg(user, 'currency', 'upgrade_msg')
        msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["integer", money_needed],
                                                  ["command_name", command.lower()], ["balance", user.balance]])
        msg = await ctx.send(msg_str)
        reaction = "\U0001f44d"
        await msg.add_reaction(reaction)  # thumbs up]
        if await self.ex.wait_for_reaction(msg, user.id, reaction):
            # set the user's new level
            await user.set_level(level + 1, command.lower())

            # let the user know their new level.
            msg_str = await self.ex.get_msg(user, 'currency', 'upgrade_msg_success')
            msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name], ["integer", level + 1],
                                                      ["command_name", command.lower()]])
            return await ctx.send(msg_str)
        else:
            # let the user know they failed to upgrade.
            msg_str = await self.ex.get_msg(user, 'currency', 'upgrade_out_of_time')
            msg_str = await self.ex.replace(msg_str, [["name", ctx.author.display_name],
                                                      ["command_name", command.lower()]])
            return await ctx.send(msg_str)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, *, person_to_rob: discord.Member):
        """
        Rob a user

        [Format: %rob @user]
        """
        pass

    @commands.command()
    async def give(self, ctx, person_to_give: discord.Member, amount_to_give: int):
        """
        Give a user money

        [Format: %give (@user) (amount)]
        """
        pass

    @commands.command(aliases=['rockpaperscissors'])
    async def rps(self, ctx, rps_choice='', amount="0"):
        """
        Play Rock Paper Scissors for Money

        [Format: %rps (r/p/s)(amount)]
        [Aliases: rockpaperscissors]
        """
        pass
