import discord
from discord.ext import commands, tasks
from Utility import resources as ex
from module import logger as log
from module.keys import twitch_client_id
import asyncio
import json


class Twitch(commands.Cog):
    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def addtwitch(self, ctx, *, twitch_username):
        """Adds a Twitch username to keep track of. Maximum 2 twitch channels per server.
        [Format: %addtwitch (twitch username)]
        """
        try:
            guild_id = await ex.get_server_id(ctx)
            if not guild_id:
                return await ctx.send("> You can not use this command in DMs.")
            if not await ex.u_twitch.check_guild_limit(guild_id):
                return await ctx.send(f"> You are only allowed to have {ex.twitch_guild_follow_limit} channels followed.")
            if await ex.u_twitch.check_channel_followed(twitch_username, guild_id):
                return await ctx.send("> That twitch channel is already being followed.")

            await ex.u_twitch.add_channel(twitch_username, guild_id)
            log.console(f"{guild_id} is now receiving twitch notifications for {twitch_username}.")
            return await ctx.send(f"> This server will now receive notifications for {twitch_username}.")
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> An error occurred -> Please report it on the support server.\n Error MSG: {e}")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def removetwitch(self, ctx, *, twitch_username):
        """Removes a twitch username that is being kept track of.
        [Format: %removetwitch (twitch username)]
        """
        try:
            guild_id = await ex.get_server_id(ctx)
            if not guild_id:
                return await ctx.send("> You can not use this command in DMs.")
            await ex.u_twitch.remove_channel(twitch_username, guild_id)
            log.console(f"{guild_id} is no longer receiving twitch notifications for {twitch_username}.")
            return await ctx.send(f"> If this server was following that twitch channel, it was removed.")
        except Exception as e:
            log.console(e)
            return await ctx.send(f"> An error occurred -> Please report it on the support server.\n Error MSG: {e}")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def settwitchchannel(self, ctx, text_channel: discord.TextChannel = None):
        """Set the discord channel that the twitch announcements will be posted on.
        [Format: %settwitchchannel #discord-channel]"""
        guild_id = await ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send("> You can not use this command in DMs.")
        if not text_channel:
            text_channel = ctx.channel

        await ex.u_twitch.set_discord_channel(guild_id, text_channel.id)
        log.console(f"{guild_id} now has their discord channel set to {text_channel.id} for twitch updates.")
        await ctx.send(f"> Twitch announcements wil now be sent to {text_channel}.")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def settwitchrole(self, ctx, role: discord.Role = None):
        """Set the discord role that will be mentioned on twitch announcements. If a discord role is set,
        everyone will not be mentioned. Use the command without a role to mention everyone.
        [Format: %settwitchrole @role]"""
        guild_id = await ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send("> You can not use this command in DMs.")

        if not role:
            await ex.u_twitch.delete_twitch_role(guild_id)
            return await ctx.send("> Everyone will be tagged when there is a twitch announcement.")

        await ex.u_twitch.change_twitch_role(guild_id, role.id)
        log.console(f"{guild_id} will now mention {role.id} on twitch announcements.")
        return await ctx.send("> That role will be tagged when there is a twitch announcement.")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def listtwitch(self, ctx):
        """List the twitch channels the guild/server follows.
        [Format: %listtwitch]"""
        guild_id = await ex.get_server_id(ctx)
        if not guild_id:
            return await ctx.send("> You can not use this command in DMs.")
        channels_followed = await ex.u_twitch.get_channels_followed(guild_id)
        await ctx.send(f"> This server is following these channels: **{', '.join(channels_followed)}**")

    @tasks.loop(seconds=30, minutes=0, hours=0, reconnect=True)
    async def twitch_updates(self):
        """Process for checking for Twitch channels that are live and sending to discord channels."""
        try:
            if not ex.twitch_token:
                await ex.u_twitch.reset_twitch_token()
                await asyncio.sleep(5)  # allow time for token to refresh.

            headers = {
                'Authorization': f'Bearer {ex.twitch_token}',
                'client-id': twitch_client_id
            }

            for twitch_username in ex.cache.twitch_channels.keys():
                try:
                    end_point = f"https://api.twitch.tv/helix/search/channels?query={twitch_username}"
                    async with ex.session.get(end_point, headers=headers) as r:
                        if r.status == 200:
                            data = await r.text()
                            data_json = json.loads(data)
                            all_streamers = data_json.get('data')
                            for streamer in all_streamers:
                                if streamer.get('display_name') == twitch_username:
                                    was_live = ex.cache.twitch_channels_is_live.get(twitch_username)
                                    is_live = streamer.get('is_live')
                                    if (not was_live) and is_live:
                                        await ex.u_twitch.send_twitch_announcement(twitch_username)
                                    ex.cache.twitch_channels_is_live[twitch_username] = is_live
                        elif r.status == 401:
                            ex.twitch_token = None  # resets twitch token on next loop
                            break
                except Exception as e:
                    log.console(e)
        except Exception as e:
            log.console(e)
