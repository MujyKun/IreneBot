from discord.ext import commands
from Utility import resources as ex
from module.keys import wolfram_app_id, patreon_link
import xmltodict
import urllib.parse


class Wolfram(commands.Cog):
    def __init__(self):
        self.division_by_zero = "It is not possible to divide by zero."
        self.patreon_msg = f">>> **You must be a patron in order to use the WolframAlpha API due to the " \
            f"limited amount of requests. Any small math requests can be done " \
            f"without being a patron. Become a patron at {patreon_link}.**"

    def evalute_math(self, query):
        try:
            # do not allow user input to use any python functions.
            query = query.replace("^", '**')
            result = eval(query, {'__builtins__': None})
            return float(result)
        except ZeroDivisionError:
            return self.division_by_zero
        except SyntaxError:
            return False
        except:
            return False

    @commands.command()
    async def w(self, ctx, *, query):
        """Send a request to Wolfram.
        [Format: %w (query)]"""
        async with ctx.typing():
            result = self.evalute_math(query)
            if not result:
                if await ex.check_if_patreon(ctx.author.id):
                    query = urllib.parse.quote(query)
                    query_link = f"http://api.wolframalpha.com/v2/query?input={query}&appid={wolfram_app_id}"
                    async with ex.session.get(query_link) as r:
                        ex.cache.wolfram_per_minute += 1
                        xml_content = await r.content.read()
                        dict_content = (xmltodict.parse(xml_content)).get('queryresult')
                        results = []
                        pods = dict_content.get('pod')
                        if pods:
                            # we need to iterate through the pods, so put it in a list if there is only one.
                            if len(pods) == 1:  # do not shorten, has to be exactly 1
                                pods = [pods]
                            for pod in pods:
                                try:
                                    sub_pods = pod.get('subpod')
                                    if sub_pods:
                                        # we need to iterate through the pods, so put it in a list if there is only one.
                                        if pod.get('@numsubpods') == '1':
                                            sub_pods = [sub_pods]
                                        for sub_pod in sub_pods:
                                            image = sub_pod.get('img')
                                            sub_pod_result = image.get('@alt')
                                            if pod.get('@primary'):
                                                sub_pod_result = f"**{sub_pod_result}**"
                                            results.append(sub_pod_result)
                                except Exception as e:
                                    pass
                        if not results:
                            return await ctx.send(f"> **{ctx.author.display_name}, I could not find an answer to that.**")
                        await ctx.send("\n".join(results))

                else:
                    return await ctx.send(self.patreon_msg)
            else:
                await ctx.send(result)
