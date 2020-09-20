from module.keys import client, trash_emoji, check_emoji, dead_image_channel_id, patreon_super_role_id, patreon_role_id
from module import logger as log
import discord
from Utility import resources as ex
from discord.ext import commands
import time


class Events(commands.Cog):
    @staticmethod
    async def process_on_message(message):
        try:
            # fetching temporary channels that have delays for removed messages.
            temp_channels = await ex.get_temp_channels()
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
                            checker = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.Counter WHERE UserID = $1::bigint", author_id))
                            if checker > 0:
                                current_count = ex.first_result(await ex.conn.fetchrow("SELECT NWord FROM currency.Counter WHERE UserID = $1::bigint", author_id))
                                current_count += 1
                                await ex.conn.execute("UPDATE currency.Counter SET NWord = $1 WHERE UserID = $2::bigint", current_count, author_id)
                            if checker == 0:
                                await ex.conn.execute("INSERT INTO currency.Counter VALUES ($1,$2)", author_id, 1)
                if ex.check_message_not_empty(message):
                    if len(message_content) >= len(current_server_prefix):
                        bot_prefix = await client.get_prefix(message)
                        default_prefix = bot_prefix + 'setprefix'
                        if message.content[0:len(current_server_prefix)].lower() == current_server_prefix.lower() or message.content == default_prefix or message.content == (bot_prefix + 'checkprefix'):
                            message.content = message.content.replace(current_server_prefix, await client.get_prefix(message))
                            if await ex.check_if_bot_banned(message_sender.id):
                                if ex.check_message_is_command(message):
                                    await ex.send_ban_message(message_channel)
                            else:
                                await client.process_commands(message)
        except Exception as e:
            log.console(e)

    @staticmethod
    async def error(ctx, error):
        embed = discord.Embed(title="Error", description=f"** {error} **", color=0xff00f6)
        await ctx.send(embed=embed)
        log.console(f"{error}")

    @staticmethod
    @client.event
    async def on_ready():
        app = await client.application_info()
        log.console(f'{app.name} is online')
        # Create Cache
        # It is fine to create cache in on_ready because the cache is correlated with the DB
        # and is constantly updated.
        past_time = time.time()
        await ex.create_cache()
        log.console(f"Cache Created in {await ex.get_cooldown_time(time.time() - past_time)}.")

    @staticmethod
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, commands.errors.CommandInvokeError):
            log.console(f"Command Invoke Error -- {error}")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Error", description=f"""** You are on cooldown. Try again in 
                    {await ex.get_cooldown_time(error.retry_after)}.**""", color=0xff00f6)
            await ctx.send(embed=embed)
            log.console(f"{error}")
        elif isinstance(error, commands.errors.BadArgument):
            await Events.error(ctx, error)
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.errors.MissingPermissions) or isinstance(error, commands.errors.UserInputError):
            await Events.error(ctx, error)

    @staticmethod
    @client.event
    async def on_guild_join(guild):
        if guild.system_channel is not None:
            await guild.system_channel.send(f">>> Hello!\nMy prefix for this server is set to {await ex.get_server_prefix(guild.id)}.\nIf you have any questions or concerns, you may join the support server ({await ex.get_server_prefix(guild.id)}support).")
            log.console(f"{guild.name} ({guild.id}) has invited Irene.")

    @staticmethod
    @client.event
    async def on_message(message):
        await Events.process_on_message(message)

    @staticmethod
    @client.event
    async def on_message_edit(msg_before, message):
        msg_created_at = msg_before.created_at
        msg_edited_at = message.edited_at
        if msg_edited_at is not None:
            difference = msg_edited_at - msg_created_at  # datetime.timedelta
            # the message has to be edited at least 60 seconds within it's creation.
            if difference.total_seconds() > 60:
                return
        await Events.process_on_message(message)

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

    @staticmethod
    @client.event
    async def on_command_completion(ctx):
        await ex.add_command_count()

    @staticmethod
    @client.event
    async def on_guild_remove(guild):
        id = guild.id
        name = guild.name
        region = str(guild.region)
        owner_id = guild.owner.id
        member_count = guild.member_count
        try:
            await ex.conn.execute("INSERT INTO stats.leftguild (id, name, region, ownerid, membercount) VALUES($1, $2, $3, $4, $5)", id, name, region, owner_id, member_count)
        except Exception as e:
            log.console(f"{name} ({id})has already kicked Irene before. - {e}")

    @staticmethod
    @client.event
    async def on_raw_reaction_add(payload):
        """Checks if a bot mod is deleting an idol photo."""
        try:
            message_id = payload.message_id
            user_id = payload.user_id
            emoji = payload.emoji
            channel_id = payload.channel_id
            guild_id = payload.guild_id

            async def get_msg_and_image():
                """Gets the message ID if it matches with the reaction."""
                try:
                    if channel_id == dead_image_channel_id:
                        channel = await ex.client.fetch_channel(dead_image_channel_id)
                        msg = await channel.fetch_message(message_id)
                        for record in await ex.get_dead_links():
                            image_link = await ex.get_google_drive_link(record[0])
                            msg_id = record[1]
                            idol_id = record[2]
                            if message_id == msg_id:
                                return msg, image_link, idol_id
                except Exception as e:
                    log.console(e)
                return None, None, None

            if ex.check_if_mod(user_id, mode=1):
                if str(emoji) == trash_emoji:
                    msg, link, idol_id = await get_msg_and_image()
                    if link is not None:
                        await ex.conn.execute("DELETE FROM groupmembers.imagelinks WHERE link = $1 AND memberid = $2",
                                              link, idol_id)
                        await ex.delete_dead_link(link, idol_id)
                        await ex.set_forbidden_link(link, idol_id)
                        await msg.delete()

                elif str(emoji) == check_emoji:
                    msg, link, idol_id = await get_msg_and_image()
                    if link is not None:
                        await ex.delete_dead_link(link, idol_id)
                        await msg.delete()

        except Exception as e:
            log.console(e)

    @staticmethod
    @client.event
    async def on_member_update(member_before, member_after):
        if not member_before.bot:
            before_roles = member_before.roles
            after_roles = member_after.roles
            added_roles = (list(set(after_roles) - set(before_roles)))
            removed_roles = (list(set(before_roles) - set(after_roles)))
            # if the user received the patron or super patron role, update cache
            if len(added_roles) != 0:
                for role in added_roles:
                    if role.id == patreon_super_role_id:
                        ex.cache.patrons[member_after.id] = True
                    if role.id == patreon_role_id:
                        ex.cache.patrons[member_after.id] = False
            # if the user was removed from patron or super patron role, update cache
            after_role_ids = [after_role.id for after_role in after_roles]
            if len(removed_roles) != 0:
                # only update if there were removed roles
                if patreon_super_role_id in after_role_ids:
                    ex.cache.patrons[member_after.id] = True
                elif patreon_role_id in after_role_ids:
                    ex.cache.patrons[member_after.id] = False
                else:
                    ex.cache.patrons.pop(member_after.id, None)



