from typing import List, Union, Optional

import disnake
from IreneAPIWrapper.models import TwitterAccount, Channel, Tweet, User, Wolfram
from disnake.ext import commands
from models import Bot
from ..helper import (
    get_channel_model,
    create_guild_model,
    get_discord_channel,
    send_message, get_message
)
from util import logger
import numexpr
import urllib.parse
from ..helper import (
    get_channel_model,
    create_guild_model,
    get_discord_channel,
    send_message, get_message
)


async def evaluate_math(query, user: User):
    """Evaluate a math expression."""
    try:
        # do not allow user input to use any python functions.
        query = query.replace("^", "**")
        # switched to third party library for simpler evaluations.
        result = numexpr.evaluate(query).item()
        return float(result)
    except ZeroDivisionError:
        return await get_message(user, "error_division_by_zero")
    except SyntaxError:
        return False
    except Exception as e:
        logger.error(
            f"{e} (evaluate_math) (Exception) - Failed to evaluate numexpr expression {query}."
        )
        return False


async def process_wolfram_query(query, user_id, ctx=None, inter=None, allowed_mentions=None):
    user = await User.get(user_id)
    result = await evaluate_math(query, user)
    if result:
        return await send_message(query, result, user=user, ctx=ctx, inter=inter,
                                  allowed_mentions=allowed_mentions, key="wolfram_query")
    if not user.is_patron:
        return await send_message(user=user, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions,
                                  key="error_wolfram_patron")

    parsed_query = urllib.parse.quote(query)
    results = await Wolfram.query(parsed_query)
    num_of_pods = results.get("@numpods")
    if not num_of_pods or num_of_pods == "0":
        return await send_message(user=user, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions,
                                  key="wolfram_no_results")

    list_of_pods = results.get("pod")
    primary_result_pods = [pod_dict for pod_dict in list_of_pods if (pod_dict['@title'] in ['Result', 'Results']
                                                             and pod_dict['@primary'] == 'true')]

    result_image = None
    result_text = None
    for pod_dict in primary_result_pods:
        sub_pod = pod_dict.get("subpod") or {}
        plain_text_result = sub_pod.get("plaintext")
        if plain_text_result:
            result_text = plain_text_result

        img_dict = sub_pod.get("img") or {}
        src_link = img_dict.get("@src")
        if src_link:
            result_image = src_link
            if not result_text:
                result_text = img_dict.get("@alt")

        result = f"{result_text} {result_image if result_image else ''}"

        return await send_message(query, result, user=user, ctx=ctx, inter=inter,
                                  allowed_mentions=allowed_mentions, key="wolfram_query")
