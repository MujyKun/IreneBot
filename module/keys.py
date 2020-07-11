import asyncpg
from pypapago import Translator
from discord.ext import commands
import dbl
import discordboats
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()  # Adds .env to memory
# DISCORD
# client token ( to run )
client_token = os.getenv("LIVE_BOT_TOKEN")
test_client_token = os.getenv("TEST_BOT_TOKEN")

bot_id = int(os.getenv("BOT_ID"))
owner_id = int(os.getenv("OWNER_ID"))
mods_list_split = (os.getenv("MODS_LIST")).split(',')
mods_list = []
for mod in mods_list_split:
    mods_list.append(int(mod))
bot_invite_link = os.getenv("BOT_INVITE_LINK")
bot_support_server_link = os.getenv("SUPPORT_SERVER_LINK")
bot_prefix = os.getenv("BOT_PREFIX")

client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, owner_id=owner_id)


# Twitter Keys - https://developer.twitter.com/en/docs/basics/getting-started
twitter_account_id = os.getenv("TWITTER_ACCOUNT_ID")
twitter_username = os.getenv("TWITTER_USERNAME")
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_KEY = os.getenv("TWITTER_ACCESS_KEY")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# spotify - https://developer.spotify.com/
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# oxford dictionary - https://developer.oxforddictionaries.com/
oxford_app_id = os.getenv("OXFORD_APP_ID")
oxford_app_key = os.getenv("OXFORD_APP_KEY")

# urban dictionary - https://rapidapi.com/community/api/urban-dictionary/
X_RapidAPI_headers = {
    'x-rapidapi-host': os.getenv("URBAN_HOST"),
    'x-rapidapi-key': os.getenv("URBAN_KEY")
    }


# tenor api - https://tenor.com/gifapi/documentation
tenor_key = os.getenv("TENOR_KEY")


# top.gg api - https://top.gg/api/docs
top_gg_key = os.getenv("TOP_GG_KEY")
top_gg = dbl.DBLClient(client, top_gg_key, autopost=True)


# discord.boats api - https://docs.discord.boats/
discord_boats_key = os.getenv("DISCORD_BOATS_KEY")
discord_boats = discordboats.Client(discord_boats_key, loop=client.loop)

# postgres db connection
postgres_options = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD")
    }


async def connect_to_db():
    """Create a pool to the postgres database using asyncpg"""
    return await asyncpg.create_pool(**postgres_options, command_timeout=60)

# papago translation keys - not needed - https://developers.naver.com/docs/papago/
papago_client_id = os.getenv("PAPAGO_CLIENT_ID")
papago_client_secret = os.getenv("PAPAGO_CLIENT_SECRET")
translator = Translator()

# startup time
startup_time = datetime.now()
