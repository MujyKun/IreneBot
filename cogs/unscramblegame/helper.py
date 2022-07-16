from typing import List, Union
import disnake
from IreneAPIWrapper.models import User, Group, Person
from models import UnscrambleGame
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import create_guild_model, send_message, get_message

LIMIT_ROUNDS = [3, 60]
LIMIT_TIMEOUT = [5, 60]
DIFFICULTY_OPTIONS = ["easy", "medium", "hard"]
GENDER_OPTIONS = ["male", "female", "mixed"]


async def check_input(
    user, max_rounds, timeout, gender, difficulty
) -> Union[str, bool]:
    """Check the inputs for a guessing game and return a string with all errors."""
    input_err_msgs = [await get_message(user, "error_invalid_input")]
    if not 3 <= max_rounds <= 60:
        input_err_msgs.append(
            await get_message(
                user, "error_limit_rounds", LIMIT_ROUNDS[0], LIMIT_ROUNDS[1]
            )
        )
    if difficulty.lower() not in ["easy", "medium", "hard"]:
        input_err_msgs.append(
            await get_message(
                user, "error_difficulty_options", ", ".join(DIFFICULTY_OPTIONS)
            )
        )
    if gender.lower() not in ["male", "female", "mixed"]:
        input_err_msgs.append(
            await get_message(user, "error_gender_options", ", ".join(GENDER_OPTIONS))
        )
    if not 5 <= timeout <= 60:
        input_err_msgs.append(
            await get_message(
                user, "error_timeout_options", LIMIT_TIMEOUT[0], LIMIT_TIMEOUT[1]
            )
        )

    if len(input_err_msgs) > 1:
        return "\n".join(input_err_msgs)
    return True


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
    input_check = await check_input(
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
    msg = (
        f"Starting Unscramble Game with `{max_rounds}` rounds, "
        f"a timeout of `{timeout}` seconds per round, a difficulty of `{difficulty}`, "
        f"and with the gender selected as `{gender}`."
    )
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)
    await us_obj.start()
