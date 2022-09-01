import asyncio
from typing import List, Union

from disnake.ext.commands import AutoShardedBot, errors

from cogs import cogs_list
from datetime import datetime
from util import logger
from IreneAPIWrapper.models import IreneAPIClient, Preload, User, Guild
from IreneAPIWrapper.exceptions import APIError
import disnake


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

        self.api: IreneAPIClient = api

    @staticmethod
    def get_preload():
        preload = Preload()
        preload.all_false()
        preload.twitch_subscriptions = True
        preload.twitter_accounts = True
        preload.languages = True
        preload.affiliations = True
        preload.eight_ball_responses = True
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

        while not self.api.connected:
            await asyncio.sleep(0)

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
            logger.warn("Did not ensure patrons since the bot was not ready.")
            return

        guild = self.get_guild(self.keys.support_server_id)
        _users = []

        await self._ensure_role(
            role_to_find=self.keys.patron_role_id,
            guild=guild,
            async_callable_name="set_patron",
            attr_flag="is_patron",
            type_desc="Patron",
        )
        await self._ensure_role(
            role_to_find=self.keys.super_patron_role_id,
            guild=guild,
            async_callable_name="set_super_patron",
            attr_flag="is_super_patron",
            type_desc="Super Patron",
        )
        await self._ensure_role(
            role_to_find=self.keys.translator_role_id,
            guild=guild,
            async_callable_name="set_translator",
            attr_flag="is_translator",
            type_desc="Translator",
        )
        await self._ensure_role(
            role_to_find=self.keys.proofreader_role_id,
            guild=guild,
            async_callable_name="set_proofreader",
            attr_flag="is_proofreader",
            type_desc="Proofreader",
        )
        await self._ensure_role(
            role_to_find=self.keys.data_mod_role_id,
            guild=guild,
            async_callable_name="set_data_mod",
            attr_flag="is_data_mod",
            type_desc="Data Mod",
        )

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

    async def on_command_error(self, context, exception):
        # TODO: errors.Cooldown was not found - causes an AttributeError when put in return_error_to_user
        return_error_to_user = [
            errors.BotMissingPermissions,
            errors.BadArgument,
            errors.MemberNotFound,
            errors.UserNotFound,
            errors.EmojiNotFound,
        ]
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

    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """Check for patron updates."""

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
