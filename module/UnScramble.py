from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


def check_user_in_support_server():
    """Decorator for checking if a user is in the support server"""
    def predicate(ctx):
        return ctx.cog.ex.check_user_in_support_server(ctx)
    return commands.check(predicate)


class UnScramble(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex

    @check_user_in_support_server()
    @commands.command(aliases=["us"])
    async def unscramble(self, ctx, gender="all", difficulty="medium", rounds=20, timeout=20):
        """
        Start an idol unscrambling game in the current channel.

        The host of the game can use `stop`/`end` to end the game

        [Format: %unscramble (Male/Female/All) (easy/medium/hard) (# of rounds - default 20)
        (timeout for each round - default 20s)]
        [Aliases: us]

        Easy -> Only Stage Names
        Medium -> Stage Names and Full Names
        Hard -> Former Full/Stage Names + All capitalized letters are now lowercase.
        """
        if not ctx.guild:
            return await ctx.send("> You are not allowed to play the unscramble game in DMs.")
        server_prefix = await self.ex.get_server_prefix(ctx)

        if ctx.channel.id in self.ex.cache.channels_with_disabled_games:
            msg = await self.ex.get_msg(ctx.author.id, "general", "game_disabled", [
                ["name", ctx.author.display_name], ["server_prefix", server_prefix]
            ])
            return await ctx.send(msg)

        if self.ex.cache.unscramble_games.get(ctx.channel.id):
            return await ctx.send(f"> **An Unscramble game is currently in progress in this channel. "
                                  f"If this is a mistake, use `{server_prefix}stopus`.**")
        if rounds > 60 or timeout > 60:
            return await ctx.send("> **ERROR -> The max rounds is 60 and the max timeout is 60s.**")
        elif rounds < 1 or timeout < 3:
            return await ctx.send("> **ERROR -> The minimum rounds is 1 and the minimum timeout is 3 seconds.**")
        await self.start_game(ctx, rounds, timeout, gender, difficulty)

    @commands.command()
    async def stopus(self, ctx):
        """
        Force-end an unscramble game if you are a moderator or host of the game.

        This command is meant for any issues or if a game happens to be stuck.
        [Format: %stopus]
        """
        if not await self.ex.stop_game(ctx, self.ex.cache.unscramble_games):
            msg = await self.ex.get_msg(ctx, "miscellaneous", "no_game", ["string", "unscramble"])
            return await ctx.send(msg)
        log.console(f"Force-Ended Unscramble Game in {ctx.channel.id}")

    async def start_game(self, ctx, rounds, timeout, gender, difficulty):
        """Officially starts the unscramble game."""
        game = self.ex.u_objects.UnScrambleGame(self.ex, ctx, max_rounds=rounds, timeout=timeout, gender=gender,
                                                difficulty=difficulty)
        self.ex.cache.unscramble_games[ctx.channel.id] = game
        await ctx.send(f"> Starting an Unscramble game for "
                       f"`{game.gender if game.gender != 'all' else 'both male and female'}` idols"
                       f" with `{game.difficulty}` difficulty, `{rounds}` rounds, and `{timeout}s` of answering time.")
        await game.process_game()
        await self.ex.stop_game(ctx, self.ex.cache.unscramble_games)
        log.console(f"Ended Unscramble Game in {ctx.channel.id}")
