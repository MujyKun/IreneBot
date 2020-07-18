from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from random import *
import discord
from module import logger as log
from module.keys import client, bot_website
from Utility import resources as ex


class Currency(commands.Cog):
    def __init__(self):
        self.counter2 = -1
        self.counter = 0

    @commands.command()
    @commands.cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        """Gives a certain amount of money every 24 hours [Format: %daily]"""
        try:
            user_balance = await ex.get_balance(ctx.author.id)
            user_level = await ex.get_level(ctx.author.id, "daily")
            daily_amount = int(user_balance * (user_level/200))
            if daily_amount < 100:
                daily_amount = 100
            await ex.update_balance(ctx.author.id, str(user_balance + daily_amount))
            await ctx.send(f"> **{ctx.author.display_name} has been given ${daily_amount:,}.**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=['b', 'bal', '$'])
    async def balance(self, ctx, *, user: discord.Member = discord.Member):
        """View your balance [Format: %balance (@user)][Aliases: b,bal,$]"""
        if user == discord.Member:
            user_id = ctx.author.id
        else:
            user_id = user.id
        try:
            await ex.register_user(user_id)
            amount = await ex.get_balance(user_id)
            await ctx.send("> **{} currently has {:,} Dollars.**".format(client.get_user(user_id), amount))
        except Exception as e:
            log.console(e)

    @commands.command()
    async def bet(self, ctx, *, balance="1"):
        """Bet your money [Format: %bet (amount)]"""
        try:
            balance = ex.remove_commas(balance)
            check = True
        except Exception as e:
            await ctx.send(f"> **{balance} is not a proper value.**")
            check = False
        try:
            if check:
                user_id = ctx.author.id
                if not await ex.check_in_game(user_id, ctx):
                    keep_going = True
                    if balance == 0:
                        await ctx.send("> **You are not allowed to bet 0.**")
                        keep_going = False
                    if balance > 0:
                        if keep_going:
                            await ex.register_user(user_id)
                            amount = await ex.get_balance(user_id)
                            if balance > amount:
                                await ctx.send(embed=await ex.create_embed(title="Not Enough Money", title_desc=f"**You do not have enough money to bet {balance:,}. You have {amount:,} Dollars.**" ))
                            if balance <= amount:
                                a = randint(1, 100)
                                if a <= 50:
                                    if a <= 10:
                                        new_balance = round(balance)
                                        new_amount = round(amount - balance)
                                        await ctx.send(embed=await ex.create_embed(title="Bet Loss", title_desc=f"**<@{user_id}> Got Super Unlucky! You lost {new_balance:,} out of {balance:,}. Your updated balance is {new_amount:,}.**"))
                                        await ex.update_balance(user_id, str(new_amount))
                                    if a > 10:
                                        new_balance = round(balance - (balance / 2))
                                        new_amount = round(amount - new_balance)
                                        await ctx.send(embed=await ex.create_embed(title="Bet Loss", title_desc=f"**<@{user_id}> Lost! You lost {new_balance:,} out of {balance:,}. Your updated balance is {new_amount:,}.**"))
                                        await ex.update_balance(user_id, str(new_amount))
                                if a > 50:
                                    if a <= 60:
                                        new_balance = round(balance / 5)
                                        new_amount = round(amount + new_balance)
                                        await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                        await ex.update_balance(user_id, str(new_amount))
                                    if a > 60:
                                        if a <= 70:
                                            new_balance = round(balance / 4)
                                            new_amount = round(amount + new_balance)
                                            await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                            await ex.update_balance(user_id, str(new_amount))
                                        if a > 70:
                                            if a <= 80:
                                                new_balance = round(balance / 2)
                                                new_amount = round(amount + new_balance)
                                                await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                                await ex.update_balance(user_id, str(new_amount))
                                            if a > 80:
                                                if a <= 90:
                                                    new_balance = round(balance * 1.5)
                                                    new_amount = round((amount - balance) + new_balance)
                                                    await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                                    await ex.update_balance(user_id, str(new_amount))
                                                if a > 90:
                                                    if a <= 99:
                                                        new_balance = round(balance * 2)
                                                        new_amount = round((amount - balance) + new_balance)
                                                        await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                                        await ex.update_balance(user_id, str(new_amount))
                                                    if a == 100:
                                                        new_balance = round(balance * 3)
                                                        new_amount = round((amount - balance) + new_balance)
                                                        await ctx.send(embed=await ex.create_embed(title="Bet Win", title_desc=f"**<@{user_id}> Won! You bet {balance:,} and received {new_balance:,}. Your updated balance is {new_amount:,}.**"))
                                                        await ex.update_balance(user_id, str(new_amount))
        except Exception as e:
            log.console(e)

    @commands.command(aliases=['leaderboards', 'lb'])
    async def leaderboard(self, ctx):
        """Shows Top 10 Users [Format: %leaderboard][Aliases: leaderboards, lb]"""
        counter = ex.first_result(await ex.conn.fetchrow("SELECT count(UserID) FROM currency.Currency"))
        embed = discord.Embed(title=f"Currency Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url=bot_website, icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %bal (user) to view their balance.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        if counter == 0:
            await ctx.send("> **There are no users to display.**", delete_after=60)
        if counter > 0:
            amount = await ex.conn.fetch("Select UserID,Money FROM currency.Currency")
            sort_money = []
            for sort in amount:
                new_user = [sort[0], int(sort[1])]
                sort_money.append(new_user)
            sort_money.sort(key=lambda x: x[1], reverse=True)
            count = 0
            for a in sort_money:
                count += 1
                UserID = a[0]
                Money = a[1]
                UserName = client.get_user(UserID)
                if count <= 10:
                    embed.add_field(name=f"{count}) {UserName} ({UserID})", value=await ex.shorten_balance(str(Money)), inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def beg(self, ctx):
        """Beg a homeless man for money [Format: %beg]"""
        try:
            user_balance = await ex.get_balance(ctx.author.id)
            user_level = await ex.get_level(ctx.author.id, "beg")
            daily_amount = int(7/10 * (2 ** (user_level - 2)))
            if daily_amount < 100:
                if user_balance > 10000:
                    daily_amount = randint(50, 100)
                else:
                    daily_amount = randint(1, 25)
            await ex.update_balance(ctx.author.id, str(user_balance + daily_amount))
            await ctx.send(f"> ** A homeless man has given {ctx.author.display_name} {daily_amount:,} dollars.**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=["levelup"])
    @commands.cooldown(1, 61, BucketType.user)
    async def upgrade(self, ctx, command=""):
        """Upgrade a command to the next level with your money. [Format: %upgrade rob/daily/beg]"""
        try:
            user_id = ctx.author.id
            user_balance = await ex.get_balance(user_id)
            user_level = await ex.get_level(user_id, command.lower())
            money_needed_to_level = await ex.get_xp(user_level, command.lower())
            async def not_enough_money():
                embed = await ex.create_embed(title="Not Enough Money!", title_desc=f"<@{user_id}> does not have **{money_needed_to_level:,}** dollars in order to level up {command}!")
                await ctx.send(embed=embed)
                ctx.command.reset_cooldown(ctx)

            async def level_up_process():
                if await ex.get_user_has_money(user_id):
                    desc = f"Press the Thumbs Up Reaction within 1 minute to level up.\n<@{ctx.author.id}>, you are currently at level **{user_level}** and need at least **{money_needed_to_level:,}** dollars in order to level up."
                    embed = await ex.create_embed(title="Level Up", title_desc=desc)
                    msg = await ctx.send(embed=embed)
                    reaction = "\U0001f44d"
                    await msg.add_reaction(reaction)  # thumbs up
                    if await ex.check_reaction(msg, user_id, reaction):
                        await msg.delete()
                        if user_balance < money_needed_to_level:
                            await not_enough_money()
                        else:
                            await ex.update_balance(user_id, str(user_balance - money_needed_to_level))
                            await ex.set_level(user_id, user_level + 1, command.lower())
                            embed = await ex.create_embed(title="You Have Leveled Up!",
                                                       title_desc=f"<@{ctx.author.id}>, You are now at level {user_level+1}")
                            await ctx.send(embed=embed)
                            ctx.command.reset_cooldown(ctx)
                else:
                    await ctx.send("> **You are not registered. Please type %register.**")
            if command.lower() == "rob":
                await level_up_process()
            elif command.lower() == "daily":
                await level_up_process()
            elif command.lower() == "beg":
                await level_up_process()
            else:
                await ctx.send("> **You are able to upgrade rob, daily, and beg. (ex: %upgrade rob)**")
                ctx.command.reset_cooldown(ctx)
        except Exception as e:
            await ctx.send("> **Please choose to upgrade rob, daily, or beg.**")
            ctx.command.reset_cooldown(ctx)
            log.console(e)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, *, user: discord.Member = discord.Member):
        """Rob a user [Format: %rob @user]"""
        try:
            # not actually a percent, this contains the a value of the random integer.
            level = await ex.get_level(ctx.author.id, "rob")
            rob_percent_to_win = await ex.get_rob_percentage(level)
            do_this = True
            robbed_user_id = user.id
            if user == discord.Member:
                await ctx.send("> **Please choose someone to rob!**")
                ctx.command.reset_cooldown(ctx)
                do_this = False
            if ctx.author.id == robbed_user_id:
                await ctx.send("> **You can't rob yourself!**")
                ctx.command.reset_cooldown(ctx)
                do_this = False
            if do_this:
                try:
                    await ex.register_user(robbed_user_id)
                    await ex.register_user(ctx.author.id)
                    user_money = await ex.get_balance(robbed_user_id)
                    author_money = await ex.get_balance(ctx.author.id)
                    if author_money >= 0:
                        if user_money >= 0:
                                # b value is out of 20 so each 5% is considered 1
                                all_possible_values = []
                                for i in range (rob_percent_to_win, 21):
                                    if i == rob_percent_to_win:
                                        for j in range (rob_percent_to_win):
                                            all_possible_values.append(i)
                                    else:
                                        all_possible_values.append(i)
                                random_number = choice(all_possible_values)
                                if random_number != rob_percent_to_win:
                                    await ctx.send(embed=await ex.create_embed(title="Robbed User",
                                                                            title_desc=f"**<@{ctx.author.id}> has failed to rob <@{robbed_user_id}>.**"))
                                if random_number == rob_percent_to_win:
                                    if user_money >= 100:
                                        random_amount = await ex.get_robbed_amount(author_money, user_money, level)
                                        try:
                                            await ex.update_balance(robbed_user_id, str(user_money - random_amount))
                                            await ex.update_balance(ctx.author.id, str(author_money + random_amount))
                                            await ctx.send(embed=await ex.create_embed(title="Robbed User",
                                                                                    title_desc=f"**<@{ctx.author.id}> has stolen ${random_amount:,} from <@{robbed_user_id}>.**"))
                                        except Exception as e:
                                            await ctx.send(f"> **The Database is locked... -- {e}**")
                                    elif user_money < 100:
                                        await ctx.send("> **That user has less than $100!**")
                                        ctx.command.reset_cooldown(ctx)
                except Exception as e:
                    log.console(e)
                    await ctx.send(f"> **An error occurred. Please %report it.**")
                    ctx.command.reset_cooldown(ctx)
        except Exception as e:
            log.console(e)

    @commands.command()
    async def give(self, ctx, mentioned_user: discord.Member = discord.Member, amount="0"):
        """Give a user money [Format: %give (@user) (amount)]"""
        try:
            amount = ex.remove_commas(amount)
            check = True
        except Exception as e:
            await ctx.send(f"> **{amount} is not a proper value.**")
            check = False
        try:
            if check:
                user_id = ctx.author.id
                if not await ex.check_in_game(user_id, ctx):
                    await ex.register_user(user_id)
                    if mentioned_user.id != user_id:
                        current_amount = await ex.get_balance(user_id)
                        if amount == 0:
                            await ctx.send("> **Please specify an amount [Format: %give (@user) (amount)]**", delete_after=60)
                        if amount > 0:
                            if amount > current_amount:
                                await ctx.send("> **You do not have enough money to give!**", delete_after=60)
                            if amount <= current_amount:
                                mentioned_money = await ex.get_balance(mentioned_user.id)
                                new_amount = mentioned_money + amount
                                subtracted_amount = current_amount - amount
                                await ex.update_balance(mentioned_user.id, str(new_amount))
                                await ex.update_balance(user_id, str(subtracted_amount))
                                await ctx.send("> **Your money has been transferred.**")
                    elif mentioned_user.id == user_id:
                        await ctx.send("> **You can not give money to yourself!**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=['rockpaperscissors'])
    async def rps(self, ctx, choice='', amount="0"):
        """Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]"""
        try:
            amount = ex.remove_commas(amount)
            check = True
        except Exception as e:
            await ctx.send(f"> **{amount} is not a proper value.**")
            check = False
        try:
            if check:
                if amount < 0:
                    await ctx.send("> **You can't bet a negative number!**")
                elif amount >= 0:
                    user_id = ctx.author.id
                    await ex.register_user(user_id)
                    if not await ex.check_in_game(user_id, ctx):
                        current_balance = await ex.get_balance(user_id)
                        if amount > current_balance:
                            await ctx.send("> ** You do not have enough money **", delete_after=60)
                        if amount <= current_balance:
                            rps = ['rock', 'paper', 'scissors']
                            a = randint(0, 2)
                            b = randint(0, 2)
                            cd = int(amount // (1/1.5))  # using floor division instead of multiplication
                            if amount == 0:
                                cd = 0
                            if choice == '':
                                choice = rps[a]
                            compchoice = rps[b]
                            if compchoice == 'rock':
                                if choice == 'rock' or choice == 'r':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**We Both Chose {compchoice} and Tied! You get nothing!**"))
                                if choice == 'paper' or choice == 'p':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**You Won {cd:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance + cd))
                                if choice == 'scissors' or choice == 's':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors",title_desc=f"**You Lost {amount:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance - amount))
                            if compchoice == 'paper':
                                if choice == 'rock' or choice == 'r':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**You Lost {amount:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance - amount))
                                    check_amount = str(current_balance - amount)
                                    await ex.update_balance(user_id, check_amount)
                                if choice == 'paper' or choice == 'p':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**We Both Chose {compchoice} and Tied! You get nothing!**"))
                                if choice == 'scissors' or choice == 's':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**You Won {cd:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance + cd))
                            if compchoice == 'scissors':
                                if choice == 'rock' or choice == 'r':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**You Won {cd:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance + cd))
                                if choice == 'paper' or choice == 'p':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**You Lost {amount:,} Dollars! I chose {compchoice} while you chose {choice}!**"))
                                    await ex.update_balance(user_id, str(current_balance - amount))
                                if choice == 'scissors' or choice == 's':
                                    await ctx.send(embed=await ex.create_embed(title="Rock Paper Scissors", title_desc=f"**We Both Chose {compchoice} and Tied! You get nothing!**"))
                await ctx.message.delete(delay=15)
        except Exception as e:
            log.console(e)
