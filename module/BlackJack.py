import discord
from discord.ext import commands, tasks
from random import *
from module import logger as log
from module.keys import client, bot_id
from Utility import DBconn, c, fetch_one, fetch_all, remove_commas, set_embed_author_and_footer, get_game_by_player, add_bj_game, process_bj_game, get_game, add_player_two, add_card, start_game, compare_channels, delete_game, set_player_stand, get_player_total, check_game_over, finish_game, get_server_prefix_by_context, check_if_bot, get_int_index


class BlackJack(commands.Cog):
    def __init__(self):
        pass

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, amount="0", versus="player"):
        """Start a game of BlackJack [Format: %blackjack (amount)] [Aliases: bj]"""
        try:
            amount = remove_commas(amount)
            user_id = ctx.author.id
            if versus != "bot":
                if await process_bj_game(ctx, amount, user_id):
                    await add_bj_game(user_id, amount, ctx, "player")
            else:
                if await process_bj_game(ctx, amount, user_id):
                    await add_bj_game(user_id, amount, ctx, "bot")
                    game_id = get_game_by_player(user_id)
                    fake_bot_id = int(f"{get_int_index(bot_id, 9)}{randint(1,999999999)}")
                    add_player_two(game_id, fake_bot_id, amount)
                    await start_game(game_id)
        except Exception as e:
            log.console(e)
            pass

    @commands.command(aliases=['jg'])
    async def joingame(self, ctx, game_id=0, amount="0"):
        """Join a game [Format: %joingame (gameid) (bid)] [Aliases: jg]"""
        try:
            amount = remove_commas(amount)
            user_id = ctx.author.id
            if await process_bj_game(ctx, amount, user_id):
                game = get_game(game_id)
                if game is None:
                    await ctx.send(f"> **{ctx.author}, {game_id} is not a valid game.**")
                else:
                    if game[5] == ctx.channel.id:  # Did not use already existing function due to incompatibility.
                        add_player_two(game_id, user_id, amount)
                        await start_game(game_id)
                    else:
                        await ctx.send(f"> **{ctx.author}, that game ({game_id}) is not available in this text channel.**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=['eg'])
    async def endgame(self, ctx):
        """End your current game [Format: %endgame] [Aliases: eg]"""
        try:
            game_id = get_game_by_player(ctx.author.id)
            if game_id is None:
                await ctx.send(f"> **{ctx.author}, you are not in a game.**")
            else:
                delete_game(game_id)
                await ctx.send(f"> **{ctx.author}, your game has been deleted.**")
        except Exception as e:
            log.console(e)

    @commands.command()
    @commands.is_owner()
    async def addcards(self, ctx):
        """Fill The CardValues Table with Cards [Format: %addcards]"""
        c.execute("DELETE FROM blackjack.cards")
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
            c.execute("INSERT INTO blackjack.cards (name, value) VALUES (%s, %s)", (card, cardvalues[countx]))
        DBconn.commit()
        await ctx.send("> **All cards have been added into the table.**", delete_after=40)

    @commands.command()
    async def hit(self, ctx):
        """Pick A Card [Format: %hit]"""
        try:
            game_id = get_game_by_player(ctx.author.id)
            if game_id is None:
                await ctx.send(f"> **{ctx.author}, you are not in a game.**")
            else:
                if await compare_channels(ctx.author.id, ctx.channel):
                    game = get_game(game_id)
                    if check_if_bot(game[2]):
                        if get_player_total(game[2]) < 16:
                            await add_card(game[2])
                    await add_card(ctx.author.id)
        except Exception as e:
            log.console(e)

    @commands.command(aliases=['stay'])
    async def stand(self, ctx):
        """Keep Your Cards/Stand [Format: %stand]"""
        try:
            check = False
            user_id = ctx.author.id
            game_id = get_game_by_player(user_id)
            if game_id is None:
                await ctx.send(f"> **{ctx.author}, you are not in a game.**")
            else:
                if await compare_channels(user_id, ctx.channel):
                    # Do not inform other users that the player already stood by busting.
                    # Instead, just send the same message that they are standing every time this command is called.
                    set_player_stand(user_id)
                    game = get_game(game_id)
                    if check_if_bot(game[2]):
                        check = True
                        await finish_game(game_id, ctx.channel)
                    if not check:
                        total_score = str(get_player_total(user_id))
                        if len(total_score) == 1:
                            total_score = '0' + total_score  # this is to prevent being able to detect the number of digits by the spoiler
                        if not check_if_bot(game[2]):
                            await ctx.send(f"> **{ctx.author} finalized their deck with ||{total_score}|| points.**")
                        if check_game_over(game_id):
                            await finish_game(game_id, ctx.channel)
        except Exception as e:
            log.console(e)

    @commands.command()
    async def rules(self, ctx):
        """View the rules of BlackJack."""
        server_prefix = await get_server_prefix_by_context(ctx)
        msg = f"""**Each Player gets 2 cards at the start.\n
        In order to get blackjack, your final value must equal 21.\n
        If Player1 exceeds 21 and Player2 does not, Player1 busts and Player2 wins the game.\n
        You will have two options.\n
        The first option is to `{server_prefix}hit`, which means to grab another card.\n
        The second option is to `{server_prefix}stand` to finalize your deck.\n
        If both players bust, Player closest to 21 wins!\n
        Number cards are their face values.\n
        Aces can be 1 or 11 depending on the situation you're in.\n
        Jack, Queen, and King are all worth 10.\n
        Do not use `{server_prefix}hit` if you are over 21 points. This will give away that you busted!\n
        MOST IMPORTANTLY!!! DO NOT peek at your opponent's cards or points!\n
        You can play against a bot by typing `{server_prefix}blackjack (amount) bot`\n
        Betting with the bot will either double your bet or lose all of it.**
        """
        embed = discord.Embed(title="BlackJack Rules", description=msg)
        embed = await set_embed_author_and_footer(embed, f"{server_prefix}help BlackJack for the available commands.")
        await ctx.send(embed=embed)
