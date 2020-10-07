import discord
from discord.ext import commands, tasks
from module import logger as log, events
import random
from module import keys
from Utility import resources as ex
import asyncio
import time
import typing

client = keys.client
patron_message = f"""
As of September 23rd, non-Patrons can only send {keys.idol_post_send_limit} photos a day maximum, as the current host can not reliably handle additional traffic.
You may become a patron for as little as $1 per month in order to send unlimited photos; every Patron contributes to upgrading and maintaining the host.
Please support <@{keys.bot_id}>'s development at {keys.patreon_link}.
Thank You."""


def check_reset_limits():
    if time.time() - ex.cache.commands_used['reset_time'] > 86400:  # 1 day in seconds
        # reset the dict
        ex.cache.commands_used = {"reset_time": time.time()}


def add_user_limit(message_sender):
    if message_sender.id not in ex.cache.commands_used:
        ex.cache.commands_used[message_sender.id] = [1, time.time()]
    else:
        ex.cache.commands_used[message_sender.id] = [ex.cache.commands_used[message_sender.id][0] + 1, time.time()]


async def check_user_limit(message_sender, message_channel):
    if message_sender.id in ex.cache.commands_used:
        if not await ex.check_if_patreon(message_sender.id) and ex.cache.commands_used[message_sender.id][0] > keys.idol_post_send_limit:
            return await message_channel.send(patron_message)
    return False


