import asyncio
from typing import List, Union

import aiohttp
from disnake.ext.commands import AutoShardedBot, errors
from disnake import ApplicationCommandInteraction as AppCmdInter

from cogs import cogs_list
from datetime import datetime
from util import logger
from IreneAPIWrapper.models import IreneAPIClient, Preload, User, Guild, Notification
from IreneAPIWrapper.exceptions import APIError
from cogs import helper
from models import (
    UserCommand,
    RegularCommand,
    MessageCommand,
    SlashCommand,
    get_cog_dicts,
)
import disnake
from cogs.helper import defer_inter


class Bot(AutoShardedBot):
    def __init__(self, default_bot_prefix, keys, dev_mode=False, **settings):
        super(Bot, self).__init__(self.prefix_check, **settings)
        self.default_prefix = default_bot_prefix
        self.keys = keys
        for cog in cogs_list:
            self.load_extension(f"cogs.{cog}")

        self.dev_mode = dev_mode
        self.logger = logger

        api = IreneAPIClient(
            token=keys.api_token,
            user_id=keys.bot_owner_id,
            api_url=keys.api_url,
            port=keys.api_port,
            preload_cache=Bot.get_preload(),
            verbose=True,
            logger=logger,
        )

        self.http_session = aiohttp.ClientSession()

        self.api: IreneAPIClient = api

    @staticmethod
    def get_preload():
        preload = Preload()
        preload.all_false()
        preload.persons = (
            preload.groups
        ) = (
            preload.twitch_subscriptions
        ) = (
            preload.twitter_accounts
        ) = (
            preload.languages
        ) = (
            preload.affiliations
        ) = (
            preload.eight_ball_responses
        ) = (
            preload.notifications
        ) = (
            preload.interactions
        ) = (
            preload.person_aliases
        ) = (
            preload.group_aliases
        ) = (
            preload.tags
        ) = (
            preload.socials
        ) = (
            preload.displays
        ) = (
            preload.companies
        ) = (
            preload.dates
        ) = (
            preload.names
        ) = (
            preload.bloodtypes
        ) = (
            preload.locations
        ) = (
            preload.auto_media
        ) = preload.reminders = preload.reaction_role_messages = preload.tiktok_subscriptions = True
        return preload

    async def prefix_check(
        self, bot: AutoShardedBot, msg: disnake.Message
    ) -> List[str]:
        """Get a list of prefixes for a Guild."""
        default = [self.default_prefix]
        if not hasattr(msg, "guild") or msg.guild is None:
            return default

        guild_id = msg.guild.id

        from cogs.helper import create_guild_model

        await create_guild_model(msg.guild)
        guild = await Guild.get(guild_id)
        if guild and guild.prefixes:
            return guild.prefixes

        return [self.default_prefix]

    async def run_api_before_bot(self):
        """Run the API and the Bot afterwards."""

        self.loop.create_task(self.api.connect())

        while not self.api.connected and not self.api.is_preloaded:
            await asyncio.sleep(0)

        await self.update_local_commands()

        await self.start(
            self.keys.prod_bot_token if not self.dev_mode else self.keys.dev_bot_token
        )

    async def on_ready(self):
        msg = (
            f"{self.keys.bot_name} is now ready at {datetime.now()}.\n"
            f"{self.keys.bot_name} is now active in test guild {self.keys.support_server_id}."
        )
        print(msg)
        logger.info(msg)

        await self.ensure_custom_roles()

    async def ensure_custom_roles(self):
        """
        Confirm the patrons, super patrons, translators, data mods, proofreaders, ... are set correctly.

        Should only be used when the bot is ready.
        """
        if not self.is_ready():
            logger.warn("Did not ensure roles since the bot was not ready.")
            return

        guild = self.get_guild(self.keys.support_server_id)

        for func_kwargs in self.keys.role_update_kwargs:
            await self._ensure_role(guild=guild, **func_kwargs)

        logger.info(
            "Finished ensuring custom roles for users associated with the bots development."
        )

    async def _ensure_role(
        self,
        role_to_find: int,
        guild: disnake.Guild,
        async_callable_name: str,
        attr_flag: str,
        type_desc=None,
    ):
        """
        role_to_find: int
            The role to find in the guild.
        guild: disnake.Guild
            Disnake Guild
        async_callable_name: Asynchronous Method Name
            This will be the User method name that will be called if the user is in the role and the attr_flag
            result ends up false.
        attr_flag: bool
            The attribute flag belonging to the User object.
        type_desc: Optional[str]
            The description of the type we are handling [Ex: Patron, Translator]
        """
        if not role_to_find:
            return  # no need for logging, role was not added as an env variable.

        role = guild.get_role(role_to_find)
        if not role:
            if type_desc:
                logger.warning(f"{type_desc} role not found for updates.")
            return

        for member in role.members:
            user = await User.get(member.id)
            active_status = getattr(user, attr_flag)
            if not active_status:
                async_callable = getattr(user, async_callable_name)
                await async_callable(active=True)
                self.logger.info(f"Made {user.id} a {type_desc}.")

    async def handle_api_error(
        self,
        context: Union[disnake.Message, disnake.ext.commands.Context],
        exception: APIError,
    ):
        logger.error(f"{exception}")
        bug_channel_id = self.keys.bug_channel_id
        embed = disnake.Embed(
            title="API Error",
            description=exception.get_detailed_report(),
            color=disnake.Color.dark_red(),
        )
        try:
            if bug_channel_id:
                channel = self.get_channel(bug_channel_id)
                if channel:
                    await channel.send(embed=embed)
            return await context.channel.send(embed=embed)
        except disnake.errors.HTTPException as e:
            logger.error(f"Could not send embedded error to channel - {e}")
        await helper.increment_trackable("api_errors_from_bot")

    async def on_slash_command_error(
        self, interaction: AppCmdInter, exception: errors.CommandError
    ) -> None:
        inter = await defer_inter(interaction, True)
        await helper.increment_trackable("slash_command_errors")
        await helper.increment_trackable("all_command_errors")

        if isinstance(exception, errors.NotOwner):
            error_message = "Only the bot owner can use this command."
        elif isinstance(exception, errors.CheckFailure):
            error_message = str(exception)
        else:
            logger.error(exception)
            error_message = str(exception)

        if error_message:
            await inter.send(error_message, ephemeral=True)

    async def on_command_error(self, context, exception):
        # TODO: errors.Cooldown was not found - causes an AttributeError when put in return_error_to_user
        return_error_to_user = [
            errors.BotMissingPermissions,
            errors.BadArgument,
            errors.MemberNotFound,
            errors.UserNotFound,
            errors.EmojiNotFound,
        ]
        await helper.increment_trackable("all_command_errors")
        if isinstance(exception, errors.CommandNotFound):
            return
        elif isinstance(exception, errors.CommandInvokeError):
            if isinstance(exception.original, APIError):
                return await self.handle_api_error(context, exception.original)
            logger.error(exception)
            try:
                if exception.original.status == 403:
                    return
            except AttributeError:
                return
            return await context.send(f"{exception}")
        if any(isinstance(exception, error) for error in return_error_to_user):
            return await context.send(f"{exception}")
        else:
            logger.error(exception)

    async def on_message(self, message):
        if message.author.bot:
            return

        from cogs.groupmembers.helper import (
            idol_send_on_message,
        )  # avoids circular import

        ctx = await self.get_context(message)
        if not ctx.command:
            await idol_send_on_message(
                self, message, await self.prefix_check(self, message)
            )
        else:
            await self.process_commands(message)
            await helper.increment_trackable("commands_used")
        await self.check_for_notification(message)
        await helper.increment_trackable("messages_received")

    async def on_message_edit(self, before, after):
        await self.on_message(after)
        await helper.increment_trackable("messages_edited")

    async def check_for_notification(self, message: disnake.Message):
        """Check for a user notification and send it out."""
        if (
            not message.guild
            or message.guild is None
            or not message.content
            or message.author.bot
        ):
            return

        notifications = await Notification.get_all(message.guild.id)
        if not notifications:
            return

        for noti in notifications:
            split_noti = noti.phrase.lower().split(" ")
            split_content = message.content.lower().split(" ")
            if not all(split_phrase in split_content for split_phrase in split_noti):
                continue

            desc = f"""
            Phrase: {noti.phrase}
            Message Author: {message.author.display_name}
            
            **Message:** {message.content}
            [Click to go to the Message]({message.jump_url})        
            """
            if (
                noti.user_id == message.author.id
            ):  # should not be notified of their own message.
                continue

            noti_member = message.guild.get_member(
                noti.user_id
            ) or await message.guild.fetch_member(noti.user_id)
            if not noti_member:
                await noti.delete()  # user not in guild.
                continue

            if noti_member not in message.channel.members:
                continue  # not able to view channel.

            embed = disnake.Embed(
                color=disnake.Color.random(), title="Phrase Found", description=desc
            )
            embed = await helper.add_embed_footer_and_author(embed)
            try:
                await noti_member.send(embed=embed)
            except Exception as e:
                logger.warning(
                    f"Could not send Noti DM to {noti_member} - {noti_member.id}. Removing Notification."
                )
                await noti.delete()

    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """Check for custom role updates. (ex: patron/translator)"""

        # only check support server.
        if after.guild.id != self.keys.support_server_id:
            return

        for func_kwargs in self.keys.role_update_kwargs:
            await self._check_role_update(member=after, **func_kwargs)

    async def _check_role_update(
        self,
        member: disnake.Member,
        role_to_find: int,
        async_callable_name: str,
        attr_flag: str,
        type_desc=None,
    ):
        """
        member: disnake.Member
            The Member to check the role status for.
        role_to_find: int
            The role to find in the guild.
        async_callable_name: Asynchronous Method Name
            This will be the User method name that will be called if the user is in the role and the attr_flag
            result ends up false.
        attr_flag: bool
            The attribute flag belonging to the User object.
        type_desc: Optional[str]
            The description of the type we are handling [Ex: Patron, Translator]
        """
        if not role_to_find:
            return  # no need for logging, role was not added as an env variable.

        guild = member.guild
        role = guild.get_role(role_to_find)
        if not role:
            if type_desc:
                logger.warning(f"{type_desc} role not found for role updates.")
            return
        user = await User.get(member.id)

        # check for active status
        status_check = getattr(user, attr_flag)
        async_callable = getattr(user, async_callable_name)

        if role in member.roles and not status_check:
            await async_callable(active=True)
            self.logger.info(f"Made {user.id} a {type_desc}.")

        # check for inactive status
        if role not in member.roles and status_check:
            await async_callable(active=False)
            self.logger.info(f"Removed {user.id} as a Patron.")

    async def update_local_commands(self):
        _commands = {
            "Message Commands": get_cog_dicts(
                self.all_message_commands.values(), MessageCommand
            ),
            "Slash Commands": get_cog_dicts(
                self.all_slash_commands.values(), SlashCommand
            ),
            "Regular Commands": get_cog_dicts(
                self.all_commands.values(), RegularCommand
            ),
            "User Commands": get_cog_dicts(
                self.all_user_commands.values(), UserCommand
            ),
        }
        await self.api.update_commands(_commands)
