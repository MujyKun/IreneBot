import asyncio

from discord.ext import commands
import xmltodict
import urllib.parse
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
import numexpr


# noinspection PyBroadException,PyPep8
class Wolfram(commands.Cog):
    def __init__(self, ex):
        self.ex: Utility = ex
        self.division_by_zero = "It is not possible to divide by zero."
        self.patreon_msg = f">>> **You must be a patron in order to use the WolframAlpha API due to the " \
            f"limited amount of requests. Any small math requests can be done " \
            f"without being a patron. Become a patron at {self.ex.keys.patreon_link}.**"

    def evalute_math(self, query):
        try:
            # do not allow user input to use any python functions.
            query = query.replace("^", '**')
            # switched to third party library for simpler evaluations.
            result = numexpr.evaluate(query).item()
            return float(result)
        except ZeroDivisionError:
            return self.division_by_zero
        except SyntaxError:
            return False
        except Exception as e:
            log.useless(f"{e} - Failed to evaluate numexpr expression {query}. Wolfram.evaluate_math()")
            return False

    @commands.command()
    async def w(self, ctx, *, query):
        """
        Send a request to Wolfram.

        [Format: %w (query)]
        """
        async with ctx.typing():
            result = self.evalute_math(query)
            if result:
                return await ctx.send(result)
            if not await self.ex.u_patreon.check_if_patreon(ctx.author.id):
                return await ctx.send(self.patreon_msg)
            query = urllib.parse.quote(query)
            query_link = f"http://api.wolframalpha.com/v2/query?input={query}&appid={self.ex.keys.wolfram_app_id}"
            async with self.ex.session.get(query_link) as r:
                self.ex.cache.wolfram_per_minute += 1
                xml_content = await r.content.read()
                dict_content = (xmltodict.parse(xml_content)).get('queryresult')
                results = []
                pods = dict_content.get('pod')
                if pods:
                    # we need to iterate through the pods, so put it in a list if there is only one.
                    if len(pods) == 1:  # do not shorten, has to be exactly 1
                        pods = [pods]
                    for pod in pods:
                        await asyncio.sleep(0)
                        try:
                            sub_pods = pod.get('subpod')
                            if not sub_pods:
                                continue
                            # we need to iterate through the pods, so put it in a list if there is only one.
                            if pod.get('@numsubpods') == '1':
                                sub_pods = [sub_pods]
                            for sub_pod in sub_pods:
                                await asyncio.sleep(0)
                                image = sub_pod.get('img')
                                sub_pod_result = image.get('@alt')
                                if pod.get('@primary'):
                                    sub_pod_result = f"**{sub_pod_result}**"
                                results.append(sub_pod_result)
                        except Exception as e:
                            log.useless(f"{e} - Failed to go through a weverse pod - Wolfram.w")

                if not results:
                    return await ctx.send(f"> **{ctx.author.display_name}, I could not find an answer to that.**")
                final_result = "\n".join(results)

                # if the result is less than 1500 chars, just send it as a body with no embed.
                if len(final_result) < 1500:
                    return await ctx.send(final_result)
                embed_msg = ""
                embed_list = []
                page_number = 1
                for result in results:
                    await asyncio.sleep(0)
                    if len(embed_msg) > 1500:
                        embed_list.append(
                            await self.ex.create_embed(title=f"Wolfram Request Page: {page_number} (FULL) ",
                                                       title_desc=embed_msg))
                        embed_msg = ""
                        page_number += 1
                    embed_msg += f"{result}\n"

                if embed_msg:
                    embed_list.append(
                        await self.ex.create_embed(title=f"Wolfram Request Page: {page_number} (FULL)",
                                                   title_desc=embed_msg))

                msg = await ctx.send(embed=embed_list[0])
                await self.ex.check_left_or_right_reaction_embed(msg, embed_list)
