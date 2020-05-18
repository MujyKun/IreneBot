import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soup
from module import logger as log
import random
from module import keys
import json
from module import quickstart
from Utility import fetch_one, fetch_all, DBconn, c, get_members_in_group, get_all_groups, send_names, set_embed_with_all_aliases, get_id_where_group_matches_name, get_id_where_member_matches_name, get_random_photo_from_member, check_idol_post_reactions, idol_post, get_all_members, get_group_name


class GroupMembers(commands.Cog):
    def __init__(self, client):
        client.add_listener(self.on_message2, 'on_message')
        self.already_exists = []
        self.client = client
        self.all_links = []
        pass

    async def on_message2(self, message, from_sorting=0):
        message_sender = message.author
        message_channel = message.channel
        message_content = message.content
        if from_sorting == 1:
            def check(m):
                return m.channel == message_channel and m.author == message_sender

            msg = await self.client.wait_for('message', check=check)
            if msg.content.lower() == "delete":
                return 'delete'
            elif msg.content.lower() == "stop":
                return 'stop'
            elif msg.content.lower() == "deleteall":
                return 'deleteall'
            else:
                return msg.content.lower()
        if from_sorting == 0:
            try:
                if message_content[0] == '%' and message_content != "%null":
                    match_name = message_content[1:len(message_content)]
                    member_ids = await get_id_where_member_matches_name(match_name)
                    group_ids = await get_id_where_group_matches_name(match_name)
                    photo_msg = None
                    if len(member_ids) != 0:
                        random_member = random.choice(member_ids)
                        random_link = await get_random_photo_from_member(random_member)
                        photo_msg = await idol_post(message_channel, random_member, random_link)
                    elif len(group_ids) != 0:
                        group_id = random.choice(group_ids)
                        random_member = random.choice(await get_members_in_group(await get_group_name(group_id)))
                        random_link = await get_random_photo_from_member(random_member[0])
                        photo_msg = await idol_post(message_channel, random_member[0], random_link, group_id=group_id)
                    await check_idol_post_reactions(photo_msg, self.client, message)

                else:
                    pass
            except Exception as e:
                pass

    @commands.command(aliases=['%'])
    async def randomidol(self, ctx):
        """Sends a photo of a random idol. [Format: %%]"""
        member_ids = await get_all_members()
        random_idol_id = (random.choice(member_ids))[0]
        random_link = await get_random_photo_from_member(random_idol_id)
        photo_msg = await idol_post(ctx.channel, random_idol_id, random_link)
        await check_idol_post_reactions(photo_msg, self.client, ctx.message)

    async def get_photos(self, url, member, groups, stage_name, aliases):
        try:
            if aliases != "NULL":
                aliases = aliases.lower()
            c.execute("SELECT COUNT(*) FROM groupmembers.Member WHERE FullName = %s", (member,))
            count = fetch_one()
            if count == 0:
                c.execute("INSERT INTO groupmembers.Member VALUES (%s,%s,%s,%s)", (member, stage_name, groups, aliases))
                DBconn.commit()
                c.execute("SELECT ID FROM groupmembers.Member WHERE FullName = %s", (member,))
                id = fetch_one()
                c.execute("INSERT INTO groupmembers.ImageLinks VALUES (%s,%s)", (url, id))
                DBconn.commit()
            else:
                c.execute("SELECT ID FROM groupmembers.Member WHERE FullName = %s", (member,))
                id = fetch_one()
                c.execute("INSERT INTO groupmembers.ImageLinks VALUES (%s,%s)", (url, id))
            log.console(f"Added {url} for {member}")
        except Exception as e:
            # most likely unique constraint failed.
            log.console(f"{e} {url} for {member}")
            pass
        DBconn.commit()

    async def get_folders(self, url, member, group, stage_name, aliases):
        url_id = url[39:len(url)]
        check = False

        async def straight_to_images(folder_id):
            try:
                ids = await quickstart.Drive.get_ids(folder_id)
                if len(ids) == 0:
                    return False
                for id in ids:
                    # if id not in self.already_exists:
                    # self.already_exists.append(id)
                    view_url = f"https://drive.google.com/uc?export=view&id={id}"
                    await self.get_photos(view_url, member, group, stage_name, aliases)
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
                    await self.get_folders(view_url, member, group, stage_name, aliases)
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
                            async with aiohttp.ClientSession() as session2:
                                async with session2.get(viewable_url) as w:
                                    if w.status == 200:
                                        if not await straight_to_folders(new_id):
                                            pass
                                        """
                                        if await straight_to_images(new_id):
                                            return True
                                        else:
                                            return False
                                        """
                                    elif w.status == 404:
                                        if not await straight_to_images(url_id):
                                            pass
                                    elif w.status == 403:
                                        if not await straight_to_images(url_id):
                                            pass
                                    elif w.status == 400:
                                        pass
                                    else:
                                        log.console(f"GroupMembers.py -> get_folders2: {w.status} {viewable_url} /2")
                elif r.status == 404:
                    view_url = f"https://drive.google.com/uc?export=view&id={url_id}"
                    await self.get_photos(view_url, member, group, stage_name, aliases)
                    # if not await straight_to_images(url_id):
                    # return check
                else:
                    log.console(f"GroupMembers.py -> get_folders1: {r.status} {url} /1")
        return check


    @commands.is_owner()
    @commands.command()
    async def getlinks(self, ctx, link="NULL", member="NULL", group="NULL", stage_name="NULL", aliases="NULL"):
        """Add links of photos to database from linked Archives"""
        try:
            stage_name = stage_name.replace('_', ' ')
            member = member.replace('_', ' ')
            if 'folder' in link or 'bit.ly' in link:
                if await self.get_folders(link, member, group, stage_name, aliases):
                    await ctx.send(f"> **Added photos from <{link}> to Member: {member} from Group: {group}**")
                else:
                    await ctx.send(f"> **Check page source for <{link}>. It seems no images were found.**")
            else:
                await ctx.send("> **Please use a google drive folder link**")
        except Exception as e:
            log.console(e)

    @commands.command()
    async def countmember(self, ctx, *, member=""):
        """Shows how many photos of a certain member there are. [Format: %countmember <name>]"""

        async def amount_of_links(member_id, current_full_name, current_stage_name):
            c.execute("SELECT COUNT(*) FROM groupmembers.ImageLinks WHERE MemberID = %s", (member_id,))
            counter = fetch_one()
            if counter == 0:
                await ctx.send(f"> **There are no results for {current_full_name} ({current_stage_name})**")
            else:
                await ctx.send(f"> **There are {counter} images for {current_full_name} ({current_stage_name}).**")

        if member == "":
            await ctx.send("> **Please specify a member's full name, stage name, or alias.**")
        member = member.replace("_", " ")
        c.execute("SELECT ID, FullName, StageName, Aliases FROM groupmembers.Member")
        all_members = fetch_all()
        for all_member in all_members:
            id = all_member[0]
            full_name = all_member[1]
            stage_name = all_member[2]
            aliases = all_member[3]
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

    @commands.command()
    async def fullnames(self, ctx):
        """Lists the full names of idols the bot has photos of [Format: %fullnames]"""
        await send_names(ctx, "fullname", self.client)

    @commands.command()
    async def members(self, ctx):
        """Lists the names of idols the bot has photos of [Format: %members]"""
        await send_names(ctx, "members", self.client)

    @commands.command()
    async def groups(self, ctx):
        """Lists the groups of idols the bot has photos of [Format: %groups]"""
        all_groups = await get_all_groups()
        all_groups_listed = ""
        new_group_list = []
        for group in all_groups:
            new_group_list.append(group)
        try:
            new_group_list.remove("NULL")
        except Exception as e:
            pass
        for group in new_group_list:
            if group[1] != "NULL":
                desc_msg = group[1] + ' | '
                all_groups_listed += desc_msg
        embed = discord.Embed(title="Idol Group List", description=f"{all_groups_listed}", color=0xffb6c1)
        await ctx.send(embed=embed)

    @commands.command()
    async def aliases(self, ctx, mode="member"):
        """Lists the aliases of idols that have one [Format: %aliases (members/groups)]"""
        if 'member' in mode.lower():
            embed = await set_embed_with_all_aliases("Idol")
            await ctx.send(embed=embed)
        elif 'group' in mode.lower():
            embed = await set_embed_with_all_aliases("Group")
            await ctx.send(embed=embed)
        else:
            await ctx.send("> **I don't know if you want member or group aliases.**")


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
    async def addalias(self, ctx, alias, *, member):
        """Add alias to a member [Format: %addalias (alias) (member full name)]"""
        try:
            c.execute("SELECT COUNT(*) FROM groupmembers.Member WHERE FullName = %s", (member,))
            counter = fetch_one()
            if counter == 0:
                await ctx.send("> **That person does not exist.**")
            else:
                c.execute("SELECT Aliases FROM groupmembers.Member WHERE FullName = %s", (member,))
                current_aliases = fetch_one()
                if current_aliases == "NULL":
                    new_aliases = alias
                else:
                    new_aliases = f"{current_aliases},{alias.lower()}"
                c.execute("UPDATE groupmembers.Member SET Aliases = %s WHERE FullName = %s", (new_aliases, member))
                DBconn.commit()
                await ctx.send(f"> **Added Alias: {alias} to {member}**")
        except Exception as e:
            await ctx.send(e)
            log.console(e)

    @commands.is_owner()
    @commands.command()
    async def removealias(self, ctx, alias, *, member):
        """Add alias to a member [Format: %addalias (alias) (member full name)]"""
        try:
            c.execute("SELECT COUNT(*) FROM groupmembers.Member WHERE FullName = %s", (member,))
            count = fetch_one()
            if count == 0:
                await ctx.send("> **That person does not exist.**")
            else:
                c.execute("SELECT Aliases FROM groupmembers.Member WHERE FullName = %s", (member,))
                current_aliases = fetch_one()
                if current_aliases == "NULL":
                    await ctx.send("> **That alias does not exist**")
                else:
                    check = current_aliases.find(alias.lower(), 0)
                    if check == -1:
                        await ctx.send(f"> **Could not find alias: {alias}**")
                    else:
                        new_aliases = ""
                        alias_list = current_aliases.split(',')
                        for alias2 in alias_list:
                            if alias.lower() != alias2.lower():
                                new_aliases += f"{alias2.lower()},"
                        if new_aliases == "" or new_aliases == ",":
                            new_aliases = "NULL"
                        if new_aliases[len(new_aliases)-1] == ',':
                            new_aliases = new_aliases[0:len(new_aliases)-2]
                        c.execute("UPDATE groupmembers.Member SET Aliases = %s WHERE FullName = %s", (new_aliases, member))
                        DBconn.commit()
                        await ctx.send (f"> **Alias: {alias} was removed from {member}.**")
        except Exception as e:
            await ctx.send(e)
            log.console(e)

    @commands.is_owner()
    @commands.command()
    async def sort(self, ctx):
        """Approve member links with a small sorting game."""
        try:
            keep_going = True
            while keep_going:
                c.execute("SELECT COUNT(*) FROM groupmembers.ScrapedLinks")
                counter = fetch_one()
                if counter == 0:
                    await ctx.send("> **There are no links to sort.**")
                    keep_going = False
                c.execute("SELECT ID,Link FROM groupmembers.ScrapedLinks")
                all_links = fetch_all()
                for data in all_links:
                    data_id = data[0]
                    link = data[1]
                    await ctx.send(f"> {link} **Please respond with the member's ID, delete, or stop**")
                    check_msg = await self.on_message2(ctx.message, 1)
                    if check_msg == 'delete':
                        c.execute("DELETE FROM groupmembers.ScrapedLinks WHERE ID = %s", (data_id,))
                        DBconn.commit()
                        await ctx.send("> **The link has been removed.**")
                    elif check_msg == 'stop':
                        await ctx.send("> **Stopping Sort**")
                        keep_going = False
                        break
                    elif check_msg == 'deleteall':
                        await ctx.send("> **Deleted all links**")
                        c.execute("DELETE FROM groupmembers.ScrapedLinks")
                        DBconn.commit()
                        keep_going = False
                        break
                    else:
                        c.execute("INSERT INTO groupmembers.imagelinks VALUES (%s,%s)", (link, int(check_msg)))
                        c.execute("DELETE FROM groupmembers.scrapedlinks WHERE ID = %s", (data_id,))
                        DBconn.commit()
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
                            c.execute("INSERT INTO groupmembers.ScrapedLinks VALUES (%s)", (url,))
                        await ctx.send(f"> **{count} link(s) for {keyword} were added to the Database.**")
                        DBconn.commit()
        except Exception as e:
            log.console(e)

    @commands.command()
    async def count(self, ctx, *, name):
        """Shows howmany times an idol has been called. [Format: %count (idol's name)]"""
        try:
            c.execute("SELECT ID, FullName, StageName, Aliases FROM groupmembers.Member")
            all_members = fetch_all()
            final_count = "Unknown"
            for mem in all_members:
                check = 0
                ID = mem[0]
                full_name = mem[1]
                stage_name = mem[2]
                aliases = mem[3]
                if aliases != "NULL":
                    aliases = aliases.split(',')
                    for alias in aliases:
                        if alias.lower() == name.lower():
                            check = 1
                if name.lower() == full_name.lower() or name.lower() == stage_name.lower():
                    check = 1
                if check == 1:
                    c.execute("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = %s", (ID,))
                    counter = fetch_one()
                    if counter == 0:
                        await ctx.send(f"> **{full_name} ({stage_name}) has not been called by a user yet.**")
                    else:
                        c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (ID,))
                        counter = fetch_one()
                        c.execute("SELECT MemberID FROM groupmembers.Count ORDER BY Count DESC")
                        all_counters = fetch_all()
                        count = 0
                        for rank in all_counters:
                            count += 1
                            mem_id = rank[0]
                            if mem_id == ID:
                                final_count = count

                        await ctx.send(f"> **{full_name} ({stage_name}) has been called {counter} times at rank {final_count}.**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=["highestcount", "cb", "clb"])
    async def countleaderboard(self, ctx):
        """Shows leaderboards for how many times an idol has been called. [Format: %clb]"""
        embed = discord.Embed(title=f"Idol Leaderboard", color=0xffb6c1)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %count (idol name) to view their individual stats.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        c.execute("SELECT MemberID, Count FROM groupmembers.Count ORDER BY Count DESC")
        all_members = fetch_all()
        count_loop = 0
        for mem in all_members:
            count_loop += 1
            if count_loop <= 10:
                MemberID = mem[0]
                count = mem[1]
                c.execute("SELECT fullname, stagename FROM groupmembers.Member WHERE ID = %s", (MemberID,))
                idol = c.fetchone()
                embed.add_field(name=f"{count_loop}) {idol[0]} ({idol[1]})", value=count)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def scandrive(self, ctx, name="NULL", member_id=0):
        """Scan DriveIDs Table and update other tables."""
        try:
            c.execute("SELECT id, linkid, name FROM archive.DriveIDs")
            all_links = fetch_all()
            for pic in all_links:
                try:
                    ID = pic[0]
                    Link_ID = pic[1]
                    Link_Name = pic[2]
                    new_link = f"https://drive.google.com/uc?export=view&id={Link_ID}"
                    c.execute("SELECT Name FROM archive.ChannelList")
                    all_names = fetch_all()
                    if name == "NULL" and member_id == 0:
                        for idol_name in all_names:
                            idol_name = idol_name[0]
                            if idol_name == Link_Name and (idol_name != "Group" or idol_name != "MDG Group"):
                                c.execute("SELECT ID FROM groupmembers.Member WHERE StageName = %s", (idol_name,))
                                member_id1 = fetch_one()
                                c.execute("INSERT INTO groupmembers.ImageLinks VALUES(%s,%s)", (new_link, member_id1))
                                c.execute("DELETE FROM archive.DriveIDs WHERE ID = %s", (ID,))
                                DBconn.commit()
                    elif Link_Name.lower() == name.lower():
                        c.execute("DELETE FROM archive.DriveIDs WHERE ID = %s", (ID,))
                        c.execute("INSERT INTO groupmembers.ImageLinks VALUES(%s,%s)", (new_link, member_id))
                        DBconn.commit()
                except Exception as e:
                    log.console(e)
                    DBconn.commit()
            await ctx.send(f"> **Completed Scan**")
        except Exception as e:
            log.console(e)
            DBconn.commit()
