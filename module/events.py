from module.keys import client, bot_support_server_link
from module import logger as log
import discord
from Utility import resources as ex
from discord.ext import commands


class Events(commands.Cog):
    @staticmethod
    @client.event
    async def on_ready():
        log.console('Irene is online')

    @staticmethod
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, commands.errors.CommandInvokeError):
            log.console(f"Command Invoke Error -- {error}")
            pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Error", description=f"""** You are on cooldown. Try again in 
                    {await ex.get_cooldown_time(error.retry_after)}.**""", color=0xff00f6)
            await ctx.send(embed=embed)
            log.console(f"{error}")
            pass
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="Error", description=f"** {error} **", color=0xff00f6)
            await ctx.send(embed=embed)
            log.console(f"{error}")
            ctx.command.reset_cooldown(ctx)
            pass
        elif isinstance(error, commands.errors.MissingPermissions):
            embed = discord.Embed(title="Error", description=f"** {error} **", color=0xff00f6)
            await ctx.send(embed=embed)
            log.console(f"{error}")
            pass

    @staticmethod
    @client.event
    async def on_guild_join(guild):
        if guild.system_channel is not None:
            await guild.system_channel.send(f""">>> Hello!\nMy prefix for this server is set to
                    {await ex.get_server_prefix(guild.id)}.\nIf you have any questions or concerns,
                    you may join the support server ({await ex.get_server_prefix(guild.id)}support).""")
            log.console(f"{guild.name} ({guild.id}) has invited Irene.")

    @staticmethod
    @client.event
    async def on_message(message):
        try:
            # fetching temporary channels that have delays for removed messages.
            ex.c.execute("SELECT chanID, delay FROM currency.TempChannels")
            temp_channels = ex.fetch_all()
            message_sender = message.author
            message_content = message.clean_content
            message_channel = message.channel
            try:
                current_server_prefix = await ex.get_server_prefix(message.guild.id)
            except Exception as e:
                current_server_prefix = await client.get_prefix(message)
            # check if messages are in a temporary channel
            for temp in temp_channels:
                chan_id = temp[0]
                delay = temp[1]
                if message_channel.id == chan_id:
                    await message.delete(delay=delay)
            if ex.check_message_not_empty(message):
                # check if the message belongs to the bot
                if message_sender.id != client.user.id:
                    if message_content[0] != '%':
                        if ex.check_nword(message_content):
                            author_id = message_sender.id
                            # checks how many instances ( should logically only be 0 or 1 )
                            ex.c.execute("SELECT COUNT(*) FROM currency.Counter WHERE UserID = %s::bigint", (author_id,))
                            checker = ex.fetch_one()
                            if checker > 0:
                                ex.c.execute("SELECT NWord FROM currency.Counter WHERE UserID = %s::bigint", (author_id,))
                                current_count = ex.fetch_one()
                                current_count += 1
                                ex.c.execute("UPDATE currency.Counter SET NWord = %s WHERE UserID = %s::bigint", (current_count, author_id))
                            if checker == 0:
                                ex.c.execute("INSERT INTO currency.Counter VALUES (%s,%s)", (author_id, 1))
                            ex.DBconn.commit()
                if ex.check_message_not_empty(message):
                    if len(message_content) >= len(current_server_prefix):
                        bot_prefix = await client.get_prefix(message)
                        default_prefix = bot_prefix + 'setprefix'
                        if message.content[0:len(current_server_prefix)].lower() == current_server_prefix or message.content == default_prefix or message.content == (bot_prefix + 'checkprefix'):
                            message.content = message.content.replace(current_server_prefix, await client.get_prefix(message))
                            if await ex.check_if_bot_banned(message_sender.id):
                                if ex.check_message_is_command(message):
                                    await ex.send_ban_message(message_channel)
                            else:
                                await client.process_commands(message)
        except Exception as e:
            log.console(e)
            ex.DBconn.rollback()

    @staticmethod
    @client.event
    async def on_command(ctx):
        msg_content = ctx.message.clean_content
        if not ex.check_if_mod(ctx.author.id, 1):
            log.console(
                f"CMD LOG: ChannelID = {ctx.channel.id} - {ctx.author} ({ctx.author.id})|| {msg_content} ")
        else:
            log.console(
                f"MOD LOG: ChannelID = {ctx.channel.id} - {ctx.author} ({ctx.author.id})|| {msg_content} ")
        if await ex.check_if_bot_banned(ctx.author.id):
            ex.send_ban_message(ctx.channel)
