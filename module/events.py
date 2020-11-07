from module.keys import client, trash_emoji, check_emoji, dead_image_channel_id, patreon_super_role_id, patreon_role_id, next_emoji, bot_name
from module import logger as log
from Utility import resources as ex
from discord.ext import commands
import discord
import asyncio


class Events(commands.Cog):
    @staticmethod
    async def process_on_message(message):
        try:
            # delete messages that are in temp channels
            await ex.delete_temp_messages(message)
            # check for the n word
            await ex.check_for_nword(message)
            # process the commands with their prefixes.
            await ex.process_commands(message)
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
        global bot_name
        bot_name = app.name
        log.console(f'{app.name} is online')
        ex.discord_cache_loaded = True

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
        try:
            if guild.system_channel is not None:
                await guild.system_channel.send(f">>> Hello!\nMy prefix for this server is set to {await ex.get_server_prefix(guild.id)}.\nIf you have any questions or concerns, you may join the support server ({await ex.get_server_prefix(guild.id)}support).")
        except Exception as e:
            pass
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
        await ex.add_command_count(ctx.command.name)
        await ex.add_session_count()

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
                        channel = ex.cache.dead_image_channel
                        msg = await channel.fetch_message(message_id)
                        msg_info = ex.cache.dead_image_cache.get(message_id)
                        if msg_info:
                            dead_link = msg_info[0]
                            member_id = msg_info[2]
                            guessing_game = msg_info[3]
                            image_link = await ex.get_google_drive_link(dead_link)
                            return msg, image_link, member_id, guessing_game
                except Exception as e:
                    log.console(e)
                return None, None, None, None

            if ex.check_if_mod(user_id, mode=1):
                if str(emoji) == trash_emoji:
                    msg, link, idol_id, is_guessing_game = await get_msg_and_image()
                    if link is not None:
                        await ex.conn.execute("DELETE FROM groupmembers.imagelinks WHERE link = $1 AND memberid = $2",
                                              link, idol_id)
                        await ex.delete_dead_link(link, idol_id)
                        await ex.set_forbidden_link(link, idol_id)
                        await msg.delete()

                elif str(emoji) == check_emoji:
                    msg, link, idol_id, is_guessing_game = await get_msg_and_image()
                    if link is not None:
                        await ex.delete_dead_link(link, idol_id)
                        await msg.delete()

                elif str(emoji) == '➡':
                    msg, link, idol_id, is_guessing_game = await get_msg_and_image()
                    if link is not None:
                        await ex.set_as_group_photo(link)
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

    @staticmethod
    @client.event
    async def on_member_join(member):
        guild = member.guild
        server = ex.cache.welcome_messages.get(guild.id)
        if server is not None:
            if server.get('enabled'):
                channel = guild.get_channel(server.get('channel_id'))
                if channel is not None:
                    message = server.get("message")
                    message = message.replace("%user", f"<@{member.id}>")
                    message = message.replace("%guild_name", guild.name)
                    await channel.send(message)

    @staticmethod
    @client.check
    async def check_maintenance(ctx):
        """Return true if the user is a mod. If a maintenance is going on, return false for normal users."""
        try:
            check = not ex.cache.maintenance_mode or ex.check_if_mod(ctx) or ctx.author.bot
            if not check:
                await ex.send_maintenance_message(ctx)
            return check
        except Exception as e:
            log.console(f"{e} - Check Maintenance")
            return False



