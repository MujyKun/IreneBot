from IreneAPIWrapper.models import User, Group, Person
from models import GuessingGame, GroupGuessingGame
from disnake.ext import commands
from disnake import AppCmdInter
from ..helper import send_message, check_game_input, in_game


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
        contains_nsfw=contains_nsfw,
    )
    # inputs did not pass.
    if input_check is not True:
        # no need to pass in a user/key since we used get_message in our game input check.
        return await send_message(
            msg=input_check, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    contains_nsfw = True if contains_nsfw.lower() == "yes" else False
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
    game_type = "`Group` " if group_mode else ""
    await send_message(
        game_type,
        max_rounds,
        timeout,
        difficulty,
        gender,
        nsfw_select,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        key="start_gg",
        user=user,
    )
    await game_obj.start()


async def process_toggle_gg_filter(
    user_id, ctx=None, inter=None, allowed_mentions=None
):
    """Toggle the GG filter."""
    user = await User.get(user_id)
    await user.toggle_gg_filter()
    await send_message(
        "enabled" if user.gg_filter_active else "disabled",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        key="toggle_gg_filter",
        user=user,
    )


async def process_gg_filter(
    user_id, selection_id, ctx=None, inter=None, allowed_mentions=None, group_mode=False
):
    """Do additions and removals in the person/group guessing game filters."""
    user = await User.get(user_id)
    if not user.gg_filter_person_ids and not user.gg_filter_active:
        await process_toggle_gg_filter(
            user.id, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions
        )

    type_class = Group if group_mode else Person
    type_object = await type_class.get(selection_id)
    if not type_object:
        return await send_message(
            "Person" if not group_mode else "Group",
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
            user=user,
            key="error_gg_filter_selection",
        )

    if group_mode:
        if selection_id not in user.gg_filter_group_ids:
            user.gg_filter_group_ids.append(selection_id)
        else:
            user.gg_filter_group_ids.remove(selection_id)
        await user.upsert_filter_groups(tuple(user.gg_filter_group_ids))
    else:
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
    await send_message(
        obj_type,
        f"\n{names if names else 'Empty.'}",
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        user=user,
        key="view_gg_filter",
    )
