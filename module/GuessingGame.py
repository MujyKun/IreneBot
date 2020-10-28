from Utility import resources as ex
from discord.ext import commands, tasks
from module import keys
import asyncio


class GuessingGame(commands.Cog):
    def __init__(self):
        # all games currently existing
        self.games = []

    @commands.command(aliases=['gg'])
    async def guessinggame(self, ctx, gender="all", rounds=20, timeout=20):
        """Start an idol guessing game in the current channel. The host of the game can use `stop`/`end` to end the game or `skip` to skip the current round without affecting the round number.
        [Format: %guessinggame (Male/Female/All) (# of rounds - default 20) (timeout for each round - default 20s)]"""
        if await self.check_game_exists(ctx.channel):
            return await ctx.send("> **A guessing game is currently in progress in this channel.**")
        if rounds > 60 or timeout > 60:
            return await ctx.send("> **ERROR -> The max rounds is 60 and the max timeout is 60s.**")
        elif rounds < 1 or timeout < 3:
            return await ctx.send("> **ERROR -> The minimum rounds is 1 and the minimum timeout is 3 seconds.")
        game = Game()
        self.games.append(game)
        await game.start_game(ctx.channel, ctx.author.id, max_rounds=rounds, timeout=timeout, gender=gender)
        self.games.remove(game)

    async def check_game_exists(self, channel):
        for game in self.games:
            if game.channel == channel:
                return game


class Game:
    def __init__(self):
        # user_id : score
        self.host = None
        self.players = {}
        self.rounds = 0
        self.channel = None
        self.idol = None
        self.correct_answers = []
        self.timeout = 0
        self.max_rounds = 0
        self.force_ended = False
        self.idol_post_msg = None
        self.gender = None

    async def start_game(self, channel, host, max_rounds=20, timeout=20, gender="all"):
        self.channel = channel
        self.host = host
        self.max_rounds = max_rounds
        self.timeout = timeout
        if gender.lower() in ['male', 'm', 'female', 'f']:
            self.gender = gender.lower()[0]
        await self.create_new_question()

    async def check_message(self):
        stop_phrases = ['stop', 'end']

        def check_correct_answer(message):
            """Check if the user has the correct answer."""
            return ((message.content.lower() in self.correct_answers) or
                    ((message.content.lower() == 'skip' or message.content.lower() in stop_phrases)
                     and message.author.id == self.host)) and \
                     message.channel == self.channel
        try:
            msg = await ex.client.wait_for('message', check=check_correct_answer, timeout=self.timeout)
            await msg.add_reaction(keys.check_emoji)
            if msg.content.lower() == 'skip':
                await msg.channel.send(f'Question skipped. The answer was {self.idol.full_name} ({self.idol.stage_name})', delete_after=15)
            elif msg.content.lower() in stop_phrases:
                await msg.channel.send(f"The current game has now ended.")
                self.force_ended = True
                self.rounds = self.max_rounds
                return await self.display_winners()
            else:
                score = self.players.get(msg.author.id)
                if not score:
                    self.players[msg.author.id] = 1
                else:
                    self.players[msg.author.id] = score + 1
                self.rounds += 1
            await self.create_new_question()
        except asyncio.TimeoutError:
            # reveal the answer and make a new question.
            self.rounds += 1
            if not self.force_ended:
                await self.channel.send(f"The correct answer was {self.idol.full_name} ({self.idol.stage_name})", delete_after=15)
            await self.create_new_question()

    async def create_new_question(self):
        """Create a new question and send it to the channel."""
        if self.idol_post_msg:
            await self.idol_post_msg.delete()
        if self.rounds >= self.max_rounds:
            if self.force_ended:
                return
            return await self.display_winners()
        self.idol = await ex.get_random_idol()
        if self.gender:
            while self.idol.gender != self.gender:
                self.idol = await ex.get_random_idol()
        self.correct_answers = []
        for alias in self.idol.aliases:
            self.correct_answers.append(alias.lower())
        self.correct_answers.append(self.idol.full_name.lower())
        self.correct_answers.append(self.idol.stage_name.lower())
        print(self.correct_answers)
        self.idol_post_msg, url = await ex.idol_post(self.channel, self.idol, user_id=self.host, guessing_game=True, scores=self.players)
        # add reaction here
        await self.check_message()

    async def display_winners(self):
        final_scores = ""
        if self.players:
            for user_id in self.players:
                final_scores += f"<@{user_id}> -> {self.players.get(user_id)}\n"
        return await self.channel.send(f">>> Guessing game has finished.\nScores:\n{final_scores}")

    async def end_game(self):
        self.force_ended = True
        self.rounds = self.max_rounds
        await self.display_winners()

