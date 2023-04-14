from typing import Optional

from IreneAPIWrapper.models import User, EightBallResponse, Interaction, InteractionType
from disnake import ApplicationCommandInteraction as AppCmdInter, Message
from disnake.ext import commands
from ..helper import send_message


async def auto_complete_interaction_types(inter: AppCmdInter, user_input: str):
    """Auto complete interaction types"""
    interaction_types = list(await InteractionType.get_all())
    return [interaction_type.name for interaction_type in interaction_types][:24]


async def get_interaction_type_by_name(type_name: str) -> Optional[InteractionType]:
    """Get an interaction type by its name."""
    interaction_types = list(await InteractionType.get_all())
    matches = [
        interaction_type
        for interaction_type in interaction_types
        if interaction_type.name.lower() == type_name.lower()
    ]
    if matches:
        return matches[0]


async def process_interaction_type_add(
    type_name: str, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """Add an interaction type"""
    user = await User.get(user_id)
    if await get_interaction_type_by_name(type_name):
        # type already exists
        return await send_message(
            key="interaction_type_exists",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    await InteractionType.insert(type_name)
    return await send_message(
        key="interaction_type_added",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def process_interaction_type_delete(
    type_name: str, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """Delete an interaction type"""
    user = await User.get(user_id)
    interaction_type = await get_interaction_type_by_name(type_name)
    if interaction_type:
        await interaction_type.delete()
        return await send_message(
            key="interaction_type_deleted",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    return await send_message(
        key="interaction_type_does_not_exist",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def process_interaction_add(
    type_name: str, url: str, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """Add an interaction"""
    user = await User.get(user_id)
    interaction_type = await get_interaction_type_by_name(type_name)
    if interaction_type:
        interaction = await get_interaction_by_url(url=url)
        if interaction:
            return await send_message(
                key="interaction_already_exists",
                user=user,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
            )

        await Interaction.insert(type_id=interaction_type.id, url=url)
        return await send_message(
            key="interaction_added",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    return await send_message(
        key="interaction_type_does_not_exist",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def process_interaction_remove(
    type_name: str, url: str, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """Remove an interaction"""
    user = await User.get(user_id)
    interaction_type = await get_interaction_type_by_name(type_name)
    if interaction_type:
        interaction = await get_interaction_by_url(url)
        if interaction:
            await interaction.delete()
            return await send_message(
                key="interaction_deleted",
                user=user,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
            )
        else:
            return await send_message(
                key="interaction_does_not_exist",
                user=user,
                ctx=ctx,
                inter=inter,
                allowed_mentions=allowed_mentions,
            )

    return await send_message(
        key="interaction_type_does_not_exist",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
    )


async def get_interaction_by_url(url: str) -> Optional[Interaction]:
    interactions = list(await Interaction.get_all())
    matches = [
        interaction
        for interaction in interactions
        if interaction.url.lower() == url.lower()
    ]
    if matches:
        return matches[0]


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
