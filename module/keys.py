import psycopg2
from pypapago import Translator
from discord.ext import commands
import dbl
import discordboats
import json


def get_keys():
    with open('irene_credentials.json', 'r') as data:
        return json.load(data)


keys = get_keys()

# client token ( to run )
client_token = keys['discord']['liveBotToken']
test_client_token = keys['discord']['testBotToken']
bot_id = keys['discord']['botId']
owner_id = keys['discord']['ownerId']
mods_list = []
for mod in keys['discord']['modsList']:
    mods_list.append(mod['modId'])
bot_invite_link = keys['discord']['bot_invite_link']
bot_support_server_link = keys['discord']['bot_support_server_link']
bot_prefix = keys['discord']['bot_prefix']
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, owner_id=owner_id)

# Twitter Keys
CONSUMER_KEY = keys['twitter']['consumerKey']
CONSUMER_SECRET = keys['twitter']['consumerSecret']
ACCESS_KEY = keys['twitter']['accessKey']
ACCESS_SECRET = keys['twitter']['accessSecret']

# spotify
spotify_client_id = keys['spotify']['clientId']
spotify_client_secret = keys['spotify']['clientSecret']

# oxford dictionary
oxford_app_id = keys['oxford']['appId']
oxford_app_key = keys['oxford']['appKey']

# urban dictionary
X_RapidAPI_headers = {
    'x-rapidapi-host': keys['urban']['host'],
    'x-rapidapi-key': keys['urban']['key']
    }


# tenor api key
tenor_key = keys['tenor']['key']


# top.gg api
top_gg_key = keys['top_gg']['key']
top_gg = dbl.DBLClient(client, top_gg_key, autopost=True)


# discord.boats api


discord_boats_key = keys['discord_boats']['key']
discord_boats = discordboats.Client(discord_boats_key, loop=client.loop)

# postgres db connection
postgres_options = keys['postgres']
DBconn = psycopg2.connect(**postgres_options)


# papago translation keys - not needed
papago_client_id = keys['papago']['clientId']
papago_client_secret = keys['papago']['clientSecret']
translator = Translator()
