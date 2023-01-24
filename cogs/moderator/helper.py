from typing import List
from util import logger
import aiohttp
import disnake
from IreneAPIWrapper.models import Guild, User, ReactionRoleMessage
from disnake.ext import commands
from disnake import AppCmdInter, MessageInteraction
from ..helper import create_guild_model, send_message, defer_inter

PRUNE_MAX = 100
PRUNE_MIN = 0


async def process_prune(
    channel, amount, user_id: int, ctx=None, inter=None, allowed_mentions=None
):
    """Process the prune/clear command."""
    user = await User.get(user_id)
    if amount not in range(PRUNE_MIN, PRUNE_MAX):
        return await send_message(
            PRUNE_MIN,
            PRUNE_MAX,
            key="not_in_range",
            user=user,
            ctx=ctx,
            inter=inter,
            allowed_mentions=allowed_mentions,
        )

    await channel.purge(limit=amount, bulk=True)
    return await send_message(
        amount if inter else amount - 1,
        key="messages_cleared",
        user=user,
        ctx=ctx,
        inter=inter,
        allowed_mentions=allowed_mentions,
        delete_after=5,
    )


async def process_prefix_add_remove(
    guild: disnake.Guild,
    prefix: str,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
    add=False,
):
    """Add a command prefix to a guild.

    :param guild: disnake.Guild
        Guild object
    :param prefix: str
        Prefix to add/remove
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    :param add: bool
        Whether to add a prefix. Defaults to removing.
    """
    await create_guild_model(guild)
    guild = await Guild.get(guild.id)

    if add:
        await guild.add_prefix(prefix)
        msg = f"{prefix.lower()} has been added as a command prefix for {guild.name}."
    else:
        await guild.delete_prefix(prefix)
        msg = (
            f"{prefix.lower()} has been removed as a command prefix from {guild.name}."
        )

    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def process_add_emoji(
    emoji,
    emoji_name,
    user_id,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """
    Process the adding of an emoji to a server.

    :param emoji: Union[disnake.PartialEmoji, str]
        The emoji to add.
    :param emoji_name: str
        The emoji name.
    :param user_id: int
        The command user's ID.
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    """
    response_deferred = await defer_inter(inter)
    url = emoji if not isinstance(emoji, disnake.PartialEmoji) else emoji.url
    user = await User.get(user_id)
    args = tuple()
    key = "add_emoji_fail"
    if len(emoji_name) < 2:
        emoji_name = "EmojiName"

    if ctx:
        http_session = ctx.bot.http_session
        guild = ctx.guild
    else:
        http_session = inter.bot.http_session
        guild = inter.guild

    try:
        async with http_session.get(url) as r:
            if r.status == 200:
                await guild.create_custom_emoji(name=emoji_name, image=await r.read())
                key = "add_emoji_success"
    except aiohttp.InvalidURL:
        key = "invalid_url"
    except disnake.HTTPException as e:
        if e.code == 30008:
            key = "max_emojis"
        if e.code == 50035:
            key = "emoji_size_reached"
            args = (f"https://ezgif.com/optimize?url={url}",)
    except Exception as e:
        logger.error(
            f"{e} - Processing AddEmoji command failed. "
            f"EMOJI: {emoji} -> EMOJI NAME: {emoji_name}, User ID: {user_id}"
        )
        key = "add_emoji_fail"

    return await send_message(
        *args,
        key=key,
        user=user,
        inter=inter,
        ctx=ctx,
        allowed_mentions=allowed_mentions,
        response_deferred=response_deferred,
    )


async def process_prefix_list(
    guild: disnake.Guild,
    ctx: commands.Context = None,
    inter: AppCmdInter = None,
    allowed_mentions=None,
):
    """Send the command prefixes of a guild.

    :param guild: disnake.Guild
        Guild object
    :param ctx: commands.Context
        Context of the command.
    :param inter: AppCmdInter
        App Command Context
    :param allowed_mentions: disnake.AllowedMentions
        The settings for allowed mentions.
    """
    await create_guild_model(guild)
    guild = await Guild.get(guild.id)
    msg = f"The following are the custom prefixes for {guild.name}:\n" + ", ".join(
        guild.prefixes
    )
    await send_message(msg=msg, ctx=ctx, inter=inter, allowed_mentions=allowed_mentions)


async def auto_complete_type_guild_prefixes(
    inter: disnake.AppCmdInter, user_input: str
) -> List[str]:
    """Auto-complete typing for the command prefixes in a guild."""
    await create_guild_model(inter.guild)
    guild = await Guild.get(inter.guild_id)
    return guild.prefixes[:24]


async def process_add_reaction_role(
    user_id, description, ctx=None, inter=None, allowed_mentions=None
):
    """
    Add a reaction role.

    :param user_id: int
        Command Invoker
    :param description: str
        The description needed
    :param ctx: disnake.Context
        Command Context
    :param inter: disnake.AppCmdInter
        App Command
    :param allowed_mentions:
        The allowed mentions in a response.
    """
    user = await User.get(user_id)
    response_deferred = await defer_inter(inter, ephemeral=True)
    view = disnake.ui.View(timeout=None)
    view.add_item(RoleDropdown(description))
    await send_message(
        key="choose_roles",
        user=user,
        view=view,
        ephemeral=True,
        response_deferred=response_deferred,
        inter=inter,
    )


async def reaction_roles_post(inter: MessageInteraction, description, roles):
    """
    Post the reaction roles message

    :param inter: AppCmdInter
        Interaction Message
    :param description: str
        Content of the message.
    :param roles: List[disnake.Role]
        A list of discord roles.
    """
    view = disnake.ui.View(timeout=None)
    for role in roles:
        view.add_item(disnake.ui.Button(label=role.name, custom_id=role.id))
    messages = await send_message(msg=description, channel=inter.channel, view=view)
    for message in messages:
        await ReactionRoleMessage.insert(message.id)


async def handle_role_reaction_press(interaction: disnake.MessageInteraction):
    """
    Handles role reaction button presses.

    A 'on_button_click' listener.

    :param interaction: disnake.MessageInteraction
        The interaction.
    """
    if interaction.message not in await ReactionRoleMessage.get_all():
        return

    role_id = int(interaction.component.custom_id)
    member: disnake.Member = interaction.author
    user = await User.get(member.id)
    role = member.get_role(role_id)
    if role:
        await member.remove_roles(role, reason="Reaction Role Message")
        await send_message(user=user, key="role_removed", inter=interaction, ephemeral=True)
    else:
        role = interaction.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role, reason="Reaction Role Message")
                await send_message(user=user, key="role_added", inter=interaction, ephemeral=True)
            except disnake.errors.Forbidden as e:
                await send_message(user=user, key="no_permissions", inter=interaction, ephemeral=True)
        else:
            await send_message(user=user, key="role_not_found", inter=interaction, ephemeral=True)


class RoleDropdown(disnake.ui.RoleSelect):
    def __init__(self, desc):
        self.desc = desc
        super(RoleDropdown, self).__init__(min_values=1, max_values=25)

    async def callback(self, interaction, /):
        await reaction_roles_post(interaction, self.desc, self.values)
        # prevent a failed interaction message.
        await send_message(msg="Success.", inter=interaction, ephemeral=True)
