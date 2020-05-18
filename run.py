from module import Currency, Twitter2, DreamCatcher, BlackJack, Miscellaneous, keys, Cogs, Youtube, Games, GroupMembers, Archive, Moderator, logger as log, Profile, TopGG, Help, Logging
from discord.ext import commands
from Utility import get_cooldown_time, fetch_one, fetch_all, DBconn, c, check_embed_exists, check_message_not_empty, get_message_prefix, check_logging_requirements, get_attachments, get_log_channel_id
import discord
import threading

client = commands.Bot(command_prefix='%', case_insensitive=True)
first_run = True


def IreneBot():
    # events
    @client.event
    async def on_ready():
        global first_run
        if first_run:
            await client.change_presence(status=discord.Status.online, activity=discord.Game("%help"))
        log.console('Irene is online')
        first_run = False

    @client.event
    async def on_guild_join(guild):
        if guild.system_channel is not None:
            await guild.system_channel.send(f">>> Hello!\nMy prefix for this server is set to `%`.\nIf you have any questions or concerns, you may join the support server (%support).")

    @client.event
    async def on_message(message):
        try:
            # fetching temporary channels that have delays for removed messages.
            c.execute("SELECT chanID, delay FROM currency.TempChannels")
            temp_channels = fetch_all()
            message_sender = message.author
            message_content = message.clean_content
            message_channel = message.channel
            # check if messages are in a temporary channel
            for temp in temp_channels:
                chan_id = temp[0]
                delay = temp[1]
                if message_channel.id == chan_id:
                    await message.delete(delay=delay)
            if check_message_not_empty(message):
                # check if the message belongs to the bot
                if message_sender.id != client.user.id:
                    if message_content[0] != '%':
                        # it had to be written somewhere :( and I'm not about to pull it from a table
                        if 'nigga' in message_content.lower() or 'nigger' in message_content.lower() and ':' not in message_content.lower():
                            author_id = message_sender.id
                            # checks how many instances ( should logically only be 0 or 1 )
                            c.execute("SELECT COUNT(*) FROM currency.Counter WHERE UserID = %s::bigint", (author_id,))
                            checker = fetch_one()
                            if checker > 0:
                                c.execute("SELECT NWord FROM currency.Counter WHERE UserID = %s::bigint", (author_id,))
                                current_count = fetch_one()
                                current_count += 1
                                c.execute("UPDATE currency.Counter SET NWord = %s WHERE UserID = %s::bigint", (current_count, author_id))
                            if checker == 0:
                                c.execute("INSERT INTO currency.Counter VALUES (%s,%s)", (author_id, 1))
                            DBconn.commit()
                if get_message_prefix(message) == '%':
                    log.console(f"CMD LOG: ChannelID = {message_channel.id} - {message_sender} || {message_content} ")
                await client.process_commands(message)
        except Exception as e:
            log.console(e)
            DBconn.rollback()

    @client.event
    async def on_message_edit(msg_before, message):
        try:
            if await check_logging_requirements(message):
                logging_channel = await get_log_channel_id(message, client)
                files = await get_attachments(message)
                embed_message = f"**{message.author} ({message.author.id})\nOld Message: **{msg_before.content}**\nNew Message: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}\n<{message.jump_url}>**"
                embed = discord.Embed(title="Message Edited", description=embed_message, color=0x00ff00)
                await logging_channel.send(embed=embed, files=files)
        except Exception as e:
            log.console(f"ON_MESSAGE_EDIT ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")

    @client.event
    async def on_message_delete(message):
        try:
            if await check_logging_requirements(message):
                logging_channel = await get_log_channel_id(message, client)
                files = await get_attachments(message)
                embed_message = f"**{message.author} ({message.author.id})\nMessage: **{message.content}**\nFrom {message.guild} in {message.channel}\nCreated at {message.created_at}**"
                embed = discord.Embed(title="Message Deleted", description=embed_message, color=0xff0000)
                await logging_channel.send(embed=embed, files=files)
        except Exception as e:
            log.console(f"ON_MESSAGE_DELETE ERROR: {e} Server ID: {message.guild.id} Channel ID: {message.channel.id}")

    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, commands.errors.CommandInvokeError):
            log.console(f"Command Invoke Error -- {error}")
            pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Error", description=f"** You are on cooldown. Try again in {await get_cooldown_time(error.retry_after)}.**", color=0xff00f6)
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


    # Start Automatic DC Loop
    DreamCatcher.DCAPP(client).new_task4.start()
    # Start Automatic Youtube Scrape Loop
    Youtube.YoutubeLoop().new_task5.start()

    client.add_cog(Miscellaneous.Miscellaneous(client))
    client.add_cog(Twitter2.Twitter(client))
    client.add_cog(Currency.Currency(client))
    client.add_cog(DreamCatcher.DreamCatcher(client))
    client.add_cog(BlackJack.BlackJack(client))
    client.add_cog(Cogs.Cogs(client))
    client.add_cog(Youtube.Youtube(client))
    client.add_cog(Games.Games(client))
    client.add_cog(GroupMembers.GroupMembers(client))
    client.add_cog(Archive.Archive(client))
    client.add_cog(TopGG.TopGG(client))
    client.add_cog(Moderator.Moderator(client))
    client.add_cog(Profile.Profile(client))
    client.add_cog(Help.Help(client))
    client.add_cog(Logging.Logging(client))
    # client.add_cog(Help.Help(client))
    # start logging console and file
    # For INFO Logging
    log.info()
    # For Debugging
    # log.debug()
    # run bot
    client.run(keys.client_token)


# Threads created in case needed for future
t1 = threading.Thread(target=IreneBot)
t1.start()