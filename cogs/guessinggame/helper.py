from typing import List, Union
import disnake
from IreneAPIWrapper.models import User, Group, Person
from models import GuessingGame, GroupGuessingGame
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import create_guild_model, send_message


async def check_input(
    max_rounds, timeout, gender, difficulty, contains_nsfw
) -> Union[str, bool]:
    """Check the inputs for a guessing game and return a string with all errors."""
    input_err_msg = ""
    if not 3 <= max_rounds <= 60:
        input_err_msg += "Your max rounds must be in between 3 and 60.\n"
    if difficulty.lower() not in ["easy", "medium", "hard"]:
        input_err_msg += "Your difficulty must be either 'easy', 'medium', or 'hard'.\n"
    if contains_nsfw.lower() not in ["yes", "no"]:
        input_err_msg += "Your nsfw choice must be 'yes' or 'no'\n"
    if gender.lower() not in ["male", "female", "mixed"]:
        input_err_msg += "Your gender choice needs to be 'male', 'female' or 'mixed'.\n"
    if not 5 <= timeout <= 60:
        input_err_msg += "Your timeout must be in between 5 and 60 seconds.\n"

    if input_err_msg:
        return "Your input does not work.\n" + input_err_msg
    return True


async def process_gg(
    bot,
    max_rounds,
    timeout,
    gender,
    difficulty,
    user_id: int,
    contains_nsfw: str,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
    group_mode=False,
):
    input_check = await check_input(
        max_rounds=max_rounds,
        timeout=timeout,
        gender=gender,
        difficulty=difficulty,
        contains_nsfw=contains_nsfw,
    )
    # inputs did not pass.
    if input_check is not True:
        return await send_message(
            msg=input_check, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    contains_nsfw = True if contains_nsfw.lower() == "yes" else False
    user = await User.get(user_id)
    game_class = GuessingGame if not group_mode else GroupGuessingGame
    game_obj = game_class(
        bot,
        max_rounds,
        timeout,
        gender,
        difficulty,
        contains_nsfw,
        user=user,
        ctx=ctx,
        inter=inter,
    )
    nsfw_select = "may not" if not contains_nsfw else "may"
    msg = (
        f"Starting {'Group ' if group_mode else ''}Guessing Game with `{max_rounds}` rounds, "
        f"a timeout of `{timeout}` seconds per round, a difficulty of `{difficulty}`, "
        f"with the gender selected as `{gender}`, and `{nsfw_select}` contain NSFW content."
    )
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)
    await game_obj.start()


async def process_toggle_gg_filter(
    user_id, ctx=None, inter=None, allowed_mentions=None
):
    """Toggle the GG filter."""
    user = await User.get(user_id)
    await user.toggle_gg_filter()
    msg = f"Your guessing game filter (including groups) is now {'enabled' if user.gg_filter_active else 'disabled'}."
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def process_gg_filter(
    user_id, selection_id, ctx=None, inter=None, allowed_mentions=None, group_mode=False
):
    """Do additions and removals in the person/group guessing game filters."""
    user = await User.get(user_id)
    if not user.gg_filter_person_ids and not user.gg_filter_active:
        await process_toggle_gg_filter(
            user.id, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    selection_err_msg = (
        f"No {'Person' if not group_mode else 'Group'} exists with that ID."
    )
    if group_mode:
        group = await Group.get(selection_id)
        if not group:
            return await send_message(
                selection_err_msg,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
            )
        if selection_id not in user.gg_filter_group_ids:
            user.gg_filter_group_ids.append(selection_id)
        else:
            user.gg_filter_group_ids.remove(selection_id)
        await user.upsert_filter_groups(tuple(user.gg_filter_group_ids))
    else:
        person = await Person.get(selection_id)
        if not person:
            return await send_message(
                selection_err_msg,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
            )

        if selection_id not in user.gg_filter_person_ids:
            user.gg_filter_person_ids.append(selection_id)
        else:
            user.gg_filter_person_ids.remove(selection_id)
        await user.upsert_filter_persons(tuple(user.gg_filter_person_ids))

    await process_view_gg_filter(
        user_id,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        group_mode=group_mode,
    )


async def process_view_gg_filter(
    user_id, ctx=None, inter=None, allowed_mentions=None, group_mode=False
):
    user = await User.get(user_id)
    if not group_mode:
        objects = [
            await Person.get(person_id) for person_id in user.gg_filter_person_ids
        ]
        names = "\n".join([f"{person.id}) {str(person.name)}" for person in objects])
    else:
        objects = [await Group.get(group_id) for group_id in user.gg_filter_group_ids]
        names = "\n".join([f"{group.id}) {group.name}" for group in objects])

    obj_type = "Persons" if not group_mode else "Groups"
    msg = f"Your GG Filter for {obj_type} is now:\n{names if names else 'Empty.'}"
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)
