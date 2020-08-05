import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup as soup
from module import logger as log
import random
from module import keys
import json
from module import quickstart
from Utility import resources as ex
import asyncio
client = keys.client


class GroupMembers(commands.Cog):
    def __init__(self):
        self.first_loop = True
        self.image_already_exists = []
        self.folder_already_checked = []
        self.all_links = []

    @staticmethod
    async def on_message2(message, from_sorting=0):
        message_sender = message.author
        message_channel = message.channel
        message_content = message.content
        if not message_sender.bot:
            if from_sorting == 1:
                def check(m):
                    return m.channel == message_channel and m.author == message_sender

                msg = await client.wait_for('message', check=check)
                return msg.content.lower()

            if from_sorting == 0:
                if await ex.check_channel_sending_photos(message_channel.id):
                    try:
                        if await ex.check_server_sending_photos(message.guild.id):
                            message_channel = await ex.get_channel_sending_photos(message.guild.id)
                    except Exception as e:
                        pass  # error is guild not found, likely being accessed from DMs
                    posted = False
                    try:
                        if ex.check_message_not_empty(message):
                            random_member = False
                            server_prefix = await ex.get_server_prefix_by_context(message)
                            if message_content[0:len(server_prefix)] == server_prefix and message_content != f"{server_prefix}null":
                                message_content = message_content[len(server_prefix):len(message_content)]
                                member_ids = await ex.get_id_where_member_matches_name(message_content)
                                group_ids = await ex.get_id_where_group_matches_name(message_content)
                                photo_msg = None
                                if len(member_ids) != 0:
                                    random_member = random.choice(member_ids)
                                    random_link = await ex.get_random_photo_from_member(random_member)
                                    if not await ex.check_if_bot_banned(message_sender.id):
                                        async with message_channel.typing():
                                            photo_msg = await ex.idol_post(message_channel, random_member, random_link)
                                            posted = True
                                elif len(group_ids) != 0:
                                    group_id = random.choice(group_ids)
                                    random_member = (random.choice(await ex.get_members_in_group(await ex.get_group_name(group_id))))[0]
                                    random_link = await ex.get_random_photo_from_member(random_member)
                                    if not await ex.check_if_bot_banned(message_sender.id):
                                        async with message_channel.typing():
                                            photo_msg = await ex.idol_post(message_channel, random_member, random_link, group_id=group_id)
                                            posted = True
                                else:
                                    member_ids = await ex.check_group_and_idol(message_content)
                                    if member_ids is not None:
                                        random_member = random.choice(member_ids)
                                        random_link = await ex.get_random_photo_from_member(random_member)
                                        if not await ex.check_if_bot_banned(message_sender.id):
                                            async with message_channel.typing():
                                                photo_msg = await ex.idol_post(message_channel, random_member, random_link)
                                                posted = True
                                if posted:
                                    ex.log_idol_command(message)
                                    await ex.add_command_count()
                                    await ex.check_idol_post_reactions(photo_msg, message, random_member)
                            else:
                                pass
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
        async with ctx.typing():
            random_idol_id = await ex.get_random_idol_id()
            random_link = await ex.get_random_photo_from_member(random_idol_id)
            photo_msg = await ex.idol_post(ctx.channel, random_idol_id, random_link)
        await ex.check_idol_post_reactions(photo_msg, ctx.message, random_idol_id)

    async def get_photos(self, url, member, groups, stage_name, aliases, member_id):
        try:
            if member_id == 0:
                if aliases != "NULL":
                    aliases = aliases.lower()
                count = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.Member WHERE FullName = $1", member))
                if count == 0:
                    await ex.conn.execute("INSERT INTO groupmembers.Member VALUES ($1,$2,$3,$4)", member, stage_name, groups, aliases)
                    id = ex.first_result(await ex.conn.fetchrow("SELECT ID FROM groupmembers.Member WHERE FullName = $1", member))
                    await ex.conn.execute("INSERT INTO groupmembers.ImageLinks VALUES ($1,$2)", url, id)
                else:
                    id = ex.first_result(await ex.conn.fetchrow("SELECT ID FROM groupmembers.Member WHERE FullName = $1", member))
                    await ex.conn.execute("INSERT INTO groupmembers.ImageLinks VALUES ($1,$2)", url, id)
                log.console(f"Added {url} for {member}")
            else:
                await ex.conn.execute("INSERT INTO groupmembers.ImageLinks VALUES ($1,$2)", url, member_id)
                log.console(f"Added {url} for MemberID: {member_id}")
        except Exception as e:
            # most likely unique constraint failed.
            log.console(f"{e} for {member} ({member_id})")
            pass

    async def get_folders(self, url, member, group, stage_name, aliases, member_id):
        try:
            url_id = url[39:len(url)]
            check = False

            async def straight_to_images(folder_id, image_id=0):
                try:
                    if image_id == 0:
                        ids = await quickstart.Drive.get_ids(folder_id)
                        if len(ids) == 0:
                            return False
                        for id in ids:
                            if id not in self.image_already_exists:
                                self.image_already_exists.append(id)
                                view_url = f"https://drive.google.com/uc?export=view&id={id}"
                                await self.get_photos(view_url, member, group, stage_name, aliases, member_id)
                    else:
                        if image_id not in self.image_already_exists:
                            self.image_already_exists.append(image_id)
                            view_url = f"https://drive.google.com/uc?export=view&id={image_id}"
                            await self.get_photos(view_url, member, group, stage_name, aliases, member_id)
                    return True
                except Exception as e:
                    log.console(f"{e} /4")

            async def straight_to_folders(folder_id):
                try:
                    ids = await quickstart.Drive.get_ids(folder_id)
                    if len(ids) == 0:
                        return False
                    for id in ids:
                        view_url = f"https://drive.google.com/drive/folders/{id}"
                        if await ex.check_if_folder(view_url):
                            await straight_to_folders(id)
                        else:
                            if id not in self.image_already_exists:
                                self.image_already_exists.append(id)
                                view_url = f"https://drive.google.com/uc?export=view&id={id}"
                                await self.get_photos(view_url, member, group, stage_name, aliases, member_id)
                    return True
                except Exception as e:
                    log.console(f"{e} /3")
            async with ex.session.get(url) as r:
                if r.status == 200:
                    page_html = await r.text()
                    page_soup = soup(page_html, "html.parser")
                    # log.console(page_soup)
                    image_id_src = (page_soup.findAll("script"))
                    string_src = str(image_id_src[21]).split("x22")
                    for id in string_src:
                        if (len(id) == 34 or len(id) == 29) and (id[0:33] != url_id and id[0:28] != url_id):
                            check = True
                            if len(id) == 34:
                                # viewable_url = f"https://drive.google.com/uc?export=view&id={id[0:33]}"
                                viewable_url = f"https://drive.google.com/drive/folders/{id[0:33]}"
                                new_id = id[0:33]
                            elif len(id) == 29:
                                # viewable_url = f"https://drive.google.com/uc?export=view&id={id[0:28]}"
                                viewable_url = f"https://drive.google.com/drive/folders/{id[0:28]}"
                                new_id = id[0:28]
                            else:
                                new_id = None
                            async with ex.session.get(viewable_url) as w:
                                if w.status == 200:
                                    if new_id not in self.folder_already_checked:
                                        self.folder_already_checked.append(new_id)
                                        if not await straight_to_folders(new_id):
                                            pass
                                elif w.status == 404:
                                    # this part is in the case there is only one folder with many photos
                                    # and no other folders are present.
                                    if url_id not in self.folder_already_checked:
                                        self.folder_already_checked.append(url_id)
                                        if not await straight_to_folders(url_id):
                                            pass
                                    # it's fine if the url doesn't exist
                                    # when it's actually called, it will be auto deleted.
                                    if not await straight_to_images(url_id, new_id):
                                        pass
                                elif w.status == 403:
                                    if not await straight_to_images(url_id):
                                        pass
                                else:
                                    log.console(f"GroupMembers.py -> get_folders2: {w.status} {viewable_url} /2")
                elif r.status == 404:
                    view_url = f"https://drive.google.com/uc?export=view&id={url_id}"
                    await self.get_photos(view_url, member, group, stage_name, aliases, member_id)
                    # if not await straight_to_images(url_id):
                    # return check
                else:
                    log.console(f"GroupMembers.py -> get_folders1: {r.status} {url} /1")
        except Exception as e:
            log.console(e)
        return check

    @commands.is_owner()
    @commands.command()
    async def getlinks(self, ctx, link="NULL", member_id=0, member="NULL", group="NULL", stage_name="NULL", aliases="NULL"):
        """Add links of photos to database from linked Archives"""
        try:
            stage_name = stage_name.replace('_', ' ')
            member = member.replace('_', ' ')
            if 'folder' in link or 'bit.ly' in link:
                if await self.get_folders(link, member, group, stage_name, aliases, member_id):
                    await ctx.send(f"> **Added photos from <{link}> to Member: {member} from Group: {group}**")
                else:
                    await ctx.send(f"> **Check page source for <{link}>. It seems no images were found.**")
            else:
                await ctx.send("> **Please use a google drive folder link**")
        except Exception as e:
            log.console(e)

    @commands.command()
    async def countgroup(self, ctx, *, group_name=""):
        """Shows how many photos of a certain group there are. [Format: %countmember <name>]"""
        all_groups = await ex.get_all_groups()
        real_group_name = None
        members = None
        for group_info in all_groups:
            if group_name.lower() == group_info[1].lower():
                members = await ex.get_members_in_group(group_info[1])
                real_group_name = group_info[1]
            try:
                aliases = group_info[2]
                aliases = aliases.split(",")
                for alias in aliases:
                    if group_name.lower() == alias.lower():
                        members = await ex.get_members_in_group(group_info[1])
                        real_group_name = group_info[1]
            except:
                pass
        if members is None:
            await ctx.send(f"> **{group_name} either has no members or does not exist.**")
        else:
            counter = 0
            for member in members:
                counter += await ex.get_idol_count(member[0])
            await ctx.send(f"> **There are {counter} images for {real_group_name}.**")

    @commands.command()
    async def countmember(self, ctx, *, member=None):
        """Shows how many photos of a certain member there are. [Format: %countmember <name/all>)]"""
        async def amount_of_links(member_id, current_full_name, current_stage_name):
            counter = await ex.get_idol_count(member_id)
            if counter == 0:
                await ctx.send(f"> **There are no results for {current_full_name} ({current_stage_name})**")
            else:
                await ctx.send(f"> **There are {counter} images for {current_full_name} ({current_stage_name}).**")

        if member is None:
            await ctx.send("> **Please specify a member's full name, stage name, or alias.**")
        elif member == "all":
            await ctx.send(f"> **There are {await ex.get_all_images_count():,} images of idols.**")
        else:
            member = member.replace("_", " ")
            all_members = await ex.get_all_members()
            for all_member in all_members:
                id = all_member[0]
                full_name = all_member[1]
                stage_name = all_member[2]
                aliases = all_member[4]
                if member.lower() == full_name.lower():
                    await amount_of_links(id, full_name, stage_name)
                elif member.lower() == stage_name.lower():
                    await amount_of_links(id, full_name, stage_name)
                try:
                    aliases = aliases.split(",")
                    for alias in aliases:
                        if member.lower() == alias.lower():
                            await amount_of_links(id, full_name, stage_name)
                except:
                    pass

    @commands.command(aliases=['fullname'])
    async def fullnames(self, ctx, page_number: int = 1):
        """Lists the full names of idols the bot has photos of [Format: %fullnames]"""
        await ex.send_names(ctx, "fullname", page_number)

    @commands.command(aliases=['member'])
    async def members(self, ctx, page_number: int = 1):
        """Lists the names of idols the bot has photos of [Format: %members]"""
        await ex.send_names(ctx, "members", page_number)

    @commands.command()
    async def groups(self, ctx):
        """Lists the groups of idols the bot has photos of [Format: %groups]"""
        all_groups = await ex.get_all_groups()
        new_group_list = []
        is_mod = ex.check_if_mod(ctx)
        page_number = 1
        embed = discord.Embed(title=f"Idol Group List Page {page_number}", color=0xffb6c1)
        embed_list = []
        counter = 1
        for group in all_groups:
            new_group_list.append(group)
        try:
            new_group_list.remove("NULL")
        except Exception as e:
            pass
        for group in new_group_list:
            if group[1] != "NULL" or is_mod:
                group_photo_count = await ex.get_photo_count_of_group(group[0])
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
            check = True
            if 'member' in mode.lower():
                embed_list = await ex.set_embed_with_all_aliases("Idol")
            elif 'group' in mode.lower():
                embed_list = await ex.set_embed_with_all_aliases("Group")
            else:
                await ctx.send("> **I don't know if you want member or group aliases.**")
                check = False
            if check:
                if page_number > len(embed_list):
                    page_number = 1
                elif page_number < 1:
                    page_number = 1
                msg = await ctx.send(embed=embed_list[page_number-1])
                await ex.check_left_or_right_reaction_embed(msg, embed_list, page_number - 1)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Error - {e}**")

    @commands.is_owner()
    @commands.command()
    async def scrapelink(self, ctx, url):
        """Connection to site + put html to html_page.txt"""
        async with ex.session.get(url) as r:
            if r.status == 200:
                page_html = await r.text()
                page_soup = soup(page_html, "html.parser")
                page_soup = page_soup.encode("utf-8")
                log.console(page_soup)
                with open('html_page.txt', 'w+') as f:
                    f.write(str(page_soup))
        await ctx.send("> **Complete**")

    @commands.is_owner()
    @commands.command()
    async def sort(self, ctx):
        """Approve member links with a small sorting game."""
        try:
            keep_going = True
            while keep_going:
                counter = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.ScrapedLinks"))
                if counter == 0:
                    await ctx.send("> **There are no links to sort.**")
                    keep_going = False
                all_links = await ex.conn.fetch("SELECT ID,Link FROM groupmembers.ScrapedLinks")
                for data in all_links:
                    data_id = data[0]
                    link = data[1]
                    await ctx.send(f"> {link} **Please respond with the member's ID, delete, or stop**")
                    check_msg = await self.on_message2(ctx.message, 1)
                    if check_msg == 'delete':
                        await ex.conn.execute("DELETE FROM groupmembers.ScrapedLinks WHERE ID = $1", data_id)
                        await ctx.send("> **The link has been removed.**")
                    elif check_msg == 'stop':
                        await ctx.send("> **Stopping Sort**")
                        keep_going = False
                        break
                    elif check_msg == 'deleteall':
                        await ctx.send("> **Deleted all links**")
                        await ex.conn.execute("DELETE FROM groupmembers.ScrapedLinks")
                        keep_going = False
                        break
                    else:
                        await ex.conn.execute("INSERT INTO groupmembers.imagelinks VALUES ($1,$2)", link, int(check_msg))
                        await ex.conn.execute("DELETE FROM groupmembers.scrapedlinks WHERE ID = $1", data_id)
        except Exception as e:
            log.console(e)

    @commands.is_owner()
    @commands.command()
    async def tenor(self, ctx, keyword, limit=1):
        """Connection to tenor API // Sends Links of gifs to Database. // dashes are spaces between words"""
        # base_url = f'https://api.tenor.com/v1/search?<parameters>'
        # https://tenor.com/developer/dashboard
        try:
            url = f'https://api.tenor.com/v1/search?q={keyword}&key={keys.tenor_key}&limit={limit}'
            async with ex.session.get(url) as r:
                if r.status == 200:
                    content = await r.content.read()
                    gifs = json.loads(content)
                    count = 0
                    for key in gifs['results']:
                        count += 1
                        # await ctx.send((key['url']))
                        url = key['url']
                        await ex.conn.execute("INSERT INTO groupmembers.ScrapedLinks VALUES ($1)", url)
                    await ctx.send(f"> **{count} link(s) for {keyword} were added to the Database.**")
        except Exception as e:
            log.console(e)

    @commands.command()
    async def count(self, ctx, *, name=None):
        """Shows howmany times an idol has been called. [Format: %count (idol's name)]"""
        check_if_existed = 0
        try:
            all_members = await ex.conn.fetch("SELECT ID, FullName, StageName, Aliases FROM groupmembers.Member")
            final_count = "Unknown"

            if name is not None:
                for mem in all_members:
                    check = 0
                    ID = mem[0]
                    full_name = mem[1]
                    stage_name = mem[2]
                    aliases = mem[3]
                    if aliases is not None:
                        aliases = aliases.split(',')
                        for alias in aliases:
                            if alias.lower() == name.lower():
                                check = 1
                    if name.lower() == full_name.lower() or name.lower() == stage_name.lower():
                        check_if_existed = 1
                        check = 1
                    if check == 1:
                        counter = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = $1", ID))
                        if counter == 0:
                            await ctx.send(f"> **{full_name} ({stage_name}) has not been called by a user yet.**")
                        else:
                            counter = await ex.get_idol_called(ID)
                            all_counters = await ex.conn.fetch("SELECT MemberID FROM groupmembers.Count ORDER BY Count DESC")
                            count = 0
                            for rank in all_counters:
                                count += 1
                                mem_id = rank[0]
                                if mem_id == ID:
                                    final_count = count
                            await ctx.send(f"> **{full_name} ({stage_name}) has been called {counter} times at rank {final_count}.**")
            else:
                counter = 0
                for mem in all_members:
                    count = await ex.get_idol_called(mem[0])
                    if count is not None:
                        counter += await ex.get_idol_called(mem[0])
                await ctx.send(f"> **All Idols have been called a total of {counter} times.**")
        except Exception as e:
            log.console(e)
        if check_if_existed == 0:
            await ctx.send(f"> **{name} could not be found.**")

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
                MemberID = mem[0]
                count = mem[1]
                idol = await ex.conn.fetchrow("SELECT fullname, stagename FROM groupmembers.Member WHERE ID = $1", MemberID)
                embed.add_field(name=f"{count_loop}) {idol[0]} ({idol[1]})", value=count)
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
                                await ex.conn.execute("INSERT INTO groupmembers.ImageLinks VALUES($1,$2)", new_link, member_id1)
                                await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", ID)
                    elif Link_Name.lower() == name.lower():
                        await ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", ID)
                        await ex.conn.execute("INSERT INTO groupmembers.ImageLinks VALUES($1,$2)", new_link, member_id)
                except Exception as e:
                    log.console(e)
            await ctx.send(f"> **Completed Scan**")
        except Exception as e:
            log.console(e)

    @tasks.loop(seconds=0, minutes=0, hours=24, reconnect=True)
    async def update_group_photo_count(self):
        """Looped every 24 hours to update the group photo count."""
        async def update_groups():
            try:
                await ex.update_photo_count_of_groups()
            except Exception as e:
                log.console(e)

        if self.first_loop:
            await asyncio.sleep(10)
            await update_groups()
            self.first_loop = False
