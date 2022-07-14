import asyncio
from disnake.ext.commands import AutoShardedBot, errors
from cogs import cogs
from datetime import datetime
from util import logger
from IreneAPIWrapper.models import IreneAPIClient, Preload
from IreneAPIWrapper.exceptions import APIError
import disnake
from pprint import pformat


class Bot(AutoShardedBot):
    def __init__(self, bot_prefix, keys, dev_mode=False, **settings):
        super(Bot, self).__init__(bot_prefix, **settings)
        self.keys = keys
        for cog in cogs:
            self.load_extension(f"cogs.{cog}")

        self.dev_mode = dev_mode

        preload = Preload()
        preload.twitch_subscriptions = True
        preload.twitter_accounts = True

        api = IreneAPIClient(
            token=keys.api_token,
            user_id=keys.bot_owner_id,
            api_url=keys.api_url,
            port=keys.api_port,
            preload_cache=preload,
        )

        self.api: IreneAPIClient = api

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
        print(
            f"{self.keys.bot_name} is now ready at {datetime.now()}.\n"
            f"{self.keys.bot_name} is now active in test guild {self.keys.support_server_id}."
        )

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
                logger.error(exception)
                bug_channel_id = self.keys.bug_channel_id
                embed = disnake.Embed(title='API Error',
                                      description=exception.original.get_detailed_report(),
                                      color=disnake.Color.dark_red())

                if bug_channel_id:
                    channel = self.get_channel(bug_channel_id)
                    if channel:
                        await channel.send(embed=embed)
                return await context.channel.send(embed=embed)
            print(exception)
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
        await self.process_commands(message)
