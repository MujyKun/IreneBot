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


class IdolCard():
    def __init__(self, idol, issue_number, rap_skill, vocal_skill, dance_skill, rarity):
        self.idol = idol
        self.issue_number = issue_number
        self.rap_skill = rap_skill
        self.vocal_skill = vocal_skill
        self.dance_skill = dance_skill
        self.rarity = rarity

    @staticmethod
    async def create_new_idol_card(user):
        pass


class Album():
    def __init__(self, album_name, idol_cards, rap_score, dance_score, vocal_score, popularity, income_rate):
        self.album_name = album_name
        self.idol_cards = idol_cards
        self.idol_number = len(idols)
        self.rap_score = rap_score
        self.dance_score = dance_score
        self.vocal_score = vocal_score
        self.popularity = popularity
        self.income_rate = income_rate
        self.active = True
        self.total_generated_currency = 0

    @staticmethod
    async def create_album(album_name, idol_cards):
        popularity = await ex.u_gacha.random_album_popularity()
        album = Album(album_name, idol_cards, popularity=popularity)
        album.rap_score = await album.calculate_rap_score()
        album.dance_score = await album.calculate_dance_score()
        album.vocal_score = await album.calculate_vocal_score()
        album.income_rate = await album.calculate_income_rate()

        await album.calculate_income_rate()

        return album

    async def calculate_income_rate(self):
        max_income_rate = 10000

        completion_bonus = await self.full_group_stat_bonus()
        # This assumes that idols have only 1 primary skill that ranges 0-99.
        income_rate = max_income_rate * self.popularity \
                      * (self.rap_score + self.dance_score + self.vocal_score) / (100*self.idol_number) \
                      * completion_bonus

    async def full_group_stat_bonus(self):
        """Provides a small bonus for having idols that fulfill all of the different categories."""
        number_of_non_zero_skills = bool(self.rap_score) + bool(self.vocal_score) + bool(self.dance_score)
        if number_of_non_zero_skills == 3:
            return 1
        elif number_of_non_zero_skills == 2:
            return 0.8
        else:
            return 0.6

    async def calculate_rap_score(self):
        """Returns the total rap skills of all idols in the album"""
        return sum(idol_card.rap_skill for idol_card in self.idol_cards)

    async def calculate_dance_score(self):
        """Returns the total dance skills of all idols in the album"""
        return sum(idol_card.dance_skill for idol_card in self.idol_cards)

    async def calculate_vocal_score(self):
        """returns the total vocal skills of all idols in the album"""
        return sum(idol_card.vocal_skill for idol_card in self.idol_cards)
