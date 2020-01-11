from random import *
from module import BlackJack
from discord.ext import commands

client = 0


def setup(client1):
    client1.add_cog(Miscellaneous(client1))
    global client
    client = client1


class Miscellaneous(commands.Cog):
    def __init__(self, client):
        pass

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        x = client.guilds
        await ctx.send(x)

    @commands.command(aliases=['8ball', '8'])
    async def _8ball(self, ctx, *, question):
        """Asks the 8ball a question. [Format: %8ball Question]"""
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
            "Why the fuck are you asking me you dumb rat.",
            "You should already know this you babo.",
            "Try Asking Lance.", ]
        await ctx.send(">>> **Question: {} \nAnswer: {}**".format(question, choice(responses)))

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, message):
        """Owner to Bot Message"""
        await ctx.send(">>> {}".format(message), delete_after=30)

    @commands.command()
    @commands.is_owner()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(">>> {}".format(message), tts=True, delete_after=5)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """Shows Latency to Discord [Format: %ping]"""
        await ctx.send("> My ping is currently {}ms.".format(int(client.latency * 1000)))

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        """Kills the bot [Format: %kill]"""
        await ctx.send("> **The bot is now offline.**")
        await client.logout()

    @commands.command(aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, *, amount):
        """Prune Messages [Format: %clear (amount)][Aliases: prune]"""
        amount = int(amount)
        original = amount
        amount = amount + 1
        if amount <= 101:
            await ctx.channel.purge(limit=amount)
            print("Pruned {} messages".format(amount))
        if amount >= 102:
            number = (amount // 100)
            await ctx.send(
                "> **{}** messages will be deleted in 5 seconds and will be split in intervals of 100.".format(
                    original))
            for i in range(number):
                await ctx.channel.purge(limit=100)
                print("Pruned 100 messages")
            await ctx.send("> **{}** messages have been pruned.".format(original))
