import discord
from discord.ext import commands, tasks
import sqlite3
from random import *


client = 0
path = 'module\currency.db'
DBconn = sqlite3.connect(path)
c = DBconn.cursor()

def setup(client1):
    client1.add_cog(BlackJack(client1))
    global client
    client = client1


class BlackJack(commands.Cog):
    def __init__(self, client):
        self.count = 0
        self.aces = 0
        self.game_list = []
        # self.game2_list = []
        self.tasks = list()
        self.task_list = []
        self.ace_list = []
        self.ace2_list = []
        pass

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, *, amount=0):
        """Start a game of BlackJack [Format: %blackjack (amount)] [Aliases: bj]"""
        try:
            game_type = 'blackjack'
            player_1 = ctx.author.id
            counter = \
            c.execute("SELECT count(*) FROM Games WHERE Player1 = ? or Player2 = ?", (player_1, player_1)).fetchone()[0]
            if counter == 1:
                await ctx.send(
                    "> **You are already in a pending/active game. Please type %endgame to end your current game.**",
                    delete_after=40)
            if counter == 0:
                player_2 = 0
                player1_bid = amount
                player2_bid = 0
                count = c.execute("SELECT count(UserID) FROM Currency WHERE USERID = ?", (player_1,)).fetchone()[0]
                if count == 0:
                    await ctx.send("> **You are not currently registered. Please type %register to register.**",
                                   delete_after=40)
                if count == 1:
                    current_amount = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                    if amount > current_amount:
                        await ctx.send("> **You do not have enough money to give!**", delete_after=40)
                    if amount <= current_amount:
                        c.execute("INSERT INTO Games VALUES (NULL, ?, ?, ?, ?, 0, 0, ?, 11)",
                                  (player_1, player_2, player1_bid, player2_bid, game_type))
                        DBconn.commit()
                        game_id = c.execute("SELECT GameID FROM Games WHERE Player1 = ?", (player_1,)).fetchone()[0]
                        await ctx.send(
                            "> **There are currently 1/2 members signed up for BlackJack. To join the game, please type %joingame {} (bid)**".format(
                                game_id), delete_after=40)
                if count > 1:
                    await ctx.send("> **There is an error with the database. Please report to an administrator**",
                                   delete_after=40)
        except:
            await ctx.send(
                "> **You are already in a pending/active game. Please type %endgame to end your current game.**",
                delete_after=40)

    # background loops
    def _start_tasks(self, ctx, game_id, player_1, player_2):
        for game in self.game_list:
            # if not game in self.game2_list:
            # self.game2_list.append(game)
            @tasks.loop(seconds=5.0)
            async def new_task():
                self.count += 1
                # print (game)
                stand = str(c.execute("SELECT Stand FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0])
                if stand == '22':
                    score_1 = c.execute("SELECT Score1 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                    score_2 = c.execute("SELECT Score2 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                    bid_1 = c.execute("SELECT Bid1 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                    bid_2 = c.execute("SELECT Bid2 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                    bid_sum = bid_1 + bid_2
                    c.execute("DELETE FROM Games WHERE GameID = ?", (game_id,))
                    c.execute("DELETE FROM BlackJack WHERE GameID = ?", (game_id,))
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
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                            total_amount = bid_2 + current_val
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                            # subtract money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                            total_amount = current_val - bid_2
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                            await ctx.send(
                                "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_1, bid_sum, score_1, player_2, score_2), delete_after=40)

                        if result_2 < result_1:
                            # player 2 wins
                            # add money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                            total_amount = bid_1 + current_val
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                            # subtract money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                            total_amount = current_val - bid_1
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                            await ctx.send(
                                "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    if score_1 < 21 and score_2 < 21:
                        if score_1 == score_2:
                            await ctx.send(
                                "> **You have both tied with a score of {}! No prizes were given.**".format(score_1),
                                delete_after=40)
                        if score_1 > score_2:
                            # player 1 wins
                            # add money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                            total_amount = bid_2 + current_val
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                            # subtract money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                            total_amount = current_val - bid_2
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                            await ctx.send(
                                "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                    player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                        if score_2 > score_1:
                            # player 2 wins
                            # add money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                            total_amount = bid_1 + current_val
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                            # subtract money
                            current_val = \
                            c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                            total_amount = current_val - bid_1
                            c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                            await ctx.send(
                                "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
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
                                current_val = \
                                c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                                total_amount = bid_2 + current_val
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                                # subtract money
                                current_val = \
                                c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                                total_amount = current_val - bid_2
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                                await ctx.send(
                                    "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                        player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                            if score_2 == 21:
                                # player2 wins
                                # add money
                                current_val = \
                                c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                                total_amount = bid_1 + current_val
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                                # subtract money
                                current_val = \
                                c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[0]
                                total_amount = current_val - bid_1
                                c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                                await ctx.send(
                                    "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                        player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    if score_1 < 21 and score_2 > 21:
                        # player1 wins
                        # add money
                        current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[
                            0]
                        total_amount = bid_2 + current_val
                        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                        # subtract money
                        current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[
                            0]
                        total_amount = current_val - bid_2
                        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                        await ctx.send(
                            "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                player_1, bid_sum, score_1, player_2, score_2), delete_after=40)
                    if score_1 > 21 and score_2 < 21:
                        # player2 wins
                        # add money
                        current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[
                            0]
                        total_amount = bid_1 + current_val
                        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_2))
                        # subtract money
                        current_val = c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_1,)).fetchone()[
                            0]
                        total_amount = current_val - bid_1
                        c.execute("UPDATE Currency SET Money = ? WHERE UserID = ?", (total_amount, player_1))
                        await ctx.send(
                            "> **<@{}> has won {} Dollars with {} points against <@{}> with {} points in BlackJack.**".format(
                                player_2, bid_sum, score_2, player_1, score_1), delete_after=40)
                    DBconn.commit()
                    self.tasks.remove(self.task_list)
                    self.count = 0
                    self.new_task.stop()
                if self.count == 60:
                    await ctx.send("> **Game {} has been deleted due to it's 5 minute limit.**".format(game_id),
                                   delete_after=40)
                    # await ctx.send("sending {}".format(self.task_list))
                    c.execute("DELETE FROM Games WHERE GameID = ?", (game_id,))
                    c.execute("DELETE FROM BlackJack WHERE GameID = ?", (game_id,))
                    self.tasks.remove(self.task_list)
                    self.count = 0
                    DBconn.commit()
                    self.new_task.stop()

            self.task_list = []
            self.task_list.append(new_task)
            self.task_list.append(player_1)
            self.task_list.append(player_2)
            self.tasks.append(self.task_list)
            new_task.start()

    # BACKGROUND LOOP FOR MANY INSTANCES
    """
    def _start_tasks(self, ctx, game_id, player_1, player_2):
        for game in self.game_list:
            if not game in self.game2_list:
                self.game2_list.append(game)
                @tasks.loop(seconds = 5)
                async def new_task():
                    self.count += 1
                    print (game)
                    if self.count == 60:
                        new_task.close()
                self.tasks.append(new_task)
                new_task.start()
    """

    @commands.command(aliases=['jg'])
    async def joingame(self, ctx, gameid=0, amount=0):
        """Join a game [Format: %joingame (gameid) (bid)] [Aliases: jg]"""
        if gameid == 0:
            await ctx.send("> **Please include the game id in your command. [Format: %jg (gameid) (bid)]**",
                           delete_after=40)
        if gameid != 0:
            try:
                rules = "**Each Player gets 2 cards.\nIn order to get blackjack, your final value must equal 21.\nIf Player1 exceeds 21 and Player2 doesn't, Player1 busts and Player2 wins the game.\nYou will have two options.\nThe first option is to %Hit, which means to grab another card.\nThe second option is to %Stay to not pick up anymore cards.\nEach Player will play one at a time so think ahead!\nIf both players bust, Player closest to 21 wins!\nNumber cards are their values.\nAces can be 1 or 11 depending on the scenario.\nJack, Queen, and King are all worth 10. **"
                player_2 = ctx.author.id
                player2_bid = amount
                game_id = gameid
                check = c.execute("SELECT Player1 FROM Games WHERE GameID = ?", (game_id)).fetchone()[0]
                check2 = c.execute("SELECT Player2 FROM Games WHERE GameID = ?", (game_id)).fetchone()[0]
                count_checker = c.execute("SELECT COUNT(*) FROM Games WHERE Player1 = ? OR Player2 = ?",
                                          (player_2, player_2)).fetchone()[0]
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
                            count = \
                            c.execute("SELECT count(UserID) FROM Currency WHERE USERID = ?", (player_2,)).fetchone()[0]
                            if count == 0:
                                await ctx.send(
                                    "> **You are not currently registered. Please type %register to register.**",
                                    delete_after=40)
                            if count == 1:
                                current_amount = \
                                c.execute("SELECT Money FROM Currency WHERE UserID = ?", (player_2,)).fetchone()[0]
                                if amount > current_amount:
                                    await ctx.send("> **You do not have enough money to give!**", delete_after=40)
                                if amount <= current_amount:
                                    c.execute("UPDATE Games SET Player2 = ?, Bid2 = ? WHERE GameID = ?",
                                              (player_2, player2_bid, game_id))
                                    DBconn.commit()
                                    total_1 = c.execute("SELECT Bid1, Bid2 FROM Games Where GameID = ?",
                                                        (game_id,)).fetchall()
                                    for a in total_1:
                                        x = a[0]
                                        y = a[1]
                                    total = x + y
                                    await ctx.send(
                                        "> **Starting BlackJack with a total bid of {} Dollars.**".format(total),
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
                                        card_name = c.execute("SELECT * FROM CardValues WHERE CardID = ?",
                                                              (new_list[i],)).fetchone()[1]
                                        card_value = c.execute("SELECT * FROM CardValues WHERE CardID = ?",
                                                               (new_list[i],)).fetchone()[2]
                                        current_val = \
                                        c.execute("SELECT Score1 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                                        c.execute("INSERT INTO BlackJack VALUES (?, ?, ?)", (game_id, new_list[i], 1))
                                        tot1 = current_val + card_value
                                        c.execute("UPDATE Games SET Score1 = ? WHERE GameID = ?", (tot1, game_id))
                                        card_1 = discord.File(fp='Cards/{}.jpg'.format(new_list[i]),
                                                              filename='{}.jpg'.format(new_list[i]), spoiler=True)
                                        file_1.append(card_1)
                                        DBconn.commit()
                                    for i in range(2, 4):
                                        card_name = c.execute("SELECT * FROM CardValues WHERE CardID = ?",
                                                              (new_list[i],)).fetchone()[1]
                                        card_value = c.execute("SELECT * FROM CardValues WHERE CardID = ?",
                                                               (new_list[i],)).fetchone()[2]
                                        current_val = \
                                        c.execute("SELECT Score2 FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0]
                                        c.execute("INSERT INTO BlackJack VALUES (?, ?, ?)", (game_id, new_list[i], 2))
                                        tot = current_val + card_value
                                        c.execute("UPDATE Games SET Score2 = ? WHERE GameID = ?", (tot, game_id))
                                        card_2 = discord.File(fp='Cards/{}.jpg'.format(new_list[i]),
                                                              filename='{}.jpg'.format(new_list[i]), spoiler=True)
                                        file_2.append(card_2)
                                        DBconn.commit()
                                    player_1 = \
                                    c.execute("SELECT Player1 FROM Games WHERE GameID = ?", (game_id)).fetchone()[0]
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
            except:
                await ctx.send("> **Failed to join. This game does not exist.**", delete_after=40)

    @commands.command(aliases=['eg'])
    async def endgame(self, ctx):
        """End your current game [Format: %endgame] [Aliases: eg]"""
        try:
            game_id = c.execute("SELECT GameID FROM Games WHERE Player1 = ? OR Player2 = ?",
                                (ctx.author.id, ctx.author.id)).fetchone()[0]
            c.execute("DELETE FROM Games WHERE Player1 = ? OR Player2 = ?", (ctx.author.id, ctx.author.id))
            c.execute("DELETE FROM BlackJack WHERE GameID = ?", (game_id,))
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
        c.execute("DELETE FROM CardValues")
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
            c.execute("INSERT INTO CardValues VALUES (NULL, ?, ?)", (card, cardvalues[countx]))
        DBconn.commit()
        await ctx.send("> **All cards have been added into the table.**", delete_after=40)

    @commands.command()
    async def hit(self, ctx):
        """Pick A Card [Format: %hit]"""
        userid = ctx.author.id
        try:
            random_card = randint(1, 52)
            game_id = \
            c.execute("SELECT GameID FROM Games WHERE Player1 = ? OR Player2 = ?", (userid, userid)).fetchone()[0]
            player = c.execute("SELECT Player1,Player2 FROM Games WHERE Player1 = ? OR Player2 = ?",
                               (userid, userid)).fetchone()
            cards = c.execute("SELECT CardID FROM BlackJack WHERE GameID =?", (game_id,)).fetchall()
            while random_card in cards:
                random_card = randint(1, 52)
            Player1 = player[0]
            Player2 = player[1]
            current_stand = str(c.execute("SELECT Stand FROM Games WHERE GameID = ?", (game_id,)).fetchone()[0])
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
                c.execute("INSERT INTO BlackJack VALUES (?, ?, ?)", (game_id, random_card, xyz))
                abc = discord.File(fp='Cards/{}.jpg'.format(random_card), filename='{}.jpg'.format(random_card),
                                   spoiler=True)
                card_value = c.execute("SELECT * FROM CardValues WHERE CardID = ?", (random_card,)).fetchone()[2]
                current_val = \
                c.execute("SELECT Score{} FROM Games WHERE GameID = ?".format(xyz), (game_id,)).fetchone()[0]
                tot = current_val + card_value
                check_for_ace1 = \
                c.execute("SELECT COUNT(*) FROM BlackJack WHERE CardID = ? AND Position = ? AND GameID = ?",
                          (1, xyz, game_id)).fetchone()[0]
                check_for_ace2 = \
                c.execute("SELECT COUNT(*) FROM BlackJack WHERE CardID = ? AND Position = ? AND GameID = ?",
                          (14, xyz, game_id)).fetchone()[0]
                check_for_ace3 = \
                c.execute("SELECT COUNT(*) FROM BlackJack WHERE CardID = ? AND Position = ? AND GameID = ?",
                          (27, xyz, game_id)).fetchone()[0]
                check_for_ace4 = \
                c.execute("SELECT COUNT(*) FROM BlackJack WHERE CardID = ? AND Position = ? AND GameID = ?",
                          (40, xyz, game_id)).fetchone()[0]
                self.aces = 0
                if check_for_ace1 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE BlackJack SET Position = ? WHERE GameID = ? AND CardID = ?", (3, game_id, 1))
                if check_for_ace2 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE BlackJack SET Position = ? WHERE GameID = ? AND CardID = ?", (3, game_id, 14))
                if check_for_ace3 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE BlackJack SET Position = ? WHERE GameID = ? AND CardID = ?", (3, game_id, 27))
                if check_for_ace4 == 1:
                    self.aces += 1
                    current = 1
                    c.execute("UPDATE BlackJack SET Position = ? WHERE GameID = ? AND CardID = ?", (3, game_id, 40))
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
                c.execute("UPDATE Games SET Score{} = ? WHERE GameID = ?".format(xyz), (tot, game_id))
                DBconn.commit()
        except:
            await ctx.send("> **You are not currently playing a game.**", delete_after=40)

    @commands.command()
    async def stand(self, ctx):
        """Keep Your Cards [Format: %stand]"""
        userid = ctx.author.id
        try:
            game_id = \
            c.execute("SELECT GameID FROM Games WHERE Player1 = ? OR Player2 = ?", (userid, userid)).fetchone()[0]
            player = c.execute("SELECT PLayer1,Player2 FROM Games WHERE Player1 = ? OR Player2 = ?",
                               (userid, userid)).fetchone()
            Player1 = player[0]
            Player2 = player[1]
            stand = str(c.execute("SELECT Stand FROM GAMES WHERE GameID = ?", (game_id,)).fetchone()[0])
            if userid == Player1:
                xyz = 1
                if stand == '11' or stand == '12':
                    if stand[1] == '1':
                        new_stand = 21
                    if stand[1] == '2':
                        new_stand = 22
                    c.execute("UPDATE Games SET Stand = ? WHERE GameID = ?", (new_stand, game_id,))
                    DBconn.commit()

            if userid == Player2:
                xyz = 2
                if stand == '11' or stand == '21':
                    if stand[0] == '1':
                        new_stand = 12
                    if stand[0] == '2':
                        new_stand = 22
                    c.execute("UPDATE Games SET Stand = ? WHERE GameID = ?", (new_stand, game_id,))
                    DBconn.commit()
            current_val = c.execute("SELECT Score{} FROM Games WHERE GameID = ?".format(xyz), (game_id,)).fetchone()[0]
            await ctx.send(
                "> **<@{}> has finalized their deck with a total of ||{}|| points.**".format(userid, current_val),
                delete_after=40)
        except:
            await ctx.send("> **You are not currently in a game.**", delete_after=40)