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
    async def reloadpatrons(self, ctx):
        """Will attempt to reload patrons

        [Format: %reloadpatrons]
        """
        await self.ex.u_cache.create_patreons()
        return await ctx.send("Done")

    @commands.command()
    async def reloadlanguages(self, ctx):
        """
        Reloads the language packs for the bot.

        [Format: %reloadlanguages]
        """
        await self.ex.u_cache.load_language_packs()
        await self.ex.u_cache.create_original_command_cache()
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

    @commands.command(aliases=["reloadcogs"])
    async def reloadmodules(self, ctx):
        """Reload all modules/cogs

        [Format: %reloadmodules]
        [Aliases: %reloadcogs]
        """
        self.startup_obj.reload_cogs()
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
    async def resetidolcache(self, ctx):
        """Reset Idol Cache."""
        await self.ex.u_cache.create_idol_cache()
        await ctx.send("Finished creating idol cache.")

    @commands.command()
    async def resetidolphotos(self, ctx):
        """Reset Idol Photo Cache."""
        await self.ex.u_cache.create_idols()
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



