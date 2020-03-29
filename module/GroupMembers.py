import discord
from discord.ext import commands
import sqlite3
import aiohttp
from bs4 import BeautifulSoup as soup
from module import logger as log
import random
from module import keys
import json


client = 0
path = 'module/GroupMembers.db'
DBconn = sqlite3.connect(path, check_same_thread=False)
c = DBconn.cursor()


def setup(client1):
    client1.add_cog(GroupMembers(client1))
    global client
    client = client1


async def on_message2(message, from_sorting=0):
    message_sender = message.author
    message_channel = message.channel
    message_content = message.content
    if from_sorting == 1:
        def check(m):
            return m.channel == message_channel and m.author == message_sender

        msg = await client.wait_for('message', check=check)
        if msg.content.lower() == "delete":
            return 'delete'
        elif msg.content.lower() == "stop":
            return 'stop'
        elif msg.content.lower() == "deleteall":
            return 'deleteall'
        else:
            return msg
    if from_sorting == 0:
        try:
            if message_content[0] == '%':
                member_names = c.execute("SELECT FullName, StageName ,Aliases  FROM Member").fetchall()
                group_names = c.execute("SELECT InGroup,InGroup2,InGroup3 FROM Member").fetchall()

                new_group_list = []
                for group in group_names:
                    in_group = group[0]
                    in_group2 = group[1]
                    in_group3 = group[2]
                    new_group_list.append(in_group)
                    new_group_list.append(in_group2)
                    new_group_list.append(in_group3)
                # remove duplicates
                member_names = list(dict.fromkeys(member_names))
                group_names = list(dict.fromkeys(new_group_list))
                group_names.remove("NULL")
                for group in group_names:
                    if message_content.lower() == f"%{group}".lower():
                        await GroupMembers.member_group_post(message_channel, group, "InGroup")
                duplicate = False
                for member in member_names:
                    duplicate_stage_names = []
                    multiple_users = False
                    full_name = member[0]
                    stage_name = member[1]
                    aliases = member[2]
                    for member2 in member_names:
                        full_name2 = member2[0]
                        stage_name2 = member2[1]
                        if stage_name == stage_name2 and full_name != full_name2:
                            multiple_users = True
                            duplicate_stage_names.append(full_name)
                            duplicate_stage_names.append(full_name2)
                    aliases = aliases.split(',')
                    for alias in aliases:
                        if message_content.lower() == f"%{alias}".lower():
                            await GroupMembers.member_group_post(message_channel, full_name, "FullName")
                    if message_content.lower() == f"%{full_name}".lower() or message_content.lower() == f"%{stage_name}".lower():
                        if not multiple_users:
                            await GroupMembers.member_group_post(message_channel, full_name, "FullName")
                        else:
                            if not duplicate:
                                full_name = random.choice(duplicate_stage_names)
                                await GroupMembers.member_group_post(message_channel, full_name, "FullName")
                                duplicate = True
        except Exception as e:
            pass


