import discord
from discord.ext import commands
import aiofiles
import os
from module import logger as log
from module.keys import client, bot_prefix
from Utility import resources as ex


class Moderator(commands.Cog):
    def __init__(self):
        pass

    async def get_mute_role(self, ctx):
        mute_roles = await ex.conn.fetch("SELECT roleid FROM general.muteroles")
        for role in mute_roles:
            role_id = role[0]
            role = ctx.guild.get_role(role_id)
            if role is not None:
                return role
        return None

    async def check_if_muted(self, user_id, role):
        users = role.members
        for user in users:
            if user.id == user_id:
                return True
        return False

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True, manage_roles=True)
    async def mute(self, ctx, user: discord.Member = None, *, reason=None):
        """Mutes a user.
        Format: [%mute @user (reason)]"""
        try:
            if user is None:
                return await ctx.send(f"> **<@{ctx.author.id}>, Please specify a user to mute.**")
            if user.id == ctx.author.id:
                return await ctx.send(f"> **<@{ctx.author.id}>, You cannot mute yourself.**")
            mute_role = await self.get_mute_role(ctx)
            guild_channels = ctx.guild.text_channels
            if mute_role is None:
                mute_role = await ctx.guild.create_role(reason="Creating Mute Role", name="Muted")
                await ex.conn.execute("INSERT INTO general.muteroles(roleid) VALUES($1)", mute_role.id)
                for channel in guild_channels:
                    try:
                        await channel.set_permissions(mute_role, send_messages=False)
                    except Exception as e:
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
            if user is None:
                return await ctx.send(f"> **<@{ctx.author.id}>, Please specify a user to unmute.**")
            if user.id == ctx.author.id:
                return await ctx.send(f"> **<@{ctx.author.id}>, You cannot unmute yourself.**")
            mute_role = await self.get_mute_role(ctx)
            muted = await self.check_if_muted(user.id, mute_role)
            if mute_role is None:
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
    async def say(self, ctx, *, message):
        """Make Irene say a message.
        Requires Manage Messages
        """
        await ctx.send(">>> {}".format(message))

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
            else:
                if prefix != "%":
                    await ex.conn.execute("UPDATE general.serverprefix SET prefix = $1 WHERE serverid = $2", prefix, ctx.guild.id)
                else:
                    await ex.conn.execute("DELETE FROM general.serverprefix WHERE serverid = $1", ctx.guild.id)
            await ctx.send(f"> **This server's prefix has been set to {prefix}.**")

    @commands.command(aliases=['prune', 'purge'])
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, user: discord.Member = discord.Member):
        """Prune Messages (Max 1000) [Format: %clear (amount)][Aliases: prune]
        Requires Manage Messages
        """
        amount = int(amount) + 1

        def clear_x(m):
            return m.author == user
        if user == discord.Member:
            checker = 1
        else:
            checker = 0
        if amount <= 101:
            if checker == 0:
                await ctx.channel.purge(limit=amount, check=clear_x, bulk=True)
            elif checker == 1:
                await ctx.channel.purge(limit=amount, bulk=True)
            log.console(f"Pruned {amount} messages from {ctx.channel.id}")
        if amount >= 102:
            if amount > 1000:
                amount = 1000
            number = (amount // 100)
            await ctx.send(
                f"> **{amount}** messages will be deleted in 5 seconds and will be split in intervals of 100.")
            for i in range(number):
                if checker == 0:
                    await ctx.channel.purge(limit=100, check=clear_x, bulk=True)
                elif checker == 1:
                    await ctx.channel.purge(limit=100, bulk=True)
                log.console(f"Pruned 100 messages from {ctx.channel.id}")
            await ctx.send(f"> **{amount}** messages have been pruned from {ctx.channel.id}.")

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = discord.Member, *, reason="No Reason"):
        """Ban A User [Format: %ban @user]
        Requires Ban Members
        """
        check = True
        if user == discord.Member:
            await ctx.send("> **Please choose a person to ban.**")
        else:
            if user.id == ctx.author.id:
                await ctx.send("> **You can not ban yourself!**")
                check = False
            try:
                if check:
                    await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
                    embed = discord.Embed(title="User Banned!", description=f"> **<@{user.id}> was banned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
                    await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> was not able to be banned by <@{ctx.author.id}> successfully. \n {e}**!", color=0xff00f6)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = discord.User, *, reason="No Reason"):
        """Unban A User [Format: %unban @user]
        Requires Ban Members
        """
        if user == discord.User:
            await ctx.send("> **Please choose a person to unban.**")
        else:
            try:
                if user.id == ctx.author.id:
                    await ctx.send("> **You can not unban yourself!**")
                await ctx.guild.unban(user=user, reason=reason)
                embed = discord.Embed(title="User Unbanned!", description=f"> **<@{user.id}> was unbanned by <@{ctx.author.id}> for {reason}**!", color=0xff00f6)
            except Exception as e:
                embed = discord.Embed(title="Error", description=f"**<@{user.id}> could not be unbanned by <@{ctx.author.id}> \n {e}**!", color=0xff00f6)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = discord.Member, reason="No Reason"):
        """Kick A User [Format: %kick @user]
        Requires Kick Members
        """
        if user == discord.Member:
            await ctx.send("> **Please choose a person to kick.**")
        else:
            try:
                if user.id == ctx.author.id:
                    await ctx.send("> **You can not kick yourself!**")
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
        """Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel. [Format: %temp (delay)]
        Requires Manage Messages
        """
        channel_id = ctx.channel.id
        try:
            if delay == -1:
                    await ex.conn.execute("DELETE FROM currency.TempChannels WHERE chanID = $1", channel_id)
                    await ctx.send ("> **If this channel was a temporary channel, it has been removed.**")
            if delay >= 60:
                new_delay = f"{(delay/60)} minutes"
            if 0 <= delay < 60:
                new_delay = f"{delay} seconds"
            if delay < -1:
                await ctx.send("> **The delay cannot be negative.**")
            if delay >= 0:
                channel_id = ctx.channel.id
                counter = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.TempChannels WHERE chanID = $1", channel_id))
                if counter == 1:
                    old_delay = ex.first_result(await ex.conn.fetchrow("SELECT delay FROM currency.TempChannels WHERE chanID = $1", channel_id))
                    if old_delay == delay:
                        await ctx.send(f"> **This channel is already a temp channel that deletes messages every {new_delay}.**")
                    else:
                        await ex.conn.execute("UPDATE currency.TempChannels SET delay = $1 WHERE chanID = $2", delay, channel_id)
                        await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                if counter == 0:
                    await ctx.send(f"> **This channel now deletes messages every {new_delay}.**")
                    await ex.conn.execute("INSERT INTO currency.TempChannels VALUES ($1, $2)", channel_id, delay)
        except Exception as e:
            log.console(e)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True, manage_emojis=True)
    async def addemoji(self, ctx, url, emoji_name):
        """Adds an emoji to the server. [Format: %addemoji (url) (emoji name)]
        Requires Manage Messages & Manage Emojis
        """
        if "?v=1" in url or ".jpg" in url or ".png" in url or ".gif" in url:
            file_format = url[52:56]
        else:
            file_format = "None"
            await ctx.send(f">>> **Please use a url that ends in ?v=1 or a file format like .png or edit your emoji on \n <https://ezgif.com/resize?url={url}>**")
            log.console (f"Please use a url that ends in ?v=1 or a file format like .png or edit your emoji on https://ezgif.com/resize?url={url}")
        if len(emoji_name) < 2:
            file_format = "None"
            await ctx.send("> **Please enter an emoji name more than two letters.**")
        if file_format != "None":
            # await ctx.send(file_format)
            async with ex.session.get('{}'.format(url)) as r:
                if r.status == 200:
                    # await ctx.send("Connection Successful")
                    fd = await aiofiles.open('Emoji/{}'.format(f"{emoji_name}{file_format}"), mode='wb')
                    await fd.write(await r.read())
                    await fd.close()
                    log.console(f"Downloaded {emoji_name}{file_format}")
                    full_file_name = emoji_name + file_format
                    file_size = (os.path.getsize(f'Emoji/{full_file_name}'))
                    if file_size > 262144:
                        await ctx.send(f">>> **File cannot be larger than 256.0 kb. Please resize the emoji here (for the resize method, use Gifsicle).**\n <https://ezgif.com/resize?url={url}>")
                        log.console(f"File cannot be larger than 256.0 kb. Please resize the emoji here. https://ezgif.com/resize?url={url}")
                    elif file_size <= 262144:
                        v = await aiofiles.open(f'Emoji/{full_file_name}', mode='rb')
                        # await ctx.guild.create_custom_emoji(name=emoji_name, image=f'Emoji/{full_file_name}')
                        await ctx.guild.create_custom_emoji(name=emoji_name, image=await v.read())
                        await v.close()
                        emojis = client.emojis
                        max_emoji_length = len(emojis)
                        if emoji_name in str(emojis[max_emoji_length-1]):
                            await ctx.send(emojis[max_emoji_length-1])
                        elif emoji_name in str(emojis[0]):
                            await ctx.send(emojis[0])
                        else:
                            await ctx.send(f"> **Added :{emoji_name}:**")
                    all_photos = os.listdir('Emoji')
                    for photo in all_photos:
                        try:
                            os.unlink('Emoji/{}'.format(photo))
                        except:
                            pass
                elif r.status == 404:
                    await ctx.send("> **That URL was not Found.**")
                elif r.status == 403:
                    await ctx.send("> **I do not have access to that site.**")
                else:
                    await ctx.send("> **I was not able to connect to that url**")
