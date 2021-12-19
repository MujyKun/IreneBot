import asyncio

from discord.ext.commands import AutoShardedBot, errors
from models import PgConnection
from keys import Keys
import discord

DEV_MODE = True


class Bot(AutoShardedBot):
    def __init__(self, bot_prefix, keys, **settings):
        super(Bot, self).__init__(bot_prefix, **settings)
        self.keys = keys
        self.db = PgConnection(**keys.get_keys("db_host", "db_name", "db_user", "db_pass", "db_port"))
        self.keys.__delattr__("db_pass")  # we no longer need the db pass stored in keys mem.

        try:
            self.loop.run_until_complete(self.db.connect())
            self.loop.run_until_complete(self.start(t_keys.prod_bot_token if not DEV_MODE else t_keys.dev_bot_token))

        except KeyboardInterrupt:
            self.loop.run_until_complete(self.close())
            # cancel all tasks lingering
        finally:
            self.loop.close()

    async def on_command_error(self, context, exception):
        if isinstance(exception, errors.CommandNotFound):
            ...
        elif isinstance(exception, errors.CommandInvokeError):
            try:
                if exception.original.status == 403:
                    return
            except AttributeError:
                return
            return await context.send(f"{exception}")
        elif isinstance(exception, errors.BadArgument):
            return await context.send(f"{exception}")
        else:
            ...


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True  # turn on privileged members intent
    # intents.presences = True  # turn on presences intent

    t_keys = Keys()

    options = {
        "case_insensitive": True,
        "owner_id": t_keys.bot_owner_id,
        "intents": intents
    }

    bot = Bot(t_keys.bot_prefix, t_keys, **options)

    cogs = []

    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


