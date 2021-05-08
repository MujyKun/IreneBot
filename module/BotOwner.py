import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log


# noinspection PyPep8
class BotOwner(commands.Cog):
    def __init__(self, ex):
        self.ex = ex

    @commands.is_owner()
    @commands.command()
    async def resetcache(self, ctx):
        """Reset the cache."""
        await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'cache_reset'))
        await self.ex.u_cache.create_cache(on_boot_up=False)

    @commands.is_owner()
    @commands.command()
    async def scandrive(self, ctx, name="NULL", member_id=0):
        """Scan DriveIDs Table and update other tables."""
        try:
            all_links = await self.ex.conn.fetch("SELECT id, linkid, name FROM archive.DriveIDs")
            for p_id, link_id, link_name in all_links:
                try:
                    new_link = f"https://drive.google.com/uc?export=view&id={link_id}"
                    all_names = await self.ex.conn.fetch("SELECT Name FROM archive.ChannelList")
                    if name == "NULL" and member_id == 0:
                        for idol_name in all_names:
                            idol_name = idol_name[0]
                            if idol_name == link_name and (idol_name != "Group" or idol_name != "MDG Group"):
                                member_id1 = self.ex.first_result(await self.ex.conn.fetchrow("SELECT ID FROM groupmembers.Member WHERE StageName = $1", idol_name))
                                await self.ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id1)
                                await self.ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", p_id)
                    elif link_name.lower() == name.lower():
                        await self.ex.conn.execute("DELETE FROM archive.DriveIDs WHERE ID = $1", p_id)
                        await self.ex.conn.execute("INSERT INTO groupmembers.uploadimagelinks VALUES($1,$2)", new_link, member_id)
                except Exception as e:
                    log.console(e)
            await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'scan_drive_complete'))
        except Exception as e:
            log.console(e)

    @commands.command()
    @commands.is_owner()
    async def addcards(self, ctx):
        """Fill The CardValues Table with Cards [Format: %addcards]"""
        await self.ex.conn.execute("DELETE FROM blackjack.cards")
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
            await self.ex.conn.execute("INSERT INTO blackjack.cards (id, name, value) VALUES ($3, $1, $2)", card, card_values[count_x], count_x+1)
        await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'cards_added'), delete_after=40)

    @commands.command()
    @commands.is_owner()
    async def addpatreon(self, ctx, *, users):
        """Adds a patreon. [Format: %addpatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user_id in users:
            await self.ex.u_patreon.add_to_patreon(user_id)
        msg = await self.ex.get_msg(ctx, 'botowner', 'patrons_added')
        msg = await self.ex.replace(msg, ['users', users])
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def removepatreon(self, ctx, *, users):
        """Removes a patreon. [Format: %removepatreon (userid,userid,userid)]"""
        users = users.split(",")
        for user_id in users:
            await self.ex.u_patreon.remove_from_patreon(user_id)
        msg = await self.ex.get_msg(ctx, 'botowner', 'patrons_removed')
        msg = await self.ex.replace(msg, ['users', users])
        await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def clearnword(self, ctx, user: discord.Member):
        """Clear A User's Nword Counter [Format: %clearnword @user]"""
        if not (await self.ex.get_user(user.id)).n_word:
            return await ctx.send(await self.ex.get_msg(ctx, 'general', 'no_n_word'))

        await self.ex.conn.execute("DELETE FROM general.nword where userid = $1", user.id)
        (await self.ex.get_user(user.id)).n_word = 0
        await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'cleared'))

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, channel_id, *, message_to_send):
        """Send a message to a text channel."""
        try:
            channel = await self.ex.client.fetch_channel(channel_id)  # 403 forbidden on tests.
            await channel.send(message_to_send)
            await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'message_sent'))
        except Exception as e:
            log.console(e)
            msg = await self.ex.get_msg(ctx, 'general', 'error_no_support')
            msg = await self.ex.replace(msg, ['e', e])
            await ctx.send(msg)

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
            group = await self.ex.conn.fetchrow("""SELECT groupname, debutdate, disbanddate, description, twitter, youtube, 
            melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website, thumbnail, banner,
             gender, tags FROM groupmembers.unregisteredgroups WHERE id = $1""", query_id)

            # create a new group
            await self.ex.conn.execute("""INSERT INTO groupmembers.groups(groupname, debutdate, disbanddate, description, 
            twitter, youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website,
             thumbnail, banner, gender, tags) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
             $15, $16, $17, $18, $19, $20)""", *group)

            # get the new group's ID
            group_id = self.ex.first_result(await self.ex.conn.fetchrow("""SELECT groupid FROM groupmembers.groups WHERE 
            groupname = $1 ORDER BY groupid DESC""", group.get("groupname")))

            # send message to the approver.
            msg = await self.ex.get_msg(ctx, 'botowner', 'group_query_approved')
            msg = await self.ex.replace(msg, [['query_id', query_id], ['group_id', group_id]])
            await ctx.send(msg)

        if mode == "idol":
            # get the query
            idol = await self.ex.conn.fetchrow("""SELECT fullname, stagename, formerfullname, formerstagename, birthdate, 
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify, 
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags
            FROM groupmembers.unregisteredmembers WHERE id = $1""", query_id)

            # make a separate call for group ids to separate the record later for inserting.
            group_ids = self.ex.first_result(await self.ex.conn.fetchrow("""SELECT groupids FROM groupmembers.unregisteredmembers WHERE id = $1""", query_id))
            if group_ids:
                group_ids = group_ids.split(',')

            # create a new idol
            await self.ex.conn.execute("""INSERT INTO groupmembers.member(fullname, stagename, formerfullname, formerstagename, birthdate, 
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify, 
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
             $15, $16, $17, $18, $19, $20, $21 ,$22, $23, $24)""", *idol)

            # get the new idol's ID
            idol_id = self.ex.first_result(await self.ex.conn.fetchrow("""SELECT id FROM groupmembers.member WHERE fullname = $1 
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
                    group = await self.ex.u_group_members.get_group_where_group_matches_name(group_id)
                    if group:
                        # add to the first group found in the list
                        # not accurate, but IDs should have been given anyway.
                        # will be accurate if the full group name is given.
                        group_id = group[0].id
                try:
                    await self.ex.conn.execute("""INSERT INTO groupmembers.idoltogroup(idolid, groupid) 
                    VALUES($1, $2)""", idol_id, group_id)
                except Exception as e:
                    log.console(e)
                    msg = await self.ex.get_msg(ctx, 'botowner', 'group_fail')
                    msg = await self.ex.replace(msg, ['group_id', group_id])
                    await ctx.send(msg)

            # send message to the approver.
            msg = await self.ex.get_msg(ctx, 'botowner', 'idol_query_approved')
            msg = await self.ex.replace(msg, [['query_id', query_id], ['idol_id', idol_id], ['group_ids', group_ids]])
            await ctx.send(msg)

        # reset cache for idols/groups.
        await self.ex.u_cache.create_group_cache()
        await self.ex.u_cache.create_idol_cache()

