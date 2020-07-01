import discord
from discord.ext import commands
from module import logger as log
from Utility import resources as ex


class BotMod(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botban(self, ctx, *, user: discord.Member):
        """Bans a user from Irene. [Format: %botban (user id)]"""
        user_id = user.id
        if not ex.check_if_mod(user_id, 1):
            await ex.ban_user_from_bot(user_id)
            await ctx.send(f"> **<@{user_id}> has been banned from using Irene.**")
        else:
            await ctx.send(f"> **<@{ctx.author.id}>, you cannot ban a bot mod.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botunban(self, ctx, *, user: discord.Member):
        """UnBans a user from Irene. [Format: %botunban (user id)]"""
        user_id = user.id
        await ex.unban_user_from_bot(user_id)
        await ctx.send(f"> **If the user was banned, they are now unbanned.**")


    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addstatus(self, ctx, *, status: str):
        """Add a playing status to Irene. [Format: %addstatus (status)]"""
        ex.c.execute("INSERT INTO general.botstatus (status) VALUES (%s)", (status,))
        ex.DBconn.commit()
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
    async def addalias(self, ctx, alias, mem_id, mode="idol"):
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
                ex.c.execute(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = %s", (mem_id,))
                counter = ex.fetch_one()
                if counter == 0:
                    await ctx.send("> **That ID does not exist.**")
                else:
                    ex.c.execute(f"SELECT aliases FROM groupmembers.{mode} WHERE {param} = %s", (mem_id,))
                    current_aliases = ex.fetch_one()
                    if current_aliases is None:
                        new_aliases = alias.lower()
                    else:
                        new_aliases = f"{current_aliases},{alias.lower()}"
                    ex.c.execute(f"UPDATE groupmembers.{mode} SET aliases = %s WHERE {param} = %s", (new_aliases, mem_id))
                    ex.DBconn.commit()
                    await ctx.send(f"> **Added Alias: {alias} to {mem_id}**")
            except Exception as e:
                await ctx.send(e)
                log.console(e)

    @commands.command(aliases=['removealias'])
    @commands.check(ex.check_if_mod)
    async def deletealias(self, ctx, alias, mem_id, mode="idol"):
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
                ex.c.execute(f"SELECT COUNT(*) FROM groupmembers.{mode} WHERE {param} = %s", (mem_id,))
                count = ex.fetch_one()
                if count == 0:
                    await ctx.send("> **That ID does not exist.**")
                else:
                    ex.c.execute(f"SELECT Aliases FROM groupmembers.{mode} WHERE {param} = %s", (mem_id,))
                    current_aliases = ex.fetch_one()
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
                                ex.c.execute(f"UPDATE groupmembers.{mode} SET aliases = NULL WHERE {param} = %s", (mem_id,))
                            else:
                                ex.c.execute(f"UPDATE groupmembers.{mode} SET aliases = %s WHERE {param} = %s", (new_aliases, mem_id))
                            ex.DBconn.commit()
                            await ctx.send(f"> **Alias: {alias} was removed from {mem_id}.**")
            except Exception as e:
                await ctx.send(e)
                log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidoltogroup(self, ctx, idol_id, group_id):
        """Adds idol to group. [Format: %addidoltogroup (idol id) (group id)"""
        try:
            ex.c.execute("SELECT ingroups from groupmembers.member WHERE id = %s", (idol_id,))
            in_groups = ex.fetch_one()
            if in_groups is None:
                ex.c.execute("UPDATE groupmembers.member SET ingroups = %s WHERE id = %s", (group_id, idol_id))
            else:
                in_groups += f",{group_id}"
                ex.c.execute("UPDATE groupmembers.member SET ingroups = %s WHERE id = %s", (in_groups, idol_id))
            ex.DBconn.commit()
            await ctx.send(f"**Added {(await ex.get_member(idol_id))[1]} to {await ex.get_group_name(group_id)}.**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidolfromgroup'])
    @commands.check(ex.check_if_mod)
    async def deleteidolfromgroup(self, ctx, idol_id, group_id):
        """Deletes idol from group. [Format: %deleteidolfromgroup (idol id) (group id)"""
        try:
            ex.c.execute("SELECT ingroups from groupmembers.member WHERE id = %s", (idol_id,))
            in_groups = ex.fetch_one()
            in_groups_split = in_groups.split(',')
            if group_id not in in_groups_split:
                await ctx.send(f"> **{(await ex.get_member(idol_id))[1]} is not in that group.**")
            else:
                in_groups_split.remove(group_id)
                if len(in_groups_split) == 0:
                    in_groups = "2"  # NULL
                else:
                    in_groups = ','.join(in_groups_split)
                ex.c.execute("UPDATE groupmembers.member SET ingroups = %s WHERE id = %s", (in_groups, idol_id))
                ex.DBconn.commit()
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
            ex.c.execute("INSERT INTO groupmembers.member (fullname, stagename, ingroups) VALUES(%s, %s, %s)", (full_name, stage_name, group_id))
            ex.DBconn.commit()
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
            ex.c.execute("DELETE FROM groupmembers.members WHERE id = %s", (idol_id,))
            ex.DBconn.commit()
            await ctx.send(f"{idol_name} ({idol_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addgroup(self, ctx, *, group_name):
        """Adds a group [Format: %addgroup (group name)]"""
        try:
            ex.c.execute("INSERT INTO groupmembers.groups (groupname) VALUES(%s)", (group_name,))
            ex.DBconn.commit()
            await ctx.send(f"{group_name} was added.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removegroup'])
    @commands.check(ex.check_if_mod)
    async def deletegroup(self, ctx, group_id):
        """Deletes a group [Format: %deletegroup (group id)]"""
        try:
            ex.c.execute("DELETE FROM groupmembers.groups WHERE groupid = %s", (group_id,))
            ex.DBconn.commit()
            await ctx.send(f"{await ex.get_group_name(group_id)} ({group_id}) deleted.")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)
