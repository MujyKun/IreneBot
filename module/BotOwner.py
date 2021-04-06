import discord
from Utility import resources as ex
from discord.ext import commands
from util import logger as log


# noinspection PyPep8
class BotOwner(commands.Cog):
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

    @commands.command()
    @commands.is_owner()
    async def addcards(self, ctx):
        """Fill The CardValues Table with Cards [Format: %addcards]"""
        await ex.conn.execute("DELETE FROM blackjack.cards")
        suit_names = ("Hearts", "Diamonds", "Spades", "Clubs")
        rank_names = ("Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
                    "Eight", "Nine", "Ten", "Jack", "Queen", "King")
        card_values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3,
                      4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        cards = []
        for suit in suit_names[0:4]:
            for rank in rank_names[0:13]:
                cards += [("{} of {}".format(rank, suit))]
        count_x = -1
        for card in cards:
            count_x += 1
            await ex.conn.execute("INSERT INTO blackjack.cards (id, name, value) VALUES ($3, $1, $2)", card, card_values[count_x], count_x+1)
        await ctx.send("> **All cards have been added into the table.**", delete_after=40)

    @commands.command()
    @commands.is_owner()
    async def addpatreon(self, ctx, *, users):
        """Adds a patreon. [Format: %addpatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.u_patreon.add_to_patreon(user)
        await ctx.send(f">>> **Added {users} to Patreon.**")

    @commands.command()
    @commands.is_owner()
    async def removepatreon(self, ctx, *, users):
        """Removes a patreon. [Format: %removepatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user in users:
            await ex.u_patreon.remove_from_patreon(user)
        await ctx.send(f">>> **Removed {users} from Patreon.**")

    @commands.is_owner()
    @commands.command()
    async def clearnword(self, ctx, user: discord.Member = None):
        """Clear A User's Nword Counter [Format: %clearnword @user]"""
        if not user:
            return await ctx.send("> **Please @ a user**")

        if not (await ex.get_user(user.id)).n_word:
            return await ctx.send(f"> **<@{user.id}> has not said the N-Word a single time!**")

        await ex.conn.execute("DELETE FROM general.nword where userid = $1", user.id)
        (await ex.get_user(user.id)).n_word = 0
        await ctx.send("**> Cleared.**")

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, channel_id, *, new_message):
        """Send a message to a text channel."""
        try:
            channel = await ex.client.fetch_channel(channel_id)  # 403 forbidden on tests.
            await channel.send(new_message)
            await ctx.send("> **Message Sent.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **ERROR: {e}**")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """Displays which servers Irene is in."""
        guilds = ex.client.guilds
        count = 1
        page_number = 1
        embed = discord.Embed(title=f"{len(guilds)} Servers - Page {page_number}", color=0xffb6c1)
        embed.set_author(name="Irene", url=ex.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text="Thanks for using Irene.",
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        guilds_ordered = [[guild.id, guild.member_count] for guild in guilds]
        guilds_ordered.sort(key=lambda server_info: server_info[1])
        guild_ids_sorted = [guild[0] for guild in guilds_ordered]
        embed_list = []
        try:
            for main_guild_id in guild_ids_sorted:
                # need to do a nested loop due to fetch_guild not containing attributes needed.
                for guild in guilds:
                    if guild.id != main_guild_id:
                        continue
                    member_count = f"Member Count: {guild.member_count}\n"
                    owner = f"Guild Owner: {guild.owner} ({guild.owner.id})\n"
                    desc = member_count + owner
                    embed.add_field(name=f"{guild.name} ({guild.id})", value=desc, inline=False)
                    if count == 25:
                        count = 0
                        embed_list.append(embed)
                        page_number += 1
                        embed = discord.Embed(title=f"{len(guilds)} Servers - Page {page_number}", color=0xffb6c1)
                        embed.set_author(name="Irene", url=ex.keys.bot_website,
                                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
                        embed.set_footer(text="Thanks for using Irene.",
                                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
                    count += 1
        except Exception as e:
            log.console(e)
        if count:
            embed_list.append(embed)
        msg = await ctx.send(embed=embed_list[0])
        await ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command()
    @commands.is_owner()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(f">>> {message}", tts=True, delete_after=10)

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

