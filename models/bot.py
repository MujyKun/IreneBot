import asyncio
from typing import List, Union

import IreneAPIWrapper.models
from disnake.ext.commands import AutoShardedBot, errors

from cogs import cogs_list
from datetime import datetime
from util import logger
from IreneAPIWrapper.models import IreneAPIClient, Preload
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

        preload = Preload()
        preload.all_false()
        preload.twitch_subscriptions = True
        preload.twitter_accounts = True
        preload.languages = True
        preload.affiliations = True

        api = IreneAPIClient(
            token=keys.api_token,
            user_id=keys.bot_owner_id,
            api_url=keys.api_url,
            port=keys.api_port,
            preload_cache=preload,
        )

        self.api: IreneAPIClient = api

    async def prefix_check(
        self, bot: AutoShardedBot, msg: disnake.Message
    ) -> List[str]:
        """Get a list of prefixes for a Guild."""
        default = [self.default_prefix]
        if not hasattr(msg, "guild"):
            return default

        guild_id = msg.guild.id

        from cogs.helper import create_guild_model

        await create_guild_model(msg.guild)
        guild = await IreneAPIWrapper.models.Guild.get(guild_id)
        if guild and guild.prefixes:
            return guild.prefixes

        return [self.default_prefix]

    async def run_api_before_bot(self):
        """Run the API and the Bot afterwards."""

        self.loop.create_task(self.api.connect())

        while not self.api.connected:
            await asyncio.sleep(0)

        print(f"Connected to IreneAPI at {datetime.now()}")

        await self.start(
            self.keys.prod_bot_token if not self.dev_mode else self.keys.dev_bot_token
        )

    async def on_ready(self):
        msg = f"{self.keys.bot_name} is now ready at {datetime.now()}.\n" \
              f"{self.keys.bot_name} is now active in test guild {self.keys.support_server_id}."
        print(msg)
        logger.info(msg)

    async def handle_api_error(self, context: Union[disnake.Message, disnake.ext.commands.Context],
                               exception: APIError):
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
        from cogs.groupmembers.helper import idol_send_on_message  # avoids circular import
        await idol_send_on_message(self, message, await self.prefix_check(self, message))
        await self.process_commands(message)
