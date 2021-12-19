from discord.ext import commands


class BiasGame(commands.Cog):
    @staticmethod
    def setup(bot: commands.AutoShardedBot):
        bot.add_cog(BiasGame(bot))

    def __init__(self, bot):
        self.bot = bot

    ...