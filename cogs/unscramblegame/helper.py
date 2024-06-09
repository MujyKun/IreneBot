from IreneAPIWrapper.models import User
from models import UnscrambleGame
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import send_message, check_game_input, in_game


async def process_us(
    bot,
    max_rounds,
    timeout,
    gender,
    difficulty,
    user_id: int,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    user = await User.get(user_id)
    if await in_game(user):
        return await send_message(
            key="already_in_game",
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
        )
    input_check = await check_game_input(
        user=user,
        max_rounds=max_rounds,
        timeout=timeout,
        gender=gender,
        difficulty=difficulty,
    )

    # inputs did not pass.
    if input_check is not True:
        return await send_message(
            msg=input_check, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    us_obj = UnscrambleGame(
        bot, max_rounds, timeout, gender, difficulty, user=user, ctx=ctx, inter=inter
    )
    await send_message(
        max_rounds,
        timeout,
        difficulty,
        gender,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        key="start_us",
        user=user,
    )
    await us_obj.start()
