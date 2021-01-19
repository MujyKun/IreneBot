import discord
from discord.ext import commands, tasks
from Utility import resources as ex
from module import logger as log
import datetime

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

    @tasks.loop(seconds=0, minutes=5, hours=0, reconnect=True)
    async def album_loop(self):
        for user_id in ex.cache.gacha_albums:
            albums = ex.cache.gacha_albums.get(user_id)
            if not albums:
                continue
            for album in albums:
                current_time = datetime.datetime.now()
                next_money_add_time = album.last_money_generated_time + \
                                      datetime.timedelta(minutes=GachaValues.album_money_generation_time_in_minutes)
                if not album.active and current_time > next_money_add_time:
                    # TODO: Update user money in cache and in db
                    album.total_generated_currency += GachaValues.album_inactive_income_rate
                    album.last_money_generated_time = current_time
                elif album.active and current_time > next_money_add_time:
                    # TODO: Update user money in cache and in db
                    album.total_generated_currency += album.income_rate
                    album.last_money_generated_time = current_time
                if current_time > album.inactive_time:
                    album.active = False


class GachaValues:
    album_max_income_rate = 10000
    album_inactive_income_rate = 5
    album_three_skill_mult = 1
    album_two_skill_mult = 0.8
    album_one_skill_mult = 0.6
    album_money_generation_time_in_minutes = 30
    album_active_time_in_hours = 24

class IdolCard:
    def __init__(self, idol, card_owner: discord.User, issue_number=1,
                 rap_skill=0, vocal_skill=0, dance_skill=0, rarity='common'):
        self.idol = idol
        self.issue_number = issue_number
        self.rap_skill = rap_skill
        self.vocal_skill = vocal_skill
        self.dance_skill = dance_skill
        self.rarity = rarity
        self.card_owner = card_owner

    @staticmethod
    async def create_new_idol_card(user, idol=None,
                                   rap_skill=0, vocal_skill=0, dance_skill=0, card_rarity='common'):
        if not idol:
            idol = ex.u_group_members.get_random_idol()
        idol_card = IdolCard(idol, user)
        if not rap_skill:
            idol_card.rap_skill = rap_skill
        if not vocal_skill:
            idol_card.vocal_skill = vocal_skill
        if not dance_skill:
            idol_card.dance_skill = dance_skill
        setattr(idol_card, f"{idol.skill}_skill", ex.u_gacha.random_skill_score(card_rarity))

        return idol_card


class Album:
    def __init__(self, album_name, idol_cards,
                 rap_score=0, dance_score=0, vocal_score=0, popularity=0, income_rate=0,
                 album_active_time=datetime.timedelta(hours=GachaValues.album_active_time_in_hours)):
        self.album_name = album_name
        self.idol_cards = idol_cards
        self.idol_number = len(idol_cards)
        self.rap_score = rap_score
        self.dance_score = dance_score
        self.vocal_score = vocal_score
        self.popularity = popularity
        self.income_rate = income_rate
        self.active = True
        self.total_generated_currency = 0
        self.creation_time = datetime.datetime.now()
        self.inactive_time = self.creation_time + album_active_time
        self.last_money_generated_time = datetime.datetime.now()

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
        max_income_rate = GachaValues.album_max_income_rate

        completion_bonus = await self.skill_completion_multiplier()

        # This assumes that idols have only 1 primary skill that ranges 0-99.
        income_rate = int(max_income_rate * self.popularity *
                          (self.rap_score + self.dance_score + self.vocal_score) / (100 * self.idol_number)
                          * completion_bonus)
        return income_rate

    async def skill_completion_multiplier(self):
        """Provides a small bonus for having idols that fulfill all of the different categories."""
        number_of_non_zero_skills = bool(self.rap_score) + bool(self.vocal_score) + bool(self.dance_score)
        if number_of_non_zero_skills == 3:
            return GachaValues.album_three_skill_mult
        elif number_of_non_zero_skills == 2:
            return GachaValues.album_two_skill_mult
        else:
            return GachaValues.album_one_skill_mult

    async def calculate_rap_score(self):
        """Returns the total rap skills of all idols in the album"""
        return sum(idol_card.rap_skill for idol_card in self.idol_cards)

    async def calculate_dance_score(self):
        """Returns the total dance skills of all idols in the album"""
        return sum(idol_card.dance_skill for idol_card in self.idol_cards)

    async def calculate_vocal_score(self):
        """returns the total vocal skills of all idols in the album"""
        return sum(idol_card.vocal_skill for idol_card in self.idol_cards)
