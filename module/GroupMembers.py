import discord
from discord.ext import commands
from module import logger as log, events
import random
from module import keys
from Utility import resources as ex
import time
import typing

client = keys.client
# the amount normal users can use if the guild owner is a super patron.
owner_super_patron_benefit = keys.idol_post_send_limit * 2
patron_message = f"""
As of September 23rd 2020, non-Patrons can only send {keys.idol_post_send_limit} photos a day maximum, as the current host can not reliably handle additional traffic.
You may become a patron for as little as $3 per month in order to send unlimited photos; every Patron contributes to upgrading and maintaining the host.
If the guild owner is a super patron, All guild members (non-patrons) get {owner_super_patron_benefit} photos a day.
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


async def check_user_limit(message_sender, message_channel, no_vote_limit=False):
    limit = keys.idol_post_send_limit
    if no_vote_limit:
        # amount of votes that can be sent without voting.
        limit = keys.idol_no_vote_send_limit
    if message_sender.id in ex.cache.commands_used:
        if not await ex.check_if_patreon(message_sender.id) and ex.cache.commands_used[message_sender.id][0] > limit:
            if not await ex.check_if_patreon(message_channel.guild.owner.id, super=True) and not no_vote_limit:
                return await message_channel.send(patron_message)
            elif ex.cache.commands_used[message_sender.id][0] > owner_super_patron_benefit and not no_vote_limit:
                return await message_channel.send(patron_message)
            else:
                return True
    return False


async def request_image_post(message, idol, channel):
    photo_msg, api_url, posted = None, None, False
    if not await ex.u_miscellaneous.check_if_bot_banned(message.author.id):
        async with channel.typing():
            try:
                if await check_user_limit(message.author, message.channel, no_vote_limit=True):
                    if not await ex.u_group_members.get_if_user_voted(message.author.id) and not await ex.check_if_patreon(message.author.id):
                        return await ex.u_group_members.send_vote_message(message)
            except Exception as e:
                log.console(e)
            if not await check_user_limit(message.author, channel):
                if not await events.Events.check_maintenance(message):
                    return await ex.u_miscellaneous.send_maintenance_message(channel)
                photo_msg, api_url = await ex.u_group_members.idol_post(channel, idol, user_id=message.author.id)
                posted = True
    return photo_msg, api_url, posted


async def choose_random_member(members=None, groups=None):
    """Choose a random member object from a member or group list given."""
    async def check_photo_count(t_member_ids):
        t_member_id = random.choice(t_member_ids)
        t_member = await ex.u_group_members.get_member(t_member_id)
        if not t_member.photo_count:
            t_member = await check_photo_count(t_member_ids)
        return t_member

    idol = None
    new_groups = []
    if groups:
        for group in groups:
            if group.photo_count:
                new_groups.append(group)
    if new_groups:
        member_ids = (random.choice(new_groups)).members
        idol = await check_photo_count(member_ids)

    new_members = []
    if members:
        for member in members:
            if member.photo_count:
                new_members.append(member)
    if new_members:
        idol = random.choice(new_members)
    return idol


class GroupMembers(commands.Cog):
    @staticmethod
    async def on_message2(message):
        # create modifiable var without altering original
        channel = message.channel
        if not message.author.bot and await ex.u_group_members.check_channel_sending_photos(channel.id) and not await ex.u_miscellaneous.check_if_temp_channel(channel.id):
            try:
                if await ex.u_group_members.check_server_sending_photos(message.guild.id):
                    channel = await ex.u_group_members.get_channel_sending_photos(message.guild.id)
            except Exception as e:
                pass  # error is guild not found, likely being accessed from DMs
            posted = False
            api_url = None
            try:
                check_reset_limits()
                if message.author.id in ex.cache.commands_used:
                    time_difference = time.time() - ex.cache.commands_used[message.author.id][1]
                    if time_difference < 2:
                        # await asyncio.sleep(1)
                        pass
                if ex.u_miscellaneous.check_message_not_empty(message):
                    random_member = False
                    # since this is a listener, the prefix is put back to the default
                    # (from the original on_message)
                    # and we do not need to worry about the user's server prefix for idol photos
                    # we just need to make sure it has the bot's default prefix
                    # however this means if a user changes the prefix and uses the bot's default prefix
                    # it will still process idol photos, but not regular commands.
                    if message.content[0:len(keys.bot_prefix)] == keys.bot_prefix and message.content.lower() != f"{keys.bot_prefix}null":
                        message_content = message.content[len(keys.bot_prefix):len(message.content)]
                        server_id = await ex.get_server_id(message)
                        members = await ex.u_group_members.get_idol_where_member_matches_name(message_content, server_id=server_id)
                        groups = await ex.u_group_members.get_group_where_group_matches_name(message_content, server_id=server_id)
                        photo_msg = None
                        if members:
                            random_member = await choose_random_member(members=members)
                            if random_member:
                                photo_msg, api_url, posted = await request_image_post(message, random_member, channel)
                        elif groups:
                            random_member = await choose_random_member(groups=groups)
                            if random_member:
                                photo_msg, api_url, posted = await request_image_post(message, random_member, channel)
                        else:
                            members = await ex.u_group_members.check_group_and_idol(message_content, server_id=server_id)
                            if members:
                                random_member = await choose_random_member(members=members)
                                if random_member:
                                    photo_msg, api_url, posted = await request_image_post(message, random_member, channel)
                        if posted:
                            ex.u_group_members.log_idol_command(message)
                            await ex.u_miscellaneous.add_command_count(f"Idol {random_member.id}")
                            await ex.u_miscellaneous.add_session_count()
                            add_user_limit(message.author)
                            if api_url:
                                await ex.u_group_members.check_idol_post_reactions(photo_msg, message, random_member, api_url)
            except Exception as e:
                pass

    @commands.command()
    async def card(self, ctx, *, name):
        """Displays an Idol/Group's profile card.
        [Format: %card (idol/group name/id)]"""
        server_id = await ex.get_server_id(ctx)
        members = await ex.u_group_members.get_idol_where_member_matches_name(name, server_id=server_id)
        groups = await ex.u_group_members.get_group_where_group_matches_name(name, server_id=server_id)
        member_by_id = await ex.u_group_members.get_member(name)
        group_by_id = await ex.u_group_members.get_group(name)

        if member_by_id:
            if members:
                members.append(member_by_id)
            else:
                members = [member_by_id]

        if group_by_id:
            if groups:
                groups.append(group_by_id)
            else:
                groups = [group_by_id]

        embed_list = []
        for member in members:
            embed = await ex.u_group_members.set_embed_card_info(member, server_id=server_id)
            embed_list.append(embed)
        for group in groups:
            embed = await ex.u_group_members.set_embed_card_info(group, group=True, server_id=server_id)
            embed_list.append(embed)
        if embed_list:
            msg = await ctx.send(embed=embed_list[0])
            if len(embed_list) > 1:
                await ex.check_left_or_right_reaction_embed(msg, embed_list)
        else:
            return await ctx.send(f"> I could not find any information regarding {name}.")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def stopimages(self, ctx, text_channel: discord.TextChannel = None):
        """Stops Irene from posting/recognizing idol photos in a specific text channel. To undo, type it again.
        [Format: %stopimages #text-channel]"""
        if not text_channel:
            text_channel = ctx.channel
        if await ex.u_group_members.check_channel_sending_photos(text_channel.id):
            try:
                await ex.conn.execute("INSERT INTO groupmembers.restricted(channelid, serverid, sendhere) VALUES($1, $2, $3)", text_channel.id, ctx.guild.id, 0)
                ex.cache.restricted_channels[text_channel.id] = [ctx.guild.id, 0]
                await ctx.send(f"> **{text_channel.name} can no longer send idol photos.**")
            except Exception as e:
                await ctx.send(f"> **{text_channel.name} is currently being used with {await ex.get_server_prefix_by_context(ctx)}sendimages and can not be restricted.**")
        else:
            await ex.conn.execute("DELETE FROM groupmembers.restricted WHERE channelid = $1 AND sendhere = $2", text_channel.id, 0)
            await ex.u_group_members.delete_restricted_channel_from_cache(text_channel.id, 0)
            await ctx.send(f"> **{text_channel.name} can now send idol photos.**")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def sendimages(self, ctx, text_channel: discord.TextChannel = None):
        """All idol photo commands from the server will post idol photos in a specific text channel. To undo, type it again.
        [Format: %sendimages #text-channel]"""
        if not text_channel:
            text_channel = ctx.channel
        if await ex.u_group_members.check_channel_sending_photos(text_channel.id):
            if await ex.u_group_members.check_server_sending_photos(server_id=ctx.guild.id):
                old_channel = await ex.u_group_members.get_channel_sending_photos(ctx.guild.id)
                if old_channel:
                    if old_channel.id == text_channel.id:
                        await ex.conn.execute("DELETE FROM groupmembers.restricted WHERE channelid = $1 AND serverid = $2 AND sendhere = $3", text_channel.id, ctx.guild.id, 1)
                        await ex.u_group_members.delete_restricted_channel_from_cache(text_channel.id, 1)
                        return await ctx.send(f"> **{text_channel.name} will no longer send all idol photo commands.**")
                else:
                    delete_channel_id = None
                    await ex.conn.execute("UPDATE groupmembers.restricted SET channelid = $1 WHERE serverid = $2 AND sendhere = $3", text_channel.id, ctx.guild.id, 1)
                    for channel_id in ex.cache.restricted_channels:
                        channel_info = ex.cache.restricted_channels.get(channel_id)
                        if channel_info[0] == ctx.guild.id and channel_info[1] == 1:
                            delete_channel_id = channel_id
                    if delete_channel_id:
                        # this seemingly useless snippet of code is to avoid runtime errors during iteration.
                        ex.cache.restricted_channels.pop(delete_channel_id)
                        ex.cache.restricted_channels[text_channel.id] = [ctx.guild.id, 1]
            else:
                await ex.conn.execute("INSERT INTO groupmembers.restricted(channelid, serverid, sendhere) VALUES ($1, $2, $3)", text_channel.id, ctx.guild.id, 1)
                ex.cache.restricted_channels[text_channel.id] = [ctx.guild.id, 1]
            await ctx.send(f"> **{text_channel.name} will now receive and send all idol photo commands coming from this server.**")
        else:
            await ctx.send(f"> **{text_channel.name} is currently restricted from idol photos with {await ex.get_server_prefix_by_context(ctx)}stopimages.**")

    @commands.command(aliases=['%'])
    async def randomidol(self, ctx):
        """Sends a photo of a random idol. [Format: %%]"""
        if await ex.u_group_members.check_channel_sending_photos(ctx.channel.id) and not await ex.u_miscellaneous.check_if_temp_channel(ctx.channel.id):
            channel = ctx.channel
            try:
                if await ex.u_group_members.check_server_sending_photos(ctx.guild.id):
                    channel = await ex.u_group_members.get_channel_sending_photos(ctx.guild.id)
            except Exception as e:
                pass  # error is guild not found, likely being accessed from DMs
            idol = await ex.u_group_members.get_random_idol()
            photo_msg, api_url, posted = await request_image_post(ctx.message, idol, channel)
            if posted:
                add_user_limit(ctx.author)
                if api_url:
                    await ex.u_group_members.check_idol_post_reactions(photo_msg, ctx.message, idol.id, api_url)

    @commands.command()
    async def countgroup(self, ctx, *, group_name):
        """Shows how many photos of a certain group there are. [Format: %countmember <name>]"""
        server_id = await ex.get_server_id(ctx)
        groups = await ex.u_group_members.get_group_where_group_matches_name(group_name, server_id=server_id)
        if not groups:
            return await ctx.send(f"> **I could not find a group named {group_name}.**")
        for group in groups:
            await ctx.send(f"> **There are {group.photo_count} images for {group.name}.**")

    @commands.command()
    async def countmember(self, ctx, *, member_name):
        """Shows how many photos of a certain member there are. [Format: %countmember <name/all>)]"""
        if member_name.lower() == "all":
            return await ctx.send(f"> **There are {await ex.u_group_members.get_all_images_count()} photos stored.**")
        server_id = await ex.get_server_id(ctx)
        members = await ex.u_group_members.get_idol_where_member_matches_name(member_name, server_id=server_id)
        if not members:
            return await ctx.send(f"> **I could not find an idol named {member_name}.**")
        for member in members:
            await ctx.send(f"> **There are {member.photo_count} images for {member.full_name} ({member.stage_name}).**")

    @commands.command(aliases=['fullname'])
    async def fullnames(self, ctx, *, page_number_or_group: typing.Union[int, str] = 1):
        """Lists the full names of idols the bot has photos of [Format: %fullnames (page number/group name)]"""
        await ex.u_group_members.process_names(ctx, page_number_or_group, "fullname")

    @commands.command(aliases=['member'])
    async def members(self, ctx, *, page_number_or_group: typing.Union[int, str] = 1):
        """Lists the names of idols the bot has photos of [Format: %members (page number/group name)]"""
        await ex.u_group_members.process_names(ctx, page_number_or_group, "members")

    @commands.command()
    async def groups(self, ctx):
        """Lists the groups of idols the bot has photos of [Format: %groups]"""
        is_mod = ex.check_if_mod(ctx)
        page_number = 1
        embed = discord.Embed(title=f"Idol Group List Page {page_number}", color=0xffb6c1)
        embed_list = []
        counter = 1
        for group in ex.cache.groups:
            if group.name != "NULL" or is_mod:
                if is_mod:
                    embed.insert_field_at(counter, name=f"{group.name} ({group.id})", value=f"{group.photo_count} Photos", inline=True)
                else:
                    embed.insert_field_at(counter, name=f"{group.name}", value=f"{group.photo_count} Photos", inline=True)
                if counter == 25:
                    counter = 0
                    embed_list.append(embed)
                    page_number += 1
                    embed = discord.Embed(title=f"Idol Group List Page {page_number}", color=0xffb6c1)
                counter += 1
        if counter:
            embed_list.append(embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list, 0)

    @commands.command()
    async def aliases(self, ctx, mode="member", page_number=1):
        """Lists the aliases of idols or groups that have one. Underscores are spaces and commas are to split idol or group names
[Format: %aliases (names of idols/groups) (page number)]"""
        try:
            mode = mode.replace("_", " ")
            mode = mode.replace(",", " ")
            server_id = await ex.get_server_id(ctx)
            embed_list = await ex.u_group_members.set_embed_with_aliases(mode, server_id=server_id)
            if not embed_list:
                if 'member' in mode.lower():
                    embed_list = await ex.u_group_members.set_embed_with_all_aliases("Idol", server_id=server_id)
                elif 'group' in mode.lower():
                    embed_list = await ex.u_group_members.set_embed_with_all_aliases("Group", server_id=server_id)
                else:
                    return await ctx.send(f">>> **No results were found. Please specify whether you want member or group aliases, or enter a name of an idol/group.\n`{await ex.get_server_prefix_by_context(ctx)}help aliases`**")
            if len(embed_list) < page_number or page_number < 1:
                page_number = 1
            msg = await ctx.send(embed=embed_list[page_number-1])
            if len(embed_list) > 1:
                await ex.check_left_or_right_reaction_embed(msg, embed_list, page_number - 1)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Error - {e}**")

    @commands.command()
    async def count(self, ctx, *, name=None):
        """Shows howmany times an idol has been called. [Format: %count (idol's name/all)]"""
        try:
            if name == 'all' or not name:
                idol_called = 0
                for member in ex.cache.idols:
                    idol_called += member.called
                return await ctx.send(f"> **All Idols have been called a total of {idol_called} times.**")
            server_id = await ex.get_server_id(ctx)
            members = await ex.u_group_members.get_idol_where_member_matches_name(name, server_id=server_id)
            if not members:
                return await ctx.send(f"> **{name} could not be found.**")
            for member in members:
                if not member.called:
                    await ctx.send(f"> **{member.full_name} ({member.stage_name}) has not been called by a user yet.**")
                else:
                    rank_list = await ex.conn.fetch("SELECT memberid FROM groupmembers.count ORDER BY Count DESC")
                    count = 0
                    for rank_row in rank_list:
                        count += 1
                        mem_id = rank_row[0]
                        if mem_id == member.id:
                            final_rank = count
                            await ctx.send(f"> **{member.full_name} ({member.stage_name}) has been called {member.called} times at rank {final_rank}.**")
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
        for member_id, count in all_members:
            count_loop += 1
            if count_loop <= 10:
                idol = await ex.u_group_members.get_member(member_id)
                embed.add_field(name=f"{count_loop}) {idol.full_name} ({idol.stage_name})", value=count)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def scandrive(self, ctx, name="NULL", member_id=0):
        """Scan DriveIDs Table and update other tables."""
        try:
            all_links = await ex.conn.fetch("SELECT id, linkid, name FROM archive.DriveIDs")
            for p_id, link_id, link_name in all_links:
                try:
                    new_link = f"https://drive.google.com/uc?export=view&id={link_id}"
                    all_names = await ex.conn.fetch("SELECT Name FROM archive.ChannelList")
                    if name == "NULL" and member_id == 0:
                        for idol_name in all_names:
                            idol_name = idol_name[0]
                            if idol_name == link_name and (idol_name != "Group" or idol_name != "MDG Group"):
                                member_id1 = ex.first_result(await ex.conn.fetchrow("SELECT ID FROM groupmembers.Member WHERE StageName = $1", idol_name))
                                await ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id1)
                                await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", p_id)
                    elif link_name.lower() == name.lower():
                        await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", p_id)
                        await ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id)
                except Exception as e:
                    log.console(e)
            await ctx.send(f"> **Completed Scan**")
        except Exception as e:
            log.console(e)
