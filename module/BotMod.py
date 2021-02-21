import discord
from discord.ext import commands
from module import logger as log, keys
from Utility import resources as ex
import aiofiles


# noinspection PyBroadException,PyPep8
class BotMod(commands.Cog):
    @staticmethod
    async def mod_mail_on_message(message):
        # mod mail
        try:
            message_sender = message.author
            message_channel = message.channel
            message_content = message.content
            if message_sender.id == keys.bot_id:
                return
            if 'closedm' in message_content or 'createdm' in message_content:
                return
            for user in ex.cache.users.values():
                try:
                    if not user.mod_mail_channel_id:
                        continue
                    channel_id = user.mod_mail_channel_id
                    try:
                        mod_channel = ex.client.get_channel(channel_id)
                    except:
                        mod_channel = await ex.client.fetch_channel(channel_id)

                    dm_channel = await ex.get_dm_channel(message_sender.id)
                    if user.id == message_sender.id:
                        if not dm_channel:
                            continue
                        if message_channel == dm_channel:
                            await mod_channel.send(
                                f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                        if message_channel == mod_channel:
                            await dm_channel.send(
                                f">>> FROM: {message_sender.display_name} ({message_sender.id}) - {message_content}")
                except Exception as e:
                    log.console(f"{e} - Iteration Error in BotMod.mod_mail_on_message")
        except Exception as e:
            log.console(f"{e} - BotMod.mod_mail_on_message")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def weverseauth(self, ctx, token):
        """Updates Weverse Authentication Token without restarting bot.
        Only use this in DMs or a private channel for security purposes.
        [Format %weverseauth <token>]
        """
        keys.weverse_auth_token = token
        ex.weverse_client = ex.WeverseAsync(authorization=keys.weverse_auth_token, web_session=ex.session,
                                            verbose=True, loop=ex.asyncio.get_event_loop())
        await ctx.send("> Token and Weverse client has been updated.")
        await ex.weverse_client.start()

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def moveto(self, ctx, idol_id, link):
        """Moves a link to another idol. (Cannot be used for adding new links)[Format: %moveto (idol id) (link)]"""
        try:
            drive_link = ex.first_result(await ex.conn.fetchrow("SELECT driveurl FROM groupmembers.apiurl WHERE apiurl = $1", link))
            if not drive_link:
                return await ctx.send(f"> **{link} does not have a connection to a google drive link.**")
            await ex.conn.execute("UPDATE groupmembers.imagelinks SET memberid = $1 WHERE link = $2", int(idol_id), drive_link)
            await ctx.send(f"> **Moved {link} to {idol_id} if it existed.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **{e}**")

    @commands.command()
    @commands.is_owner()
    async def approve(self, ctx, query_id: int, mode="idol"):
        """Approve a query id for an unregistered group or idol."""
        if mode == "group":
            # get the query
            group = await ex.conn.fetchrow("""SELECT groupname, debutdate, disbanddate, description, twitter, youtube, 
            melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website, thumbnail, banner,
             gender, tags FROM groupmembers.unregisteredgroups WHERE id = $1""", query_id)

            # create a new group
            await ex.conn.execute("""INSERT INTO groupmembers.groups(groupname, debutdate, disbanddate, description, 
            twitter, youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website,
             thumbnail, banner, gender, tags) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
             $15, $16, $17, $18, $19, $20)""", *group)

            # get the new group's ID
            group_id = ex.first_result(await ex.conn.fetchrow("""SELECT groupid FROM groupmembers.groups WHERE 
            groupname = $1 ORDER BY groupid DESC""", group.get("groupname")))

            # send message to the approver.
            await ctx.send(f"> Added Query ID {query_id} as a Group ({group_id}). "
                           f"The cache is now refreshing.")

        if mode == "idol":
            # get the query
            idol = await ex.conn.fetchrow("""SELECT fullname, stagename, formerfullname, formerstagename, birthdate, 
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify, 
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags
            FROM groupmembers.unregisteredmembers WHERE id = $1""", query_id)

            # make a separate call for group ids to separate the record later for inserting.
            group_ids = ex.first_result(await ex.conn.fetchrow("""SELECT groupids FROM groupmembers.unregisteredmembers WHERE id = $1""", query_id))
            if group_ids:
                group_ids = group_ids.split(',')

            # create a new idol
            await ex.conn.execute("""INSERT INTO groupmembers.member(fullname, stagename, formerfullname, formerstagename, birthdate, 
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify, 
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
             $15, $16, $17, $18, $19, $20, $21 ,$22, $23, $24)""", *idol)

            # get the new idol's ID
            idol_id = ex.first_result(await ex.conn.fetchrow("""SELECT id FROM groupmembers.member WHERE fullname = $1 
            AND stagename = $2 ORDER BY id DESC""", idol.get("fullname"), idol.get("stagename")))

            # create the idol to group relationships.
            for group_id in group_ids:
                try:
                    # check if the group id can be made into an integer when it doesn't have spaces.
                    # fancy way of doing .replace (the attribute doesn't exist)
                    group_id_without_spaces = ("".join(char for char in group_id if char != " "))
                    int(group_id_without_spaces)
                    # if it succeeds, replace the current group id with the version without spaces
                    group_id = int(group_id_without_spaces)
                except:
                    # could not make the group id an integer, it must be a group name.
                    group = await ex.u_group_members.get_group_where_group_matches_name(group_id)
                    if group:
                        # add to the first group found in the list
                        # not accurate, but IDs should have been given anyway.
                        # will be accurate if the full group name is given.
                        group_id = group[0].id
                try:
                    await ex.conn.execute("""INSERT INTO groupmembers.idoltogroup(idolid, groupid) 
                    VALUES($1, $2)""", idol_id, group_id)
                except Exception as e:
                    log.console(e)
                    await ctx.send(f"> Failed to add Group {group_id}. Proceeding to add idol.")

            # send message to the approver.
            await ctx.send(f"> Added Query ID {query_id} as an Idol ({idol_id}). "
                           f"This idol has been added to the following groups: {group_ids}."
                           f" The cache is now refreshing.")

        # reset cache for idols/groups.
        await ex.u_cache.create_group_cache()
        await ex.u_cache.create_idol_cache()

    @commands.command()
    @commands.is_owner()
    async def fixlinks(self, ctx):
        """Fix thumbnails and banners of idols and groups and put them on the host.
        NOTE: this is not an official command is just used momentarily for updates. No reason for this code to be
        simplified and is not a permanent command.
        """
        mem_info = await ex.conn.fetch('SELECT id, thumbnail, banner FROM groupmembers.member')
        grp_info = await ex.conn.fetch('SELECT groupid, thumbnail, banner FROM groupmembers.groups')

        async def download_image(link):
            async with ex.session.get(link) as resp:
                fd = await aiofiles.open(file_loc, mode='wb')
                await fd.write(await resp.read())

        for mem_id, mem_thumbnail, mem_banner in mem_info:
            file_name = f"{mem_id}_IDOL.png"
            if mem_thumbnail:
                file_loc = f"{keys.idol_avatar_location}{file_name}"
                if 'images.irenebot.com' not in mem_thumbnail:
                    await download_image(mem_thumbnail)
                if ex.check_file_exists(file_loc):
                    image_url = f"https://images.irenebot.com/avatar/{file_name}"
                    await ex.conn.execute("UPDATE groupmembers.member SET thumbnail = $1 WHERE id = $2", image_url, mem_id)
            if mem_banner:
                file_loc = f"{keys.idol_banner_location}{file_name}"
                if 'images.irenebot.com' not in mem_banner:
                    await download_image(mem_banner)
                image_url = f"https://images.irenebot.com/banner/{file_name}"
                if ex.check_file_exists(file_loc):
                    await ex.conn.execute("UPDATE groupmembers.member SET banner = $1 WHERE id = $2", image_url, mem_id)
        for grp_id, grp_thumbnail, grp_banner in grp_info:
            file_name = f"{grp_id}_GROUP.png"
            if grp_thumbnail:
                file_loc = f"{keys.idol_avatar_location}{file_name}"
                if 'images.irenebot.com' not in grp_thumbnail:
                    await download_image(grp_thumbnail)
                image_url = f"https://images.irenebot.com/avatar/{file_name}"
                if ex.check_file_exists(file_loc):
                    await ex.conn.execute("UPDATE groupmembers.groups SET thumbnail = $1 WHERE groupid = $2", image_url, grp_id)
            if grp_banner:
                file_loc = f"{keys.idol_banner_location}{file_name}"
                if 'images.irenebot.com' not in grp_banner:
                    await download_image(grp_banner)
                image_url = f"https://images.irenebot.com/banner/{file_name}"
                if ex.check_file_exists(file_loc):
                    await ex.conn.execute("UPDATE groupmembers.groups SET banner = $1 WHERE groupid = $2", image_url, grp_id)
        return await ctx.send("> All images have been fixed, merged to image hosting service and have links set up for them.")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def mergeidol(self, ctx, original_idol_id: int, duplicate_idol_id: int):
        """Merge a duplicated idol with it's original idol.
        CAUTION: All aliases and are moved to the original idol, idol information is left alone
        If a group ID is not in the original idol, it will be added and then the dupe idol will be deleted along with
        all of it's connections.
        [Format: %mergeidol (original idol id) (duplicate idol id)]"""
        # check groups
        original_idol = await ex.u_group_members.get_member(original_idol_id)
        duplicate_idol = await ex.u_group_members.get_member(duplicate_idol_id)

        if not duplicate_idol:
            return await ctx.send(f"> {duplicate_idol_id} could not find an Idol.")
        if not original_idol:
            return await ctx.send(f"> {original_idol} could not find an Idol.")
        for group_id in duplicate_idol.groups:
            if group_id not in original_idol.groups:
                # add groups from dupe to original.
                await ex.conn.execute("UPDATE groupmembers.idoltogroup SET idolid = $1 WHERE groupid = $2 AND idolid = $3", original_idol.id, group_id, duplicate_idol.id)
        # delete idol
        await ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", duplicate_idol.id)
        # recreate cache
        await ex.u_cache.create_idol_cache()
        await ex.u_cache.create_group_cache()
        await ctx.send(f"> Merged {duplicate_idol_id} to {original_idol_id}.")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def mergegroup(self, ctx, original_group_id: int, duplicate_group_id: int):
        """Merge a duplicated group with it's original group.
        CAUTION: All aliases and are moved to the original group, group information is left alone
        If an idol ID is not in the original group, it will be added and then this group will be deleted along with
        all of it's connections.
        [Format: %mergegroup (original group id) (duplicate group id)]"""
        original_group = await ex.u_group_members.get_group(original_group_id)
        duplicate_group = await ex.u_group_members.get_group(duplicate_group_id)
        if not duplicate_group:
            return await ctx.send(f"> {duplicate_group_id} could not find a Group.")
        if not original_group:
            return await ctx.send(f"> {original_group} could not find a Group.")
        # move aliases
        await ex.conn.execute("UPDATE groupmembers.aliases SET objectid = $1 WHERE isgroup = $2 AND objectid = $3", original_group.id, 1, duplicate_group.id)
        for member_id in duplicate_group.members:
            if member_id not in original_group.members:
                # update the member location to the original group
                await ex.conn.execute("UPDATE groupmembers.idoltogroup SET groupid = $1 WHERE idolid = $2 AND groupid = $3", original_group.id, member_id, duplicate_group.id)
        # delete group
        await ex.conn.execute("DELETE FROM groupmembers.groups WHERE groupid = $1", duplicate_group.id)
        # recreate cache
        await ex.u_cache.create_idol_cache()
        await ex.u_cache.create_group_cache()
        await ctx.send(f"> Merged {duplicate_group_id} to {original_group_id}.")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def killapi(self, ctx):
        """Restarts the API. [Format: %killapi]"""
        await ctx.send("> Restarting the API.")
        message = f"Irene is restarting. All games will be stopped."
        for game in ex.cache.bias_games:
            await game.channel.send(message)
        for game in ex.cache.guessing_games:
            await game.channel.send(message)
        await ex.kill_api()

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def maintenance(self, ctx, *, maintenance_reason=None):
        """Enable/Disable Maintenance Mode. [Format: %maintenance (reason)]"""
        ex.cache.maintenance_mode = not ex.cache.maintenance_mode
        ex.cache.maintenance_reason = maintenance_reason

        return await ctx.send(f"> **Maintenance mode is set to {ex.cache.maintenance_mode}.**")

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
        if not dm_channel:
            return await ctx.send(f"> Could not find <@{user.id}>'s DM channel.")
        try:
            await dm_channel.send(message)
            return await ctx.send(f"> **Message was sent to <@{user.id}>**")
        except:
            return await ctx.send(f"> I do not have permission to send a message to <@{user.id}>")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def kill(self, ctx):
        """Kills the bot [Format: %kill]"""
        await ctx.send("> **The bot is now offline.**")
        message = "Irene is restarting... All games in this channel will force-end."
        for game in ex.cache.bias_games:
            try:
                await game.channel.send(message)
            except:
                pass
        for game in ex.cache.guessing_games:
            try:
                await game.channel.send(message)
            except:
                pass
        await ex.session.close()  # close the aiohttp client session.
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
            except:
                pass
        await ctx.send("Finished.")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botban(self, ctx, *, user: discord.User):
        """Bans a user from Irene. [Format: %botban (user id)]"""
        if not ex.check_if_mod(user.id, 1):
            await ex.u_miscellaneous.ban_user_from_bot(user.id)
            await ctx.send(f"> **<@{user.id}> has been banned from using Irene.**")
        else:
            await ctx.send(f"> **<@{ctx.author.id}>, you cannot ban a bot mod.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def botunban(self, ctx, *, user: discord.User):
        """UnBans a user from Irene. [Format: %botunban (user id)]"""
        await ex.u_miscellaneous.unban_user_from_bot(user.id)
        await ctx.send(f"> **If the user was banned, they are now unbanned.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addstatus(self, ctx, *, status: str):
        """Add a playing status to Irene. [Format: %addstatus (status)]"""
        await ex.conn.execute("INSERT INTO general.botstatus (status) VALUES ($1)", status)
        ex.cache.bot_statuses.append(status)
        await ctx.send(f"> **{status} was added.**")

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def getstatuses(self, ctx):
        """Get all statuses of Irene."""
        final_list = ""
        if ex.cache.bot_statuses:
            counter = 0
            for status in ex.cache.bot_statuses:
                final_list += f"{counter}) {status}\n"
                counter += 1
        else:
            final_list = "None"
        embed = discord.Embed(title="Statuses", description=final_list)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def removestatus(self, ctx, status_index: int):
        """Remove a status based on it's index. The index can be found using %getstatuses.
        [Format: %removestatus (status index)]"""
        try:
            status = ex.cache.bot_statuses[status_index]
            await ex.conn.execute("DELETE FROM general.botstatus WHERE status = $1", status)
            ex.cache.bot_statuses.pop(status_index)
            await ctx.send(f"> {status} was removed from the bot statuses.")
        except Exception as e:
            log.console(e)
            await ctx.send(e)

    @commands.command()
    @commands.check(ex.check_if_mod)
    async def addidoltogroup(self, ctx, idol_id: int, group_id: int):
        """Adds idol to group. [Format: %addidoltogroup (idol id) (group id)"""
        try:
            member_name = (await ex.u_group_members.get_member(idol_id))[1]
            group_name = await ex.get_group_name(group_id)
            if await ex.check_member_in_group(idol_id, group_id):
                return await ctx.send(f'> **{member_name} ({idol_id}) is already in {group_name} ({group_id}).**')
            else:
                await ex.u_group_members.add_idol_to_group(idol_id, group_id)
                await ctx.send(f"**Added {member_name} ({idol_id}) to {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidolfromgroup'])
    @commands.check(ex.check_if_mod)
    async def deleteidolfromgroup(self, ctx, idol_id: int, group_id: int):
        """Deletes idol from group. [Format: %deleteidolfromgroup (idol id) (group id)"""
        try:
            member_name = (await ex.u_group_members.get_member(idol_id))[1]
            group_name = await ex.get_group_name(group_id)
            if not await ex.check_member_in_group(idol_id, group_id):
                await ctx.send(f"> **{member_name} ({idol_id}) is not in {group_name} ({group_id}).**")
            else:
                await ex.u_group_members.remove_idol_from_group(idol_id, group_id)
                await ctx.send(f"**Removed {member_name} ({idol_id}) from {group_name} ({group_id}).**")
        except Exception as e:
            await ctx.send(f"Something went wrong - {e}")
            log.console(e)

    @commands.command(aliases=['removeidol'])
    @commands.check(ex.check_if_mod)
    async def deleteidol(self, ctx, idol_id: int):
        """Deletes an idol [Format: %deleteidol (idol id)]"""
        try:
            idol_name = (await ex.u_group_members.get_member(idol_id))[1]
            await ex.conn.execute("DELETE FROM groupmembers.member WHERE id = $1", idol_id)
            await ctx.send(f"{idol_name} ({idol_id}) deleted.")
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
            if dm_channel:
                user = await ex.get_user(user.id)
                user.mod_mail_channel_id = ctx.channel.id
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
            if user:
                user_id = user.id
            else:
                user_id = ex.first_result(await ex.conn.fetchrow("SELECT userid FROM general.modmail WHERE channelid = $1", ctx.channel.id))
            dm_channel = await ex.get_dm_channel(user_id)
            if not dm_channel:
                return await ctx.send("> **There are no DMs set up in this channel.**")
            user = await ex.get_user(user_id)
            user.mod_mail_channel_id = None
            await ex.conn.execute("DELETE FROM general.modmail WHERE userid = $1 and channelid = $2", user_id, ctx.channel.id)
            await ctx.send(f"> The DM with {user_id} has been deleted successfully.")
            await dm_channel.send(f"> {ctx.author.display_name} ({ctx.author.id}) has closed the DM with you. Your messages will no longer be sent to them.")
        except Exception as e:
            await ctx.send(f"ERROR - {e}")
            log.console(e)




