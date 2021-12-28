from disnake.ext import commands


class GuessingGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ...


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(GuessingGameCog(bot))
