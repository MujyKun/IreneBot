from disnake.ext import commands


class BiasGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @slash_command(description="Bias Game: Pick between idols to find out who your true bias is!")
    # async def biasgame(self, inter: SlashInteraction):
    #     pass
    #
    # BgGender = option_enum({"male": "Male", "female": "Female", "all": "All"})
    # BgBracketSize = option_enum({"4": 4, "8": 8, "16": 16, "32": 32})
    #
    # @biasgame.sub_command(description="Start a bias game.")
    # async def start(self, inter: SlashInteraction,
    #                 gender: BgGender = OptionParam(desc="Gender of idols included in the bias game."),
    #                 bracket_size: BgBracketSize = OptionParam(desc="Number of idols in the game bracket")
    #                 ):
    #     embed = await create_bot_author_embed(self.bot.keys, title="Starting Bias Game")
    #     embed.add_field(name="Gender", value=str(gender))
    #     embed.add_field(name="Bracket Size", value=str(bracket_size))
    #     await inter.reply(embed=embed)
    #     # TODO add bias game cog
    #     await inter.send("No games yet sorry.")
    #
    # @biasgame.sub_command(description="Stop current bias game.")
    # async def stop(self, inter: SlashInteraction):
    #     await inter.respond("Game stopped.")
    #     # TODO: stop bias game
    #
    # @biasgame.sub_command(description="List your bias game leaderboard.")
    # async def list(self, inter: SlashInteraction):
    #     await inter.reply("List out all bias game results")
    #     # TODO: list out all bias game results


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(BiasGameCog(bot))
