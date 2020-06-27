from module import Currency, Twitter2, DreamCatcher, BlackJack, Miscellaneous, keys, Cogs, Youtube, Games, GroupMembers, Archive, Moderator, logger as log, Profile, BotSites, Help, Logging, status, Music, BotMod
from discord.ext import commands
from Utility import get_cooldown_time, fetch_one, fetch_all, DBconn, c, check_message_not_empty, get_server_prefix, delete_all_games, check_if_mod, check_nword, check_if_bot_banned
import discord
import threading
from module.keys import client, bot_support_server_link


def irene_bot():
    # events
    @client.event
    async def on_ready():
        log.console('Irene is online')

    @client.event
    async def on_guild_join(guild):
        if guild.system_channel is not None:
            await guild.system_channel.send(f">>> Hello!\nMy prefix for this server is set to {await get_server_prefix(guild.id)}.\nIf you have any questions or concerns, you may join the support server ({await get_server_prefix(guild.id)}support).")
            log.console(f"{guild.name} ({guild.id}) has invited Irene.")

    @client.event
    async def on_message(message):
        try:
            # fetching temporary channels that have delays for removed messages.
            c.execute("SELECT chanID, delay FROM currency.TempChannels")
            temp_channels = fetch_all()
            message_sender = message.author
            message_content = message.clean_content
            message_channel = message.channel
            try:
                current_server_prefix = await get_server_prefix(message.guild.id)
            except Exception as e:
                current_server_prefix = await client.get_prefix(message)
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
                        if check_nword(message_content):
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
                if check_message_not_empty(message):
                    if len(message_content) >= len(current_server_prefix):
                        bot_prefix = await client.get_prefix(message)
                        default_prefix = bot_prefix + 'setprefix'
                        if message.content[0:len(current_server_prefix)].lower() == current_server_prefix or message.content == default_prefix or message.content == (bot_prefix + 'checkprefix'):
                            message.content = message.content.replace(current_server_prefix, await client.get_prefix(message))
                            if not check_if_mod(message.author.id, 1):
                                log.console(f"CMD LOG: ChannelID = {message_channel.id} - {message_sender} ({message.author.id})|| {message_content} ")
                            else:
                                log.console(f"MOD LOG: ChannelID = {message_channel.id} - {message_sender} ({message.author.id})|| {message_content} ")
                            if not await check_if_bot_banned(message_sender.id):
                                await client.process_commands(message)
                            else:
                                await message_channel.send(f"> **You are banned from using Irene. Join {bot_support_server_link}**")
        except Exception as e:
            log.console(e)
            DBconn.rollback()

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
    DreamCatcher.DcApp().new_task4.start()
    # Start Automatic Youtube Scrape Loop
    Youtube.YoutubeLoop().new_task5.start()
    # Start Status Change Loop
    status.Status().change_bot_status_loop.start()

    # Start Checking Voice Clients
    Music.Music().check_voice_clients.start()

    # Delete all active blackjack games
    delete_all_games()

    client.add_cog(Miscellaneous.Miscellaneous())
    client.add_cog(Twitter2.Twitter())
    client.add_cog(Currency.Currency())
    client.add_cog(DreamCatcher.DreamCatcher())
    client.add_cog(BlackJack.BlackJack())
    client.add_cog(Cogs.Cogs())
    client.add_cog(Youtube.Youtube())
    client.add_cog(Games.Games())
    client.add_cog(GroupMembers.GroupMembers())
    client.add_cog(Archive.Archive())
    client.add_cog(BotSites.BotSites())
    client.add_cog(Moderator.Moderator())
    client.add_cog(Profile.Profile())
    client.add_cog(Help.Help())
    client.add_cog(Logging.Logging())
    client.add_cog(Music.Music())
    client.add_cog(BotMod.BotMod())
    # start logging console and file
    # For INFO Logging
    log.info()
    # For Debugging
    # log.debug()
    # run bot
    client.run(keys.client_token)


# Threads created in case needed for future
t1 = threading.Thread(target=irene_bot)
t1.start()