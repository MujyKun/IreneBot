import asyncpg
from pypapago import Translator
from discord.ext import commands
import discord
import discordboats
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
import ksoftapi


def make_int(var):
    # noinspection PyBroadException,PyPep8
    try:
        return int(var)
    except:
        return None


load_dotenv()  # Adds .env to memory
# DISCORD
# client token ( to run )
client_token = os.getenv("LIVE_BOT_TOKEN")
test_client_token = os.getenv("TEST_BOT_TOKEN")

bot_name = None  # this is set in the on_ready event
bot_id = make_int(os.getenv("BOT_ID"))
owner_id = make_int(os.getenv("OWNER_ID"))
# noinspection PyBroadException
try:
    mods_list_split = (os.getenv("MODS_LIST")).split(',')
except Exception as e:
    mods_list_split = None

mods_list = []
for mod in mods_list_split:
    mods_list.append(int(mod))
bot_invite_link = os.getenv("BOT_INVITE_LINK")
bot_support_server_id = make_int(os.getenv("SUPPORT_SERVER_ID"))
bot_support_server_link = os.getenv("SUPPORT_SERVER_LINK")
bot_prefix = os.getenv("BOT_PREFIX")
bot_website = os.getenv("BOT_WEBSITE") or "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
dc_app_test_channel_id = make_int(os.getenv("DC_APP_TEST_CHANNEL_ID"))
report_channel_id = make_int(os.getenv("REPORT_CHANNEL_ID"))
suggest_channel_id = make_int(os.getenv("SUGGEST_CHANNEL_ID"))
dead_image_channel_id = make_int(os.getenv("DEAD_IMAGE_CHANNEL_ID"))
add_idol_channel_id = make_int(os.getenv("ADD_IDOL_CHANNEL_ID"))
add_group_channel_id = make_int(os.getenv("ADD_GROUP_CHANNEL_ID"))
idol_post_send_limit = make_int(os.getenv("IDOL_POST_LIMIT"))
# the amount normal users can use if the guild owner is a super patron.
owner_super_patron_benefit = idol_post_send_limit * 2
idol_no_vote_send_limit = make_int(os.getenv("IDOL_NO_VOTE_LIMIT"))  # amount of votes that can be sent without voting.
reminder_limit = make_int(os.getenv("REMINDER_LIMIT"))
currency_name = os.getenv("CURRENCY_NAME")
icon_url = os.getenv("ICON_URL")
footer_url = os.getenv("FOOTER_URL")


try:
    n_word_list = (os.getenv("NWORD_LIST")).split(',')
except Exception:
    n_word_list = []

interaction_list = [
    'slap',
    'kiss',
    'lick',
    'hug',
    'punch',
    'spit',
    'pat',
    'cuddle',
    'pullhair',
    'choke',
    'stepon',
    'stab'
]

# client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, owner_id=owner_id)
intents = discord.Intents.default()
intents.members = True  # turn on privileged members intent
# intents.presences = True  # turn on presences intent
client = commands.AutoShardedBot(command_prefix=bot_prefix, case_insensitive=True, owner_id=owner_id, intents=intents)

# Reactions/Emotes


def get_emoji(string):
    if len(string) != 0:
        if string[0] == "<":
            return string
        else:
            string = chr(int(string, 16))
    return string


trash_emoji = get_emoji(os.getenv("TRASH_EMOJI"))
check_emoji = get_emoji(os.getenv("CHECK_MARK_EMOJI"))
reload_emoji = get_emoji(os.getenv("RELOAD_IMAGE_EMOJI"))
dead_emoji = get_emoji(os.getenv("DEAD_LINK_EMOJI"))
previous_emoji = get_emoji(os.getenv("PREVIOUS_EMOJI"))
next_emoji = get_emoji(os.getenv("NEXT_EMOJI"))


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

# this is set in run.py (ONLY ON THE LIVE/PRODUCTION BOT)
top_gg = None


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

db_conn: asyncpg.pool.Pool = None  # to be directly imported from files without access to the Utility object.


async def connect_to_db():
    """Create a pool to the postgres database using asyncpg"""
    # pool is not being used as recommended, however, since we do not deal with millions of requests a second,
    # the current usage is fine. connections from the pool are also not released after completion and we let asyncpg
    # release the inactive connection once it recognizes it is inactive.
    # instead of acquiring a connection from the pool, we just let the pool select a connection for us and
    # execute directly that way. this limits the amount of methods we have access to,
    # but in the case those methods are needed, just acquire the connection and use that instead.
    global db_conn
    db_conn = await asyncpg.create_pool(**postgres_options, command_timeout=60)
    return db_conn

# papago translation keys - not needed - https://developers.naver.com/docs/papago/
papago_client_id = os.getenv("PAPAGO_CLIENT_ID")
papago_client_secret = os.getenv("PAPAGO_CLIENT_SECRET")
translator = Translator()

# LastFM
last_fm_api_key = os.getenv("LAST_API_KEY")
last_fm_shared_secret = os.getenv("LAST_SHARED_SECRET")
last_fm_root_url = os.getenv("LAST_ROOT_URL")
last_fm_headers = {
    'user-agent': os.getenv("LAST_USER_AGENT")
}

# Patreon
patreon_link = os.getenv("PATREON_LINK")
patreon_role_id = make_int(os.getenv("PATREON_ROLE_ID"))
patreon_super_role_id = make_int(os.getenv("PATREON_SUPER_ROLE_ID"))

# startup time
startup_time = datetime.now()

# Aiohttp Client Session
client_session = aiohttp.ClientSession()

# Wolfram
wolfram_app_id = os.getenv("WOLFRAM_APP_ID")

# Song Lyrics Client
lyrics_api_key = os.getenv("LYRICS_API_KEY")
if len(lyrics_api_key) != 0:
    lyric_client = ksoftapi.Client(lyrics_api_key)
else:
    lyric_client = None


# Idol Avatar Location
idol_avatar_location = os.getenv("IDOL_AVATAR_LOCATION")

# Idol Banner Location
idol_banner_location = os.getenv("IDOL_BANNER_LOCATION")

# Bias Game Folder Location
bias_game_location = os.getenv("BIAS_GAME_LOCATION")

# Weverse
weverse_auth_token = os.getenv("WEVERSE_AUTH")
weverse_image_folder = os.getenv("WEVERSE_IMAGE_FOLDER")

# Twitch
twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")

# Datadog
datadog_api_key = make_int(os.getenv("DATADOG_API_KEY"))
datadog_app_key = make_int(os.getenv("DATADOG_APP_KEY"))

# API
api_port = os.getenv("API_PORT")
# translate private key is the same as the idol photo key.
translate_private_key = ((os.getenv("PRIVATE_KEYS")).split(','))[0]  # use the first result in the list of keys.

# Site

site_port = os.getenv("SITE_PORT")
