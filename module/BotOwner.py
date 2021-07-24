import asyncio
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..run import Irene


# noinspection PyPep8
class BotOwner(commands.Cog):
    def __init__(self, ex, startup_object):
        self.ex: Utility = ex

        # Does not serve as an actual discord client, but is the manager and main startup class.
        self.startup_obj: Irene = startup_object

    async def cog_check(self, ctx):
        """A local check for this cog."""
        return await self.ex.client.is_owner(ctx.author)

    @commands.command()
    async def reloadnodes(self, ctx):
        """Will reload the music nodes.

        [Format: %reloadnodes]
        """
        # TODO: Add to commands.json
        for key, node in self.ex.u_music.node_pool.nodes.copy().items():
            await node.disconnect(force=True)
        await self.ex.u_music.start_nodes()
        return await ctx.send("Done")

    @commands.command()
    async def reload(self, ctx):
        """Will hot reload all of IreneBot, IreneUtility, and any other self-made packages.

        [Format: %reload]
        """
        self.startup_obj.reload()
        return await ctx.send("Done")

    @commands.command()
    async def reloadutility(self, ctx):
        """
        Reloads the utility package for the bot.

        [Format: %reloadutility]
        """
        self.startup_obj.reload_utility()
        return await ctx.send("Done")

    @commands.command(aliases=["reloadcog"])
    async def reloadmodule(self, ctx, *, module_name: str):
        """Reload a module/cog from it's name.

        [Format: %reloadmodule (module name)]
        [Aliases: %reloadcog (cog name)]
        """
        cog = self.startup_obj.cogs[module_name.lower()]
        self.startup_obj.reload_cog(cog)
        return await ctx.send("Done")

    @commands.command()
    async def uploadfromhost(self, ctx):
        """Toggles whether images are uploaded from host or not.

        [Format: %uploadfromhost]
        """
        self.ex.upload_from_host = not self.ex.upload_from_host
        return await ctx.send(f"Uploading from host is now set to {self.ex.upload_from_host}")

    @commands.command()
    async def resetcache(self, ctx):
        """Reset the cache."""
        await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'cache_reset'))
        await self.ex.u_cache.create_cache(on_boot_up=False)

    @commands.command()
    async def addcards(self, ctx):
        """
        Fill The CardValues Table with Cards

        [Format: %addcards]
        """
        await self.ex.conn.execute("DELETE FROM blackjack.cards")
        suit_names = ("Hearts", "Diamonds", "Spades", "Clubs")
        rank_names = ("Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
                      "Eight", "Nine", "Ten", "Jack", "Queen", "King")
        card_values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2,
                       3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        cards = []
        for suit in suit_names[0:4]:
            for rank in rank_names[0:13]:
                cards += [("{} of {}".format(rank, suit))]
        count_x = -1
        for card in cards:
            count_x += 1
            await self.ex.conn.execute("INSERT INTO blackjack.cards (id, name, value) VALUES ($3, $1, $2)", card,
                                       card_values[count_x], count_x+1)
        await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'cards_added'), delete_after=40)

    @commands.command()
    async def addpatreon(self, ctx, *, users):
        """
        Adds a patreon.

        [Format: %addpatreon (userid,userid,userid)]
        """
        users = users.split(",")
        for user_id in users:
            await asyncio.sleep(0)
            await self.ex.u_patreon.add_to_patreon(user_id)
        msg = await self.ex.get_msg(ctx, 'botowner', 'patrons_added', ['users', users])
        await ctx.send(msg)

    @commands.command()
    async def removepatreon(self, ctx, *, users):
        """
        Removes a patreon.

        [Format: %removepatreon (userid,userid,userid)]
        """
        users = users.split(",")
        for user_id in users:
            await asyncio.sleep(0)
            await self.ex.u_patreon.remove_from_patreon(user_id)
        msg = await self.ex.get_msg(ctx, 'botowner', 'patrons_removed', ['users', users])
        await ctx.send(msg)

    @commands.command()
    async def send(self, ctx, channel_id, *, message_to_send):
        """Send a message to a text channel."""
        try:
            channel = await self.ex.client.fetch_channel(channel_id)  # 403 forbidden on tests.
            await channel.send(message_to_send)
            await ctx.send(await self.ex.get_msg(ctx, 'botowner', 'message_sent'))
        except Exception as e:
            log.console(e)
            msg = await self.ex.get_msg(ctx, 'general', 'error_no_support', ['e', e])
            await ctx.send(msg)

    @commands.command()
    async def speak(self, ctx, *, message):
        """Owner to Bot TTS"""
        await ctx.send(f">>> {message}", tts=True, delete_after=10)

    @commands.command()
    async def generateplayingcards(self, ctx):
        """Generate custom playing cards with idol avatars."""
        await ctx.send("> Deleting and regenerating playing cards.")
        await self.ex.u_blackjack.generate_playing_cards()
        await ctx.send("> Finished generating all playing cards.")

    @commands.command()
    async def approve(self, ctx, query_id: int, mode="idol"):
        """Approve a query id for an unregistered group or idol."""
        if mode == "group":
            # get the query
            group = await self.ex.conn.fetchrow("""SELECT groupname, debutdate, disbanddate, description, twitter,
            youtube,
            melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website, thumbnail, banner,
             gender, tags FROM groupmembers.unregisteredgroups WHERE id = $1""", query_id)

            # create a new group
            await self.ex.conn.execute("""INSERT INTO groupmembers.groups(groupname, debutdate, disbanddate,
            description,
            twitter, youtube, melon, instagram, vlive, spotify, fancafe, facebook, tiktok, fandom, company, website,
             thumbnail, banner, gender, tags) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
             $15, $16, $17, $18, $19, $20)""", *group)

            # get the new group's ID
            group_id = self.ex.first_result(await self.ex.conn.fetchrow("""SELECT groupid FROM groupmembers.groups WHERE
            groupname = $1 ORDER BY groupid DESC""", group.get("groupname")))

            # send message to the approver.
            msg = await self.ex.get_msg(ctx, 'botowner', 'group_query_approved', [['query_id', query_id],
                                                                                  ['group_id', group_id]])
            await ctx.send(msg)

        if mode == "idol":
            # get the query
            idol = await self.ex.conn.fetchrow("""SELECT fullname, stagename, formerfullname, formerstagename,
            birthdate,
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify, 
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags
            FROM groupmembers.unregisteredmembers WHERE id = $1""", query_id)

            # make a separate call for group ids to separate the record later for inserting.
            group_ids = self.ex.first_result(await self.ex.conn.fetchrow(
                "SELECT groupids FROM groupmembers.unregisteredmembers WHERE id = $1", query_id))
            if group_ids:
                group_ids = group_ids.split(',')

            # create a new idol
            await self.ex.conn.execute("""INSERT INTO groupmembers.member(fullname, stagename, formerfullname,
            formerstagename, birthdate,
            birthcountry, birthcity, gender, description, height, twitter, youtube, melon, instagram, vlive, spotify,
            fancafe, facebook, tiktok, zodiac, thumbnail, banner, bloodtype, tags) VALUES($1, $2, $3, $4, $5, $6, $7, 
            $8, $9, $10, $11, $12, $13, $14,
             $15, $16, $17, $18, $19, $20, $21 ,$22, $23, $24)""", *idol)

            # get the new idol's ID
            idol_id = self.ex.first_result(
                await self.ex.conn.fetchrow("""SELECT id FROM groupmembers.member WHERE fullname = $1
            AND stagename = $2 ORDER BY id DESC""", idol.get("fullname"), idol.get("stagename")))

            # create the idol to group relationships.
            for group_id in group_ids:
                await asyncio.sleep(0)
                try:
                    # check if the group id can be made into an integer when it doesn't have spaces.
                    # fancy way of doing .replace (the attribute doesn't exist)
                    group_id_without_spaces = ("".join(char for char in group_id if char != " "))
                    int(group_id_without_spaces)
                    # if it succeeds, replace the current group id with the version without spaces
                    group_id = int(group_id_without_spaces)
                except Exception as e:
                    log.useless(f" {e} (Exception) | {group_id} -> could not make the group id an integer, "
                                f"it must be a group name.", method=self.approve)
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
                    msg = await self.ex.get_msg(ctx, 'botowner', 'group_fail', ['group_id', group_id])
                    await ctx.send(msg)

            # send message to the approver.
            msg = await self.ex.get_msg(ctx, 'botowner', 'idol_query_approved',
                                        [['query_id', query_id], ['idol_id', idol_id], ['group_ids', group_ids]])
            await ctx.send(msg)

        # reset cache for idols/groups.
        # await self.ex.u_cache.create_group_cache()
        # await self.ex.u_cache.create_idol_cache()

    @commands.command()
    async def resetidolcache(self, ctx):
        """Reset Idol Cache."""
        await self.ex.u_cache.create_idol_cache()
        await ctx.send("Finished creating idol cache.")

    @commands.command()
    async def resetgroupcache(self, ctx):
        """Reset Group Cache."""
        await self.ex.u_cache.create_group_cache()
        await ctx.send("Finished creating group cache.")

    @commands.command()
    async def resetgroupphotos(self, ctx):
        """Resets the amount of photos for groups."""
        # TODO: Add to commands.json
        await self.ex.u_cache.create_groups()
        await ctx.send("Finished creating group photo cache.")

    @commands.command()
    async def callidol(self, ctx, idol_id: int, amount: int):
        """Call an idol a certain amount of times.

        Amount of calls must be lower than 100.
        [Format: %callidol (idol id) (amount)]
        """
        # TODO: Add to commands.json
        member = await self.ex.u_group_members.get_member(idol_id)
        for i in range(amount if amount < 100 else 100):
            await self.ex.u_group_members.idol_post(ctx.channel, member)



