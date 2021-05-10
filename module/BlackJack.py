import IreneUtility.models
import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


# noinspection PyPep8
class BlackJack(commands.Cog):
    def __init__(self, ex):
        """

        :param ex: Utility Object
        """
        self.ex: Utility = ex

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, amount="0", versus="player"):
        """
        Start a game of BlackJack

        [Format: %blackjack (amount)]
        [Aliases: bj]
        """

    @commands.command(aliases=['jg'])
    async def joingame(self, ctx, user_or_game_id=0, bet="0"):
        """
        Join a game

        [Format: %joingame (@user or game_id) (bet)]
        [Aliases: jg]
        """

    @commands.command(aliases=['eg'])
    async def endgame(self, ctx):
        """
        End your current game

        [Format: %endgame]
        [Aliases: eg]
        """

    @commands.command()
    async def rules(self, ctx):
        """View the rules of BlackJack."""
        server_prefix = await self.ex.get_server_prefix(ctx)
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
        embed = await self.ex.set_embed_author_and_footer(
            embed, f"{server_prefix}help BlackJack for the available commands.")
        await ctx.send(embed=embed)


class Game(IreneUtility.models.Game):
    def __init__(self, *args):
        super().__init__(*args)

