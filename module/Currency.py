from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

import sqlite3
from random import *


client = 0
path = 'module\currency.db'
DBconn = sqlite3.connect(path, check_same_thread = False)
c = DBconn.cursor()

def setup(client1):
    client1.add_cog(Currency(client1))
    global client
    client = client1


class Currency(commands.Cog):
    def __init__(self, client):
        self.a = -1
        self.counter = 0
        pass

    @commands.command()
    @commands.is_owner()
    async def resetall(self, ctx):
        """Resets Leaderboard [Format: %resetall] USE WITH CAUTION"""
        count = c.execute("SELECT COUNT(UserID) FROM Currency").fetchone()[0]
        c.execute("DELETE FROM Currency")
        DBconn.commit()
        await ctx.send("> **{} users have been deleted.**".format(count))

    @commands.command()
    @commands.is_owner()
    async def rafflereset(self, ctx):
        """Resets Raffle without giving people their money back[Format: %rafflereset]"""
        c.execute("DELETE FROM RaffleData")
        c.execute("DELETE FROM Raffle")
        await ctx.send("> **Lottery was reset successfully.**")
        DBconn.commit()

    @tasks.loop(seconds=0, minutes=0, hours=24, reconnect=True, count=2)
    async def new_task2(self, ctx):
        print("Connecting to Background Task For Raffle...")
        self.a += 1
        if self.a == 0:
            pass
        if self.a == 1:
            temp_list2 = []
            fake_list3 = []
            all_balance = c.execute("SELECT SUM(Amount) FROM RaffleData").fetchone()[0]
            balance = all_balance
            if balance == 0:
                await ctx.send("> **There were no winners for the raffle. Raffle closing**")
            if balance >= 1:
                count_number = c.execute("SELECT COUNT(*) FROM RaffleData").fetchone()[0]
                random_number = randint(1, count_number)
                winner = c.execute("SELECT UserID FROM RaffleData WHERE RaffleID = ?", (random_number,)).fetchone()[0]
                current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (winner,)).fetchone()[0]
                new_total = current_val + balance
                await ctx.send("> **<@{}> has won {} Dollars from the raffle!**".format(winner, balance))
                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (new_total, winner))
                c.execute("DELETE FROM Raffle")
                c.execute("DELETE FROM RaffleData")
                DBconn.commit()

    @commands.command()
    async def raffle(self, ctx, amount=0, balance=''):
        """Join a Raffle [Format: %raffle to start a raffle; %raffle (amount) to join; %raffle 0 balance to check current amount]"""
        userid = ctx.author.id
        if amount >= 0 or balance == 'balance':

            if balance != 'balance':
                try:
                    current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
                except:
                    await ctx.send("> **You are not currently registered. Please type %register to register.**",
                                   delete_after=60)
                if current_val < amount:
                    await ctx.send("> **You do not have enough money to join this raffle.**")
                self.counter = c.execute("SELECT COUNT(*) FROM Raffle").fetchone()[0]
                if current_val >= amount and amount >= 1:
                    if self.counter == 0:
                        await ctx.send("> **Please type %raffle to start a raffle.**")
                    if self.counter == 1:
                        new_val = current_val - amount
                        search_count = \
                        c.execute("SELECT COUNT(*) FROM RaffleData WHERE UserID = ?", (userid,)).fetchone()[0]
                        if search_count == 0:
                            for b in range(0, amount):
                                c.execute("INSERT INTO RaffleData VALUES (NULL,?,?)", (userid, 1))
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (new_val, userid))
                            await ctx.send("> **You have added {} Dollars to the raffle.**".format(amount))
                        if search_count >= 1:
                            old_amount = \
                            c.execute("SELECT SUM(Amount) FROM RaffleData WHERE UserID = ?", (userid,)).fetchone()[0]
                            new_amount = old_amount + amount
                            for b in range(0, amount):
                                c.execute("INSERT INTO RaffleData VALUES (NULL,?,?)", (userid, 1))
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (new_val, userid))
                            await ctx.send(
                                "> **You have added another {} Dollars to the raffle. You currently have {} entries.**".format(
                                    amount, new_amount))
                if amount == 0:
                    if self.counter == 1:
                        await ctx.send("> **A Raffle Already Exists. Use %raffle (amount) to join.**")
                    if self.counter == 0:
                        await ctx.send("> **A Raffle has been started. Use %raffle (amount) to join.**")
                        c.execute("INSERT INTO Raffle VALUES (NULL,?,?,?)", (0, 0, 0))
                        self.a = -1
                        self.new_task2.start(ctx)
            if balance == 'balance':
                self.counter = c.execute("SELECT COUNT(*) FROM Raffle").fetchone()[0]
                if self.counter == 1:
                    try:
                        all_balance = c.execute("SELECT SUM(Amount) FROM RaffleData").fetchone()[0]
                        balance = all_balance
                        c.execute("UPDATE Raffle SET Amount = ? WHERE Finished = ?", (balance, 0))
                        await ctx.send("> **{} Dollars are currently in the raffle**".format(balance))
                    except:
                        await ctx.send("> **There are no raffle entries**")
                if self.counter == 0:
                    await ctx.send("> **No Raffle Exists. Please type %raffle to start a raffle.**")

        if amount < 0:
            await ctx.send("> You are not allowed to raffle a negative amount")
        DBconn.commit()

    @commands.command()
    async def register(self, ctx):
        """Register yourself onto the database."""
        userid = ctx.author.id
        count = c.execute("SELECT COUNT(*) FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
        if count == 0:
            c.execute("INSERT INTO Currency (UserID, Money) VALUES (?, ?)", (userid, 100))
            DBconn.commit()
            await ctx.send("> **You are now registered in the database. You have been given 100 Dollars to start.**")
        elif count == 1:
            await ctx.send("> **You are already registered in the database.**")

    @commands.command(aliases=['b', 'bal', '$'])
    async def balance(self, ctx, *, user=""):
        """View your balance [Format: %balance (@user)][Aliases: b,bal,$]"""
        if user == "":
            userid = ctx.author.id
        else:
            userid = ctx.message.raw_mentions[0]
        try:
            amount = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
            await ctx.send("> **{} currently has {} Dollars.**".format(client.get_user(userid), amount))
        except:
            c.execute("INSERT INTO Currency (UserID, Money) VALUES (?, ?)", (userid, 100))
            DBconn.commit()
            await ctx.send(
                "> **{} is now registered in the database. They have been given 100 Dollars to start.**".format(
                    client.get_user(userid)))

    @commands.command()
    async def bet(self, ctx, *, balance=1):
        """Bet your money [Format: %bet (amount)]"""
        userid = ctx.author.id
        check_1 = c.execute("SELECT COUNT(*) From Games WHERE Player1 = ? OR Player2 = ?", (userid, userid)).fetchone()[
            0]
        if check_1 == 0:
            keep_going = True
            if balance == 0:
                await ctx.send("> **You are not allowed to bet 0.**")
                keep_going = False
            if balance > 0:
                if keep_going == True:
                    try:
                        amount = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
                    except:
                        c.execute("INSERT INTO Currency (UserID, Money) VALUES (?, ?)", (userid, 100))
                        DBconn.commit()
                        await ctx.send(
                            "> **You are now registered in the database. You have been given 100 Dollars to start.**")
                        amount = 100
                    if balance > amount:
                        await ctx.send(
                            "> **You don't have enough money to bet {}. You have {} Dollars.**".format(balance, amount))
                    if balance <= amount:
                        a = randint(1, 100)
                        if a <= 50:
                            if a <= 10:
                                newbalance = round(balance)
                                newamount = round(amount - balance)
                                await ctx.send(
                                    "> **<@{}> Got Super Unlucky! You lost {} out of {}. Your updated balance is {}.**".format(
                                        userid, newbalance, balance, newamount))
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, userid))
                                DBconn.commit()
                            if a > 10:
                                newbalance = round(balance - (balance / 2))
                                newamount = round(amount - newbalance)
                                await ctx.send(
                                    "> **<@{}> Lost! You lost {} out of {}. Your updated balance is {}.**".format(
                                        userid, newbalance, balance, newamount))
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, userid))
                                DBconn.commit()
                        if a > 50:
                            if a <= 60:
                                newbalance = round(balance / 5)
                                newamount = round(amount + newbalance)
                                await ctx.send(
                                    "> **<@{}> Won! You bet {} and received {}. Your updated balance is {}.**".format(
                                        userid, balance, newbalance, newamount))
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, userid))
                                DBconn.commit()
                            if a > 60:
                                if a <= 70:
                                    newbalance = round(balance / 4)
                                    newamount = round(amount + newbalance)
                                    await ctx.send(
                                        "> **<@{}> Won! You bet {} and received {}. Your updated balance is {}.**".format(
                                            userid, balance, newbalance, newamount))
                                    c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, userid))
                                    DBconn.commit()
                                if a > 70:
                                    if a <= 80:
                                        newbalance = round(balance / 2)
                                        newamount = round(amount + newbalance)
                                        await ctx.send(
                                            "> **<@{}> Won! You bet {} and received {}. Your updated balance is {}.**".format(
                                                userid, balance, newbalance, newamount))
                                        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, userid))
                                        DBconn.commit()
                                    if a > 80:
                                        if a <= 90:
                                            newbalance = round(balance * 1.5)
                                            newamount = round((amount - balance) + newbalance)
                                            await ctx.send(
                                                "> **<@{}> Won! Your {} has been multiplied by 1.5 to {}. Your updated balance is {}.**".format(
                                                    userid, balance, newbalance, newamount))
                                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?",
                                                      (newamount, userid))
                                            DBconn.commit()
                                        if a > 90:
                                            if a <= 99:
                                                newbalance = round(balance * 2)
                                                newamount = round((amount - balance) + newbalance)
                                                await ctx.send(
                                                    "> **<@{}> Won! Your {} has been doubled to {}. Your updated balance is {}.**".format(
                                                        userid, balance, newbalance, newamount))
                                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?",
                                                          (newamount, userid))
                                                DBconn.commit()
                                            if a == 100:
                                                newbalance = round(balance * 3)
                                                newamount = round((amount - balance) + newbalance)
                                                await ctx.send(
                                                    "> **<@{}> Won! Your {} has been tripled to {}. Your updated balance is {}.**".format(
                                                        userid, balance, newbalance, newamount))
                                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?",
                                                          (newamount, userid))
                                                DBconn.commit()
        if check_1 >= 1:
            await ctx.send("> **Please type %endgame. You cannot use this command when you're in a game.**")

    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx):
        """Shows Top 10 Users [Format: %leaderboard][Aliases: leaderboards]"""
        counter = c.execute("SELECT count(UserID) FROM Currency").fetchone()[0]
        if counter == 0:
            await ctx.send("> **There are no users to display.**", delete_after=60)
        if counter > 0:
            amount = c.execute("Select UserID,Money FROM Currency ORDER BY Money DESC").fetchall()
            list_money = []
            for a in amount:
                UserID = a[0]
                Money = a[1]
                UserName = client.get_user(UserID)
                final = "**{} ({}) currently has {} Dollars.**\n".format(UserName, UserID, Money)
                list_money.append(final)
            final = list_money[0:9]
            final_list = ''
            for a in final:
                final_list += a
            await ctx.send(">>> {}".format(final_list), delete_after=60)

    @commands.command()
    async def beg(self, ctx):
        """Beg a homeless man for money [Format: %beg]"""
        userid = ctx.author.id
        broke_money = randint(1, 9)
        try:
            amount = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
        except:
            c.execute("INSERT INTO Currency (UserID, Money) VALUES (?, ?)", (userid, 100))
            DBconn.commit()
            await ctx.send("> **You are now registered in the database. You have been given 100 Dollars to start.**")
            amount = 100
        await ctx.send("> **A homeless man gave you {} Dollar(s)**.".format(broke_money))

        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (broke_money + amount, userid))
        DBconn.commit()

    @commands.command()
    async def roll(self, ctx):
        """No Description Yet"""
        pass

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, *, user = ""):
        """Rob a user - Max Value = 1000 [Format: %rob @user]"""
        # ADD A DELAY TO HOW MANY TIMES THEY CAN USE THE COMMAND
        if user == "":
            await ctx.send("> **Please @ the user you want to rob**")
        else:
            userid = ctx.message.raw_mentions[0]
        try:
            user_money = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
            actual_user_money = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (ctx.author.id,)).fetchone()[0]
        except:
            await ctx.send(f"> **Either you or <@{userid}> is not registered. Please type %register first.**")
            ctx.command.reset_cooldown(ctx)
        if ctx.author.id != userid:
            if actual_user_money >= 0:
                if user_money >= 0:
                        try:
                            random_number = randint(0, 1)
                            if random_number == 0:
                                await ctx.send(f"> **You have failed to rob <@{userid}>**")
                            if random_number == 1:
                                if user_money >= 10:
                                    # One Billion
                                    if user_money >= 1000:
                                        random_amount = randint(100, 500)
                                    elif 500 <= user_money < 1000:
                                        random_amount = randint(50, 100)
                                    elif 100 <= user_money < 500:
                                        random_amount = randint(10, 50)
                                    elif 10 <= user_money < 100:
                                        random_amount = randint(5, 10)
                                    actual_user_money = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (ctx.author.id,)).fetchone()[0]
                                    actual_user_money = actual_user_money + random_amount
                                    user_money = user_money - random_amount
                                    c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (user_money, userid))
                                    c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (actual_user_money, ctx.author.id))
                                    DBconn.commit()
                                    await ctx.send(f"> **You have stolen ${random_amount} from <@{userid}>.**")
                                elif user_money < 10:
                                    await ctx.send("> **That user has less than $10!**")
                                    ctx.command.reset_cooldown(ctx)
                        except Exception as e:
                            print(e)
                            await ctx.send("> **An error has occurred.**")
                            ctx.command.reset_cooldown(ctx)
        if ctx.author.id == userid:
            await ctx.send("> **You can't rob yourself!**")
            ctx.command.reset_cooldown(ctx)

    @commands.command()
    async def give(self, ctx, mentioned_userid="", amount=0):
        """Give a user money [Format: %give (@user) (amount)]"""
        userid = ctx.author.id
        check_1 = c.execute("SELECT COUNT(*) From Games WHERE Player1 = ? OR Player2 = ?", (userid, userid)).fetchone()[
            0]
        if check_1 == 0:
            mentioned_userid = ctx.message.raw_mentions[0]
            count = c.execute("SELECT count(UserID) FROM Currency WHERE USERID = ?", (userid,)).fetchone()[0]
            if count == 0:
                await ctx.send("> **You are not currently registered. Please type %register to register.**",
                               delete_after=60)
            if count == 1:
                current_amount = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
                if amount == 0:
                    await ctx.send("> **Please specify an amount [Format: %give (@user) (amount)]**", delete_after=60)
                if amount > 0:
                    if amount > current_amount:
                        await ctx.send("> **You do not have enough money to give!**", delete_after=60)
                    if amount <= current_amount:
                        newcount = c.execute("SELECT count(UserID) FROM Currency WHERE USERID = ?",
                                             (mentioned_userid,)).fetchone()[0]
                        if newcount == 0:
                            await ctx.send(
                                "> **That user is not currently registered. Have them type %register to register.**")
                        if newcount == 1:
                            mentioned_money = \
                            c.execute("SELECT Money FROM Currency WHERE USERID = ?", (mentioned_userid,)).fetchone()[0]
                            newamount = mentioned_money + amount
                            newamount2 = current_amount - amount
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount, mentioned_userid))
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (newamount2, userid))
                            await ctx.send("> **Your money has been transferred.**")
                            DBconn.commit()
                        if newcount > 1:
                            await ctx.send(
                                "> **There is an error with the database. Please report to an administrator**")

            if count > 1:
                await ctx.send("> **There is an error with the database. Please report to an administrator**")
        if check_1 >= 1:
            await ctx.send("> **Please type %endgame. You cannot use this command when you're in a game.**")

    @commands.command(aliases=['rockpaperscissors'])
    async def rps(self, ctx, choice='', amount=0):
        """Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]"""
        userid = ctx.author.id
        check_1 = c.execute("SELECT COUNT(*) From Games WHERE Player1 = ? OR Player2 = ?", (userid, userid)).fetchone()[
            0]
        if check_1 == 0:
            try:
                current_balance = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
            except:
                pass
            count = c.execute("SELECT count(UserID) FROM Currency WHERE USERID = ?", (userid,)).fetchone()[0]
            if count == 0:
                await ctx.send("> **You are not currently registered. Please type %register to register.**",
                               delete_after=60)
            if amount > current_balance:
                await ctx.send("> ** You do not have enough money **", delete_after=60)
            if amount <= current_balance:
                def Win(win):
                    c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (win, userid))
                    DBconn.commit()

                def Loss(loss):
                    c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (loss, userid))
                    DBconn.commit()

                if count == 1:
                    # current_balance called again incase it does not properly update
                    current_balance = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (userid,)).fetchone()[0]
                    amount = amount
                    rps = ['rock', 'paper', 'scissors']
                    a = randint(0, 2)
                    b = randint(0, 2)
                    #cd = randint(10, 30)
                    cd = 2 * amount
                    if amount == 0:
                        cd = 0
                    if choice == '':
                        choice = rps[a]
                    compchoice = rps[b]
                    if compchoice == 'rock':
                        if choice == 'rock':
                            await ctx.send("> **We Both Chose Rock and Tied! You get nothing!**", delete_after=15)
                        if choice == 'paper':
                            await ctx.send(
                                "> **You Won {} Dollars! I chose {} while you chose {}!**".format(cd, compchoice,
                                                                                                  choice),
                                delete_after=15)
                            Win(current_balance + cd)
                        if choice == 'scissors':
                            await ctx.send(
                                "> **You Lost {} Dollars! I chose {} while you chose {}!**".format(amount, compchoice,
                                                                                                   choice),
                                delete_after=15)
                            Loss(current_balance - amount)
                    if compchoice == 'paper':
                        if choice == 'rock':
                            await ctx.send(
                                "> **You Lost {} Dollars! I chose {} while you chose {}!**".format(amount, compchoice,
                                                                                                   choice),
                                delete_after=15)
                            Loss(current_balance - amount)
                        if choice == 'paper':
                            await ctx.send("> **We Both Chose Paper and Tied! You get nothing!**")
                        if choice == 'scissors':
                            await ctx.send(
                                "> **You Won {} Dollars! I chose {} while you chose {}!**".format(cd, compchoice,
                                                                                                  choice),
                                delete_after=15)
                            Win(current_balance + cd)

                    if compchoice == 'scissors':
                        if choice == 'rock':
                            await ctx.send(
                                "> **You Won {} Dollars! I chose {} while you chose {}!**".format(cd, compchoice,
                                                                                                  choice),
                                delete_after=15)
                            Win(current_balance + cd)
                        if choice == 'paper':
                            await ctx.send(
                                "> **You Lost {} Dollars! I chose {} while you chose {}!**".format(amount, compchoice,
                                                                                                   choice),
                                delete_after=15)
                            Loss(current_balance - amount)
                        if choice == 'scissors':
                            await ctx.send("> **We Both Chose Scissors and Tied! You get nothing!**")
                    if count > 1:
                        await ctx.send("> **There is an error with the database. Please report to an administrator**")
        if check_1 >= 1:
            await ctx.send("> **Please type %endgame. You cannot play a game when you're already in one.**")
