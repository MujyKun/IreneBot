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

client = commands.Bot(command_prefix='%')


# events
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Psycho by Red Velvet"))
    print('Irene is online')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    if isinstance(error, commands.errors.CommandInvokeError):
        print("Command Invoke Error")
        pass

Miscellaneous.setup(client)
Music.setup(client)
ImageUploader.setup(client)
Twitter2.setup(client)
Currency.setup(client)
DreamCatcher.setup(client)
BlackJack.setup(client)
Cogs.setup(client)
client.run(keys.client_token)
