from discord.ext.commands import AutoShardedBot, errors
from keys import Keys
import discord
from dislash import InteractionClient
from cogs import cogs

DEV_MODE = True


class Bot(AutoShardedBot):
    def __init__(self, bot_prefix, keys, **settings):
        super(Bot, self).__init__(bot_prefix, **settings)
        self.keys = keys
        self.inter_client = InteractionClient(self, test_guilds=[int(t_keys.support_server_id)])
        for cog in cogs:
            self.load_extension(f"cogs.{cog}")
        try:
            # login and connect to bot.
            self.loop.run_until_complete(self.run(t_keys.prod_bot_token if not DEV_MODE else t_keys.dev_bot_token))

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
