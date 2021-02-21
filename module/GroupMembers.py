import discord
from discord.ext import commands
from module import logger as log
from module import keys
from Utility import resources as ex
import time
import typing
import json
import datetime


# noinspection PyBroadException,PyPep8
class GroupMembers(commands.Cog):
    @staticmethod
    async def on_message2(message):
        # create modifiable var without altering original
        channel = message.channel
        if message.author.bot or not await ex.u_group_members.check_channel_sending_photos(channel.id) or await ex.u_miscellaneous.check_if_temp_channel(channel.id):
            return
        try:
            if await ex.u_group_members.check_server_sending_photos(message.guild.id):
                channel = await ex.u_group_members.get_channel_sending_photos(message.guild.id)
        except:
            pass  # error is guild not found, likely being accessed from DMs
        posted = False
        api_url = None
        try:
            ex.u_group_members.check_reset_limits()
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
                if message.content[0:len(keys.bot_prefix)] != keys.bot_prefix or message.content.lower() == f"{keys.bot_prefix}null":
                    return
                message_content = message.content[len(keys.bot_prefix):len(message.content)]
                server_id = await ex.get_server_id(message)
                members = await ex.u_group_members.get_idol_where_member_matches_name(message_content, server_id=server_id)
                groups = await ex.u_group_members.get_group_where_group_matches_name(message_content, server_id=server_id)
                photo_msg = None
                if members:
                    random_member = await ex.u_group_members.choose_random_member(members=members)
                    if random_member:
                        photo_msg, api_url, posted = await ex.u_group_members.request_image_post(message, random_member, channel)
                elif groups:
                    random_member = await ex.u_group_members.choose_random_member(groups=groups)
                    if random_member:
                        photo_msg, api_url, posted = await ex.u_group_members.request_image_post(message, random_member, channel)
                else:
                    members = await ex.u_group_members.check_group_and_idol(message_content, server_id=server_id)
                    if members:
                        random_member = await ex.u_group_members.choose_random_member(members=members)
                        if random_member:
                            photo_msg, api_url, posted = await ex.u_group_members.request_image_post(message, random_member, channel)
                if posted:
                    ex.u_group_members.log_idol_command(message)
                    await ex.u_miscellaneous.add_command_count(f"Idol {random_member.id}")
                    await ex.u_miscellaneous.add_session_count()
                    ex.u_group_members.add_user_limit(message.author)
                    if api_url:
                        await ex.u_group_members.check_idol_post_reactions(photo_msg, message, random_member, api_url)
        except:
            pass

    @commands.command()
    async def addidol(self, ctx, *, idol_json):
        """Adds an idol using the syntax from https://irenebot.com/addidol.html
        [Format: %addidol (json)]"""
        try:
            # load string to json
            idol_json = json.loads(idol_json)

            # set empty strings to NoneType
            for key in idol_json:
                if not idol_json.get(key):
                    idol_json[key] = None

            # create variables for values used more than once or that need to be adjusted.
            birth_date = idol_json.get("Birth Date")
            if birth_date:
                birth_date = (datetime.datetime.strptime(birth_date, "%Y-%m-%d")).date()
            height = idol_json.get("Height")
            full_name = idol_json.get("Full Name")
            stage_name = idol_json.get("Stage Name")
            if height:
                height = int(height)

            # for security purposes, do not simplify the structure.
            await ex.conn.execute("INSERT INTO groupmembers.unregisteredmembers(fullname, stagename, formerfullname, "
                                  "formerstagename, birthdate, birthcountry, birthcity, gender, description, height, "
                                  "twitter, youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, zodiac,"
                                  " thumbnail, banner, bloodtype, tags, groupids, notes) VALUES ($1, $2, $3, $4, $5, $6, "
                                  "$7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, "
                                  "$25, $26)", full_name, stage_name, idol_json.get("Former Full Name"),
                                  idol_json.get("Former Stage Name"), birth_date, idol_json.get("Birth Country"),
                                  idol_json.get("Birth City"), idol_json.get("Gender"), idol_json.get("Description"),
                                  height, idol_json.get("Twitter"), idol_json.get("Youtube"),
                                  idol_json.get("Melon"), idol_json.get("Instagram"), idol_json.get("VLive"),
                                  idol_json.get("Spotify"), idol_json.get("Fancafe"), idol_json.get("Facebook"),
                                  idol_json.get("TikTok"), idol_json.get("Zodiac"), idol_json.get("Avatar"),
                                  idol_json.get("Banner"), idol_json.get("BloodType"), idol_json.get("Tags"),
                                  idol_json.get("Group IDs"), idol_json.get("Approver Notes"))

            # get the id of the data that was just added to db.
            query_id = ex.first_result(await ex.conn.fetchrow("SELECT id FROM groupmembers.unregisteredmembers WHERE fullname = $1 AND stagename = $2 ORDER BY id DESC", full_name, stage_name))

            # get the channel to send idol information to.
            channel = ex.client.get_channel(keys.add_idol_channel_id)
            # fetch if discord.py cache is not loaded.
            if not channel:
                channel = await ex.client.fetch_channel(keys.add_idol_channel_id)
            title_description = f"""
==================
Query ID: {query_id} 
Requester: {ctx.author.display_name} ({ctx.author.id})
==================
"""
            # Add all the key values to the title description
            for key in idol_json:
                title_description += f"\n{key}: {idol_json.get(key)}"

            # send embed to approval/deny channel
            embed = await ex.create_embed(title="New Unregistered Idol", title_desc=title_description)
            msg = await channel.send(embed=embed)
            await msg.add_reaction(keys.check_emoji)
            await msg.add_reaction(keys.trash_emoji)
            await ctx.send(f"{ctx.author.display_name}, your request for adding this Idol has been successfully sent."
                           f"The Idol's query ID is {query_id}.")
        except Exception as e:
            log.console(e)
            await ctx.send(f"Something Went Wrong. You may not understand the following error. Please report it.-> {e}")

    @commands.command()
    async def addgroup(self, ctx, *, group_json):
        """Adds a group using the syntax from https://irenebot.com/addgroup.html
        [Format: %addgroup (json)]"""
        try:
            # load string to json
            group_json = json.loads(group_json)

            # set empty strings to NoneType
            for key in group_json:
                if not group_json.get(key):
                    group_json[key] = None

            # create variables for values used more than once or that need to be adjusted.
            debut_date = group_json.get("Debut Date")
            disband_date = group_json.get("Disband Date")
            if debut_date:
                debut_date = (datetime.datetime.strptime(debut_date, "%Y-%m-%d")).date()
            if disband_date:
                disband_date = (datetime.datetime.strptime(disband_date, "%Y-%m-%d")).date()

            group_name = group_json.get("Group Name")

            # for security purposes, do not simplify the structure.
            await ex.conn.execute("INSERT INTO groupmembers.unregisteredgroups(groupname, debutdate, disbanddate, "
                                  "description, twitter, youtube, melon, instagram, vlive, spotify, fancafe, "
                                  "facebook, tiktok, fandom, company, website, thumbnail, banner, gender, tags, "
                                  "notes) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, "
                                  "$16, $17, $18, $19, $20, $21)", group_name, debut_date, disband_date,
                                  group_json.get("Description"), group_json.get("Twitter"), group_json.get("Youtube"),
                                  group_json.get("Melon"), group_json.get("Instagram"), group_json.get("VLive"),
                                  group_json.get("Spotify"), group_json.get("Fancafe"), group_json.get("Facebook"),
                                  group_json.get("TikTok"), group_json.get("Fandom"), group_json.get("Company"),
                                  group_json.get("Website"), group_json.get("Avatar"), group_json.get("Banner"),
                                  group_json.get("Gender"), group_json.get("Tags"), group_json.get("Approver Notes"))

            # get the id of the data that was just added to db.
            query_id = ex.first_result(await ex.conn.fetchrow(
                "SELECT id FROM groupmembers.unregisteredgroups WHERE groupname = $1 ORDER BY id DESC", group_name))

            # get the channel to send idol information to.
            channel = ex.client.get_channel(keys.add_group_channel_id)
            # fetch if discord.py cache is not loaded.
            if not channel:
                channel = await ex.client.fetch_channel(keys.add_group_channel_id)
            title_description = f"""
==================
Query ID: {query_id} 
Requester: {ctx.author.display_name} ({ctx.author.id})
==================
"""
            # Add all the key values to the title description
            for key in group_json:
                title_description += f"\n{key}: {group_json.get(key)}"

            # send embed to approval/deny channel
            embed = await ex.create_embed(title="New Unregistered Group", title_desc=title_description)
            msg = await channel.send(embed=embed)
            await msg.add_reaction(keys.check_emoji)
            await msg.add_reaction(keys.trash_emoji)
            await ctx.send(f"{ctx.author.display_name}, your request for adding this Group has been successfully sent."
                           f" The Group's query ID is {query_id}.")
        except Exception as e:
            log.console(e)
            await ctx.send(f"Something Went Wrong. You may not understand the following error. Please report it.-> {e}")

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
            except:
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
            except:
                pass  # error is guild not found, likely being accessed from DMs
            idol = await ex.u_group_members.get_random_idol()
            photo_msg, api_url, posted = await ex.u_group_members.request_image_post(ctx.message, idol, channel)
            if posted:
                ex.u_group_members.add_user_limit(ctx.author)
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
            if group.name == "NULL" and not is_mod:
                continue
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
                    for count, rank_row in enumerate(rank_list):
                        mem_id = rank_row[0]
                        if mem_id == member.id:
                            final_rank = count + 1
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
