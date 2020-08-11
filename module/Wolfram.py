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
            # raise
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
                        xml_content = await r.content.read()
                        dict_content = xmltodict.parse(xml_content)
                        results = []
                        try:
                            for pod in dict_content['queryresult']['pod']:
                                """Grabs the elements in each pod looking for the correct answer."""
                                title = pod['@title'] or None
                                acceptable_titles = ['results', 'result']
                                if title.lower() in acceptable_titles:
                                    try:
                                        data = ((pod['subpod'])[1])['img']['@alt']
                                        results.append(data)
                                    except Exception as e:
                                        data = (pod['subpod']['img']['@alt'])
                                        results.append(data)
                        except Exception:
                            pass
                        if len(results) == 0:
                            return await ctx.send(f"> **{ctx.author.display_name}, I could not find an answer to that.**")
                        for data in results:
                            await ctx.send(data)
                else:
                    return await ctx.send(self.patreon_msg)
            else:
                await ctx.send(result)
