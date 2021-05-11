import discord
from discord.ext import commands
from IreneUtility.Utility import Utility


# noinspection PyPep8
class BlackJack(commands.Cog):
    def __init__(self, ex):
        """

        :param ex: Utility Object
        """
        self.ex: Utility = ex

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, bet="0"):
        """
        Start a game of BlackJack

        [Format: %blackjack (amount)]
        [Aliases: bj]
        """
        server_prefix = await self.ex.get_server_prefix(ctx)
        user = await self.ex.get_user(ctx.author.id)
        bet = self.ex.remove_commas(bet)
        if bet < 0:
            bet = 0
        if user.in_currency_game:
            # user already in a game
            return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "in_game",
                                                        [["name", ctx.author.display_name],
                                                         ["server_prefix", server_prefix]]))
        blackjack_game = self.ex.u_objects.BlackJackGame(self.ex, ctx, first_player=user, first_player_bet=bet)
        self.ex.cache.blackjack_games.append(blackjack_game)
        return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "game_created", [
            ["name", ctx.author.display_name],
            ["server_prefix", await self.ex.get_server_prefix(ctx)]]))

    @commands.command(aliases=['jg'])
    async def joingame(self, ctx, opponent: discord.Member, bet="0"):
        """
        Join a game

        [Format: %joingame (@user) (bet)]
        [Aliases: jg]
        """
        server_prefix = await self.ex.get_server_prefix(ctx)
        user = await self.ex.get_user(ctx.author.id)
        opponent_user = await self.ex.get_user(opponent.id)
        bet = self.ex.remove_commas(bet)
        if bet < 0:
            bet = 0

        if not opponent_user.in_currency_game:
            # opponent is not in a game
            return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "opponent_not_in_game",
                                                        ["name", ctx.author.display_name]))
        elif user.in_currency_game:
            # user in a game
            return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "in_game",
                                                        [["name", ctx.author.display_name],
                                                         ["server_prefix", server_prefix]]))
        blackjack_game = await self.ex.u_blackjack.find_game(opponent_user)
        blackjack_game.second_player = user
        blackjack_game.second_player_bet = bet
        blackjack_game.second_player_ctx = ctx
        await blackjack_game.process_game()  # start the blackjack game.

    @commands.command(aliases=['eg'])
    async def endgame(self, ctx):
        """
        End your current game

        [Format: %endgame]
        [Aliases: eg]
        """
        user = await self.ex.get_user(ctx.author.id)
        if not user.in_currency_game:
            # user is not in a game.
            return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "not_in_game",
                                                        ["name", ctx.author.display_name]))

        # find the game and end it.
        blackjack_game = await self.ex.u_blackjack.find_game(user)
        if blackjack_game:
            await ctx.send(await self.ex.get_msg(ctx, 'biasgame', 'force_closed'))
            return await blackjack_game.end_game()

        # send the fallback message of no game being found (the game ended in the middle of the command).
        return await ctx.send(await self.ex.get_msg(ctx, "blackjack", "ended_game",
                                                    ["name", ctx.author.display_name]))

    @commands.command()
    async def rules(self, ctx):
        """View the rules of BlackJack."""
        server_prefix = await self.ex.get_server_prefix(ctx)
        msg = f"""**Each Player gets 2 cards at the start.\n
        In order to get blackjack, your final value must equal 21.\n
        If Player1 exceeds 21 and Player2 does not, Player1 busts and Player2 wins the game.\n
        You will have two options.\n
        The first option is to `hit`, which means to grab another card.\n
        The second option is to `stand` to finalize your deck.\n
        If both players bust, Player closest to 21 wins!\n
        Number cards are their face values.\n
        Aces can be 1 or 11 depending on the situation you're in.\n
        Jack, Queen, and King are all worth 10.\n
        If you go over 35 points, the bot will automatically stand you.\n
        MOST IMPORTANTLY!!! DO NOT peek at your opponent's cards or points!\n
        """
        embed = discord.Embed(title="BlackJack Rules", description=msg)
        embed = await self.ex.set_embed_author_and_footer(
            embed, f"{server_prefix}help BlackJack for the available commands.")
        await ctx.send(embed=embed)