class GroupMembers(commands.Cog):
    def __init__(self, client):
        self.urls = []
        pass

    @staticmethod
    async def member_group_post(ctx, keyword, mode):
        try:
            if mode == "InGroup":
                checker = c.execute(f"SELECT COUNT(*) FROM Member WHERE {mode} = ? OR InGroup2 = ? OR InGroup3 = ?", (keyword, keyword, keyword)).fetchone()[0]
            elif mode == "FullName":
                checker = c.execute(f"SELECT COUNT(*) FROM Member WHERE {mode} = ?", (keyword,)).fetchone()[0]
            if checker == 0:
                await ctx.send(f"> **There are no links saved for {keyword}**")
            if checker != 0:
                if mode == "InGroup":
                    post_list = c.execute(f"SELECT ID,StageName FROM Member WHERE {mode} = ? OR InGroup2 = ? OR InGroup3 = ?", (keyword, keyword, keyword)).fetchall()
                elif mode == "FullName":
                    post_list = c.execute(f"SELECT ID,StageName FROM Member WHERE {mode} = ?", (keyword,)).fetchall()
                random_choice = random.choice(post_list)
                link = c.execute("SELECT Link FROM ImageLinks WHERE MemberID = ?", (random_choice[0],)).fetchall()
                link = random.choice(link)
                check = link[0].find("tenor.com", 0)
                if check == -1:
                    embed = discord.Embed(title=f"{keyword} ({random_choice[1]})", color=0xffb6c1, url=link[0])
                    embed.set_image(url=link[0])
                    await ctx.send(embed=embed)
                elif check != -1:
                    await ctx.send(link[0])
        except Exception as e:
            await ctx.send(e)
            log.console(e)

    async def get_photos(self, url, member, group, group2, group3, stage_name, aliases):
        if aliases != "NULL":
            aliases = aliases.lower()
        try:
            count = c.execute("SELECT COUNT(*) FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
            if count == 0:
                c.execute("INSERT INTO Member VALUES (NULL,?,?,?,?,?,?)", (member, stage_name, group, group2, group3, aliases))
                DBconn.commit()
                id = c.execute("SELECT ID FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
                c.execute("INSERT INTO ImageLinks VALUES (NULL,?,?)", (url, id))
                DBconn.commit()
            else:
                id = c.execute("SELECT ID FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
                c.execute("INSERT INTO ImageLinks VALUES (NULL,?,?)", (url, id))
            log.console(f"Added {url} for {member}")
        except Exception as e:
            log.console(f"{e} {url}")
            pass
        DBconn.commit()

    async def get_folders(self, url, member, group, group2, group3, stage_name, aliases):
        url_id = url[39:len(url)]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    page_html = await r.text()
                    page_soup = soup(page_html, "html.parser")
                    # log.console(page_soup)
                    image_id_src = (page_soup.findAll("script"))
                    string_src = str(image_id_src[21]).split("x22")
                    for id in string_src:
                        if len(id) == 34 and id[0:33] != url_id:
                            viewable_url = f"https://drive.google.com/uc?export=view&id={id[0:33]}"
                            async with aiohttp.ClientSession() as session2:
                                async with session2.get(viewable_url) as w:
                                    if w.status == 200:
                                        if " " not in viewable_url:
                                            await self.get_photos(viewable_url, member, group, group2, group3, stage_name, aliases)
                                        else:
                                            log.console(f"GroupMembers.py -> get_folders: Skipping {viewable_url}")
                                    elif w.status == 404 or w.status == 403:
                                        folder_link = f"https://drive.google.com/drive/folders/{id[0:33]}"
                                        await self.get_folders(folder_link, member, group, group2, group3, stage_name, aliases)
                                    else:
                                        log.console(f"GroupMembers.py -> get_folders2: {w.status} {viewable_url}")
                elif r.status == 404:
                    viewable_url = f"https://drive.google.com/uc?export=view&id={url_id}"
                    await self.get_photos(viewable_url, member, group, group2, group3, stage_name, aliases)
                else:
                    log.console(f"GroupMembers.py -> get_folders1: {r.status} {url}")

    @commands.is_owner()
    @commands.command()
    async def getlinks(self, ctx, link="NULL", member="NULL", group="NULL", group2="NULL", group3="NULL", stage_name="NULL", aliases="NULL"):
        """Add links of photos to database from linked Archives"""
        if "_" in group:
            group = group.replace('_', ' ')
        if "_" in group2:
            group2 = group2.replace('_', ' ')
        if "_" in group3:
            group3 = group3.replace('_', ' ')
        if link.lower() == "default":
            counter = 20
            for url in self.urls:
                if 'folder' in url:
                    await self.get_folders(url, member, group, group2, group3, stage_name, aliases)
        elif link == 'NULL':
            await ctx.send("> **Please enter a link or set the link to default to run the archives pre-existing.**")
        else:
            if 'folder' in link:
                await self.get_folders(link, member, group, group2, group3, stage_name, aliases)
                await ctx.send (f"> **Added photos from <{link}> to Member: {member} from Group: {group}**")
            else:
                await ctx.send("> **Please use a google drive folder link**")

    # Members

    @commands.command()
    async def fullnames(self, ctx):
        """Lists the full names of idols the bot has photos of [Format: %fullnames]"""
        member_names = c.execute("SELECT FullName, InGroup FROM Member").fetchall()
        # remove duplicates
        member_names = list(dict.fromkeys(member_names))
        full_names = []
        group_names = []
        embed = discord.Embed(title="Idol List", color=0xffb6c1)
        for member in member_names:
            group_name = member[1]
            group_names.append(group_name)
        group_names = list(dict.fromkeys(group_names))
        counter = 0
        for group in group_names:
            for member in member_names:
                full_name = member[0]
                group_name = member[1]
                if group_name == group:
                    full_names.append(f"{full_name} | ")
            final_names = "".join(full_names)
            try:
                embed.insert_field_at(counter, name=group, value=final_names, inline=False)
            except Exception as e:
                embed.insert_field_at(counter, name=group, value=final_names, inline=True)
                log.console(e)
            full_names = []
            counter += 1
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %members for Stage Names.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        await ctx.send(embed=embed)

    @commands.command()
    async def members(self, ctx):
        """Lists the names of idols the bot has photos of [Format: %members]"""
        member_names = c.execute("SELECT StageName, InGroup FROM Member").fetchall()
        # remove duplicates
        stage_names = []
        group_names = []
        member_names = list(dict.fromkeys(member_names))
        embed = discord.Embed(title="Idol List", color=0xffb6c1)
        for member in member_names:
            group_name = member[1]
            group_names.append(group_name)
        group_names = list(dict.fromkeys(group_names))
        counter = 0
        for group in group_names:
            for member in member_names:
                stage_name = member[0]
                group_name = member[1]
                if group_name == group:
                    stage_names.append(f"{stage_name} | ")
            final_names = "".join(stage_names)
            try:
                embed.insert_field_at(counter, name=group, value=final_names, inline=False)
            except Exception as e:
                embed.insert_field_at(counter, name=group, value=final_names, inline=True)
                log.console(e)
            stage_names = []
            counter += 1
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Type %fullnames for Full Names.", icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        await ctx.send(embed=embed)


    # Groups
    @commands.command()
    async def groups(self, ctx):
        """Lists the groups of idols the bot has photos of [Format: %groups]"""
        group_names = c.execute("SELECT InGroup, InGroup2, InGroup3 FROM Member").fetchall()
        new_group_list = []
        for group in group_names:
            in_group = group[0]
            in_group2 = group[1]
            in_group3 = group[2]
            new_group_list.append(in_group)
            new_group_list.append(in_group2)
            new_group_list.append(in_group3)
        # remove duplicates
        all_groups = ""
        group_names = list(dict.fromkeys(new_group_list))
        group_names.remove("NULL")
        for group in group_names:
            desc_msg = group + ' | '
            all_groups += desc_msg

        embed = discord.Embed(title="Idol Group List", description=f"{all_groups}", color=0xffb6c1)
        await ctx.send(embed=embed)

    @commands.command()
    async def aliases(self, ctx):
        """Lists the aliases of idols that have one [Format: %aliases]"""
        embed = discord.Embed(title="Idol Aliases", description="", color=0xffb6c1)
        information = c.execute("SELECT Aliases,StageName FROM Member").fetchall()
        for info in information:
            Aliases = info[0]
            StageName = info[1]
            if Aliases != "NULL":
                embed.insert_field_at(1, name=StageName, value=Aliases, inline=True)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def scrapelinks(self, ctx, url):
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

    @commands.is_owner()
    @commands.command()
    async def addalias(self, ctx, alias, *, member):
        """Add alias to a member [Format: %addalias (alias) (member full name)]"""
        try:
            counter = c.execute("SELECT COUNT(*) FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
            if counter == 0:
                await ctx.send("> **That person does not exist.**")
            else:
                current_aliases = c.execute("SELECT Aliases FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
                if current_aliases == "NULL":
                    new_aliases = alias
                else:
                    new_aliases = f"{current_aliases},{alias.lower()}"
                c.execute("UPDATE Member SET Aliases = ? WHERE FullName = ?", (new_aliases, member))
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
            count = c.execute("SELECT COUNT(*) FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
            if count == 0:
                await ctx.send("> **That person does not exist.**")
            else:
                current_aliases = c.execute("SELECT Aliases FROM Member WHERE FullName = ?", (member,)).fetchone()[0]
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
                        c.execute("UPDATE Member SET Aliases = ? WHERE FullName = ?", (new_aliases, member))
                        DBconn.commit()
                        await ctx.send (f"> **Alias: {alias} was removed from {member}.**")
        except Exception as e:
            await ctx.send(e)
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
                            c.execute("INSERT INTO ScrapedLinks VALUES (NULL,?)", (url,))
                        await ctx.send(f"> **{count} link(s) for {keyword} were added to the Database.**")
                        DBconn.commit()
        except Exception as e:
            log.console(e)



    @commands.is_owner()
    @commands.command()
    async def addmemberurl(self, ctx, link="NULL", member="NULL", group="NULL", group2="NULL", group3="NULL", stage_name="NULL", *, aliases="NULL"):
        """Adds URL to GroupMembers database."""
        member = member.replace('_', ' ')
        group = group.replace('_', ' ')
        group2 = group2.replace('_', ' ')
        group3 = group3.replace('_', ' ')
        stage_name = stage_name.replace('_', ' ')
        await self.get_photos(link, member, group, group2, group3, stage_name, aliases)
        await ctx.send(f"> **Added {link} for {member} in {group}.**")

    @commands.is_owner()
    @commands.command()
    async def sort(self, ctx):
        """Approve member links with a small sorting game."""
        try:
            group2 = "NULL"
            group3 = "NULL"
            aliases = "NULL"
            keep_going = True
            while keep_going:
                counter = c.execute("SELECT COUNT(*) FROM ScrapedLinks").fetchone()[0]
                if counter == 0:
                    await ctx.send("> **There are no links to sort.**")
                    keep_going = False
                all_links = c.execute("SELECT ID,Link FROM ScrapedLinks").fetchall()
                for data in all_links:
                    ID = data[0]
                    Link = data[1]
                    await ctx.send(f"> {Link} **Please respond with the member's (full name | stage name), delete, or stop**")
                    check_msg = await on_message2(ctx.message, 1)
                    if check_msg == 'delete':
                        c.execute("DELETE FROM ScrapedLinks WHERE ID = ?", (ID,))
                        DBconn.commit()
                        await ctx.send("> **The link has been removed.**")
                    elif check_msg == 'stop':
                        await ctx.send("> **Stopping Sort**")
                        keep_going = False
                        break
                    elif check_msg == 'deleteall':
                        await ctx.send("> **Deleted all links**")
                        c.execute("DELETE FROM ScrapedLinks")
                        DBconn.commit()
                        keep_going = False
                        break
                    else:
                        split_names = check_msg.content.split('|')
                        full_name = split_names[0]
                        try:
                            stage_name = split_names[1]
                            await ctx.send(f"> **What Group is {full_name} / {stage_name} in?**")
                        except:
                            stage_name = "NULL"
                        count = c.execute("SELECT COUNT(*) FROM Member WHERE FullName = ?", (full_name,)).fetchone()[0]
                        if count == 0:
                            await ctx.send(f"> **What Group is {full_name} in?**")
                            check_msg2 = await on_message2(check_msg, 1)
                            if check_msg2 == 'delete':
                                c.execute("DELETE FROM ScrapedLinks WHERE ID = ?", (ID,))
                                DBconn.commit()
                                await ctx.send("> **The link has been removed.**")
                            elif check_msg2 == 'stop':
                                await ctx.send("> **Stopping Sort**")
                                keep_going = False
                                break
                            elif check_msg2 == 'deleteall':
                                await ctx.send("> **Deleted all links**")
                                c.execute("DELETE FROM ScrapedLinks")
                                DBconn.commit()
                                keep_going = False
                                break
                            else:
                                await ctx.send(f"> **{check_msg.content} in Group: {check_msg2.content} has been sorted.**")
                                group = check_msg2.content
                                if "_" in check_msg2.content:
                                    group = group.replace('_', ' ')
                                c.execute("DELETE FROM ScrapedLinks WHERE ID = ?", (ID,))
                                await self.get_photos(Link, full_name, group, group2, group3, stage_name, aliases)
                        else:
                            c.execute("DELETE FROM ScrapedLinks WHERE ID = ?", (ID,))
                            group = "NULL"
                            await self.get_photos(Link, full_name, group, group2, group3, stage_name, aliases)
                        DBconn.commit()
        except Exception as e:
            log.console(e)
