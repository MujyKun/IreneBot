import asyncio

import disnake
from disnake.ext import commands
from disnake.ext.commands import AutoShardedBot, errors
from keys import Keys
from cogs import cogs
from datetime import datetime
import traceback
from util import logger
from IreneAPIWrapper.models import IreneAPIClient

DEV_MODE = True


class Bot(AutoShardedBot):
    def __init__(self, bot_prefix, keys, **settings):
        super(Bot, self).__init__(bot_prefix, **settings)
        self.keys = keys
        for cog in cogs:
            self.load_extension(f"cogs.{cog}")

        self.api = IreneAPIClient(token=keys.api_token,
                                  user_id=keys.bot_owner_id,
                                  api_url=keys.api_url,
                                  port=keys.api_port)

        self.loop.create_task(self.api.connect())

        self.run(self.keys.prod_bot_token if not DEV_MODE else self.keys.dev_bot_token)

    async def on_ready(self):
        print(f"{self.keys.bot_name} is now ready at {datetime.now()}.\n"
              f"{self.keys.bot_name} is now active in test guild {t_keys.support_server_id}.")

    async def on_command_error(self, context, exception):
        return_error_to_user = [errors.BotMissingPermissions, errors.BadArgument, errors.Cooldown,
                                 errors.MemberNotFound, errors.UserNotFound, errors.EmojiNotFound]
        if isinstance(exception, errors.CommandNotFound):
            return
        elif isinstance(exception, errors.CommandInvokeError):
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


if __name__ == '__main__':
    intents = disnake.Intents.default()
    intents.members = True  # turn on privileged members intent
    intents.messages = True
    # intents.presences = True  # turn on presences intent

    t_keys = Keys()

    options = {
        "case_insensitive": True,
        "owner_id": t_keys.bot_owner_id,
        "intents": intents,
        "test_guilds": [t_keys.support_server_id],
        "sync_commands_debug": True
    }

    bot = Bot(t_keys.bot_prefix, t_keys, **options)
