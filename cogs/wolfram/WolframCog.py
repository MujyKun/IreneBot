import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from . import helper


class WolframCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    @commands.command(
        name="wolfram", description="Ask a question to WolframAlpha", aliases=["w"]
    )
    async def regular_wolfram(self, ctx, *, query: str):
        await helper.process_wolfram_query(
            query,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(description="Ask a question to WolframAlpha")
    async def wolfram(
        self,
        inter: AppCmdInter,
        query: str = commands.Param(desc="WolframAlpha query"),
    ):
        await helper.process_wolfram_query(
            query,
            user_id=inter.user.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(WolframCog(bot))
