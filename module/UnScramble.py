import asyncio
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


class UnScramble(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex

    async def cog_check(self, ctx):
        """A local check for this cog. Checks if the user is in the support server."""
        return await self.ex.check_user_in_support_server(ctx)

    @commands.command(aliases=['usl', 'uslb'])
    async def usleaderboard(self, ctx, difficulty="medium", mode="server"):
        """
        Shows leaderboards for unscramble game

        [Format: %usleaderboard (easy/medium/hard) (server/global)]
        [Aliases: usl, uslb]
        """
        if difficulty.lower() not in ['easy', 'medium', 'hard']:
            difficulty = "medium"

        try:
            if mode.lower() not in ["server", "global"]:
                mode = "server"
            if mode == "server":
                server_id = await self.ex.get_server_id(ctx)
                if not server_id:
                    return await ctx.send("> You should not use this command in DMs.")
                members = f"({', '.join([str(member.id) for member in self.ex.client.get_guild(server_id).members])})"
                top_user_scores = await self.ex.u_unscramblegame.get_unscramble_game_top_ten(difficulty,
                                                                                             members=members)

            else:
                top_user_scores = await self.ex.u_unscramblegame.get_unscramble_game_top_ten(difficulty)

            lb_string = ""
            for user_position, (user_id, score) in enumerate(top_user_scores):
                await asyncio.sleep(0)
                score = await self.ex.u_unscramblegame.get_user_score(difficulty.lower(), user_id)
                lb_string += f"**{user_position + 1})** <@{user_id}> - {score}\n"
            m_embed = await self.ex.create_embed(title=f"Unscramble Game Leaderboard ({difficulty.lower()}) ({mode})",
                                                 title_desc=lb_string)
            await ctx.send(embed=m_embed)
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> You may not understand this error. Please report it -> {e}")

    @commands.command(aliases=["us"])
    async def unscramble(self, ctx, gender="all", difficulty="medium", rounds=20, timeout=20):
        """
        Start an idol unscrambling game in the current channel.

        The host of the game can use `stop`/`end` to end the game

        [Format: %unscramble (Male/Female/All) (easy/medium/hard) (# of rounds - default 20)
        (timeout for each round - default 20s)]
        [Aliases: us]

        Easy -> Only Stage Names (from easy idols).
        Medium -> Stage/Full/Group Names (from medium idols).
        Hard -> Former Full/Stage Names + Aliases + All capitalized letters are now lowercase (from hard idols).
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
