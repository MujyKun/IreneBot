import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log
from Weverse.weverseasync import WeverseAsync
import aiofiles
from IreneUtility.Utility import Utility
import asyncio


def check_if_mod():
    """Decorator for checking if a user is in the support server."""
    def predicate(ctx):
        return ctx.cog.ex.check_if_mod(ctx)
    return commands.check(predicate)


# noinspection PyBroadException,PyPep8
class BotMod(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex

    async def mod_mail_on_message(self, message):
        # mod mail
        try:
            message_sender = message.author
            message_channel = message.channel
            message_content = message.content
            if message_sender.id == self.ex.keys.bot_id:
                return
            if 'closedm' in message_content or 'createdm' in message_content:
                return

            for user_id in self.ex.cache.mod_mail:
                try:
                    channel_id = self.ex.cache.mod_mail.get(user_id)
                    mod_channel = await self.ex.client.fetch_channel(channel_id)
                    if user_id == message_sender.id:
                        dm_channel = await self.ex.get_dm_channel(message_sender.id)
                        if message_channel.id == dm_channel:
                            await mod_channel.send(
                                f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                    if mod_channel == message_channel:
                        dm_channel = await self.ex.get_dm_channel(user_id)
                        await dm_channel.send(
                            f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                except Exception as e:
                    log.console(f"{e} - Iteration Error in BotMod.mod_mail_on_message")
                    # change in dictionary size should break the loop.
                    break

        except Exception as e:
            log.console(f"{e} - BotMod.mod_mail_on_message")

    @commands.command()
    @check_if_mod()
    async def weverseauth(self, ctx, token):
        """
        Updates Weverse Authentication Token without restarting bot.

        Only use this in DMs or a private channel for security purposes.
        [Format %weverseauth <token>]
        """
        self.ex.keys.weverse_auth_token = token
        self.ex.weverse_client = WeverseAsync(authorization=self.ex.keys.weverse_auth_token,
                                              web_session=self.ex.session, verbose=True, loop=asyncio.get_event_loop())
        await ctx.send("> Token and Weverse client has been updated.")
        await self.ex.weverse_client.start()

    @commands.command()
    @check_if_mod()
    async def moveto(self, ctx, idol_id, link):
        """
        Moves a link to another idol. (Cannot be used for adding new links)

        [Format: %moveto (idol id) (link)]
        """
        try:
            drive_link = self.ex.first_result(await self.ex.conn.fetchrow("SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", link))
            if not drive_link:
                return await ctx.send(f"> **{link} does not have a connection to a google drive link.**")
            await self.ex.conn.execute("UPDATE groupmembers.imagelinks SET memberid = $1 WHERE link = $2", int(idol_id), drive_link)
            await ctx.send(f"> **Moved {link} to {idol_id} if it existed.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{e}**")

    @commands.command()
    @commands.is_owner()
    async def fixlinks(self, ctx):
        """
        Fix thumbnails and banners of idols and groups and put them on the host.

        NOTE: this is not an official command is just used momentarily for updates. No reason for this code to be
        simplified and is not a permanent command.
        """
        mem_info = await self.ex.conn.fetch('SELECT id, thumbnail, banner FROM groupmembers.member')
        grp_info = await self.ex.conn.fetch('SELECT groupid, thumbnail, banner FROM groupmembers.groups')

        async def download_image(link):
            async with self.ex.session.get(link) as resp:
                fd = await aiofiles.open(file_loc, mode='wb')
                await fd.write(await resp.read())

        for mem_id, mem_thumbnail, mem_banner in mem_info:
            file_name = f"{mem_id}_IDOL.png"
            if mem_thumbnail:
                file_loc = f"{self.ex.keys.idol_avatar_location}{file_name}"
                if 'images.irenebot.com' not in mem_thumbnail:
                    await download_image(mem_thumbnail)
                if self.ex.check_file_exists(file_loc):
                    image_url = f"{self.ex.keys.image_host}/avatar/{file_name}"
                    await self.ex.conn.execute("UPDATE groupmembers.member SET thumbnail = $1 WHERE id = $2", image_url, mem_id)
            if mem_banner:
                file_loc = f"{self.ex.keys.idol_banner_location}{file_name}"
                if 'images.irenebot.com' not in mem_banner:
                    await download_image(mem_banner)
                image_url = f"https://images.irenebot.com/banner/{file_name}"
                if self.ex.check_file_exists(file_loc):
                    await self.ex.conn.execute("UPDATE groupmembers.member SET banner = $1 WHERE id = $2", image_url, mem_id)
        for grp_id, grp_thumbnail, grp_banner in grp_info:
            file_name = f"{grp_id}_GROUP.png"
            if grp_thumbnail:
                file_loc = f"{self.ex.keys.idol_avatar_location}{file_name}"
                if 'images.irenebot.com' not in grp_thumbnail:
                    await download_image(grp_thumbnail)
                image_url = f"https://images.irenebot.com/avatar/{file_name}"
                if self.ex.check_file_exists(file_loc):
                    await self.ex.conn.execute("UPDATE groupmembers.groups SET thumbnail = $1 WHERE groupid = $2", image_url, grp_id)
            if grp_banner:
                file_loc = f"{self.ex.keys.idol_banner_location}{file_name}"
                if 'images.irenebot.com' not in grp_banner:
                    await download_image(grp_banner)
                image_url = f"https://images.irenebot.com/banner/{file_name}"
                if self.ex.check_file_exists(file_loc):
                    await self.ex.conn.execute("UPDATE groupmembers.groups SET banner = $1 WHERE groupid = $2", image_url, grp_id)
        return await ctx.send("> All images have been fixed, merged to image hosting service and have links set up for them.")

    @commands.command()
    @check_if_mod()
    async def mergeidol(self, ctx, original_idol_id: int, duplicate_idol_id: int):
        """
        Merge a duplicated idol with it's original idol.

        CAUTION: All aliases and are moved to the original idol, idol information is left alone
        If a group ID is not in the original idol, it will be added and then the dupe idol will be deleted along with
        all of it's connections.
        [Format: %mergeidol (original idol id) (duplicate idol id)]
        """
        # check groups
        original_idol = await self.ex.u_group_members.get_member(original_idol_id)
        duplicate_idol = await self.ex.u_group_members.get_member(duplicate_idol_id)

        if not duplicate_idol:
            return await ctx.send(f"> {duplicate_idol_id} could not find an Idol.")
        if not original_idol:
            return await ctx.send(f"> {original_idol} could not find an Idol.")
        for group_id in duplicate_idol.groups:
            if group_id not in original_idol.groups:
                # add groups from dupe to original.
                await self.ex.conn.execute("UPDATE groupmembers.idoltogroup SET idolid = $1 WHERE groupid = $2 AND idolid = $3", original_idol.id, group_id, duplicate_idol.id)
        # delete idol
        await self.ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", duplicate_idol.id)
        # recreate cache
        await self.ex.u_cache.create_idol_cache()
        await self.ex.u_cache.create_group_cache()
        await ctx.send(f"> Merged {duplicate_idol_id} to {original_idol_id}.")

    @commands.command()
    @check_if_mod()
    async def mergegroup(self, ctx, original_group_id: int, duplicate_group_id: int):
        """
        Merge a duplicated group with it's original group.

        CAUTION: All aliases and are moved to the original group, group information is left alone
        If an idol ID is not in the original group, it will be added and then this group will be deleted along with
        all of it's connections.
        [Format: %mergegroup (original group id) (duplicate group id)]
        """
        original_group = await self.ex.u_group_members.get_group(original_group_id)
        duplicate_group = await self.ex.u_group_members.get_group(duplicate_group_id)
        if not duplicate_group:
            return await ctx.send(f"> {duplicate_group_id} could not find a Group.")
        if not original_group:
            return await ctx.send(f"> {original_group} could not find a Group.")
        # move aliases
        await self.ex.conn.execute("UPDATE groupmembers.aliases SET objectid = $1 WHERE isgroup = $2 AND objectid = $3", original_group.id, 1, duplicate_group.id)
        for member_id in duplicate_group.members:
            if member_id not in original_group.members:
                # update the member location to the original group
                await self.ex.conn.execute("UPDATE groupmembers.idoltogroup SET groupid = $1 WHERE idolid = $2 AND groupid = $3", original_group.id, member_id, duplicate_group.id)
        # delete group
        await self.ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", duplicate_group.id)
        # recreate cache
        await self.ex.u_cache.create_idol_cache()
        await self.ex.u_cache.create_group_cache()
        await ctx.send(f"> Merged {duplicate_group_id} to {original_group_id}.")

    @commands.command()
    @check_if_mod()
    async def killapi(self, ctx):
        """
        Restarts the API.

        [Format: %killapi]
        """
        await ctx.send("> Restarting the API.")
        await self.ex.kill_api()

    @commands.command()
    @check_if_mod()
    async def maintenance(self, ctx, *, maintenance_reason=None):
        """
        Enable/Disable Maintenance Mode.

        [Format: %maintenance (reason)]
        """
        self.ex.cache.maintenance_mode = not self.ex.cache.maintenance_mode
        self.ex.cache.maintenance_reason = maintenance_reason

        return await ctx.send(f"> **Maintenance mode is set to {self.ex.cache.maintenance_mode}.**")

    @commands.command()
    @check_if_mod()
    async def botwarn(self, ctx, user: discord.User, *, reason=None):
        """
        Warns a user from Irene's DMs

        [Format: %botwarn (user id) <reason>]
        """
        message = f"""
**You have been warned by <@{ctx.author.id}>.**
**Please be aware that you may get banned from the bot if this behavior is repeated numerous times.**
**Reason:** {reason}
Have questions? Join the support server at {self.ex.keys.bot_support_server_link}."""
        dm_channel = await self.ex.get_dm_channel(user.id)
        if not dm_channel:
            return await ctx.send(f"> Could not find <@{user.id}>'s DM channel.")
        try:
            await dm_channel.send(message)
            return await ctx.send(f"> **Message was sent to <@{user.id}>**")
        except:
            return await ctx.send(f"> I do not have permission to send a message to <@{user.id}>")

    @commands.command()
    @check_if_mod()
    async def kill(self, ctx):
        """
        Kills the bot

        [Format: %kill]
        """
        await ctx.send("> **The bot is now offline.**")
        message = "Irene is restarting... All games in this channel will force-end."

        async def get_games():
            for existing_game in self.ex.cache.guessing_games.values():
                yield existing_game
            for existing_game in self.ex.cache.bias_games.values():
                yield existing_game

        async for game in get_games():
            try:
                await game.end_game()
                log.console(f"Closed the game in {game.channel.id}.")
                await game.channel.send(message)
            except Exception as e:
                log.console(f"Failed to close the game in {game.channel.id}")
                log.useless(f"{e} - Failed to close game - BotMod.kill")

        try:
            await self.ex.conn.terminate()  # close all db connections.
            log.console("Closed all DB Connections.")
        except Exception as e:
            log.console("Failed to close all DB Connections.")
            log.useless(f"{e} - Failed to close DB Connections - BotMod.kill")

        try:
            await self.ex.session.close()  # close the aiohttp client session.
            log.console("Closed the aiohttp session")
        except Exception as e:
            log.console("Failed to cose the aiohttp Client Session.")
            log.useless(f"{e} - Failed to close Web Session - BotMod.kill")

        try:
            await self.ex.client.logout()  # log out of bot.
            log.console("Logged out of the bot.")
        except Exception as e:
            log.console("Failed to log out of the bot.")
            log.useless(f"{e} - Failed to log out of bot. - BotMod.kill")

    @commands.command()
    @check_if_mod()
    async def addinteraction(self, ctx, interaction_type, *, links):
        """
        Add a gif/photo to an interaction (ex: slap,kiss,lick,hug)

        [Format: %addinteraction (interaction) (url,url)]
        """
        links = links.split(',')
        try:
            if interaction_type.lower() in self.ex.cache.interaction_list:
                for url in links:
                    url = url.replace(' ', '')
                    url = url.replace('\n', '')
                    await self.ex.conn.execute("INSERT INTO general.interactions(url, interaction) VALUES ($1, $2)", url, interaction_type.lower())
                    embed = discord.Embed(title=f"**Added {url} to {interaction_type.lower()}**", color=self.ex.get_random_color())
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("> **Please choose a proper interaction.**")
        except Exception as e:
            await ctx.send(f"**ERROR -** {e}")
            log.console(e)

    @commands.command()
    @check_if_mod()
    async def deleteinteraction(self, ctx, *, url):
        """
        Delete a url from an interaction

        [Format: %deleteinteraction (url,url)]
        """
        links = url.split(',')
        for url in links:
            try:
                url.replace(' ', '')
                url = url.replace('\n', '')
                await self.ex.conn.execute("DELETE FROM general.interactions WHERE url = $1", url)
                await ctx.send(f"Removed <{url}>")
            except Exception as e:
                log.useless(f"{e} - Failed to delete interaction. - BotMod.deleteinteraction")
        await ctx.send("Finished removing urls.")

    @commands.command()
    @check_if_mod()
    async def botban(self, ctx, *, user: discord.User):
        """
        Bans a user from Irene.

        [Format: %botban (user id)]
        """
        if not self.ex.check_if_mod(user.id, 1):
            await self.ex.u_miscellaneous.ban_user_from_bot(user.id)
            await ctx.send(f"> **<@{user.id}> has been banned from using Irene.**")
        else:
            await ctx.send(f"> **<@{ctx.author.id}>, you cannot ban a bot mod.**")

    @commands.command()
    @check_if_mod()
    async def botunban(self, ctx, *, user: discord.User):
        """
        UnBans a user from Irene.

        [Format: %botunban (user id)]
        """
        await self.ex.u_miscellaneous.unban_user_from_bot(user.id)
        await ctx.send(f"> **If the user was banned, they are now unbanned.**")

    @commands.command()
    @check_if_mod()
    async def addstatus(self, ctx, *, status: str):
        """
        Add a playing status to Irene.

        [Format: %addstatus (status)]
        """
        await self.ex.conn.execute("INSERT INTO general.botstatus (status) VALUES ($1)", status)
        self.ex.cache.bot_statuses.append(status)
        await ctx.send(f"> **{status} was added.**")

    @commands.command()
    @check_if_mod()
    async def getstatuses(self, ctx):
        """Get all statuses of Irene."""
        final_list = ""
        if self.ex.cache.bot_statuses:
            counter = 0
            for status in self.ex.cache.bot_statuses:
                final_list += f"{counter}) {status}\n"
                counter += 1
        else:
            final_list = "None"
        embed = discord.Embed(title="Statuses", description=final_list)
        await ctx.send(embed=embed)

    @commands.command()
    @check_if_mod()
    async def removestatus(self, ctx, status_index: int):
        """
        Remove a status based on it's indself.ex. The index can be found using %getstatuses.

        [Format: %removestatus (status index)]
        """
        try:
            status = self.ex.cache.bot_statuses[status_index]
            await self.ex.conn.execute("DELETE FROM general.botstatus WHERE status = $1", status)
            self.ex.cache.bot_statuses.pop(status_index)
            await ctx.send(f"> {status} was removed from the bot statuses.")
        except Exception as e:
            log.console(e)
            await ctx.send(e)

    @commands.command()
    @check_if_mod()
    async def addidoltogroup(self, ctx, idol_id: int, group_id: int):
        """
        Adds idol to group.

        [Format: %addidoltogroup (idol id) (group id)]
        """
        try:
            member_name = (await self.ex.u_group_members.get_member(idol_id))[1]
            group_name = await self.ex.get_group_name(group_id)
            if await self.ex.check_member_in_group(idol_id, group_id):
                return await ctx.send(f'> **{member_name} ({idol_id}) is already in {group_name} ({group_id}).**')
            else:
                await self.ex.u_group_members.add_idol_to_group(idol_id, group_id)
                await ctx.send(f"**Added {member_name} ({idol_id}) to {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidolfromgroup'])
    @check_if_mod()
    async def deleteidolfromgroup(self, ctx, idol_id: int, group_id: int):
        """
        Deletes idol from group.

        [Format: %deleteidolfromgroup (idol id) (group id)]
        """
        try:
            member_name = (await self.ex.u_group_members.get_member(idol_id))[1]
            group_name = await self.ex.get_group_name(group_id)
            if not await self.ex.check_member_in_group(idol_id, group_id):
                await ctx.send(f"> **{member_name} ({idol_id}) is not in {group_name} ({group_id}).**")
            else:
                await self.ex.u_group_members.remove_idol_from_group(idol_id, group_id)
                await ctx.send(f"**Removed {member_name} ({idol_id}) from {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidol'])
    @check_if_mod()
    async def deleteidol(self, ctx, idol_id: int):
        """
        Deletes an idol

        [Format: %deleteidol (idol id)]
        """
        try:
            idol_name = (await self.ex.u_group_members.get_member(idol_id))[1]
            await self.ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", idol_id)
            await ctx.send(f"{idol_name} ({idol_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removegroup'])
    @check_if_mod()
    async def deletegroup(self, ctx, group_id: int):
        """
        Deletes a group

        [Format: %deletegroup (group id)]
        """
        try:
            await self.ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", group_id)
            await ctx.send(f"{await self.ex.get_group_name(group_id)} ({group_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @check_if_mod()
    async def createdm(self, ctx, user: discord.User):
        """
        Create a DM with a user with the bot as a middle man. One user per mod channel.

        [Format: %createdm (user id)]
        """
        try:
            dm_channel = await self.ex.get_dm_channel(user=user)
            if dm_channel:
                user = await self.ex.get_user(user.id)
                user.mod_mail_channel_id = ctx.channel.id
                self.ex.cache.mod_mail[user.id] = ctx.channel.id  # full list
                await self.ex.conn.execute("INSERT INTO general.modmail(userid, channelid) VALUES ($1, $2)", user.id, ctx.channel.id)
                await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has created a DM with you. All messages sent here will be sent to them.")
                await ctx.send(f"> A DM has been created with {user.id}. All messages you type in this channel will be sent to the user.")
            else:
                await ctx.send("> I was not able to create a DM with that user.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)

    @commands.command()
    @check_if_mod()
    async def closedm(self, ctx, user: discord.User = None):
        """
        Closes a DM either by the User ID or by the current channel.

        [Format: %closedm <user id>]
        """
        try:
            if user:
                user_id = user.id
            else:
                user_id = self.ex.first_result(await self.ex.conn.fetchrow("SELECT userid FROM general.modmail WHERE channelid = $1", ctx.channel.id))
            dm_channel = await self.ex.get_dm_channel(user_id)
            if not dm_channel:
                return await ctx.send("> **There are no DMs set up in this channel.**")
            user = await self.ex.get_user(user_id)
            user.mod_mail_channel_id = 0
            self.ex.cache.mod_mail.pop(user_id, None)  # full list
            await self.ex.conn.execute("DELETE FROM general.modmail WHERE userid = $1 and channelid = $2", user_id, ctx.channel.id)
            await ctx.send(f"> The DM with {user_id} has been deleted successfully.")
            await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has closed the DM with you. Your messages will no longer be sent to them.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)




