from discord.ext import commands


class GroupMembers(commands.Cog):
    @staticmethod
    def setup(bot: commands.AutoShardedBot):
        bot.add_cog(GroupMembers(bot))

    def __init__(self, bot):
        self.bot = bot

    ...

