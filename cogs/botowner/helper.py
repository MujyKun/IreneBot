from IreneAPIWrapper.models import User, EightBallResponse
import disnake
from disnake import ApplicationCommandInteraction as AppCmdInter
from random import choice
from re import findall
from disnake.ext import commands
from ..helper import send_message
from models import all as all_games


async def process_add_eight_ball_response(
    response: str,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the 8ball command.
    """
    user = await User.get(user_id=user_id)
    await EightBallResponse.insert(response)
    await EightBallResponse.fetch_all()  # refresh objects.

    await send_message(
        response,
        key="8ball_add_response",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def process_delete_eight_ball_response(
    response_id: int,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the 8ball command.
    """
    user = await User.get(user_id=user_id)
    response = await EightBallResponse.get(response_id)
    if response:
        await response.delete()

    await send_message(
        response_id,
        key="8ball_delete_response",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )


async def process_list_eight_ball_responses(
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the 8ball command.
    """
    user = await User.get(user_id=user_id)
    responses = list(await EightBallResponse.fetch_all())  # refresh objs

    await send_message(
        "\n".join([f"{response.id} -> {response.response}" for response in responses]),
        key="8ball_list_response",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
    )
