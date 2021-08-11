import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log
import aiofiles
from IreneUtility.Utility import Utility
import asyncio


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
                await asyncio.sleep(0)
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

    async def cog_check(self, ctx):
        """A local check for this cog. Checks if the user is a mod."""
        return self.ex.check_if_mod(ctx)

    @commands.command()
    async def moveto(self, ctx, idol_id, link):
        """
        Moves a link to another idol. (Cannot be used for adding new links)

        [Format: %moveto (idol id) (link)]
        """
        try:
            drive_link = self.ex.first_result(await self.ex.conn.fetchrow(
                "SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", link))
            if not drive_link:
                return await ctx.send(f"> **{link} does not have a connection to a google drive link.**")
            await self.ex.conn.execute("UPDATE groupmembers.imagelinks SET memberid = $1 WHERE link = $2", int(idol_id),
                                       drive_link)
            msg = await self.ex.get_msg(ctx, "botmod", "linked_idol", [["result", link], ["result2", idol_id]])
            await ctx.send(msg)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{e}**")

    @commands.command()
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
            msg = await self.ex.get_msg(ctx, "botmod", "no_idol_found", ["result", duplicate_idol_id])
            return await ctx.send(msg)
        if not original_idol:
            msg = await self.ex.get_msg(ctx, "botmod", "no_idol_found", ["result", original_idol])
            return await ctx.send(msg)
        for group_id in duplicate_idol.groups:
            await asyncio.sleep(0)
            if group_id not in original_idol.groups:
                # add groups from dupe to original.
                await self.ex.conn.execute(
                    "UPDATE groupmembers.idoltogroup SET idolid = $1 WHERE groupid = $2 AND idolid = $3",
                    original_idol.id, group_id, duplicate_idol.id)
        # delete idol
        await self.ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", duplicate_idol.id)
        # recreate cache
        await self.ex.u_cache.create_idol_cache()
        await self.ex.u_cache.create_group_cache()
        msg = await self.ex.get_msg(ctx, "botmod", "merge_success", [["result", duplicate_idol_id],
                                                                     ["result2", original_idol_id]])
        await ctx.send(msg)

    @commands.command()
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
            msg = await self.ex.get_msg(ctx, "botmod", "no_group_found", ["result", duplicate_group_id])
            return await ctx.send(msg)
        if not original_group:
            msg = await self.ex.get_msg(ctx, "botmod", "no_group_found", ["result", original_group_id])
            return await ctx.send(msg)
        # move aliases
        await self.ex.conn.execute(
            "UPDATE groupmembers.aliases SET objectid = $1 WHERE isgroup = $2 AND objectid = $3",
            original_group.id, 1, duplicate_group.id)
        for member_id in duplicate_group.members:
            await asyncio.sleep(0)
            if member_id not in original_group.members:
                # update the member location to the original group
                await self.ex.conn.execute(
                    "UPDATE groupmembers.idoltogroup SET groupid = $1 WHERE idolid = $2 AND groupid = $3",
                    original_group.id, member_id, duplicate_group.id)
        # delete group
        await self.ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", duplicate_group.id)
        # recreate cache
        await self.ex.u_cache.create_idol_cache()
        await self.ex.u_cache.create_group_cache()
        msg = await self.ex.get_msg(ctx, "botmod", "merge_success", [["result", duplicate_group_id],
                                                                     ["result2", original_group_id]])
        await ctx.send(msg)

    @commands.command()
    async def killapi(self, ctx):
        """
        Restarts the API.

        [Format: %killapi]
        """
        msg = await self.ex.get_msg(ctx, "botmod", "api_restart")
        await ctx.send(msg)
        await self.ex.kill_api()

    @commands.command()
    async def maintenance(self, ctx, *, maintenance_reason=None):
        """
        Enable/Disable Maintenance Mode.

        [Format: %maintenance (reason)]
        """
        self.ex.cache.maintenance_mode = not self.ex.cache.maintenance_mode
        self.ex.cache.maintenance_reason = maintenance_reason

        msg = await self.ex.get_msg(ctx, "botmod", "maintenance_mode", ["result", self.ex.cache.maintenance_mode])
        return await ctx.send(msg)

    @commands.command()
    async def botwarn(self, ctx, user: discord.User, *, reason=None):
        """
        Warns a user from Irene's DMs

        [Format: %botwarn (user id) <reason>]
        """
        msg = await self.ex.get_msg(ctx, "botmod", "warn", [
            ["mention", ctx.author.id], ["support_server_link", self.ex.keys.bot_support_server_link]])
        dm_channel = await self.ex.get_dm_channel(user.id)
        if not dm_channel:
            msg = await self.ex.get_msg(ctx, "botmod", "dm_channel_not_found", ["mention", user.id])
            return await ctx.send(msg)
        try:
            await dm_channel.send(msg)
            msg = await self.ex.get_msg(ctx, "botmod", "message_to_user", ["mention", user.id])
            return await ctx.send(msg)
        except:
            msg = await self.ex.get_msg(ctx, "botmod", "no_permission", ["mention", user.id])
            return await ctx.send(msg)

    @commands.command()
    async def kill(self, ctx):
        """
        Kills the bot

        [Format: %kill]
        """
        await ctx.send(await self.ex.get_msg(ctx, "botmod", "bot_killed"))

        message = await self.ex.get_msg(ctx, "botmod", "restarting_msg")

        def get_games():
            # create copies to not have dictionary changed during iteration issue.
            gg_copy = self.ex.cache.guessing_games.copy()
            bg_copy = self.ex.cache.bias_games.copy()
            bj_copy = self.ex.cache.blackjack_games.copy()
            us_copy = self.ex.cache.unscramble_games.copy()

            for existing_game in gg_copy.values():
                yield existing_game
            for existing_game in bg_copy.values():
                yield existing_game
            for existing_game in us_copy.values():
                yield existing_game
            for existing_game in bj_copy:
                yield existing_game

        for game in get_games():
            try:
                await game.end_game()
                log.console(f"Closed the game in {game.channel.id}.")
                await game.channel.send(message)
            except Exception as e:
                log.console(f"Failed to close the game in {game.channel.id}")
                log.useless(f"{e} (Exception) - Failed to close game", method=self.kill)

        try:
            await self.ex.conn.terminate()  # close all db connections.
            log.console("Closed all DB Connections.")
        except Exception as e:
            log.console("Failed to close all DB Connections.")
            log.useless(f"{e} (Exception) - Failed to close DB Connections", method=self.kill)

        try:
            await self.ex.session.close()  # close the aiohttp client session.
            log.console("Closed the aiohttp session")
        except Exception as e:
            log.console("Failed to cose the aiohttp Client Session.")
            log.useless(f"{e} (Exception) - Failed to close Web Session", method=self.kill)

        try:
            await self.ex.client.logout()  # log out of bot.
            log.console("Logged out of the bot.")
        except Exception as e:
            log.console("Failed to log out of the bot.")
            log.useless(f"{e} (Exception) - Failed to log out of bot.", method=self.kill)

        tasks = asyncio.Task.all_tasks()
        pending = [task for task in tasks if not task.done()]
        for task in pending:
            if not task.done():
                log.console(f"Cancelling {task}")
                task.cancel()

        # we do not want any extra background tasks to still exist
        # so the auto restarter can instantly boot the bot back up
        exit(0)

    @commands.command()
    async def addinteraction(self, ctx, interaction_type, *, links):
        """
        Add a gif/photo to an interaction (ex: slap,kiss,lick,hug)

        [Format: %addinteraction (interaction) (url,url)]
        """
        links = links.split(',')
        try:
            if interaction_type.lower() in self.ex.cache.interaction_list:
                for url in links:
                    await asyncio.sleep(0)
                    url = url.replace(' ', '')
                    url = url.replace('\n', '')
                    await self.ex.conn.execute(
                        "INSERT INTO general.interactions(url, interaction) VALUES ($1, $2)",
                        url, interaction_type.lower())
                    embed = discord.Embed(
                        title=f"**Added {url} to {interaction_type.lower()}**", color=self.ex.get_random_color())
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("> **Please choose a proper interaction.**")
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "gen_error", ["e", f"{e}"]))
            log.console(e)

    @commands.command()
    async def deleteinteraction(self, ctx, *, url):
        """
        Delete a url from an interaction

        [Format: %deleteinteraction (url,url)]
        """
        links = url.split(',')
        for url in links:
            await asyncio.sleep(0)
            try:
                url.replace(' ', '')
                url = url.replace('\n', '')
                await self.ex.conn.execute("DELETE FROM general.interactions WHERE url = $1", url)
                await ctx.send(await self.ex.get_msg(ctx, "botmod", "interaction_removed", ["link", url]))
            except Exception as e:
                log.useless(f"{e} (Exception) - Failed to delete interaction.", self.deleteinteraction)
        await ctx.send(await self.ex.get_msg(ctx, "botmod", "interactions_removed"))

    @commands.command()
    async def botban(self, ctx, *, user: discord.User):
        """
        Bans a user from Irene.

        [Format: %botban (user id)]
        """
        if not self.ex.check_if_mod(user.id):
            await self.ex.u_miscellaneous.ban_user_from_bot(user.id)
            await ctx.send(f"> **<@{user.id}> has been banned from using Irene.**")
            await ctx.send(await self.ex.get_msg(ctx, "botmod", "bot_banned", ["mention", user.id]))
        else:
            await ctx.send(await self.ex.get_msg(ctx, "botmod", "ban_bot_mod", ["mention", ctx.author.id]))

    @commands.command()
    async def botunban(self, ctx, *, user: discord.User):
        """
        UnBans a user from Irene.

        [Format: %botunban (user id)]
        """
        await self.ex.u_miscellaneous.unban_user_from_bot(user.id)
        await ctx.send(await self.ex.get_msg(ctx, "botmod", "bot_unbanned"))

    @commands.command()
    async def addstatus(self, ctx, *, status: str):
        """
        Add a playing status to Irene.

        [Format: %addstatus (status)]
        """
        await self.ex.conn.execute("INSERT INTO general.botstatus (status) VALUES ($1)", status)
        self.ex.cache.bot_statuses.append(status)
        await self.ex.get_msg(ctx, "botmod", "status_added", ["result", status])

    @commands.command()
    async def getstatuses(self, ctx):
        """Get all statuses of Irene."""
        final_list = ""
        if self.ex.cache.bot_statuses:
            counter = 0
            for status in self.ex.cache.bot_statuses:
                await asyncio.sleep(0)
                final_list += f"{counter}) {status}\n"
                counter += 1
        else:
            final_list = "None"
        embed = discord.Embed(title="Statuses", description=final_list)
        await ctx.send(embed=embed)

    @commands.command()
    async def removestatus(self, ctx, status_index: int):
        """
        Remove a status based on it's index. The index can be found using %getstatuses.

        [Format: %removestatus (status index)]
        """
        try:
            status = self.ex.cache.bot_statuses[status_index]
            await self.ex.conn.execute("DELETE FROM general.botstatus WHERE status = $1", status)
            self.ex.cache.bot_statuses.pop(status_index)
            await ctx.send(await self.ex.get_msg(ctx, "botmod", "result", ["result", status]))
        except Exception as e:
            log.console(e)
            await ctx.send(e)

    @commands.command(aliases=['removeidol'])
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
            await ctx.send(await self.ex.get_msg(ctx, "general", "gen_error", ["e", e]))
            log.console(e)

    @commands.command(aliases=['removegroup'])
    async def deletegroup(self, ctx, group_id: int):
        """
        Deletes a group

        [Format: %deletegroup (group id)]
        """
        try:
            await self.ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", group_id)
            await ctx.send(f"{(await self.ex.u_group_members.get_group(group_id)).name} ({group_id}) deleted.")
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "gen_error", ["e", e]))
            log.console(e)

    @commands.command()
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
                await self.ex.conn.execute(
                    "INSERT INTO general.modmail(userid, channelid) VALUES ($1, $2)", user.id, ctx.channel.id)
                await dm_channel.send(
                    f"> {ctx.author.display_name} ({ctx.author.id}) has created a DM with you. "
                    f"All messages sent here will be sent to them.")
                await ctx.send(
                    f"> A DM has been created with {user.id}. "
                    f"All messages you type in this channel will be sent to the user.")
            else:
                await ctx.send("> I was not able to create a DM with that user.")
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "gen_error", ["e", e]))
            log.console(e)

    @commands.command()
    async def closedm(self, ctx, user: discord.User = None):
        """
        Closes a DM either by the User ID or by the current channel.

        [Format: %closedm <user id>]
        """
        try:
            if user:
                user_id = user.id
            else:
                user_id = self.ex.first_result(await self.ex.conn.fetchrow(
                    "SELECT userid FROM general.modmail WHERE channelid = $1", ctx.channel.id))
            dm_channel = await self.ex.get_dm_channel(user_id)
            if not dm_channel:
                return await ctx.send("> **There are no DMs set up in this channel.**")
            user = await self.ex.get_user(user_id)
            user.mod_mail_channel_id = 0
            self.ex.cache.mod_mail.pop(user_id, None)  # full list
            await self.ex.conn.execute(
                "DELETE FROM general.modmail WHERE userid = $1 and channelid = $2", user_id, ctx.channel.id)
            await ctx.send(f"> The DM with {user_id} has been deleted successfully.")
            await dm_channel.send(
                f"> {ctx.author.display_name} ({ctx.author.id}) has closed the DM with you. "
                f"Your messages will no longer be sent to them.")
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "gen_error", ["e", e]))
            log.console(e)
