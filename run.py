from module import Currency
from module import Twitter2
from module import ImageUploader
from module import Music
from module import DreamCatcher
from module import BlackJack
from module import Miscellaneous
from module import keys
from module import Cogs
from discord.ext import commands
import discord
import sqlite3

client = commands.Bot(command_prefix='%')
path = 'module\currency.db'
DBconn = sqlite3.connect(path)
c = DBconn.cursor()

# events
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Psycho by Red Velvet"))
    print('Irene is online')

#Change this to the id of a channel you want the logged messages to go to
logging_channel_id = 0
logging_channel_id2 = 0 

@client.event
async def on_message(message):
    try:
        private = []
        message_sender = message.author
        message_content = message.clean_content
        message_channel = message.channel
        message_guild = message.guild
        message_created = message.created_at
        message_link = message.jump_url
        if message_content[0] != '%':
            if message.author.id != client.user.id:
                logging_channel = client.get_channel(logging_channel_id)
                counter = c.execute("SELECT COUNT(*) FROM logging").fetchone()[0]
                if counter > 0:
                    channels = c.execute("SELECT channelid FROM logging").fetchall()
                    for channel in channels:
                        channel = channel[0]
                        if channel == message.channel.id:
                            await logging_channel.send(f">>> **{message_sender}\nMessage: **{message_content}**\nFrom {message_guild} in {message_channel}\nCreated at {message_created}\n<{message_link}>**")
        if message_channel.id in private:
            if message_content[0] != '%':
                if message.author.id != client.user.id:
                    logging_channel = client.get_channel(logging_channel_id2)
                    await logging_channel.send(f">>> **{message_sender}\nMessage: **{message_content}**\nFrom {message_guild} in {message_channel}\nCreated at {message_created}\n<{message_link}>**")

    except Exception as e:
        print(e)
    await client.process_commands(message)


"""
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    if isinstance(error, commands.errors.CommandInvokeError):
        print("Command Invoke Error")
        pass
"""





Miscellaneous.setup(client)
Music.setup(client)
ImageUploader.setup(client)
Twitter2.setup(client)
Currency.setup(client)
DreamCatcher.setup(client)
BlackJack.setup(client)
Cogs.setup(client)
client.run(keys.client_token)
