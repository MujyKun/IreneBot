import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction as AppCmdInter
from util import logger
import numexpr
import urllib.parse

class WolframCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def evaluate_math(query):
        try:
            # do not allow user input to use any python functions.
            query = query.replace("^", '**')
            # switched to third party library for simpler evaluations.
            result = numexpr.evaluate(query).item()
            return float(result)
        except ZeroDivisionError:
            return "It is not possible to divide by zero."
        except SyntaxError:
            return False
        except Exception as e:
            logger.warning(f"{e} (Exception) - Failed to evaluate numexpr expression {query}.")
            return False

    @commands.slash_command(description="Ask a question to WolframAlpha")
    async def wolfram(self, inter: AppCmdInter,
                      query: str = commands.Param(desc="WolframAlpha question as a string")):
        result = self.evaluate_math(query)
        if result:
            return await inter.send(f"**Input:** {query}\n" + f"**Result:** {result}")
        # TODO: Add patreon support
        query = urllib.parse.quote(query)
        # TODO: Add IreneAPIWrapper call for query
        # query_link = f"http://api.wolframalpha.com/v2/query?input={query}&appid={self.bot.keys.wolfram_id}"
        await inter.send("Querying Wolfram not implemented.")


def setup(bot: commands.AutoShardedBot):
    bot.add_cog(WolframCog(bot))
