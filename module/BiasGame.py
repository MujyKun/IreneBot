import asyncio

import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


def check_user_in_support_server():
    """Decorator for checking if a user is in the support server"""
    def predicate(ctx):
        return ctx.cog.ex.check_user_in_support_server(ctx)
    return commands.check(predicate)


# noinspection PyPep8
class BiasGame(commands.Cog):
    def __init__(self, t_ex):
        self.ex: Utility = t_ex

    @check_user_in_support_server()
    @commands.command(aliases=['bg'])
    async def biasgame(self, ctx, gender="all", bracket_size=8):
        """
        Start a bias game in the current channel. The host of the game can use `stopbg` to stop playing.

        [Format: %biasgame (Male/Female/All) (bracket size (4,8,16,32))]
        """
        user = await self.ex.get_user(ctx.author.id)
        server_prefix = await self.ex.get_server_prefix(ctx)

        if not ctx.guild:
            return await ctx.send(await self.ex.get_msg(user, 'biasgame', 'no_dm'))

        if ctx.channel.id in self.ex.cache.channels_with_disabled_games:
            msg = await self.ex.get_msg(user, "general", "game_disabled", [
                ["name", ctx.author.display_name], ["server_prefix", server_prefix]
            ])
            return await ctx.send(msg)

        if self.ex.cache.bias_games.get(ctx.channel.id):
            return await ctx.send(
                await self.ex.get_msg(user, 'biasgame', 'in_progress', [['server_prefix', server_prefix]]))
        game = self.ex.u_objects.BiasGame(self.ex, ctx, bracket_size=bracket_size, gender=gender)
        self.ex.cache.bias_games[ctx.channel.id] = game

        msg = await self.ex.get_msg(user, 'biasgame', 'start_game',
                                    [["bracket_size", str(game.bracket_size)],
                                     ["gender", f"{game.gender if game.gender != 'all' else 'both male and female'}"]])

        await ctx.send(msg)
        await game.process_game()  # start the game
        await self.ex.stop_game(ctx, self.ex.cache.bias_games)  # remove the game.
        log.console(f"Ended Bias Game in {ctx.channel.id}")

    @commands.command()
    async def stopbg(self, ctx):
        """
        Force-end a bias game if you are a moderator or host of the game.

        [Format: %stopbg]
        This command is meant for any issues or if a game happens to be stuck.
        """
        if not await self.ex.stop_game(ctx, self.ex.cache.bias_games):
            msg = await self.ex.get_msg(ctx, "miscellaneous", "no_game", ["string", "bias"])
            return await ctx.send(msg)
        log.console(f"Force-Ended Bias Game in {ctx.channel.id}")

    @commands.command()
    async def listbg(self, ctx, user: discord.Member = None):
        """
        List a user's bias game leaderboards.

        [Format: %listbg]
        """
        if not user:
            user = ctx.author
        user_wins = await self.ex.conn.fetch(
            "SELECT idolid, wins FROM biasgame.winners WHERE userid = $1 ORDER BY WINS DESC LIMIT $2", user.id, 15)
        if user_wins:
            msg_string = await self.ex.get_msg(user.id, 'biasgame', 'lb_title', ['name', user.display_name])

            counter = 1
            for idol_id, wins in user_wins:
                await asyncio.sleep(0)
                member = await self.ex.u_group_members.get_member(idol_id)
                msg_string += f"{counter}) {member.full_name} ({member.stage_name}) -> {wins} Win(s).\n"
                counter += 1
        else:
            msg_string = await self.ex.get_msg(user.id, 'biasgame', 'no_wins', ['name', user.display_name])
        await ctx.send(msg_string)
