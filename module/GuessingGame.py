import asyncio

from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility


def check_user_in_support_server():
    """Decorator for checking if a user is in the support server"""
    def predicate(ctx):
        return ctx.cog.ex.check_user_in_support_server(ctx)
    return commands.check(predicate)


# noinspection PyPep8,PyBroadException
class GuessingGame(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex

    @commands.command(aliases=['ggl', 'gglb'])
    async def ggleaderboard(self, ctx, difficulty="medium", mode="server"):
        """
        Shows global leaderboards for guessing game

        [Format: %ggleaderboard (easy/medium/hard) (server/global)]
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
                top_user_scores = await self.ex.u_guessinggame.get_guessing_game_top_ten(difficulty, members=members)

            else:
                top_user_scores = await self.ex.u_guessinggame.get_guessing_game_top_ten(difficulty)

            lb_string = ""
            for user_position, (user_id, score) in enumerate(top_user_scores):
                await asyncio.sleep(0)
                score = await self.ex.u_guessinggame.get_user_score(difficulty.lower(), user_id)
                lb_string += f"**{user_position + 1})** <@{user_id}> - {score}\n"
            m_embed = await self.ex.create_embed(title=f"Guessing Game Leaderboard ({difficulty.lower()}) ({mode})",
                                                 title_desc=lb_string)
            await ctx.send(embed=m_embed)
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> You may not understand this error. Please report it -> {e}")

    @check_user_in_support_server()
    @commands.command(aliases=['gg'])
    async def guessinggame(self, ctx, gender="all", difficulty="medium", rounds=20, timeout=20):
        """
        Start an idol guessing game in the current channel.

        The host of the game can use `stop`/`end` to end the game or
        `skip` to skip the current round without affecting the round number.

        [Format: %guessinggame (Male/Female/All) (easy/medium/hard) (# of rounds - default 20)
        (timeout for each round - default 20s)]
        """
        if not ctx.guild:
            return await ctx.send("> You are not allowed to play guessing game in DMs.")
        if self.ex.cache.guessing_games.get(ctx.channel.id):
            server_prefix = await self.ex.get_server_prefix(ctx)
            return await ctx.send(f"> **A guessing game is currently in progress in this channel. "
                                  f"If this is a mistake, use `{server_prefix}stopgg`.**")
        if rounds > 60 or timeout > 60:
            return await ctx.send("> **ERROR -> The max rounds is 60 and the max timeout is 60s.**")
        elif rounds < 1 or timeout < 3:
            return await ctx.send("> **ERROR -> The minimum rounds is 1 and the minimum timeout is 3 seconds.**")
        await self.start_game(ctx, rounds, timeout, gender, difficulty)
        # Bot has been crashing without issue being known. Reverting creating a separate task for every game.
        # task = asyncio.create_task(self.start_game(ctx, rounds, timeout, gender, difficulty))

    @commands.command()
    async def ggfilter(self, ctx, *, groups=None):
        """
        Add a filter for your guessing game. Only the groups you select will appear on the guessing game.

        Use the command with no group ids to enable/disable the filter. Split group ids with commas.
        Group Names are now allowed to be used, but if the group name is more than one word, an underscore must be used.
        [Format: %ggfilter [group_id_one, group_id_two, group_name_one ...]]
        [Example: %ggfilter 5, 4, blackpink, 2, red_velvet]
        """
        user = await self.ex.get_user(ctx.author.id)
        if not groups:
            # toggle guessing game filter.
            await self.ex.u_guessinggame.toggle_filter(user.id)
            return await ctx.send(f"> Your Guessing Game Filter is now {'enabled' if user.gg_filter else 'disabled'}")

        groups = groups.replace(' ', '')
        groups = groups.replace('_', ' ')
        groups = groups.split(',')

        # remove duplicate inputs
        groups = list(dict.fromkeys(groups))

        invalid_group_ids = []
        added_group_ids = []
        removed_group_ids = []

        for group_id_or_name in groups:
            await asyncio.sleep(0)

            # check for empty input in the list
            if not group_id_or_name:
                continue

            group_from_group_name = await self.ex.u_group_members.get_group_where_group_matches_name(group_id_or_name)
            if group_from_group_name:
                # only add the first group recognized, otherwise user will need to be more specific.
                group_id_or_name = str((group_from_group_name[0]).id)

            try:
                added_group = await self.ex.u_guessinggame.filter_auto_add_remove_group(
                    user_or_id=user, group_or_id=group_id_or_name)
                if added_group:
                    added_group_ids.append(group_id_or_name)
                else:
                    removed_group_ids.append(group_id_or_name)
            except self.ex.exceptions.InvalidParamsPassed:
                invalid_group_ids.append(group_id_or_name)

        final_message = f"<@{user.id}>"
        if invalid_group_ids:
            final_message += f"\nThe following groups entered do not exist: **{', '.join(invalid_group_ids)}**"
        if added_group_ids:
            final_message += f"\nThe following groups entered were added: **{', '.join(added_group_ids)}**"
        if removed_group_ids:
            final_message += f"\nThe following groups entered were removed: **{', '.join(removed_group_ids)}**"
        embed = await self.ex.create_embed(title="GuessingGame Filter", title_desc=final_message)
        # we should put the msg in an embed to avoid custom inputing mentioning @everyone.

        await ctx.send(embed=embed)

    @commands.command(aliases=["ggfilterlist", "filterlist"])
    async def ggfilteredlist(self, ctx):
        """
        View the current groups you currently have filtered.

        [Format: %ggfilteredlist]
        """
        user = await self.ex.get_user(ctx.author.id)
        toggled_message = f"<@{user.id}>, your filter is currently {'enabled' if user.gg_filter else 'disabled'}.\n"
        title = f"{ctx.author.display_name}'s  Filtered Guessing Game List"
        page_number = 1
        embed_list = []
        embed = await self.ex.create_embed(title=f"{title} (Page {page_number})", title_desc=toggled_message)
        for count, group in enumerate(user.gg_groups, 1):
            await asyncio.sleep(0)
            name = f"{group.name} [{group.id}]"
            if count % 15 == 0:  # max embed length is 25 fields, limit to 15 to avoid visual spam.
                embed_list.append(embed)
                page_number += 1
                embed = await self.ex.create_embed(title=f"{title} (Page {page_number})", title_desc=toggled_message)

            if group.members:
                try:
                    value = await self.ex.u_group_members.get_member_names_as_string(group)
                except Exception as e:
                    log.useless(f"{e} -> {group.id} has an idol that does not exist.")
                    value = f"The group ({group.id}) has an Idol that doesn't exist. Please report it.\n"
                embed.add_field(name=name, value=value, inline=True)
            else:
                embed.add_field(name=name, value="None", inline=True)

        if embed not in embed_list:
            embed_list.append(embed)

        msg = await ctx.send(embed=embed_list[0])
        if len(embed_list) > 1:
            await self.ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command()
    async def stopgg(self, ctx):
        """
        Force-end a guessing game if you are a moderator or host of the game.

        This command is meant for any issues or if a game happens to be stuck.
        [Format: %stopgg]
        """
        if not await self.ex.stop_game(ctx, self.ex.cache.guessing_games):
            return await ctx.send("> No guessing game is currently in session.")
        log.console(f"Force-Ended Guessing Game in {ctx.channel.id}")

    async def start_game(self, ctx, rounds, timeout, gender, difficulty):
        """Officially starts the guessing game."""
        game = self.ex.u_objects.GuessingGame(self.ex, ctx, max_rounds=rounds, timeout=timeout, gender=gender,
                                              difficulty=difficulty)
        self.ex.cache.guessing_games[ctx.channel.id] = game
        await ctx.send(f"> Starting a guessing game for "
                       f"`{game.gender if game.gender != 'all' else 'both male and female'}` idols"
                       f" with `{game.difficulty}` difficulty, `{rounds}` rounds, and `{timeout}s` of guessing time.")
        await game.process_game()
        await self.ex.stop_game(ctx, self.ex.cache.guessing_games)
        log.console(f"Ended Guessing Game in {ctx.channel.id}")
