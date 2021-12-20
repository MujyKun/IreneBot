from discord.ext import commands
# import BiasGame

class BiasGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ...

def setup(bot: commands.AutoShardedBot):
    bot.add_cog(BiasGameCog(bot))