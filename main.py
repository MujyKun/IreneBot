import disnake
from disnake.ext import commands
from disnake.ext.commands import AutoShardedBot, errors
from keys import Keys
from cogs import cogs
from datetime import datetime
import traceback

DEV_MODE = True


class Bot(AutoShardedBot):
    def __init__(self, bot_prefix, keys, **settings):
        super(Bot, self).__init__(bot_prefix, **settings)
        self.keys = keys
        for cog in cogs:
            self.load_extension(f"cogs.{cog}")

        self.run(self.keys.prod_bot_token if not DEV_MODE else self.keys.dev_bot_token)

    async def on_ready(self):
        print(f"{self.keys.bot_name} is now ready at {datetime.now()}.\n"
              f"{self.keys.bot_name} is now active in test guild {t_keys.support_server_id}.")

    async def on_slash_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        # TODO: Remove later when done with bot and debugging

        def fancy_traceback(exc: Exception) -> str:
            """May not fit the message content limit"""
            text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            return f"```py\n{text[-4086:]}\n```"

        embed = disnake.Embed(
            title=f"Slash command `{inter.data.name}` failed due to `{error}`",
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response._responded:
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)

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
    intents = disnake.Intents.default()
    intents.members = True  # turn on privileged members intent
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
