import discord
from discord.ext import commands, tasks
from random import *
from module import logger as log
from Utility import DBconn, c, fetch_one, fetch_all


class BlackJack(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.count = 0
        self.aces = 0
        self.game_list = []
        self.tasks = list()
        self.task_list = []
        self.ace_list = []
        self.ace2_list = []
        pass

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, *, amount=0):
        """Start a game of BlackJack [Format: %blackjack (amount)] [Aliases: bj]"""
        if amount >= 0:
            try:
                game_type = 'blackjack'
                player_1 = ctx.author.id
                c.execute("SELECT count(*) FROM currency.Games WHERE Player1 = %s or Player2 = %s", (player_1, player_1))
                counter = fetch_one()
                if counter == 1:
                    embed_message = "**You are already in a pending/active game. Please type %endgame to end your current game.**"
                    embed = discord.Embed(title="Error", description=embed_message, color=0xff00f6)
                    await ctx.send(embed=embed, delete_after=40)
                if counter == 0:
                    player_2 = 0
                    player1_bid = amount
                    player2_bid = 0
                    c.execute("SELECT count(UserID) FROM currency.Currency WHERE USERID = %s", (player_1,))
                    count = fetch_one()
                    if count == 0:
                        await ctx.send("> **You are not currently registered. Please type %register to register.**",
                                       delete_after=40)
                    if count == 1:
                        c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                        current_amount = int(fetch_one())
                        if amount > current_amount:
                            await ctx.send("> **You do not have enough money to give!**", delete_after=40)
                        if amount <= current_amount:
                            c.execute("INSERT INTO currency.Games VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                      (player_1, player_2, player1_bid, player2_bid, 0, 0, game_type, 11))
                            DBconn.commit()
                            c.execute("SELECT GameID FROM currency.Games WHERE Player1 = %s", (player_1,))
                            game_id = fetch_one()
                            await ctx.send(
                                "> **There are currently 1/2 members signed up for BlackJack. To join the game, please type %joingame {} (bid)**".format(game_id))
                    if count > 1:
                        await ctx.send("> **There is an error with the database. Please report to an administrator**",
                                       delete_after=40)
            except Exception as e:
                log.console (e)
                await ctx.send(
                    "> **You are already in a pending/active game. Please type %endgame to end your current game.**",
                    delete_after=40)
        elif amount < 0:
            await ctx.send("> **You cannot bet a negative number**")

    # background loops
    def _start_tasks(self, ctx, game_id, player_1, player_2):
        for game in self.game_list:
            # if not game in self.game2_list:
            # self.game2_list.append(game)
            @tasks.loop(seconds=5.0)
            async def new_task():
                self.count += 1
                # log.console (game)
                c.execute("SELECT Stand FROM currency.Games WHERE GameID = %s", (game_id,))
                stand = str(fetch_one())
                if stand == '22':
                    c.execute("SELECT Score1 FROM currency.Games WHERE GameID = %s", (game_id,))
                    score_1 = fetch_one()
                    c.execute("SELECT Score2 FROM currency.Games WHERE GameID = %s", (game_id,))
                    score_2 = fetch_one()
                    c.execute("SELECT Bid1 FROM currency.Games WHERE GameID = %s", (game_id,))
                    bid_1 = fetch_one()
                    c.execute("SELECT Bid2 FROM currency.Games WHERE GameID = %s", (game_id,))
                    bid_2 = fetch_one()
                    bid_sum = bid_1 + bid_2
                    c.execute("DELETE FROM currency.Games WHERE GameID = %s", (game_id,))
                    c.execute("DELETE FROM currency.BlackJack WHERE GameID = %s", (game_id,))
                    if score_1 > 21 and score_2 > 21:
                        if score_1 == score_2:
                            await ctx.send(
                                "> **You have both tied with a score of {}! No prizes were given.**".format(score_1),
                                delete_after=40)
                        result_1 = score_1 - 21
                        result_2 = score_2 - 21
                        if result_1 < result_2:
                            # player 1 wins
                            # add money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                            current_val = int(fetch_one())
                            total_amount = bid_2 + current_val
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_1))
                            # subtract money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                            current_val = int(fetch_one())
                            total_amount = current_val - bid_2
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_2))
                            await ctx.send(
                                "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_1, bid_sum, score_1, player_2, score_2), delete_after=40)

                        if result_2 < result_1:
                            # player 2 wins
                            # add money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                            current_val = fetch_one()
                            total_amount = bid_1 + current_val
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_2))
                            # subtract money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                            current_val = int(fetch_one())
                            total_amount = current_val - bid_1
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_1))
                            await ctx.send(
                                "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    if score_1 < 21 and score_2 < 21:
                        if score_1 == score_2:
                            await ctx.send(
                                "> **You have both tied with a score of {}! No prizes were given.**".format(score_1),
                                delete_after=40)
                        if score_1 > score_2:
                            # player 1 wins
                            # add money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                            current_val = int(fetch_one())
                            total_amount = bid_2 + current_val
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_1))
                            # subtract money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                            current_val = int(fetch_one())
                            total_amount = current_val - bid_2
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (total_amount, player_2))
                            await ctx.send(
                                "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                        if score_2 > score_1:
                            # player 2 wins
                            # add money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                            current_val = int(fetch_one())
                            total_amount = bid_1 + current_val
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_2))
                            # subtract money
                            c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                            current_val = int(fetch_one())
                            total_amount = current_val - bid_1
                            c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_1))
                            await ctx.send(
                                "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    if score_1 == 21 or score_2 == 21:
                        if score_1 == score_2:
                            await ctx.send(
                                "> **You have both achieved BlackJack as a tie! No prizes were given.**".format(
                                    score_1), delete_after=40)
                        if score_1 != score_2:
                            if score_1 == 21:
                                # player1 wins
                                # add money
                                c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                                current_val = int(fetch_one())
                                total_amount = bid_2 + current_val
                                c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_1))
                                # subtract money
                                c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                                current_val = int(fetch_one())
                                total_amount = current_val - bid_2
                                c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_2))
                                await ctx.send(
                                    "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                        player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                            if score_2 == 21:
                                # player2 wins
                                # add money
                                c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                                current_val = int(fetch_one())
                                total_amount = bid_1 + current_val
                                c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_2))
                                # subtract money
                                c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                                current_val = int(fetch_one())
                                total_amount = current_val - bid_1
                                c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_1))
                                await ctx.send(
                                    "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                        player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    if score_1 < 21 and score_2 > 21:
                        # player1 wins
                        # add money
                        c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                        current_val = int(fetch_one())
                        total_amount = bid_2 + current_val
                        c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_1))
                        # subtract money
                        c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                        current_val = int(fetch_one())
                        total_amount = current_val - bid_2
                        c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_2))
                        await ctx.send(
                            "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                    if score_1 > 21 and score_2 < 21:
                        # player2 wins
                        # add money
                        c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                        current_val = int(fetch_one())
                        total_amount = bid_1 + current_val
                        c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_2))
                        # subtract money
                        c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_1,))
                        current_val = int(fetch_one())
                        total_amount = current_val - bid_1
                        c.execute("UPDATE currency.Currency SET Money = %s WHERE UserID = %s", (f'{total_amount}', player_1))
                        await ctx.send(
                            "> **<@{}> has won {:,} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    DBconn.commit()
                    self.tasks.remove(self.task_list)
                    self.count = 0
                    new_task.stop()
                if self.count == 60:
                    await ctx.send("> **Game {} has been deleted due to it's 5 minute limit.**".format(game_id))
                    # await ctx.send("sending {}".format(self.task_list))
                    c.execute("DELETE FROM currency.Games WHERE GameID = %s", (game_id,))
                    c.execute("DELETE FROM currency.BlackJack WHERE GameID = %s", (game_id,))
                    DBconn.commit()
                    self.tasks.remove(self.task_list)
                    self.count = 0
                    new_task.stop()

            self.task_list = []
            self.task_list.append(new_task)
            self.task_list.append(player_1)
            self.task_list.append(player_2)
            self.tasks.append(self.task_list)
            new_task.start()

    @commands.command(aliases=['jg'])
    async def joingame(self, ctx, gameid=0, amount=0):
        """Join a game [Format: %joingame (gameid) (bid)] [Aliases: jg]"""
        if amount >= 0:
            if gameid == 0:
                await ctx.send("> **Please include the game id in your command. [Format: %jg (gameid) (bid)]**",
                               delete_after=40)
            if gameid != 0:
                try:
                    rules = "**Each Player gets 2 cards.\nIn order to get blackjack, your final value must equal 21.\nIf Player1 exceeds 21 and Player2 doesn't, Player1 busts and Player2 wins the game.\nYou will have two options.\nThe first option is to %Hit, which means to grab another card.\nThe second option is to %stand to not pick up anymore cards.\nEach Player will play one at a time so think ahead!\nIf both players bust, Player closest to 21 wins!\nNumber cards are their values.\nAces can be 1 or 11 depending on the scenario.\nJack, Queen, and King are all worth 10. **"
                    player_2 = ctx.author.id
                    player2_bid = amount
                    game_id = gameid
                    c.execute("SELECT Player1 FROM currency.Games WHERE GameID = %s", (game_id,))
                    check = fetch_one()
                    c.execute("SELECT Player2 FROM currency.Games WHERE GameID = %s", (game_id,))
                    check2 = fetch_one()
                    c.execute("SELECT COUNT(*) FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (player_2, player_2))
                    count_checker = fetch_one()
                    if count_checker >= 1:
                        await ctx.send(
                            "> **You are already in a pending/active game. Please type %endgame to end your current game.**",
                            delete_after=40)
                    if count_checker == 0:
                        if check2 != 0:
                            await ctx.send("> **This game has already started.**", delete_after=40)
                        if check2 == 0:
                            if check == player_2:
                                await ctx.send("> **You are already in this game.**", delete_after=40)
                            if check != player_2:
                                c.execute("SELECT count(UserID) FROM currency.Currency WHERE USERID = %s", (player_2,))
                                count = fetch_one()
                                if count == 0:
                                    await ctx.send(
                                        "> **You are not currently registered. Please type %register to register.**",
                                        delete_after=40)
                                if count == 1:
                                    c.execute("SELECT Money FROM currency.Currency WHERE UserID = %s", (player_2,))
                                    current_amount = int(fetch_one())
                                    if amount > current_amount:
                                        await ctx.send("> **You do not have enough money to give!**", delete_after=40)
                                    if amount <= current_amount:
                                        c.execute("UPDATE currency.Games SET Player2 = %s, Bid2 = %s WHERE GameID = %s",
                                                  (player_2, player2_bid, game_id))
                                        DBconn.commit()
                                        c.execute("SELECT Bid1, Bid2 FROM currency.Games Where GameID = %s", (game_id,))
                                        total_1 = fetch_all()
                                        for a in total_1:
                                            x = a[0]
                                            y = a[1]
                                        total = x + y
                                        await ctx.send(
                                            "> **Starting BlackJack with a total bid of {:,} Dollars.**".format(total),
                                            delete_after=60)
                                        await ctx.send(">>> {}".format(rules), delete_after=60)
                                        new_list = []
                                        file_1 = []
                                        file_2 = []
                                        for i in range(0, 4):
                                            random_card = randint(1, 52)
                                            while random_card in new_list:
                                                random_card = randint(1, 52)
                                            new_list.append(random_card)
                                        for i in range(0, 2):
                                            c.execute("SELECT cardname FROM currency.CardValues WHERE CardID = %s", (new_list[i],))
                                            card_name = fetch_one()
                                            c.execute("SELECT value FROM currency.CardValues WHERE CardID = %s", (new_list[i],))
                                            card_value = fetch_one()
                                            c.execute("SELECT Score1 FROM currency.Games WHERE GameID = %s", (game_id,))
                                            current_val = fetch_one()
                                            c.execute("INSERT INTO currency.BlackJack VALUES (%s, %s, %s)", (game_id, new_list[i], 1))
                                            tot1 = current_val + card_value
                                            c.execute("UPDATE currency.Games SET Score1 = %s WHERE GameID = %s", (tot1, game_id))
                                            card_1 = discord.File(fp='Cards/{}.jpg'.format(new_list[i]),
                                                                  filename='{}.jpg'.format(new_list[i]), spoiler=True)
                                            file_1.append(card_1)
                                            DBconn.commit()
                                        for i in range(2, 4):
                                            c.execute("SELECT cardname FROM currency.CardValues WHERE CardID = %s", (new_list[i],))
                                            card_name = fetch_one()
                                            c.execute("SELECT value FROM currency.CardValues WHERE CardID = %s", (new_list[i],))
                                            card_value = fetch_one()
                                            c.execute("SELECT Score2 FROM currency.Games WHERE GameID = %s", (game_id,))
                                            current_val = fetch_one()
                                            c.execute("INSERT INTO currency.BlackJack VALUES (%s, %s, %s)", (game_id, new_list[i], 2))
                                            tot = current_val + card_value
                                            c.execute("UPDATE currency.Games SET Score2 = %s WHERE GameID = %s", (tot, game_id))
                                            card_2 = discord.File(fp='Cards/{}.jpg'.format(new_list[i]),
                                                                  filename='{}.jpg'.format(new_list[i]), spoiler=True)
                                            file_2.append(card_2)
                                            DBconn.commit()
                                        c.execute("SELECT Player1 FROM currency.Games WHERE GameID = %s", (game_id,))
                                        player_1 = fetch_one()
                                        await ctx.send("<@{}>'s current score is ||{}||".format(player_1, tot1),
                                                       files=file_1, delete_after=120)
                                        await ctx.send("<@{}>'s current score is ||{}||".format(player_2, tot),
                                                       files=file_2, delete_after=120)
                                        self.aces = 0
                                        self.game_list = []
                                        self.game_list.append(game_id)
                                        # self._start_tasks()
                                        self._start_tasks(ctx, game_id, player_1, player_2)
                                        # self.bgloop.start(ctx, game_id, player_1, player_2)

                                if count > 1:
                                    await ctx.send(
                                        "> **There is an error with the database. Please report to an administrator**",
                                        delete_after=40)
                except Exception as e:
                    log.console (e)
                    await ctx.send("> **Failed to join. This game does not exist.**", delete_after=40)
        elif amount < 0:
            await ctx.send("> **You cannot bet a negative number**")

    @commands.command(aliases=['eg'])
    async def endgame(self, ctx):
        """End your current game [Format: %endgame] [Aliases: eg]"""
        try:
            c.execute("SELECT currency.GameID FROM Games WHERE Player1 = %s OR Player2 = %s", (ctx.author.id, ctx.author.id))
            game_id = fetch_one()
            c.execute("DELETE FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (ctx.author.id, ctx.author.id))
            c.execute("DELETE FROM currency.BlackJack WHERE GameID = %s", (game_id,))
            DBconn.commit()
            for task in self.tasks:
                # await ctx.send(task)
                x = task[0]
                y = task[1]
                z = task[2]
                if ctx.author.id == y or ctx.author.id == z:
                    x.stop()
                    self.tasks.remove(task)
            await ctx.send("> **You have been removed from your current game.**", delete_after=5)
            self.count = 0
        except:
            await ctx.send("> **You are not currently in a running game.**", delete_after=40)

    @commands.command()
    @commands.is_owner()
    async def addcards(self, ctx):
        """Fill The CardValues Table with Cards [Format: %addcards]"""
        c.execute("DELETE FROM currency.CardValues")
        suitName = ("Hearts", "Diamonds", "Spades", "Clubs")
        rankName = ("Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
                    "Eight", "Nine", "Ten", "Jack", "Queen", "King")
        cardvalues = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3,
                      4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        cards = []
        for suit in suitName[0:4]:
            for rank in rankName[0:13]:
                cards += [("{} of {}".format(rank, suit))]
        countx = -1
        for card in cards:
            countx += 1
            c.execute("INSERT INTO currency.CardValues VALUES (%s, %s)", (card, cardvalues[countx]))
        DBconn.commit()
        await ctx.send("> **All cards have been added into the table.**", delete_after=40)

    @commands.command()
    async def hit(self, ctx):
        """Pick A Card [Format: %hit]"""
        userid = ctx.author.id
        try:
            random_card = randint(1, 52)
            c.execute("SELECT GameID FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (userid, userid))
            game_id = fetch_one()
            c.execute("SELECT Player1,Player2 FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (userid, userid))
            player = c.fetchone()
            c.execute("SELECT CardID FROM currency.BlackJack WHERE GameID =%s", (game_id,))
            cards = fetch_all()
            while random_card in cards:
                random_card = randint(1, 52)
            Player1 = player[0]
            Player2 = player[1]
            c.execute("SELECT Stand FROM currency.Games WHERE GameID = %s", (game_id,))
            current_stand = str(fetch_one())
            keep_going = True
            if userid == Player1:
                xyz = 1
                if current_stand[0] == 2:
                    keep_going = False
            if userid == Player2:
                xyz = 2
                if current_stand[1] == 2:
                    keep_going = False
            if keep_going == True:
                c.execute("INSERT INTO currency.BlackJack VALUES (%s, %s, %s)", (game_id, random_card, xyz))
                abc = discord.File(fp='Cards/{}.jpg'.format(random_card), filename='{}.jpg'.format(random_card),
                                   spoiler=True)
                c.execute("SELECT value FROM currency.CardValues WHERE CardID = %s", (random_card,))
                card_value = fetch_one()
                c.execute("SELECT Score{} FROM currency.Games WHERE GameID = %s".format(xyz), (game_id,))
                current_val = fetch_one()
                tot = current_val + card_value
                c.execute("SELECT COUNT(*) FROM currency.BlackJack WHERE CardID = %s AND Position = %s AND GameID = %s", (1, xyz, game_id))
                check_for_ace1 = fetch_one()
                c.execute("SELECT COUNT(*) FROM currency.BlackJack WHERE CardID = %s AND Position = %s AND GameID = %s", (14, xyz, game_id))
                check_for_ace2 = fetch_one()
                c.execute("SELECT COUNT(*) FROM currency.BlackJack WHERE CardID = %s AND Position = %s AND GameID = %s", (27, xyz, game_id))
                check_for_ace3 = fetch_one()
                c.execute("SELECT COUNT(*) FROM currency.BlackJack WHERE CardID = %s AND Position = %s AND GameID = %s", (40, xyz, game_id))
                check_for_ace4 = fetch_one()
                self.aces = 0
                if check_for_ace1 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE currency.BlackJack SET Position = %s WHERE GameID = %s AND CardID = %s", (3, game_id, 1))
                if check_for_ace2 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE currency.BlackJack SET Position = %s WHERE GameID = %s AND CardID = %s", (3, game_id, 14))
                if check_for_ace3 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE currency.BlackJack SET Position = %s WHERE GameID = %s AND CardID = %s", (3, game_id, 27))
                if check_for_ace4 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE currency.BlackJack SET Position = %s WHERE GameID = %s AND CardID = %s", (3, game_id, 40))
                self.ace_list = []
                if self.aces >= 1:
                    self.ace_list.append(userid)
                    self.ace_list.append(self.aces)
                    self.ace2_list.append(self.ace_list)
                for ace in self.ace2_list:
                    user = ace[0]
                    card_ace = ace[1]
                    if ctx.author.id == user and tot > 21 and card_ace >= 1:
                        ace[1] -= 1
                        if ace[1] == 0:
                            self.ace2_list.remove(ace)
                        tot = tot - 10
                await ctx.send("<@{}>'s current score is ||{}||".format(userid, tot), file=abc, delete_after=120)
                c.execute("UPDATE currency.Games SET Score{} = %s WHERE GameID = %s".format(xyz), (tot, game_id))
                DBconn.commit()
        except Exception as e:
            log.console(e)
            await ctx.send("> **You are not currently playing a game.**", delete_after=40)
            pass

    @commands.command(aliases = ['stay'])
    async def stand(self, ctx):
        """Keep Your Cards [Format: %stand]"""
        userid = ctx.author.id
        try:
            c.execute("SELECT GameID FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (userid, userid))
            game_id = fetch_one()
            c.execute("SELECT PLayer1,Player2 FROM currency.Games WHERE Player1 = %s OR Player2 = %s", (userid, userid))
            player = c.fetchone
            Player1 = player[0]
            Player2 = player[1]
            c.execute("SELECT Stand FROM currency.GAMES WHERE GameID = %s", (game_id,))
            stand = str(fetch_one())
            if userid == Player1:
                xyz = 1
                if stand == '11' or stand == '12':
                    if stand[1] == '1':
                        new_stand = 21
                    if stand[1] == '2':
                        new_stand = 22
                    c.execute("UPDATE currency.Games SET Stand = %s WHERE GameID = %s", (new_stand, game_id,))
                    DBconn.commit()

            if userid == Player2:
                xyz = 2
                if stand == '11' or stand == '21':
                    if stand[0] == '1':
                        new_stand = 12
                    if stand[0] == '2':
                        new_stand = 22
                    c.execute("UPDATE currency.Games SET Stand = %s WHERE GameID = %s", (new_stand, game_id,))
                    DBconn.commit()
            c.execute("SELECT Score{} FROM currency.Games WHERE GameID = %s".format(xyz), (game_id,))
            current_val = fetch_one()
            await ctx.send(
                "> **<@{}> has finalized their deck with a total of ||{}|| points.**".format(userid, current_val),
                delete_after=40)
        except:
            await ctx.send("> **You are not currently in a game.**", delete_after=40)