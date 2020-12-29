import discord
from discord.ext import commands
from module import logger as log
from Utility import resources as ex


# noinspection PyPep8
class Logging(commands.Cog):
    @staticmethod
    async def on_message_log(message):
        if await ex.u_logging.check_logging_requirements(message):
            try:
                if await ex.u_logging.get_send_all(message.guild.id):
                    logging_channel = await ex.u_logging.get_log_channel_id(message)
                    files = await ex.u_logging.get_attachments(message)
                    embed_message = f"**{message.author} ({message.author.id})\nMessage: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}\n<{message.jump_url}>**"
                    embed = discord.Embed(title="Message Sent", description=embed_message, color=0xffffff)
                    await logging_channel.send(embed=embed, files=files)
            except Exception as e:
                log.console(f"ON_MESSAGE_LOG ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def startlogging(self, ctx):
        """Start sending log messages in the current server and channel."""
        if await ex.u_logging.check_if_logged(server_id=ctx.guild.id):
            await ctx.send(f"> **This server is already being logged.**")
        else:
            await ex.u_logging.add_to_logging(ctx.guild.id, ctx.channel.id)
            await ctx.send("> **This server is now being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def logadd(self, ctx, text_channel: discord.TextChannel = None):
        """Start logging a text channel. [Format:  %logadd #text-channel]"""
        if not text_channel:
            text_channel = ctx.channel

        if not await ex.u_logging.check_if_logged(server_id=ctx.guild.id):
            return await ctx.send(
                f"> **The server must be logged in order to log a channel. ({await ex.get_server_prefix_by_context(ctx)}startlogging)**")
        if await ex.u_logging.check_if_logged(channel_id=text_channel.id):
            return await ctx.send(f"> **{text_channel.name} is already being logged.**")

        is_logging_channel = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM logging.servers WHERE channelid = $1", text_channel.id))
        if is_logging_channel:
            return await ctx.send(f"> **{text_channel.name} can not be logged since log messages are sent here.**")
        logging_id = await ex.u_logging.get_logging_id(ctx.guild.id)
        await ex.conn.execute("INSERT INTO logging.channels (channelid, server) VALUES($1, $2)", text_channel.id, logging_id)
        ex.cache.list_of_logged_channels.append(text_channel.id)
        await ctx.send(f"> **{text_channel.name} is now being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def logremove(self, ctx, text_channel: discord.TextChannel = None):
        """Stop logging a text channel. [Format: %logremove #text-channel]"""
        if not text_channel:
            text_channel = ctx.channel
        if await ex.u_logging.check_if_logged(channel_id=text_channel.id):
            await ex.conn.execute("DELETE FROM logging.channels WHERE channelid = $1", text_channel.id)
            ex.cache.list_of_logged_channels.remove(text_channel.id)
            await ctx.send(f"> **{text_channel.name} is no longer being logged.**")
        else:
            await ctx.send(f"> **{text_channel.name} is not being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def stoplogging(self, ctx):
        """Stop sending log messages in the current server."""
        if await ex.u_logging.check_if_logged(server_id=ctx.guild.id):
            await ex.u_logging.set_logging_status(ctx.guild.id, 0)
            await ctx.send(f"> **This server is no longer being logged.**")
        else:
            await ctx.send(f"> **This server is not being logged.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def sendall(self, ctx):
        """Toggles sending all messages to log channel. If turned off, it only sends edited & deleted messages."""
        if not await ex.u_logging.check_if_logged(server_id=ctx.guild.id):
            return await ctx.send("> **This server is not being logged.**")
        if not await ex.u_logging.get_send_all(ctx.guild.id):
            await ex.conn.execute("UPDATE logging.servers SET sendall = $1 WHERE serverid = $2", 1, ctx.guild.id)
            (ex.cache.logged_channels[ctx.guild.id])['send_all'] = 1
            return await ctx.send(f"> **All messages will now be sent in the logging channel.**")

        await ex.conn.execute("UPDATE logging.servers SET sendall = $1 WHERE serverid = $2", 0, ctx.guild.id)
        (ex.cache.logged_channels[ctx.guild.id])['send_all'] = 0
        await ctx.send(f"> **Only edited and deleted messages will be sent in the logging channel.**")

    @staticmethod
    async def logging_on_message_edit(msg_before, message):
        try:
            if await ex.u_logging.check_logging_requirements(message):
                logging_channel = await ex.u_logging.get_log_channel_id(message)
                files = await ex.u_logging.get_attachments(message)
                embed_message = f"**{message.author} ({message.author.id})\nOld Message: **{msg_before.content}**\nNew Message: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}\n<{message.jump_url}>**"
                embed = discord.Embed(title="Message Edited", description=embed_message, color=0x00ff00)
                await logging_channel.send(embed=embed, files=files)
        except Exception as e:
            log.console(f"ON_MESSAGE_EDIT ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")

    @staticmethod
    async def logging_on_message_delete(message):
        try:
            if await ex.u_logging.check_logging_requirements(message):
                logging_channel = await ex.u_logging.get_log_channel_id(message)
                files = await ex.u_logging.get_attachments(message)
                embed_message = f"**{message.author} ({message.author.id})\nMessage: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}**"
                embed = discord.Embed(title="Message Deleted", description=embed_message, color=0xff0000)
                await logging_channel.send(embed=embed, files=files)
        except Exception as e:
            log.console(f"ON_MESSAGE_DELETE ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")
