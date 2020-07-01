import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soup
from module import logger as log
import random
from module import keys
import json
from module import quickstart
from Utility import resources as ex
client = keys.client


class GroupMembers(commands.Cog):
    def __init__(self):
        client.add_listener(self.on_message2, 'on_message')
        self.image_already_exists = []
        self.folder_already_checked = []
        self.all_links = []

    async def on_message2(self, message, from_sorting=0):
        message_sender = message.author
        message_channel = message.channel
        message_content = message.content
        if from_sorting == 1:
            def check(m):
                return m.channel == message_channel and m.author == message_sender

            msg = await client.wait_for('message', check=check)
            return msg.content.lower()

        if from_sorting == 0:
            try:
                if ex.check_message_not_empty(message):
                    if message_content[0:len(keys.bot_prefix)] == keys.bot_prefix and message_content != f"{keys.bot_prefix}null":
                        match_name = message_content[1:len(message_content)]
                        member_ids = await ex.get_id_where_member_matches_name(match_name)
                        group_ids = await ex.get_id_where_group_matches_name(match_name)
                        photo_msg = None
                        if len(member_ids) != 0:
                            random_member = random.choice(member_ids)
                            random_link = await ex.get_random_photo_from_member(random_member)
                            if not await ex.check_if_bot_banned(message_sender.id):
                                async with message_channel.typing():
                                    photo_msg = await ex.idol_post(message_channel, random_member, random_link)
                                    ex.log_idol_command(message)
                        elif len(group_ids) != 0:
                            group_id = random.choice(group_ids)
                            random_member = random.choice(await ex.get_members_in_group(await ex.get_group_name(group_id)))
                            random_link = await ex.get_random_photo_from_member(random_member[0])
                            if not await ex.check_if_bot_banned(message_sender.id):
                                async with message_channel.typing():
                                    photo_msg = await ex.idol_post(message_channel, random_member[0], random_link, group_id=group_id)
                                    ex.log_idol_command(message)
                        else:
                            member_ids = await ex.check_group_and_idol(match_name)
                            if member_ids is not None:
                                random_member = random.choice(member_ids)
                                random_link = await ex.get_random_photo_from_member(random_member)
                                if not await ex.check_if_bot_banned(message_sender.id):
                                    async with message_channel.typing():
                                        photo_msg = await ex.idol_post(message_channel, random_member, random_link)
                                        ex.log_idol_command(message)
                        await ex.check_idol_post_reactions(photo_msg, message)

                    else:
                        pass
            except Exception as e:
                pass

    @commands.command(aliases=['%'])
    async def randomidol(self, ctx):
        """Sends a photo of a random idol. [Format: %%]"""
        random_idol_id = await ex.get_random_idol_id()
        random_link = await ex.get_random_photo_from_member(random_idol_id)
        photo_msg = await ex.idol_post(ctx.channel, random_idol_id, random_link)
        await ex.check_idol_post_reactions(photo_msg, ctx.message)

    async def get_photos(self, url, member, groups, stage_name, aliases, member_id):
        try:
            if member_id == 0:
                if aliases != "NULL":
                    aliases = aliases.lower()
                ex.c.execute("SELECT COUNT(*) FROM groupmembers.Member WHERE FullName = %s", (member,))
                count = ex.fetch_one()
                if count == 0:
                    ex.c.execute("INSERT INTO groupmembers.Member VALUES (%s,%s,%s,%s)", (member, stage_name, groups, aliases))
                    ex.DBconn.commit()
                    ex.c.execute("SELECT ID FROM groupmembers.Member WHERE FullName = %s", (member,))
                    id = ex.fetch_one()
                    ex.c.execute("INSERT INTO groupmembers.ImageLinks VALUES (%s,%s)", (url, id))
                else:
                    ex.c.execute("SELECT ID FROM groupmembers.Member WHERE FullName = %s", (member,))
                    id = ex.fetch_one()
                    ex.c.execute("INSERT INTO groupmembers.ImageLinks VALUES (%s,%s)", (url, id))
                log.console(f"Added {url} for {member}")
            else:
                ex.c.execute("INSERT INTO groupmembers.ImageLinks VALUES (%s,%s)", (url, member_id))
                log.console(f"Added {url} for MemberID: {member_id}")
        except Exception as e:
            # most likely unique constraint failed.
            log.console(f"{e} for {member} ({member_id})")
            pass
        ex.DBconn.commit()

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

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
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
                                async with session.get(viewable_url) as w:
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
        all_groups_listed = ""
        new_group_list = []
        is_mod = ex.check_if_mod(ctx)
        for group in all_groups:
            new_group_list.append(group)
        try:
            new_group_list.remove("NULL")
        except Exception as e:
            pass
        for group in new_group_list:
            if group[1] != "NULL" or is_mod:
                if is_mod:
                    desc_msg = f"{group[1]} ({group[0]}) | "
                else:
                    desc_msg = f"{group[1]} | "
                all_groups_listed += desc_msg
        embed = discord.Embed(title="Idol Group List", description=f"{all_groups_listed}", color=0xffb6c1)
        await ctx.send(embed=embed)

    @commands.command()
    async def aliases(self, ctx, mode="member", page_number=1):
        """Lists the aliases of idols that have one [Format: %aliases (members/groups)]"""
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

    @commands.is_owner()
    @commands.command()
    async def scrapelink(self, ctx, url):
        """Connection to site + put html to html_page.txt"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
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
                ex.c.execute("SELECT COUNT(*) FROM groupmembers.ScrapedLinks")
                counter = ex.fetch_one()
                if counter == 0:
                    await ctx.send("> **There are no links to sort.**")
                    keep_going = False
                ex.c.execute("SELECT ID,Link FROM groupmembers.ScrapedLinks")
                all_links = ex.fetch_all()
                for data in all_links:
                    data_id = data[0]
                    link = data[1]
                    await ctx.send(f"> {link} **Please respond with the member's ID, delete, or stop**")
                    check_msg = await self.on_message2(ctx.message, 1)
                    if check_msg == 'delete':
                        ex.c.execute("DELETE FROM groupmembers.ScrapedLinks WHERE ID = %s", (data_id,))
                        ex.DBconn.commit()
                        await ctx.send("> **The link has been removed.**")
                    elif check_msg == 'stop':
                        await ctx.send("> **Stopping Sort**")
                        keep_going = False
                        break
                    elif check_msg == 'deleteall':
                        await ctx.send("> **Deleted all links**")
                        ex.c.execute("DELETE FROM groupmembers.ScrapedLinks")
                        ex.DBconn.commit()
                        keep_going = False
                        break
                    else:
                        ex.c.execute("INSERT INTO groupmembers.imagelinks VALUES (%s,%s)", (link, int(check_msg)))
                        ex.c.execute("DELETE FROM groupmembers.scrapedlinks WHERE ID = %s", (data_id,))
                        ex.DBconn.commit()
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
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        content = await r.content.read()
                        gifs = json.loads(content)
                        count = 0
                        for key in gifs['results']:
                            count += 1
                            # await ctx.send((key['url']))
                            url = key['url']
                            ex.c.execute("INSERT INTO groupmembers.ScrapedLinks VALUES (%s)", (url,))
                        await ctx.send(f"> **{count} link(s) for {keyword} were added to the Database.**")
                        ex.DBconn.commit()
        except Exception as e:
            log.console(e)

    @commands.command()
    async def count(self, ctx, *, name=None):
        """Shows howmany times an idol has been called. [Format: %count (idol's name)]"""
        check_if_existed = 0
        try:
            ex.c.execute("SELECT ID, FullName, StageName, Aliases FROM groupmembers.Member")
            all_members = ex.fetch_all()
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
                        ex.c.execute("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = %s", (ID,))
                        counter = ex.fetch_one()
                        if counter == 0:
                            await ctx.send(f"> **{full_name} ({stage_name}) has not been called by a user yet.**")
                        else:
                            counter = ex.get_idol_called(ID)
                            ex.c.execute("SELECT MemberID FROM groupmembers.Count ORDER BY Count DESC")
                            all_counters = ex.fetch_all()
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
                    count = ex.get_idol_called(mem[0])
                    if count is not None:
                        counter += ex.get_idol_called(mem[0])
                await ctx.send(f"> **All Idols have been called a total of {counter} times.**")
        except Exception as e:
            log.console(e)
        if check_if_existed == 0:
            await ctx.send(f"> **{name} could not be found.**")

    @commands.command(aliases=["highestcount", "cb", "clb"])
    async def countleaderboard(self, ctx):
        """Shows leaderboards for how many times an idol has been called. [Format: %clb]"""
        embed = discord.Embed(title=f"Idol Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=f"Type {await ex.get_server_prefix_by_context(ctx)}count (idol name) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        ex.c.execute("SELECT MemberID, Count FROM groupmembers.Count ORDER BY Count DESC")
        all_members = ex.fetch_all()
        count_loop = 0
        for mem in all_members:
            count_loop += 1
            if count_loop <= 10:
                MemberID = mem[0]
                count = mem[1]
                ex.c.execute("SELECT fullname, stagename FROM groupmembers.Member WHERE ID = %s", (MemberID,))
                idol = ex.c.fetchone()
                embed.add_field(name=f"{count_loop}) {idol[0]} ({idol[1]})", value=count)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def scandrive(self, ctx, name="NULL", member_id=0):
        """Scan DriveIDs Table and update other tables."""
        try:
            ex.c.execute("SELECT id, linkid, name FROM archive.DriveIDs")
            all_links = ex.fetch_all()
            for pic in all_links:
                try:
                    ID = pic[0]
                    Link_ID = pic[1]
                    Link_Name = pic[2]
                    new_link = f"https://drive.google.com/uc?export=view&id={Link_ID}"
                    ex.c.execute("SELECT Name FROM archive.ChannelList")
                    all_names = ex.fetch_all()
                    if name == "NULL" and member_id == 0:
                        for idol_name in all_names:
                            idol_name = idol_name[0]
                            if idol_name == Link_Name and (idol_name != "Group" or idol_name != "MDG Group"):
                                ex.c.execute("SELECT ID FROM groupmembers.Member WHERE StageName = %s", (idol_name,))
                                member_id1 = ex.fetch_one()
                                ex.c.execute("INSERT INTO groupmembers.ImageLinks VALUES(%s,%s)", (new_link, member_id1))
                                ex.c.execute("DELETE FROM archive.DriveIDs WHERE ID = %s", (ID,))
                                ex.DBconn.commit()
                    elif Link_Name.lower() == name.lower():
                        ex.c.execute("DELETE FROM archive.DriveIDs WHERE ID = %s", (ID,))
                        ex.c.execute("INSERT INTO groupmembers.ImageLinks VALUES(%s,%s)", (new_link, member_id))
                        ex.DBconn.commit()
                except Exception as e:
                    log.console(e)
                    ex.DBconn.commit()
            await ctx.send(f"> **Completed Scan**")
        except Exception as e:
            log.console(e)
            ex.DBconn.commit()
