import discord
from discord.ext import commands
from module.keys import client
from module import logger as log
from Utility import resources as ex


class Logging(commands.Cog):
    def __init__(self):
        client.add_listener(self.on_message_log, 'on_message')

    async def on_message_log(self, message):
        if await ex.check_logging_requirements(message):
            try:
                ex.c.execute("SELECT sendall FROM logging.servers WHERE serverid = %s", (message.guild.id,))
                if ex.fetch_one() == 1:
                    logging_channel = await ex.get_log_channel_id(message)
                    files = await ex.get_attachments(message)
                    embed_message = f"**{message.author} ({message.author.id})\nMessage: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}\n<{message.jump_url}>**"
                    embed = discord.Embed(title="Message Sent", description=embed_message, color=0xffffff)
                    await logging_channel.send(embed=embed, files=files)
            except Exception as e:
                log.console(f"ON_MESSAGE_LOG ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def startlogging(self, ctx):
        """Start sending log messages in the current server and channel."""
        if await ex.check_if_logged(server_id=ctx.guild.id):
            await ctx.send(f"> **This server is already being logged.**")
        else:
            await ex.add_to_logging(ctx.guild.id, ctx.channel.id)
            await ctx.send("> **This server is now being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def logadd(self, ctx):
        """Start logging the current text channel."""
        if await ex.check_if_logged(server_id=ctx.guild.id):
            if not await ex.check_if_logged(channel_id=ctx.channel.id):
                ex.c.execute("SELECT COUNT(*) FROM logging.servers WHERE channelid = %s", (ctx.channel.id,))
                if ex.fetch_one() == 0:
                    logging_id = await ex.get_logging_id(ctx.guild.id)
                    ex.c.execute("INSERT INTO logging.channels (channelid, server) VALUES(%s, %s)", (ctx.channel.id, logging_id))
                    ex.DBconn.commit()
                    await ctx.send(f"> **This channel is now being logged.**")
                else:
                    await ctx.send(f"> **This channel can not be logged since log messages are sent here.**")
            else:
                await ctx.send(f"> **This channel is already being logged.**")
        else:
            await ctx.send(f"> **The server must be logged in order to log a channel.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def logremove(self, ctx):
        """Stop logging the current text channel."""
        if await ex.check_if_logged(channel_id=ctx.channel.id):
            ex.c.execute("DELETE FROM logging.channels WHERE channelid = %s", (ctx.channel.id,))
            ex.DBconn.commit()
            await ctx.send("> **This channel is no longer being logged.**")
        else:
            await ctx.send(f"> **This channel is not being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def stoplogging(self, ctx):
        """Stop sending log messages in the current server."""
        if await ex.check_if_logged(server_id=ctx.guild.id):
            await ex.set_logging_status(ctx.guild.id, 0)
            await ctx.send(f"> **This server is no longer being logged.**")
        else:
            await ctx.send(f"> **This server is not being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def sendall(self, ctx):
        """Toggles sending all messages to log channel. If turned off, it only sends edited & deleted messages."""
        if await ex.check_if_logged(server_id=ctx.guild.id):
            ex.c.execute("SELECT sendall FROM logging.servers WHERE serverid = %s", (ctx.guild.id,))
            if ex.fetch_one() == 0:
                ex.c.execute("UPDATE logging.servers SET sendall = %s WHERE serverid = %s", (1, ctx.guild.id))
                await ctx.send(f"> **All messages will now be sent in the logging channel.**")
            else:
                ex.c.execute("UPDATE logging.servers SET sendall = %s WHERE serverid = %s", (0, ctx.guild.id))
                await ctx.send(f"> **Only edited and deleted messages will be sent in the logging channel.**")
        else:
            await ctx.send("> **This server is not being logged.**")


@client.event
async def on_message_edit(msg_before, message):
    try:
        if await ex.check_logging_requirements(message):
            logging_channel = await ex.get_log_channel_id(message)
            files = await ex.get_attachments(message)
            embed_message = f"**{message.author} ({message.author.id})\nOld Message: **{msg_before.content}**\nNew Message: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}\n<{message.jump_url}>**"
            embed = discord.Embed(title="Message Edited", description=embed_message, color=0x00ff00)
            await logging_channel.send(embed=embed, files=files)
    except Exception as e:
        log.console(f"ON_MESSAGE_EDIT ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")


@client.event
async def on_message_delete(message):
    try:
        if await ex.check_logging_requirements(message):
            logging_channel = await ex.get_log_channel_id(message)
            files = await ex.get_attachments(message)
            embed_message = f"**{message.author} ({message.author.id})\nMessage: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}**"
            embed = discord.Embed(title="Message Deleted", description=embed_message, color=0xff0000)
            await logging_channel.send(embed=embed, files=files)
    except Exception as e:
        log.console(f"ON_MESSAGE_DELETE ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")
