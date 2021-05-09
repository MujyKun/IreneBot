from discord.ext import commands
from IreneUtility.util import u_logger as log
import asyncio
import random
import async_timeout
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
            return await ctx.send(f"> **A guessing game is currently in progress in this channel. If this is a mistake, use `{server_prefix}stopgg`.**")
        if rounds > 60 or timeout > 60:
            return await ctx.send("> **ERROR -> The max rounds is 60 and the max timeout is 60s.**")
        elif rounds < 1 or timeout < 3:
            return await ctx.send("> **ERROR -> The minimum rounds is 1 and the minimum timeout is 3 seconds.**")
        await self.start_game(ctx, rounds, timeout, gender, difficulty)
        # Bot has been crashing without issue being known. Reverting creating a separate task for every game.
        # task = asyncio.create_task(self.start_game(ctx, rounds, timeout, gender, difficulty))

    @commands.command()
    async def ggfilter(self, ctx, *, group_ids=None):
        """
        Add a filter for your guessing game. Only the groups you select will appear on the guessing game.

        Use the command with no group ids to enable/disable the filter. Split group ids with commas.
        [Format: %ggfilter [group_id_one, group_id_two, ...]]
        """
        user = await self.ex.get_user(ctx.author.id)
        if not group_ids:
            # toggle guessing game filter.
            await self.ex.u_guessinggame.toggle_filter(user.id)
            return await ctx.send(f"> Your Guessing Game Filter is now {'enabled' if user.gg_filter else 'disabled'}")

        group_ids = group_ids.replace(' ', '')
        group_ids = group_ids.split(',')

        # remove duplicate inputs
        group_ids = list(dict.fromkeys(group_ids))

        invalid_group_ids = []
        added_group_ids = []
        removed_group_ids = []

        for group_id in group_ids:
            # check for empty input
            if not group_id:
                continue

            try:
                added_group = await self.ex.u_guessinggame.filter_auto_add_remove_group(user_or_id=user, group_or_id=group_id)
                if added_group:
                    added_group_ids.append(group_id)
                else:
                    removed_group_ids.append(group_id)
            except self.ex.exceptions.InvalidParamsPassed:
                invalid_group_ids.append(group_id)

        final_message = f"<@{user.id}>"
        if invalid_group_ids:
            final_message += f"\nThe following groups entered do not exist: **{', '.join(invalid_group_ids)}**"
        if added_group_ids:
            final_message += f"\nThe following groups entered were added: **{', '.join(added_group_ids)}**"
        if removed_group_ids:
            final_message += f"\nThe following groups entered were removed: **{', '.join(removed_group_ids)}**"

        await ctx.send(final_message)

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
        Force-end a guessing game if you are a moderator or host of the game. This command is meant for any issues or if a game happens to be stuck.

        [Format: %stopgg]
        """
        if not await self.ex.stop_game(ctx, self.ex.cache.guessing_games):
            return await ctx.send("> No guessing game is currently in session.")
        log.console(f"Force-Ended Guessing Game in {ctx.channel.id}")

    async def start_game(self, ctx, rounds, timeout, gender, difficulty):
        """Officially starts the guessing game."""
        game = Game(self.ex, ctx, max_rounds=rounds, timeout=timeout, gender=gender, difficulty=difficulty)
        self.ex.cache.guessing_games[ctx.channel.id] = game
        await ctx.send(f"> Starting a guessing game for `{game.gender if game.gender != 'all' else 'both male and female'}` idols"
                       f" with `{game.difficulty}` difficulty, `{rounds}` rounds, and `{timeout}s` of guessing time.")
        await game.process_game()
        await self.ex.stop_game(ctx, self.ex.cache.guessing_games)
        log.console(f"Ended Guessing Game in {ctx.channel.id}")


# noinspection PyBroadException,PyPep8
class Game:
    def __init__(self, utility_obj, ctx, max_rounds=20, timeout=20, gender="all", difficulty="medium"):
        """

        :param utility_obj: Utility object.
        :param ctx: Context
        :param max_rounds: The amount of rounds to stop at.
        :param timeout: Amount of time to guess a phoot.
        :param gender: Male/Female/All Gender of the idols in the photos.
        :param difficulty: Easy/Medium/Hard difficulty of the game.
        """
        self.ex = utility_obj
        self.photo_link = None
        self.host_ctx = ctx
        self.host = ctx.author.id
        self.host_user = None  # Utility user object
        # user_id : score
        self.players = {}
        self.rounds = 0
        self.channel = ctx.channel
        self.idol = None
        self.group_names = None
        self.correct_answers = []
        self.timeout = timeout
        self.max_rounds = max_rounds
        self.force_ended = False
        self.idol_post_msg = None
        self.gender = None
        self.post_attempt_timeout = 10
        if gender.lower() in self.ex.cache.male_aliases:
            self.gender = 'male'
        elif gender.lower() in self.ex.cache.female_aliases:
            self.gender = 'female'
        else:
            self.gender = "all"
        if difficulty in self.ex.cache.difficulty_selection.keys():
            self.difficulty = difficulty
        else:
            self.difficulty = "medium"

        self.idol_set: list = None
        self.results_posted = False
        self.api_issues = 0

    async def credit_user(self, user_id):
        """Increment a user's score"""
        score = self.players.get(user_id)
        if not score:
            self.players[user_id] = 1
        else:
            self.players[user_id] = score + 1
        self.rounds += 1

    async def check_message(self):
        """Check incoming messages in the text channel and determine if it is correct."""
        if self.force_ended:
            return

        stop_phrases = ['stop', 'end', 'quit']

        def check_correct_answer(message):
            """Check if the user has the correct answer."""
            if message.channel != self.channel:
                return False
            if message.content.lower() in self.correct_answers:
                return True
            if message.author.id == self.host:
                return message.content.lower() == 'skip' or message.content.lower() in stop_phrases

        try:
            msg = await self.ex.client.wait_for('message', check=check_correct_answer, timeout=self.timeout)
            await msg.add_reaction(self.ex.keys.check_emoji)
            if msg.content.lower() == 'skip':
                await self.print_answer(question_skipped=True)
                return
            elif msg.content.lower() in self.correct_answers:
                await self.credit_user(msg.author.id)
            elif msg.content.lower() in stop_phrases or self.force_ended:
                self.force_ended = True
                return
            else:
                # the only time this code is reached is when a prefix was changed in the middle of a round.
                # for example, if the user had to guess "irene", but their server prefix was 'i', then
                # the bot will change the msg content to "%rene" and the above conditions will not properly work.
                # if we had reached this point, we'll give them +1 instead of ending the game
                await self.credit_user(msg.author.id)

        except asyncio.TimeoutError:
            if not self.force_ended:
                await self.print_answer()
                self.rounds += 1

    async def create_new_question(self):
        """Create a new question and send it to the channel."""
        # noinspection PyBroadException
        question_posted = False
        while not question_posted:
            try:
                if self.idol_post_msg:
                    try:
                        await self.idol_post_msg.delete()
                    except Exception as e:
                        # message does not exist.
                        log.useless(f"{e} - Likely message doesn't exist - GuessingGame.Game.create_new_question")

                # Create random idol selection
                if not self.idol_set:
                    raise LookupError(f"No valid idols for the group {self.gender} and {self.difficulty}.")
                self.idol = random.choice(self.idol_set)

                # Create acceptable answers
                await self.create_acceptable_answers()

                # Create list of idol group names.
                self.group_names = [(await self.ex.u_group_members.get_group(group_id)).name for group_id in self.idol.groups]

                # Skip this idol if it is taking too long
                async with async_timeout.timeout(self.post_attempt_timeout) as posting:
                    self.idol_post_msg, self.photo_link = await self.ex.u_group_members.idol_post(self.channel, self.idol, user_id=self.host, guessing_game=True, scores=self.players)
                    log.console(f'{", ".join(self.correct_answers)} - {self.channel.id}')

                if posting.expired:
                    log.console(f"Posting for {self.idol.full_name} ({self.idol.stage_name}) [{self.idol.id}]"
                                f" took more than {self.post_attempt_timeout}")
                    continue
                question_posted = True
            except LookupError:
                raise
            except Exception as e:
                log.console(e)
                continue

    async def display_winners(self):
        """Displays the winners and their scores."""
        final_scores = ""
        if self.players:
            for user_id in self.players:
                final_scores += f"<@{user_id}> -> {self.players.get(user_id)}\n"
        return await self.channel.send(f">>> Guessing game has finished.\nScores:\n{final_scores}")

    async def end_game(self):
        """Ends a guessing game."""
        if self.results_posted:
            return

        await self.channel.send("The current game has now ended.")
        self.force_ended = True
        self.rounds = self.max_rounds
        if not self.host_user.gg_filter:
            # only update scores when there is no group filter on.
            await self.update_scores()
        await self.display_winners()
        self.results_posted = True

    async def update_scores(self):
        """Updates all player scores"""
        for user_id in self.players:
            await self.ex.u_guessinggame.update_user_guessing_game_score(self.difficulty, user_id=user_id,
                                                                    score=self.players.get(user_id))

    async def print_answer(self, question_skipped=False):
        """Prints the current round's answer."""
        skipped = ""
        if question_skipped:
            skipped = "Question Skipped. "
        msg = await self.channel.send(f"{skipped}The correct answer was `{self.idol.full_name} ({self.idol.stage_name})`"
                                      f" from the following group(s): `{', '.join(self.group_names)}`", delete_after=15)
        # create_task should not be awaited because this is meant to run in the background to check for reactions.
        try:
            # noinspection PyUnusedLocal
            # create task to check image reactions.
            asyncio.create_task(self.ex.u_group_members.check_idol_post_reactions(
                msg, self.host_ctx.message, self.idol, self.photo_link, guessing_game=True))
        except Exception as e:
            log.console(e)

    async def create_acceptable_answers(self):
        """Create acceptable answers."""
        self.correct_answers = [alias.lower() for alias in self.idol.aliases]
        self.correct_answers.append(self.idol.full_name.lower())
        self.correct_answers.append(self.idol.stage_name.lower())

    async def create_idol_pool(self):
        """Create the game's idol pool."""
        idol_gender_set = self.ex.cache.gender_selection.get(self.gender)
        idol_difficulty_set = self.ex.cache.difficulty_selection.get(self.difficulty)
        idol_filtered_set = set()
        self.ex.cache.idols_female.update({idol for idol in self.ex.cache.idols if idol.gender == 'f' and idol.photo_count})
        if self.host_user.gg_filter:
            for group in self.host_user.gg_groups:
                idol_filtered_set.update({await self.ex.u_group_members.get_member(idol_id) for idol_id in group.members})
            self.idol_set = list(idol_gender_set & idol_difficulty_set & idol_filtered_set)
        else:
            self.idol_set = list(idol_gender_set & idol_difficulty_set)

    async def process_game(self):
        """Ignores errors and continuously makes new questions until the game should end."""
        self.host_user = await self.ex.get_user(self.host)
        await self.create_idol_pool()
        try:
            while self.rounds < self.max_rounds and not self.force_ended:
                try:
                    await self.create_new_question()
                except LookupError as e:
                    await self.channel.send(f"The gender, difficulty, and filtered settings selected have no idols. "
                                            f"Ending Game.")
                    log.console(e)
                    return
                await self.check_message()
            await self.end_game()
        except Exception as e:
            await self.channel.send(f"An error has occurred and the game has ended. Please report this.")
            log.console(e)
