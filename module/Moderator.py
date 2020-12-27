import discord
from discord.ext import commands
from module import logger as log
from module.keys import bot_prefix, interaction_list
from Utility import resources as ex
import typing
import json
import aiohttp


# noinspection PyBroadException
class Moderator(commands.Cog):
    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def addalias(self, ctx, alias, mem_id: int, mode="idol"):
        """Add alias to an idol/group (Underscores are spaces)
        [Format: %addalias (alias) (ID of idol/group) ('idol' or 'group']"""
        alias = alias.replace("_", " ")
        if mode.lower() in ["idol", "member", "members", "idols"]:
            obj = await ex.u_group_members.get_member(mem_id)
            name = f"{obj.full_name} ({obj.stage_name}) [{obj.id}]"
        elif mode.lower() in ["group", "groups"]:
            obj = await ex.u_group_members.get_group(mem_id)
            name = f"{obj.name} [{obj.id}]"
        else:
            return await ctx.send("> Please select whether you want to add an idol or group alias.")
        if not obj:
            return await ctx.send(f"> {mem_id} is not associated with an idol or group.")
        if alias in obj.aliases:
            return await ctx.send(f"> {alias} is already a global alias for {name}.")
        if ex.check_if_mod(ctx):  # checks if the user is a bot mod.
            await ex.u_group_members.set_global_alias(obj, alias.lower())
            return await ctx.send(f"> {alias} has been added as a global alias for {mode} {mem_id}")
        else:
            server_aliases = obj.local_aliases.get(ctx.guild.id)
            if server_aliases:
                if alias.lower() in server_aliases:
                    return await ctx.send(f"> {alias} is already a server alias for {name}.")
            await ex.u_group_members.set_local_alias(obj, alias.lower(), ctx.guild.id)
            return await ctx.send(f"> {alias} has been added as a server alias for {name}.")

    @commands.command(aliases=['removealias'])
    @commands.has_guild_permissions(manage_messages=True)
    async def deletealias(self, ctx, alias, mem_id: int, mode="idol"):
        """Remove alias from an idol/group (Underscores are spaces)
        [Format: %deletealias (alias) (ID of idol/group) ('idol' or 'group')]"""
        alias = alias.replace("_", " ")
        if mode.lower() in ["idol", "member", "members", "idols"]:
            obj = await ex.u_group_members.get_member(mem_id)
            name = f"{obj.full_name} ({obj.stage_name}) [{obj.id}]"
        elif mode.lower() in ["group", "groups"]:
            obj = await ex.u_group_members.get_group(mem_id)
            name = f"{obj.name} [{obj.id}]"
        else:
            return await ctx.send("> Please select whether you want to add an idol or group alias.")
        if not obj:
            return await ctx.send(f"> {mem_id} is not associated with an idol or group.")
        if ex.check_if_mod(ctx):  # checks if the user is a bot mod.
            if alias not in obj.aliases:
                return await ctx.send(f"> {alias} is not a global alias for {name}.")
            await ex.u_group_members.remove_global_alias(obj, alias.lower())
            return await ctx.send(f"> {alias} has been removed from the global aliases for {mode} {mem_id}")
        else:
            server_aliases = obj.local_aliases.get(ctx.guild.id)
            if server_aliases:
                if alias.lower() not in server_aliases:
                    return await ctx.send(f"> {alias} is not a server alias for {name}.")
            await ex.u_group_members.remove_local_alias(obj, alias.lower(), ctx.guild.id)
            return await ctx.send(f"> {alias} has been removed from the server aliases for {name}.")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def welcome(self, ctx, *, message=None):
        """Set a welcome message or disable welcome in the current channel.
        Use %user where they should be mentioned.
        Use %guild_name if the server name should be added.
        [Format: %welcome (Welcome %user to %guild_name!)]"""
        try:
            channel_id = ctx.channel.id
            guild_id = ctx.guild.id
            server_prefix = await ex.get_server_prefix_by_context(ctx)
            server = ex.cache.welcome_messages.get(guild_id)
            welcome_new_users = f"> This server will now welcome new users. More info can be found with `{server_prefix}help welcome`"
            if not message:
                message = f"%user, Welcome to %guild_name."
                if not server:
                    await ex.u_moderator.add_welcome_message_server(channel_id, guild_id, message, 1)
                    return await ctx.send(welcome_new_users)
                else:
                    # this is to simplify code, and just swaps 0 and 1 no matter what it is.
                    updated_pos = int(not server.get("enabled"))
                    await ex.u_moderator.update_welcome_message_enabled(guild_id, updated_pos)
                    # check if the channel id was changed.
                    if not channel_id == server.get("channel_id"):
                        await ex.u_moderator.update_welcome_message_channel(guild_id, channel_id)
                    if updated_pos:
                        return await ctx.send(f"> Welcome Messages have been enabled in this channel. ")
                    else:
                        return await ctx.send(f"> Welcome Messages have been disabled in this channel. ")
            else:
                if not server:
                    await ex.u_moderator.add_welcome_message_server(channel_id, guild_id, message, 1)
                    return await ctx.send(welcome_new_users)
                else:
                    enabled = await ex.u_moderator.check_welcome_message_enabled(guild_id)
                    if not enabled:
                        await ex.u_moderator.update_welcome_message_enabled(guild_id, 1)
                    if not channel_id == server.get("channel_id"):
                        await ex.u_moderator.update_welcome_message_channel(guild_id, channel_id)
                    await ex.u_moderator.update_welcome_message(guild_id, message)
                    return await ctx.send(welcome_new_users)
        except Exception as e:
            log.console(e)
            return await ctx.send("> **An error has occurred. Please report it.**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def disableinteraction(self, ctx, interaction=None):
        """Disable an interaction on your server. Redo to enable again [Format: %disableinteraction (interaction)]"""
        interaction_msg = f"> **The available interactions are {', '.join(interaction_list)}.**"
        if not interaction:
            return await ctx.send(interaction_msg)
        interaction = interaction.lower()
        if interaction in interaction_list:
            server_id = ctx.guild.id
            if not await ex.check_interaction_enabled(server_id=server_id, interaction=interaction):
                # enable it
                await ex.u_miscellaneous.enable_interaction(server_id, interaction)
                await ctx.send(f"> **{interaction} has been enabled in this server.**")
            else:
                # disable it
                await ex.u_miscellaneous.disable_interaction(server_id, interaction)
                await ctx.send(f"> **{interaction} has been disabled in this server.**")

        else:
            return await ctx.send(f"> **That is not an interaction.**\n{interaction_msg}")

    async def get_mute_role(self, ctx):
        mute_roles = await ex.conn.fetch("SELECT roleid FROM general.muteroles")
        for role in mute_roles:
            role_id = role[0]
            role = ctx.guild.get_role(role_id)
            if role:
                return role

    async def check_if_muted(self, user_id, role):
        users = role.members
        for user in users:
            if user.id == user_id:
                return True

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True, manage_roles=True)
    async def mute(self, ctx, user: discord.Member = None, *, reason=None):
        """Mutes a user.
        Format: [%mute @user (reason)]"""
        try:
            if not user:
                return await ctx.send(f"> **<@{ctx.author.id}>, Please specify a user to mute.**")
            if user.id == ctx.author.id:
                return await ctx.send(f"> **<@{ctx.author.id}>, You cannot mute yourself.**")
            elif user.bot:
                return await ctx.send(f"> **<@{ctx.author.id}>, You cannot mute a bot.**")
            mute_role = await self.get_mute_role(ctx)
            guild_channels = ctx.guild.text_channels
            if not mute_role:
                mute_role = await ctx.guild.create_role(reason="Creating Mute Role", name="Muted")
                await ex.conn.execute("INSERT INTO general.muteroles(roleid) VALUES($1)", mute_role.id)
                for channel in guild_channels:
                    try:
                        await channel.set_permissions(mute_role, send_messages=False)
                    except:
                        pass
            muted = await self.check_if_muted(user.id, mute_role)
            if muted:
                return await ctx.send(f"**<@{user.id}> is already muted.**")
            else:
                await user.add_roles(mute_role, reason=f"Muting User - Requested by {ctx.author.display_name} ({user.id}) - Reason: {reason}.")
                return await ctx.send(f"> **Muted <@{user.id}>. Reason: {reason}**")
        except discord.Forbidden as e:
            log.console(e)
            await ctx.send(f"**I am missing the permissions to mute {user.display_name}. {e}**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"Mute - {e}")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True, manage_roles=True)
    async def unmute(self, ctx, user: discord.Member = None):
        """Unmute a user that is already muted.
        Format: [%unmute @user (reason)]"""
        try:
            if not user:
                return await ctx.send(f"> **<@{ctx.author.id}>, Please specify a user to unmute.**")
            if user.id == ctx.author.id:
                return await ctx.send(f"> **<@{ctx.author.id}>, You cannot unmute yourself.**")
            mute_role = await self.get_mute_role(ctx)
            muted = await self.check_if_muted(user.id, mute_role)
            if not mute_role:
                return await ctx.send(">**This user was not muted by me as the mute role could not be found. In order for me to create a custom mute role, I need to mute someone first.**")
            if muted:
                await user.remove_roles(mute_role,
                                     reason=f"UnMuting User - Requested by {ctx.author.display_name} ({user.id})")
                return await ctx.send(f"> **<@{user.id}> has been unmuted.**")
            else:
                return await ctx.send(f"> **<@{user.id}> is not muted.**")
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> **I am missing permissions to unmute {user.display_name}. {e}**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def say(self, ctx, text_channel: typing.Union[discord.TextChannel, str] = None, *, message=None):
        """Make Irene say a message.
        Requires Manage Messages
        [Format: %say #text-channel message]
        """
        if not text_channel:
            return await ctx.send(f"> **{ctx.author.display_name}, Please specify a message to send.**")
        if type(text_channel) == str:
            if not message:
                message = f"{text_channel} {message}"
            else:
                message = text_channel
            text_channel = ctx
        await text_channel.send(message)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def sayembed(self, ctx, text_channel: typing.Union[discord.TextChannel, str] = None, *, embed_format=None):
        """Make Irene say an embed message.
        Requires Manage Messages. Follows Format from https://embedbuilder.nadekobot.me/
        [Format: %sayembed #text-channel embed_format]
        """
        embed_creator_url = "https://embedbuilder.nadekobot.me/"
        if type(text_channel) is str:
            if type(embed_format) is str:
                embed_format = text_channel + embed_format
            text_channel = ctx.channel
        try:
            if not embed_format or not text_channel:
                return await ctx.send(f"> **This command follows the format from {embed_creator_url}**")
            else:
                author_name = None
                author_icon_url = None
                embed_footer_text = None
                embed_footer_url = None
                embed_format = json.loads(embed_format)
                embed_image = embed_format.get('image')
                embed_footer = embed_format.get('footer')
                embed_thumbnail = embed_format.get('thumbnail')
                embed_author = embed_format.get('author')
                if embed_author:
                    author_name = embed_author.get("name")
                    author_icon_url = embed_author.get("icon_url")
                if embed_footer:
                    embed_footer_text = embed_footer.get('text')
                    embed_footer_url = embed_footer.get('icon_url')
                author_url = embed_format.get('url')

                if author_icon_url or author_url:
                    embed_format.pop('author')
                if embed_footer_url:
                    embed_format.pop('footer')
                if embed_image:
                    embed_format.pop('image')
                if embed_thumbnail:
                    embed_format.pop('thumbnail')

                embed = discord.Embed.from_dict(embed_format)

                if embed_image:
                    embed.set_image(url=embed_image)
                if embed_footer_url:
                    embed.set_footer(text=embed_footer_text, icon_url=embed_footer_url)
                if embed_thumbnail:
                    embed.set_thumbnail(url=embed_thumbnail)
                if author_url and author_icon_url:
                    embed.set_author(name=author_name, url=author_url, icon_url=author_icon_url)
                elif not author_icon_url and author_url:
                    embed.set_author(name=author_name, url=author_url)
                elif not author_url and author_icon_url:
                    embed.set_author(name=author_name, icon_url=author_icon_url)

                plain_body = embed_format.get('plainText')
                if plain_body:
                    return await text_channel.send(plain_body, embed=embed)
                else:
                    return await text_channel.send(embed=embed)
        except Exception as e:
            await ctx.send(f"ERROR - {e}.\nFollow the format from {embed_creator_url}")
            log.console(e)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def setprefix(self, ctx, *, prefix=bot_prefix):
        """Set the server prefix. If prefix was forgotten, type this command with the default prefix.[Format: %setprefix %]
        Requires Manage Messages
        """
        prefix = prefix.lower()
        current_server_prefix = await ex.get_server_prefix(ctx.guild.id)
        if len(prefix) > 8:
            await ctx.send("> **Your prefix can not be more than 8 characters.**")
        else:
            # Default prefix '%' should never be in DB.
            if current_server_prefix == "%":
                if prefix != "%":
                    await ex.conn.execute("INSERT INTO general.serverprefix VALUES ($1,$2)", ctx.guild.id, prefix)
                    ex.cache.server_prefixes[ctx.guild.id] = prefix
            else:
                if prefix != "%":
                    await ex.conn.execute("UPDATE general.serverprefix SET prefix = $1 WHERE serverid = $2", prefix, ctx.guild.id)
                    ex.cache.server_prefixes[ctx.guild.id] = prefix
                else:
                    await ex.conn.execute("DELETE FROM general.serverprefix WHERE serverid = $1", ctx.guild.id)
                    ex.cache.server_prefixes.pop(ctx.guild.id, None)
            await ctx.send(f"> **This server's prefix has been set to {prefix}.**")

    @commands.command(aliases=['prune', 'purge'])
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, user: discord.Member = None):
        """Prune Messages (Max 1000) [Format: %clear (amount)][Aliases: prune]
        Requires Manage Messages
        """
        amount += 1

        def clear_x(m):
            return m.author == user
        if not user:
            everyone = True
        else:
            everyone = False
        if amount <= 101:
            if not everyone:
                await ctx.channel.purge(limit=amount, check=clear_x, bulk=True)
            elif everyone:
                await ctx.channel.purge(limit=amount, bulk=True)
            log.console(f"Pruned {amount} messages from {ctx.channel.id}")
        if amount >= 102:
            if amount > 1000:
                amount = 1000
            number = (amount // 100)
            await ctx.send(
                f"> **{amount}** messages will be deleted in 5 seconds and will be split in intervals of 100.")
            for i in range(number):
                if not everyone:
                    await ctx.channel.purge(limit=100, check=clear_x, bulk=True)
                elif everyone:
                    await ctx.channel.purge(limit=100, bulk=True)
                log.console(f"Pruned 100 messages from {ctx.channel.id}")
            await ctx.send(f"> **{amount}** messages have been pruned from {ctx.channel.id}.")

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = None, *, reason="No Reason"):
        """Ban A User [Format: %ban @user]
        Requires Ban Members
        """
        if not user:
            await ctx.send("> **Please choose a person to ban.**")
        else:
            if user.id == ctx.author.id:
                return await ctx.send(f"> **{ctx.author.display_name}, you can not ban yourself!**")
            try:
                await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
                embed = discord.Embed(title="User Banned!", description=f"> **<@{user.id}> was banned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> was not able to be banned by <@{ctx.author.id}> successfully. \n {e}**!", color=0xff00f6)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = None, *, reason="No Reason"):
        """Unban A User [Format: %unban @user]
        Requires Ban Members
        """
        if not user:
            return await ctx.send("> **Please choose a person to unban.**")
        else:
            try:
                if user.id == ctx.author.id:
                    return await ctx.send(f"> **{ctx.author.display_name}, you can not ban yourself!**")
                await ctx.guild.unban(user=user, reason=reason)
                embed = discord.Embed(title="User Unbanned!", description=f"> **<@{user.id}> was unbanned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> could not be unbanned by <@{ctx.author.id}> \n {e}**!", color=0xff00f6)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = None, reason="No Reason"):
        """Kick A User [Format: %kick @user]
        Requires Kick Members
        """
        if not user:
            return await ctx.send("> **Please choose a person to kick.**")
        else:
            try:
                if user.id == ctx.author.id:
                    return await ctx.send(f"> **{ctx.author.display_name}, you can not kick yourself!**")
                await ctx.guild.kick(user=user, reason=reason)
                embed = discord.Embed(title="User Kicked!",
                                      description=f"**<@{user.id}> was kicked by <@{ctx.author.id}> for {reason}**!",
                                      color=0xff00f6)
            except Exception as e:
                embed = discord.Embed(title="Error",
                                      description=f"**<@{user.id}> could not be kicked by <@{ctx.author.id}> \n {e}**!",
                                      color=0xff00f6)
            await ctx.send(embed=embed)

    @commands.command(aliases=['temp'])
    @commands.has_guild_permissions(manage_messages=True)
    async def tempchannel(self, ctx, delay=-1):
        """Makes Current Channel a temporary channel deleting messages after a certain time period (greater than 1 minute). If delay is -1, it will remove the channel. [Format: %temp (delay)]
        Requires Manage Messages
        """
        channel_id = ctx.channel.id
        try:
            if delay == -1:
                    await ex.conn.execute("DELETE FROM general.TempChannels WHERE chanID = $1", channel_id)
                    ex.cache.temp_channels[channel_id] = None
                    return await ctx.send("> **If this channel was a temporary channel, it has been removed.**")
            elif delay < -1:
                return await ctx.send("> **The delay cannot be negative.**")
            elif 0 < delay < 60:
                return await ctx.send("> **The delay must be greater than 1 minute due to rate-limiting issues.**")
            else:
                new_delay = await ex.u_miscellaneous.get_cooldown_time(delay)
                temp_channel_delay = ex.cache.temp_channels.get(channel_id)
                if temp_channel_delay:  # this channel is already a temp channel
                    await ex.conn.execute("UPDATE general.TempChannels SET delay = $1 WHERE chanID = $2", delay, channel_id)
                else:
                    await ex.conn.execute("INSERT INTO general.TempChannels VALUES ($1, $2)", channel_id, delay)
                await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                ex.cache.temp_channels[channel_id] = delay
        except Exception as e:
            await ctx.send(f"> Error - {e}")
            log.console(e)

    async def make_emoji(self, ctx, emoji):
        # a simple emoji converter
        try:
            return await commands.PartialEmojiConverter().convert(ctx, emoji)
        except:
            return str(emoji)

    @commands.command(aliases=['yoink'])
    @commands.has_guild_permissions(manage_messages=True, manage_emojis=True)
    async def addemoji(self, ctx, url: str, emoji_name=None):
        """Adds an emoji to the server. Several emojis can be added if split with a comma. Emoji Name is optional.
        [Format: %addemoji (url/emoji) (emoji name)]
        Requires Manage Messages & Manage Emojis"""
        org_emoji_name = emoji_name
        list_of_emojis = url.split(',')
        for emoji in list_of_emojis:
            try:
                url = await self.make_emoji(ctx, emoji)
                if type(url) == str:
                    emoji_name = str(org_emoji_name)
                if type(url) == discord.partial_emoji.PartialEmoji or type(url) == discord.PartialEmoji:
                    if not org_emoji_name or len(list_of_emojis) > 1:
                        emoji_name = f"{url.name}"
                    url = f"{url.url}"
                if len(emoji_name) < 2:
                    return await ctx.send("> **Please enter an emoji name more than two letters.**")
                async with ex.session.get(url) as r:
                    if r.status == 200:
                        await ctx.guild.create_custom_emoji(name=emoji_name, image=await r.read())
                        emojis = ex.client.emojis
                        max_emoji_length = len(emojis)
                        if emoji_name in str(emojis[max_emoji_length-1]):
                            await ctx.send(emojis[max_emoji_length-1])
                        elif emoji_name in str(emojis[0]):
                            await ctx.send(emojis[0])
                        else:
                            await ctx.send(f"> **Added :{emoji_name}:**")
                    elif r.status == 404:
                        await ctx.send("> **That URL was not Found.**")
                    elif r.status == 403:
                        await ctx.send("> **I do not have access to that site.**")
                    else:
                        await ctx.send("> **I was not able to connect to that url**")
            except discord.HTTPException as e:
                if e.code == 30008:
                    err_msg = f"Could not add emoji due to the maximum number of emojis reached."
                    log.console(f"{err_msg} Guild ID: {ctx.guild.id}")
                    return await ctx.send(f"> **{err_msg}**")
                if e.code == 50035:
                    ezgif = f"https://ezgif.com/optimize?url={url}"
                    log.console(
                        f"File cannot be larger than 256.0 kb. Please optimize the emoji here. {ezgif}")
                    return await ctx.send(
                        f">>> **File cannot be larger than 256.0 kb. Please optimize the emoji here.**\n <{ezgif}>")

            except aiohttp.InvalidURL:
                await ctx.send(f"> **Invalid URL.**")
            except Exception as e:
                log.console(e)
