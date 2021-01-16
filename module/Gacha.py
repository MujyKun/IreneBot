import discord
from discord.ext import commands
from Utility import resources as ex
from module import logger as log


# noinspection PyPep8
class Gacha(commands.Cog):
    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def startgacha(self, ctx, text_channel: discord.TextChannel = None):
        """Starts Gacha in the current Text Channel.
        [Format: %startgacha]"""
        pass

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def stopgacha(self, ctx):
        """Stops Gacha in the current server.
        [Format: %stopgacha]"""
        pass

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def gachasend(self, ctx):
        """Toggles between sending large bodies of text/embeds in text channel or DMs.
        [Format: %gachasend]"""
        pass

    @commands.command(aliases=['marketplace', 'market'])
    async def mp(self, ctx, page_number):
        """View the cards on sale in the marketplace.
        [Format: %mp (page number)]"""
        pass

    @commands.command(aliases=['marketplacebuy', 'marketbuy'])
    async def mpbuy(self, ctx, card_code):
        """Buy a card in the market place.
        [Format: %mpbuy (Card Code)]"""
        pass

    @commands.command(aliases=['marketplacesell', 'marketsell'])
    async def mpsell(self, ctx, page_number):
        """Buy a card in the market place.
        [Format: %mpbuy (Card Code)]"""
        pass

    @commands.command(aliases=['inven', 'inv'])
    async def inventory(self, ctx, user: discord.User = None):
        """View a player's inventory.
        [Format: %inventory @user]"""
        pass

    @commands.command(aliases=['fuse'])
    async def evolve(self, ctx, card_1, card_2):
        """Evolve a card to a higher rarity by fusing two cards.
        [Format: %evolve (card 1) (card 2)]"""
        pass

    @commands.command(aliases=['makealbum', 'album'])
    async def createalbum(self, ctx, album_name, *, idols):
        """Create an active album with maximum 6 idols. Album names must be unique.
        [Format: %createalbum (album name) (idol 1) (idol 2) ...]"""
        idols = idols.split(' ')
        pass

    @commands.command()
    async def viewalbums(self, ctx, user: discord.User):
        """Displays all albums of a user. Shows Album ID and Album Name.
        [Format: %viewalbums @user]"""
        pass

    @commands.command()
    async def viewalbum(self, ctx, album_id):
        """View an album's information based on the album ID.
        [Format: %viewalbum (album id)]"""
        pass

    @commands.command(aliases=['gachagive'])
    async def gift(self, ctx, user: discord.User, card_id):
        """Gift a card to another person.
        [Format: %gift @user (card id)]"""
        pass

    @commands.command(aliases=['request'])
    async def offer(self, ctx, user: discord.User, amount_or_card_id):
        """Irene sends message to seller with offer details to buy a card for a certain amount or trade a card.
        [Format: %offer @user (amount/card id)]"""
        pass

    @commands.command()
    async def transfer(self, ctx, user: discord.User, amount):
        """Gives a user Purchasable currency.
        [Format: %transfer @user (amount)]"""
        pass

    @commands.command()
    async def convert(self, ctx, amount):
        """Convert Regular Currency to Purchasable Currency
        [Format: %convert (amount)]"""
        pass

    @commands.command(aliases="gachaleaderboard")
    async def gachalb(self, ctx, mode="server"):
        """Convert Regular Currency to Purchasable Currency
        [Format: %gachalb (server/global)]"""
        pass

    @commands.command()  # alias for whatever the purchasable currency is called
    async def buy(self, ctx):
        """Guide to purchasing currency.
        [Format: %buy]"""
        pass

    @commands.command()
    async def packs(self, ctx):
        """Displays information about the available (Regular/Purchasable) packs.
        [Format: %packs]"""
        pass

    @commands.command()
    async def buypack(self, ctx, pack_name):
        """Buys/Opens a pack using Regular/Purchasable Currency. (Opens Instantly)
        [Format: %buypack (pack name)]"""
        pass

