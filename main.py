import asyncio
import disnake
from keys import Keys
from models import Bot
DEV_MODE = True


if __name__ == '__main__':
    intents = disnake.Intents.default()
    intents.members = True  # turn on privileged members intent
    intents.messages = True
    intents.message_content = True
    # intents.presences = True  # turn on presences intent
    t_keys = Keys()

    options = {
        "case_insensitive": True,
        "owner_id": t_keys.bot_owner_id,
        "intents": intents,
        "test_guilds": [t_keys.support_server_id],
        "sync_commands_debug": True
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
        ...  # we want the API to finish everything in the queue before closing the loop.
        # loop.close()


