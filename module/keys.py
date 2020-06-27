import psycopg2
from pypapago import Translator
from discord.ext import commands
import dbl
import discordboats

# client token ( to run )
client_token = ""
bot_id = int  # put bot id
owner_id = int # put your account id
mods_list = [] # any bot mods
bot_invite_link = "" # link to invite bot to a server
bot_support_server_link = "" # permanent link to discord server
bot_prefix = '%'
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, owner_id=owner_id)

# Twitter Keys
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

# spotify
spotify_client_id = ''
spotify_client_secret = ''

# oxford dictionary
oxford_app_id = ''
oxford_app_key = ''

# urban dictionary
X_RapidAPI_headers = {
    'x-rapidapi-host': "",
    'x-rapidapi-key': ""
    }


# tenor api key
tenor_key = ""


# top.gg api
top_gg_key = ""
top_gg = dbl.DBLClient(client, top_gg_key, autopost=True)


# discord.boats api


discord_boats_key = ""
discord_boats = discordboats.Client(discord_boats_key, loop=client.loop)



# postgresql db connection
# PLEASE NOTE THIS CONNECTION IS NOT ASYNC 
# THIS WILL BE CHANGED IN THE FUTURE (probably).
DBconn = psycopg2.connect(host="", database="", user="", password="")


# papago translation keys - not needed
papago_client_id = ""
papago_client_secret = ""
translator = Translator()

