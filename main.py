import asyncio
import tracemalloc

import disnake
from disnake.ext import commands
from keys import get_keys
from models import Bot

DEV_MODE = True


if __name__ == "__main__":
    tracemalloc.start()
    intents = disnake.Intents.default()
    intents.members = True  # turn on privileged members intent
    intents.messages = True
    intents.message_content = True
    # intents.presences = True  # turn on presences intent
    t_keys = get_keys()

    options = {
        "case_insensitive": True,
        "owner_id": t_keys.bot_owner_id,
        "intents": intents,
        "test_guilds": None if not DEV_MODE else [t_keys.support_server_id],
        "command_sync_flags": commands.CommandSyncFlags.all(),
    }
    loop = asyncio.get_event_loop()

    bot = Bot(t_keys.bot_prefix, t_keys, dev_mode=DEV_MODE, **options)

    try:
        loop.run_until_complete(bot.run_api_before_bot())
    except KeyboardInterrupt:
        # cancel all tasks lingering.
        loop.run_until_complete(bot.close())
        # disconnect from the api.
        loop.run_until_complete(bot.api.disconnect())
    finally:
        tracemalloc.stop()
        ...  # we want the API to finish everything in the queue before closing the loop.
        # loop.close()
