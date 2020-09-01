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
                    mod_mail = await ex.conn.fetch("SELECT userid, channelid FROM general.modmail")
                    for mail in mod_mail:
                        user_id = mail[0]
                        channel_id = mail[1]
                        mod_channel = await ex.client.fetch_channel(channel_id)
                        if user_id == message_sender.id and message_channel == dm_channel:
                            await mod_channel.send(f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                        if mod_channel == message_channel:
                            dm_channel = await ex.get_dm_channel(user_id)
                            await dm_channel.send(f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")

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
        check = True
        if mode.lower() == "idol":
            mode = "member"
            param = "id"
        elif mode.lower() == "group":
            mode = "groups"
            param = "groupid"
        else:
            await ctx.send("> **Please specify 'idol' or 'group'**.")
            check = False
        if check:
            try:
                counter = ex.first_result(await ex.conn.fetchrow(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
                if counter == 0:
                    await ctx.send("> **That ID does not exist.**")
                else:
                    current_aliases = ex.first_result(await ex.conn.fetchrow(f"SELECT aliases FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
                    if current_aliases is None:
                        new_aliases = alias.lower()
                    else:
                        new_aliases = f"{current_aliases},{alias.lower()}"
                    await ex.conn.execute(f"UPDATE groupmembers.{mode} SET aliases = $1 WHERE {param} = $2", new_aliases, mem_id)
                    await ctx.send(f"> **Added Alias: {alias} to {mem_id}**")
            except Exception as e:
                await ctx.send(e)
                log.console(e)

    @commands.command(aliases=['removealias'])
    @commands.check(ex.check_if_mod)
    async def deletealias(self, ctx, alias, mem_id: int, mode="idol"):
        """Remove alias from an idol/group (Underscores are spaces)[Format: %deletealias (alias) (ID of idol/group) ("idol" or "group")]"""
        alias = alias.replace("_", " ")
        check = True
        if mode.lower() == "idol":
            mode = "member"
            param = "id"
        elif mode.lower() == "group":
            mode = "groups"
            param = "groupid"
        else:
            await ctx.send("> **Please specify 'idol' or 'group'**.")
            check = False
        if check:
            try:
                count = ex.first_result(await ex.conn.fetchrow(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
                if count == 0:
                    await ctx.send("> **That ID does not exist.**")
                else:
                    current_aliases = ex.first_result(await ex.conn.fetchrow(f"SELECT Aliases FROM groupmembers.{mode} WHERE {param} = $1", mem_id))
                    if current_aliases is None:
                        await ctx.send("> **That alias does not exist.**")
                    else:
                        check = current_aliases.find(alias.lower(), 0)
                        if check == -1:
                            await ctx.send(f"> **Could not find alias: {alias}**")
                        else:
                            alias_list = current_aliases.split(',')
                            alias_list.remove(alias.lower())
                            if len(alias_list) == 0:
                                new_aliases = None
                            else:
                                new_aliases = f",".join(alias_list)
                            if new_aliases is None:
                                await ex.conn.execute(f"UPDATE groupmembers.{mode} SET aliases = NULL WHERE {param} = $1", mem_id)
                            else:
                                await ex.conn.execute(f"UPDATE groupmembers.{mode} SET aliases = $1 WHERE {param} = $2", new_aliases, mem_id)
                            await ctx.send(f"> **Alias: {alias} was removed from {mem_id}.**")
            except Exception as e:
                await ctx.send(e)
                log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidoltogroup(self, ctx, idol_id: int, group_id: int):
        """Adds idol to group. [Format: %addidoltogroup (idol id) (group id)"""
        try:
            in_groups = ex.first_result(await ex.conn.fetchrow("SELECT ingroups from groupmembers.member WHERE id = $1", idol_id))
            if in_groups is None:
                await ex.conn.execute("UPDATE groupmembers.member SET ingroups = $1 WHERE id = $2", group_id, idol_id)
            else:
                in_groups += f",{group_id}"
                await ex.conn.execute("UPDATE groupmembers.member SET ingroups = $1 WHERE id = $2", in_groups, idol_id)
            await ctx.send(f"**Added {(await ex.get_member(idol_id))[1]} to {await ex.get_group_name(group_id)}.**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidolfromgroup'])
    @commands.check(ex.check_if_mod)
    async def deleteidolfromgroup(self, ctx, idol_id: int, group_id: int):
        """Deletes idol from group. [Format: %deleteidolfromgroup (idol id) (group id)"""
        try:
            in_groups = ex.first_result(await ex.conn.fetchrow("SELECT ingroups from groupmembers.member WHERE id = $1", idol_id))
            in_groups_split = in_groups.split(',')
            if str(group_id) not in in_groups_split:
                await ctx.send(f"> **{(await ex.get_member(idol_id))[1]} is not in that group.**")
            else:
                in_groups_split.remove(str(group_id))
                if len(in_groups_split) == 0:
                    in_groups = "2"  # NULL
                else:
                    in_groups = ','.join(in_groups_split)
                await ex.conn.execute("UPDATE groupmembers.member SET ingroups = $1 WHERE id = $2", in_groups, idol_id)
                await ctx.send(f"**Removed {(await ex.get_member(idol_id))[1]} from {await ex.get_group_name(group_id)}.**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidol(self, ctx, full_name, stage_name, group_id,):
        """Adds an idol (Use underscores for spaces)[Format: %addidol (full name) (stage name) (group id)]"""
        full_name = full_name.replace('_', ' ')
        stage_name = stage_name.replace('_', ' ')
        try:
            await ex.conn.execute("INSERT INTO groupmembers.member (fullname, stagename, ingroups) VALUES($1, $2, $3)", full_name, stage_name, group_id)
            await ctx.send(f"{full_name} was added.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidol'])
    @commands.check(ex.check_if_mod)
    async def deleteidol(self, ctx, idol_id):
        """Deletes an idol [Format: %deleteidol (idol id)]"""
        try:
            idol_name = (await ex.get_member(idol_id))[1]
            await ex.conn.execute("DELETE FROM groupmembers.members WHERE id = $1", idol_id)
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
    async def deletegroup(self, ctx, group_id):
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
            await ex.conn.execute("DELETE FROM general.modmail WHERE userid = $1 and channelid = $2", user_id, ctx.channel.id)
            await ctx.send(f"> The DM has been deleted successfully.")
            await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has closed the DM with you. Your messages will no longer be sent to them.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)



