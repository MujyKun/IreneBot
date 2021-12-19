from discord.ext import commands


class GuessingGame(commands.Cog):
    @staticmethod
    def setup(bot: commands.AutoShardedBot):
        bot.add_cog(GuessingGame(bot))

    def __init__(self, bot):
        self.bot = bot

    ...