class GroupMembers(commands.Cog):
    @staticmethod
    async def on_message2(message):
        message_sender = message.author
        message_channel = message.channel
        message_content = message.content
        if not message_sender.bot:
            if not await ex.check_if_temp_channel(message_channel.id):
                if await ex.check_channel_sending_photos(message_channel.id):
                    try:
                        if await ex.check_server_sending_photos(message.guild.id):
                            message_channel = await ex.get_channel_sending_photos(message.guild.id)
                    except Exception as e:
                        pass  # error is guild not found, likely being accessed from DMs
                    posted = False
                    api_url = None
                    try:
                        check_reset_limits()
                        if message_sender.id in ex.cache.commands_used:
                            time_difference = time.time() - ex.cache.commands_used[message_sender.id][1]
                            if time_difference < 2:
                                await asyncio.sleep(1)
                        if ex.check_message_not_empty(message):
                            random_member = False
                            # since this is a listener, the prefix is put back to the default
                            # (from the original on_message)
                            # and we do not need to worry about the user's server prefix for idol photos
                            # we just need to make sure it has the bot's default prefix
                            # however this means if a user changes the prefix and uses the bot's default prefix
                            # it will still process idol photos, but not regular commands.
                            if message_content[0:len(keys.bot_prefix)] == keys.bot_prefix and message_content.lower() != f"{keys.bot_prefix}null":
                                message_content = message_content[len(keys.bot_prefix):len(message_content)]
                                member_ids = await ex.get_id_where_member_matches_name(message_content)
                                group_ids = await ex.get_id_where_group_matches_name(message_content)
                                photo_msg = None
                                if len(member_ids) != 0:
                                    random_member = random.choice(member_ids)
                                    if not await ex.check_if_bot_banned(message_sender.id):
                                        async with message_channel.typing():
                                            if not await check_user_limit(message_sender, message_channel):
                                                if not await events.Events.check_maintenance(message):
                                                    return await ex.send_maintenance_message(message_channel)
                                                photo_msg, api_url = await ex.idol_post(message_channel, random_member, user_id=message_sender.id)
                                                posted = True
                                elif len(group_ids) != 0:
                                    group_id = random.choice(group_ids)
                                    random_member = (random.choice(await ex.get_members_in_group(group_id=group_id)))
                                    if not await ex.check_if_bot_banned(message_sender.id):
                                        async with message_channel.typing():
                                            if not await check_user_limit(message_sender, message_channel):
                                                if not await events.Events.check_maintenance(message):
                                                    return await ex.send_maintenance_message(message_channel)
                                                photo_msg, api_url = await ex.idol_post(message_channel, random_member, user_id=message_sender.id)
                                                posted = True
                                else:
                                    member_ids = await ex.check_group_and_idol(message_content)
                                    if member_ids is not None:
                                        random_member = random.choice(member_ids)
                                        if not await ex.check_if_bot_banned(message_sender.id):
                                            async with message_channel.typing():
                                                if not await check_user_limit(message_sender, message_channel):
                                                    if not await events.Events.check_maintenance(message):
                                                        return await ex.send_maintenance_message(message_channel)
                                                    photo_msg, api_url = await ex.idol_post(message_channel, random_member, user_id=message_sender.id)
                                                    posted = True
                                if posted:
                                    ex.log_idol_command(message)
                                    await ex.add_command_count()
                                    add_user_limit(message_sender)
                                    if api_url is not None:
                                        await ex.check_idol_post_reactions(photo_msg, message, random_member, api_url)
                    except Exception as e:
                        pass

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def stopimages(self, ctx, text_channel: discord.TextChannel = None):
        """Stops Irene from posting/recognizing idol photos in a specific text channel. To undo, type it again.
        [Format: %stopimages #text-channel]"""
        if text_channel is None:
            text_channel = ctx.channel
        if await ex.check_channel_sending_photos(text_channel.id):
            try:
                await ex.conn.execute("INSERT INTO groupmembers.restricted(channelid, serverid, sendhere) VALUES($1, $2, $3)", text_channel.id, ctx.guild.id, 0)
                await ctx.send(f"> **{text_channel.name} can no longer send idol photos.**")
            except Exception as e:
                await ctx.send(f"> **{text_channel.name} is currently being used with {await ex.get_server_prefix_by_context(ctx)}sendimages and can not be restricted.**")
        else:
            await ex.conn.execute("DELETE FROM groupmembers.restricted WHERE channelid = $1 AND sendhere = $2", text_channel.id, 0)
            await ctx.send(f"> **{text_channel.name} can now send idol photos.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def sendimages(self, ctx, text_channel: discord.TextChannel = None):
        """All idol photo commands from the server will post idol photos in a specific text channel. To undo, type it again.
        [Format: %sendimages #text-channel]"""
        if text_channel is None:
            text_channel = ctx.channel
        if await ex.check_channel_sending_photos(text_channel.id):
            if await ex.check_server_sending_photos(server_id=ctx.guild.id):
                old_channel = await ex.get_channel_sending_photos(ctx.guild.id)
                if old_channel.id == text_channel.id:
                    await ex.conn.execute("DELETE FROM groupmembers.restricted WHERE channelid = $1 AND serverid = $2 AND sendhere = $3", text_channel.id, ctx.guild.id, 1)
                    return await ctx.send(f"> **{text_channel.name} will no longer send all idol photo commands.**")
                else:
                    await ex.conn.execute("UPDATE groupmembers.restricted SET channelid = $1 WHERE serverid = $2 AND sendhere = $3", text_channel.id, ctx.guild.id, 1)
            else:
                await ex.conn.execute("INSERT INTO groupmembers.restricted(channelid, serverid, sendhere) VALUES ($1, $2, $3)", text_channel.id, ctx.guild.id, 1)
            await ctx.send(f"> **{text_channel.name} will now receive and send all idol photo commands coming from this server.**")
        else:
            await ctx.send(f"> **{text_channel.name} is currently restricted from idol photos with {await ex.get_server_prefix_by_context(ctx)}stopimages.**")

    @commands.command(aliases=['%'])
    async def randomidol(self, ctx):
        """Sends a photo of a random idol. [Format: %%]"""
        async def get_post():
            random_idol_id = await ex.get_random_idol_id()
            msg, url = await ex.idol_post(ctx.channel, random_idol_id, user_id=ctx.author.id)
            return msg, url, random_idol_id

        if not await check_user_limit(ctx.author, ctx.channel):
            async with ctx.typing():
                photo_msg, api_url, idol_id = await get_post()
                # this may happen if there is no photo of the idol. Not confirmed after switching to API.
                while photo_msg is None:
                    photo_msg, api_url, idol_id = await get_post()
            if api_url is not None:
                add_user_limit(ctx.author)
                await ex.check_idol_post_reactions(photo_msg, ctx.message, idol_id, api_url)

    @commands.command()
    async def countgroup(self, ctx, *, group_name):
        """Shows how many photos of a certain group there are. [Format: %countmember <name>]"""
        photo_count = 0
        group_ids = await ex.get_id_where_group_matches_name(group_name)
        if len(group_ids) == 0:
            return await ctx.send(f"> **I could not find a group named {group_name}.**")
        for group_id in group_ids:
            real_group_name = await ex.get_group_name(group_id)
            members = await ex.get_members_in_group(group_id=group_id)
            for member_id in members:
                photo_count += await ex.get_idol_count(member_id)
            await ctx.send(f"> **There are {photo_count} images for {real_group_name}.**")

    @commands.command()
    async def countmember(self, ctx, *, member_name):
        """Shows how many photos of a certain member there are. [Format: %countmember <name/all>)]"""
        if member_name.lower() == "all":
            return await ctx.send(f"> **There are {await ex.get_all_images_count()} photos stored.**")
        members = await ex.get_id_where_member_matches_name(member_name)
        if len(members) == 0:
            return await ctx.send(f"> **I could not find an idol named {member_name}.**")
        for member_id in members:
            member = await ex.get_member(member_id)
            full_name = member[1]
            stage_name = member[2]
            photo_count = await ex.get_idol_count(member_id)
            await ctx.send(f"> **There are {photo_count} images for {full_name} ({stage_name}).**")

    @commands.command(aliases=['fullname'])
    async def fullnames(self, ctx, *, page_number_or_group: typing.Union[int, str] = 1):
        """Lists the full names of idols the bot has photos of [Format: %fullnames (page number/group name)]"""
        await ex.process_names(ctx, page_number_or_group, "fullname")

    @commands.command(aliases=['member'])
    async def members(self, ctx, *, page_number_or_group: typing.Union[int, str] = 1):
        """Lists the names of idols the bot has photos of [Format: %members (page number/group name)]"""
        await ex.process_names(ctx, page_number_or_group, "members")

    @commands.command()
    async def groups(self, ctx):
        """Lists the groups of idols the bot has photos of [Format: %groups]"""
        all_groups = await ex.get_all_groups()
        is_mod = ex.check_if_mod(ctx)
        page_number = 1
        embed = discord.Embed(title=f"Idol Group List Page {page_number}", color=0xffb6c1)
        embed_list = []
        counter = 1
        if len(ex.cache.group_photos) == 0:
            await ex.update_groups()
        for group in all_groups:
            if group[1] != "NULL" or is_mod:
                group_photo_count = ex.cache.group_photos.get(group[0])
                if group_photo_count is None:
                    group_photo_count = 0
                if is_mod:
                    embed.insert_field_at(counter, name=f"{group[1]} ({group[0]})", value=f"{group_photo_count} Photos", inline=True)
                else:
                    embed.insert_field_at(counter, name=f"{group[1]}", value=f"{group_photo_count} Photos", inline=True)
                if counter == 25:
                    counter = 0
                    embed_list.append(embed)
                    page_number += 1
                    embed = discord.Embed(title=f"Idol Group List Page {page_number}", color=0xffb6c1)
                counter += 1
        if counter != 0:
            embed_list.append(embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list, 0)

    @commands.command()
    async def aliases(self, ctx, mode="member", page_number=1):
        """Lists the aliases of idols that have one [Format: %aliases (members/groups)]"""
        try:
            if 'member' in mode.lower():
                embed_list = await ex.set_embed_with_all_aliases("Idol")
            elif 'group' in mode.lower():
                embed_list = await ex.set_embed_with_all_aliases("Group")
            else:
                return await ctx.send(f">>> **Please specify whether you want member or group aliases\n`{await ex.get_server_prefix_by_context(ctx)}help aliases`**")
            if page_number > len(embed_list):
                page_number = 1
            elif page_number < 1:
                page_number = 1
            msg = await ctx.send(embed=embed_list[page_number-1])
            await ex.check_left_or_right_reaction_embed(msg, embed_list, page_number - 1)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Error - {e}**")

    @commands.command()
    async def count(self, ctx, *, name=None):
        """Shows howmany times an idol has been called. [Format: %count (idol's name/all)]"""
        try:
            if name == 'all' or name is None:
                counter = 0
                for mem in await ex.get_all_members():
                    count = await ex.get_idol_called(mem[0])
                    if count is not None:
                        counter += await ex.get_idol_called(mem[0])
                return await ctx.send(f"> **All Idols have been called a total of {counter} times.**")
            member_ids = await ex.get_id_where_member_matches_name(name)
            if len(member_ids) == 0:
                return await ctx.send(f"> **{name} could not be found.**")
            for member_id in member_ids:
                member = await ex.get_member(member_id)
                full_name = member[1]
                stage_name = member[2]
                counter = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.count WHERE memberid = $1", member_id))
                if counter == 0:
                    await ctx.send(f"> **{full_name} ({stage_name}) has not been called by a user yet.**")
                else:
                    counter = await ex.get_idol_called(member_id)
                    rank_list = await ex.conn.fetch("SELECT memberid FROM groupmembers.count ORDER BY Count DESC")
                    count = 0
                    for rank_row in rank_list:
                        count += 1
                        mem_id = rank_row[0]
                        if mem_id == member_id:
                            final_rank = count
                            await ctx.send(f"> **{full_name} ({stage_name}) has been called {counter} times at rank {final_rank}.**")
        except Exception as e:
            await ctx.send(f"> **ERROR: {e}**")
            log.console(e)

    @commands.command(aliases=["highestcount", "cb", "clb"])
    async def countleaderboard(self, ctx):
        """Shows leaderboards for how many times an idol has been called. [Format: %clb]"""
        embed = discord.Embed(title=f"Idol Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url=keys.bot_website, icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=f"Type {await ex.get_server_prefix_by_context(ctx)}count (idol name) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        all_members = await ex.conn.fetch("SELECT MemberID, Count FROM groupmembers.Count ORDER BY Count DESC")
        count_loop = 0
        for mem in all_members:
            count_loop += 1
            if count_loop <= 10:
                member_id = mem[0]
                count = mem[1]
                idol = await ex.get_member(member_id)
                embed.add_field(name=f"{count_loop}) {idol[1]} ({idol[2]})", value=count)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def scandrive(self, ctx, name="NULL", member_id=0):
        """Scan DriveIDs Table and update other tables."""
        try:
            all_links = await ex.conn.fetch("SELECT id, linkid, name FROM archive.DriveIDs")
            for pic in all_links:
                try:
                    ID = pic[0]
                    Link_ID = pic[1]
                    Link_Name = pic[2]
                    new_link = f"https://drive.google.com/uc?export=view&id={Link_ID}"
                    all_names = await ex.conn.fetch("SELECT Name FROM archive.ChannelList")
                    if name == "NULL" and member_id == 0:
                        for idol_name in all_names:
                            idol_name = idol_name[0]
                            if idol_name == Link_Name and (idol_name != "Group" or idol_name != "MDG Group"):
                                member_id1 = ex.first_result(await ex.conn.fetchrow("SELECT ID FROM groupmembers.Member WHERE StageName = $1", idol_name))
                                await ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id1)
                                await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", ID)
                    elif Link_Name.lower() == name.lower():
                        await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", ID)
                        await ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id)
                except Exception as e:
                    log.console(e)
            await ctx.send(f"> **Completed Scan**")
        except Exception as e:
            log.console(e)
