import discord
from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
from module.keys import twitch_client_id
import asyncio
import json


class Twitch(commands.Cog):
    def __init__(self, ex):
        self.ex = ex

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def addtwitch(self, ctx, *, twitch_username):
        """Adds a Twitch username to keep track of. Maximum 2 twitch channels per server.
        [Format: %addtwitch (twitch username)]
        """
        try:
            guild_id = await self.ex.get_server_id(ctx)
            if not guild_id:
                return await ctx.send(await self.ex.get_msg(ctx.author.id, "general", "no_dm"))
            if not await self.ex.u_twitch.check_guild_limit(guild_id):
                msg = await self.ex.get_msg(ctx.author.id, "twitch", "follow_limit")
                msg = await self.ex.replace(msg, ["follow_limit", self.ex.twitch_guild_follow_limit])
                return await ctx.send(msg)
            if await self.ex.u_twitch.check_channel_followed(twitch_username, guild_id):
                return await ctx.send(await self.ex.get_msg(ctx.author.id, "twitch", "already_followed"))

            await self.ex.u_twitch.add_channel(twitch_username, guild_id)
            log.console(f"{guild_id} is now receiving twitch notifications for {twitch_username}.")
            msg = await self.ex.get_msg(ctx.author.id, "twitch", "now_following")
            msg = await self.ex.replace(msg, ['twitch_username', twitch_username])
            return await ctx.send(msg)
        except Exception as e:
            log.console(e)
            msg = await self.ex.get_msg(ctx.author.id, "general", "error")
            msg = await self.ex.replace(msg, "e", e)
            return await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def removetwitch(self, ctx, *, twitch_username):
        """Removes a twitch username that is being kept track of.
        [Format: %removetwitch (twitch username)]
        """
        try:
            guild_id = await self.ex.get_server_id(ctx)
            if not guild_id:
                return await ctx.send(await self.ex.get_msg(ctx.author.id, "general", "no_dm"))
            await self.ex.u_twitch.remove_channel(twitch_username, guild_id)
            log.console(f"{guild_id} is no longer receiving twitch notifications for {twitch_username}.")
            return await ctx.send(await self.ex.get_msg(ctx.author.id, "twitch", "stop_following"))
        except Exception as e:
            log.console(e)
            msg = await self.ex.get_msg(ctx.author.id, "general", "error")
            msg = await self.ex.replace(msg, "e", e)
            return await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def settwitchchannel(self, ctx, text_channel: discord.TextChannel = None):
        """Set the discord channel that the twitch announcements will be posted on.
        [Format: %settwitchchannel #discord-channel]"""
        guild_id = await self.ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send(await self.ex.get_msg(ctx.author.id, "general", "no_dm"))
        if not text_channel:
            text_channel = ctx.channel

        await self.ex.u_twitch.set_discord_channel(guild_id, text_channel.id)
        log.console(f"{guild_id} now has their discord channel set to {text_channel.id} for twitch updates.")
        msg = await self.ex.get_msg(ctx.author.id, "twitch", "announcement_channel")
        msg = await self.ex.replace(msg, ['text_channel', text_channel])
        await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def settwitchrole(self, ctx, role: discord.Role = None):
        """Set the discord role that will be mentioned on twitch announcements. If a discord role is set,
        everyone will not be mentioned. Use the command without a role to mention everyone.
        [Format: %settwitchrole @role]"""
        guild_id = await self.ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send(await self.ex.get_msg(ctx.author.id, "general", "no_dm"))

        if not role:
            await self.ex.u_twitch.delete_twitch_role(guild_id)
            return await ctx.send(await self.ex.get_msg(ctx.author.id, "twitch", "no_role"))

        await self.ex.u_twitch.change_twitch_role(guild_id, role.id)
        log.console(f"{guild_id} will now mention {role.id} on twitch announcements.")
        return await ctx.send(await self.ex.get_msg(ctx.author.id, "twitch", "role"))

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def listtwitch(self, ctx):
        """List the twitch channels the guild/server follows.
        [Format: %listtwitch]"""
        guild_id = await self.ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send(await self.ex.get_msg(ctx.author.id, "general", "no_dm"))
        channels_followed = await self.ex.u_twitch.get_channels_followed(guild_id)
        msg = await self.ex.get_msg(ctx.author.id, "twitch", "following")
        msg = await self.ex.replace(msg, ["channels_followed", ', '.join(channels_followed)])
        await ctx.send(msg)

    # we now check every minute instead of 30 seconds since Irene was at times posting twice.
    # instead of keeping track of which channels it was sent to, increasing the check time uses less resources
    # and would prevent the issue at hand.
    @tasks.loop(seconds=0, minutes=1, hours=0, reconnect=True)
    async def twitch_updates(self):
        """Process for checking for Twitch channels that are live and sending to discord channels."""
        try:
            if not self.ex.twitch_token:
                await self.ex.u_twitch.reset_twitch_token()
                await asyncio.sleep(5)  # allow time for token to refresh.

            headers = {
                'Authorization': f'Bearer {self.ex.twitch_token}',
                'client-id': twitch_client_id
            }
            for twitch_username in self.ex.cache.twitch_channels.keys():
                try:
                    end_point = f"https://api.twitch.tv/helix/search/channels?query={twitch_username}"
                    async with self.ex.session.get(end_point, headers=headers) as r:
                        if r.status == 200:
                            data = await r.text()
                            data_json = json.loads(data)
                            all_streamers = data_json.get('data')
                            for streamer in all_streamers:
                                if streamer.get('display_name').lower() == twitch_username.lower():
                                    was_live = self.ex.cache.twitch_channels_is_live.get(twitch_username)
                                    is_live = streamer.get('is_live')

                                    if not is_live:
                                        await self.ex.sql.s_twitch.delete_twitch_posted(twitch_username.lower())

                                    if (not was_live) and is_live:
                                        await self.ex.u_twitch.send_twitch_announcement(twitch_username)
                                    self.ex.cache.twitch_channels_is_live[twitch_username] = is_live
                        elif r.status == 401:
                            self.ex.twitch_token = None  # resets twitch token on next loop
                            break
                except Exception as e:
                    log.console(e)
        except Exception as e:
            log.console(e)
