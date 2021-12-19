from os import getenv
from discord.ext.commands import AutoShardedBot, errors
from models import PgConnection
import discord

class Bot(AutoShardedBot):
    def __init__(self, command_prefix, **settings):
        super(Bot, self).__init__(command_prefix, **settings.get("options"))

        # self.conn:
        top_gg_key = getenv("TOP_GG_KEY")

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
    # generate db
    db = PgConnection



    # migration
    #
    ...

    intents = discord.Intents.default()
    # intents.members = True  # turn on privileged members intent
    # intents.presences = True  # turn on presences intent

    kwargs = {
        "options": {
            "case_insensitive": True,
            "owner_id": int(getenv("BOT_OWNER_ID")),
            "intents": intents
        },
        "db_kwargs": {
            "host": getenv("POSTGRES_HOST"),
            "database": getenv("POSTGRES_DATABASE"),
            "user": getenv("POSTGRES_USER"),
            "password": getenv("POSTGRES_PASSWORD"),
            "port": getenv("POSTGRES_PORT")
        }
    }

    bot = Bot(getenv("BOT_PREFIX"), **kwargs)

    cogs = ["BotInfo", "Weverse"]

    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")

    bot.run(getenv("BOT_TOKEN"))