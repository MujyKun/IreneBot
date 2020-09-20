import discord
from discord.ext import commands
from module import logger as log, keys
import module
from Utility import resources as ex


class BotMod(commands.Cog):
    @staticmethod
    async def mod_on_message(message):
        message_sender = message.author
        message_channel = message.channel
        message_content = message.content
        if message_sender.id != keys.bot_id:
            if 'closedm' not in message_content and 'createdm' not in message_content:
                dm_channel = await ex.get_dm_channel(message_sender.id)
                if dm_channel is not None:
                    for user_id in ex.cache.mod_mail:
                        channel_id = ex.cache.mod_mail.get(user_id)
                        mod_channel = await ex.client.fetch_channel(channel_id)
                        if user_id == message_sender.id and message_channel == dm_channel:
                            await mod_channel.send(f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                        if mod_channel == message_channel:
                            dm_channel = await ex.get_dm_channel(user_id)
                            await dm_channel.send(f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botwarn(self, ctx, user: discord.User, *, reason=None):
        """Warns a user from Irene's DMs [Format: %botwarn (user id) <reason>]"""
        message = f"""
**You have been warned by <@{ctx.author.id}>.**
**Please be aware that you may get banned from the bot if this behavior is repeated numerous times.**
**Reason:** {reason}
Have questions? Join the support server at {keys.bot_support_server_link}."""
        dm_channel = await ex.get_dm_channel(user.id)
        await dm_channel.send(message)
        await ctx.send(f"> **Message was sent to <@{user.id}>**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def deletelink(self, ctx, link):
        """Removes a link from an idol. [Format: %deletelink (link)]"""
        try:
            await ex.conn.execute("DELETE FROM groupmembers.imagelinks WHERE link = $1", link)
            await ctx.send(f"> **Deleted {link} if it existed.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{e}**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def moveto(self, ctx, idol_id, link):
        """Moves a link to another idol. (Cannot be used for adding new links)[Format: %moveto (idol id) (link)]"""
        try:
            await ex.conn.execute("UPDATE groupmembers.imagelinks SET memberid = $1 WHERE link = $2", int(idol_id), link)
            await ctx.send(f"> **Moved {link} to {idol_id} if it existed.")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{e}**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def repost(self, ctx, post_number):
        """Reposts a certain post from the DC APP to all channels. [Format: %repost post_number]"""
        await ctx.send(f"> **Reposting...**")
        await module.DreamCatcher.DcApp().check_dc_post(post_number, repost=True, test=False)
        await ctx.send(f"> **Successfully reposted to all channels.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def kill(self, ctx):
        """Kills the bot [Format: %kill]"""
        await ctx.send("> **The bot is now offline.**")
        await ex.client.logout()

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addinteraction(self, ctx, interaction_type, *, links):
        """Add a gif/photo to an interaction (ex: slap,kiss,lick,hug) [Format: %addinteraction (interaction) (url,url)"""
        links = links.split(',')
        try:
            if interaction_type.lower() in keys.interaction_list:
                for url in links:
                    url = url.replace(' ', '')
                    url = url.replace('\n', '')
                    await ex.conn.execute("INSERT INTO general.interactions(url, interaction) VALUES ($1, $2)", url, interaction_type.lower())
                    embed = discord.Embed(title=f"**Added {url} to {interaction_type.lower()}**", color=ex.get_random_color())
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f"> **Please choose a proper interaction.**")
        except Exception as e:
            await ctx.send(f"**ERROR -** {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def deleteinteraction(self, ctx, *, url):
        """Delete a url from an interaction [Format: %deleteinteraction (url,url)"""
        links = url.split(',')
        for url in links:
            try:
                url.replace(' ', '')
                url = url.replace('\n', '')
                await ex.conn.execute("DELETE FROM general.interactions WHERE url = $1", url)
                await ctx.send(f"Removed <{url}>")
            except Exception as e:
                pass
        await ctx.send("Finished.")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botban(self, ctx, *, user: discord.User):
        """Bans a user from Irene. [Format: %botban (user id)]"""
        user_id = user.id
        if not ex.check_if_mod(user_id, 1):
            await ex.ban_user_from_bot(user_id)
            await ctx.send(f"> **<@{user_id}> has been banned from using Irene.**")
        else:
            await ctx.send(f"> **<@{ctx.author.id}>, you cannot ban a bot mod.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botunban(self, ctx, *, user: discord.User):
        """UnBans a user from Irene. [Format: %botunban (user id)]"""
        user_id = user.id
        await ex.unban_user_from_bot(user_id)
        await ctx.send(f"> **If the user was banned, they are now unbanned.**")


    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addstatus(self, ctx, *, status: str):
        """Add a playing status to Irene. [Format: %addstatus (status)]"""
        await ex.conn.execute("INSERT INTO general.botstatus (status) VALUES ($1)", status)
        await ctx.send(f"> **{status} was added.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def getstatuses(self, ctx):
        """Get all statuses of Irene."""
        final_list = ""
        statuses = await ex.get_bot_statuses()
        if statuses is not None:
            for status in await ex.get_bot_statuses():
                final_list += f"{status[0]}\n"
        else:
            final_list = "None"
        embed = discord.Embed(title="Statuses", description=final_list)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addalias(self, ctx, alias, mem_id: int, mode="idol"):
        """Add alias to an idol/group (Underscores are spaces)[Format: %addalias (alias) (ID of idol/group) ("idol" or "group"]"""
        alias = alias.replace("_", " ")
        if mode.lower() == "idol":
            mode = "member"
            param = "id"
            is_group = False
        elif mode.lower() == "group":
            mode = "groups"
            param = "groupid"
            is_group = True
        else:
            return await ctx.send("> **Please specify 'idol' or 'group'**.")
        try:
            id_exists = ex.first_result(await ex.conn.fetchrow(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
            if id_exists == 0:
                return await ctx.send(f"> **That ID ({mem_id}) does not exist.**")
            else:
                # check if the alias already exists, if not, add it
                aliases = await ex.get_aliases(object_id=mem_id, group=is_group)
                if alias not in aliases:
                    await ex.conn.execute("INSERT INTO groupmembers.aliases(objectid, alias, isgroup) VALUES ($1, $2, $3)", mem_id, alias.lower(), int(is_group))
                    await ctx.send(f"> **Added Alias: {alias} to {mem_id}**")
                else:
                    return await ctx.send(f"> **{alias} already exists with {mem_id}.**")
        except Exception as e:
            await ctx.send(e)
            log.console(e)

    @commands.command(aliases=['removealias'])
    @commands.check(ex.check_if_mod)
    async def deletealias(self, ctx, alias, mem_id: int, mode="idol"):
        """Remove alias from an idol/group (Underscores are spaces)[Format: %deletealias (alias) (ID of idol/group) ("idol" or "group")]"""
        alias = alias.replace("_", " ")
        if mode.lower() == "idol":
            mode = "member"
            param = "id"
            is_group = False
        elif mode.lower() == "group":
            mode = "groups"
            param = "groupid"
            is_group = True
        else:
            return await ctx.send("> **Please specify 'idol' or 'group'**.")
        try:
            id_exists = ex.first_result(await ex.conn.fetchrow(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
            if id_exists == 0:
                return await ctx.send("> **That ID does not exist.**")
            else:
                # check if the alias exists, if it does delete it.
                aliases = await ex.get_aliases(object_id=mem_id, group=is_group)
                if alias in aliases:
                    await ex.conn.execute("DELETE FROM groupmembers.aliases WHERE objectid = $1 AND alias = $2 AND isgroup = $3", mem_id, alias.lower(), int(is_group))
                    return await ctx.send(f"> **Alias: {alias} was removed from {mem_id}.**")
                else:
                    return await ctx.send(f"> **Could not find alias: {alias}**")
        except Exception as e:
            await ctx.send(e)
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidoltogroup(self, ctx, idol_id: int, group_id: int):
        """Adds idol to group. [Format: %addidoltogroup (idol id) (group id)"""
        try:
            member_name = (await ex.get_member(idol_id))[1]
            group_name = await ex.get_group_name(group_id)
            if await ex.check_member_in_group(idol_id, group_id):
                return await ctx.send(f'> **{member_name} ({idol_id}) is already in {group_name} ({group_id}).**')
            else:
                await ex.add_idol_to_group(idol_id, group_id)
                await ctx.send(f"**Added {member_name} ({idol_id}) to {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidolfromgroup'])
    @commands.check(ex.check_if_mod)
    async def deleteidolfromgroup(self, ctx, idol_id: int, group_id: int):
        """Deletes idol from group. [Format: %deleteidolfromgroup (idol id) (group id)"""
        try:
            member_name = (await ex.get_member(idol_id))[1]
            group_name = await ex.get_group_name(group_id)
            if not await ex.check_member_in_group(idol_id, group_id):
                await ctx.send(f"> **{member_name} ({idol_id}) is not in {group_name} ({group_id}).**")
            else:
                await ex.remove_idol_from_group(idol_id, group_id)
                await ctx.send(f"**Removed {member_name} ({idol_id}) from {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidol(self, ctx, full_name, stage_name, group_id: int):
        """Adds an idol (Use underscores for spaces)[Format: %addidol (full name) (stage name) (group id)]"""
        full_name = full_name.replace('_', ' ')
        stage_name = stage_name.replace('_', ' ')
        try:
            group_name = await ex.get_group_name(group_id)
            await ex.conn.execute("INSERT INTO groupmembers.member (fullname, stagename) VALUES($1, $2)", full_name, stage_name)
            idol_id = await ex.get_idol_id_by_both_names(full_name, stage_name)
            await ex.add_idol_to_group(idol_id, group_id)
            await ctx.send(f"{full_name} was added and is in {group_name} ({group_id}).")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidol'])
    @commands.check(ex.check_if_mod)
    async def deleteidol(self, ctx, idol_id: int):
        """Deletes an idol [Format: %deleteidol (idol id)]"""
        try:
            idol_name = (await ex.get_member(idol_id))[1]
            await ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", idol_id)
            await ctx.send(f"{idol_name} ({idol_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addgroup(self, ctx, *, group_name):
        """Adds a group [Format: %addgroup (group name)]"""
        try:
            await ex.conn.execute("INSERT INTO groupmembers.groups (groupname) VALUES($1)", group_name)
            await ctx.send(f"{group_name} was added.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removegroup'])
    @commands.check(ex.check_if_mod)
    async def deletegroup(self, ctx, group_id: int):
        """Deletes a group [Format: %deletegroup (group id)]"""
        try:
            await ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", group_id)
            await ctx.send(f"{await ex.get_group_name(group_id)} ({group_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def createdm(self, ctx, user: discord.User):
        """Create a DM with a user with the bot as a middle man. One user per mod channel.
        [Format: %createdm (user id)]"""
        try:
            dm_channel = await ex.get_dm_channel(user=user)
            if dm_channel is not None:
                ex.cache.mod_mail[user.id] = ctx.channel.id
                await ex.conn.execute("INSERT INTO general.modmail(userid, channelid) VALUES ($1, $2)", user.id, ctx.channel.id)
                await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has created a DM with you. All messages sent here will be sent to them.")
                await ctx.send(f"> A DM has been created with {user.id}. All messages you type in this channel will be sent to the user.")
            else:
                await ctx.send("> I was not able to create a DM with that user.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def closedm(self, ctx, user: discord.User = None):
        """Closes a DM either by the User ID or by the current channel.
        [Format: %closedm <user id>] """
        try:
            if user is not None:
                user_id = user.id
            else:
                user_id = ex.first_result(await ex.conn.fetchrow("SELECT userid FROM general.modmail WHERE channelid = $1", ctx.channel.id))
            dm_channel = await ex.get_dm_channel(user_id)
            if dm_channel is None:
                return await ctx.send("> **There are no DMs set up in this channel.**")
            ex.cache.mod_mail.pop(user_id, None)
            await ex.conn.execute("DELETE FROM general.modmail WHERE userid = $1 and channelid = $2", user_id, ctx.channel.id)
            await ctx.send(f"> The DM has been deleted successfully.")
            await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has closed the DM with you. Your messages will no longer be sent to them.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)



