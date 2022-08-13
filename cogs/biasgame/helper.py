from IreneAPIWrapper.models import User, BiasGame as BiasGameModel, Person
from disnake import AppCmdInter
from disnake.ext import commands
from ..helper import send_message, check_game_input
from models import BiasGame


async def process_list_bg(
    user_id,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    user = await User.get(user_id)

    scores = await BiasGameModel.fetch_winners(user_id, limit=15) or {}

    results = ""
    for score_info in scores.values():
        person_id, wins = score_info["personid"], score_info["wins"]
        person = await Person.get(person_id)
        if not person:
            continue
        results += f"{str(person.name)} [ID: {person.id}] - {wins} Wins\n"

    if not results:
        results = "None"

    await send_message(
        user_id,
        results,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        key="list_bg",
        user=user,
    )


async def process_bg(
    bot,
    user_id,
    bracket_size,
    gender,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    user = await User.get(user_id)

    input_check = await check_game_input(
        user=user,
        bracket_size=bracket_size,
        gender=gender,
    )

    # inputs did not pass.
    if input_check is not True:
        return await send_message(
            msg=input_check, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    await send_message(
        bracket_size,
        gender,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        key="start_bg",
        user=user,
    )

    game_obj = BiasGame(
        bot,
        bracket_size,
        gender,
        user=user,
        ctx=ctx,
        inter=inter,
    )

    await game_obj.start()
