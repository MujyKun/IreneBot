from decimal import Decimal
from math import log10
from random import randint
from util.sql import SQL

sql: SQL = None


# noinspection PyBroadException
class User:
    """Represents a discord user."""
    def __init__(self, user_id: int):
        self.id = user_id
        self.mod_mail_channel_id: int = None
        self.bot_banned: bool = False
        self.idol_cards: list = []
        self.gacha_albums: list = []
        self.patron: bool = False
        self.super_patron: bool = False
        self.notifications: list = []  # [ [guild_id, phrase], ... ]
        self.reminders: list = []  # [ [remind_id, remind_reason, remind_time], ... ]
        self.timezone: str = None
        self.n_word: int = 0  # amount of times the user has said the N-Word.
        self.gg_filter: bool = False
        self.gg_groups: list = []
        self.money: int = -1
        self.profile_level: int = 0
        self.beg_level: int = 0
        self.rob_level: int = 0
        self.daily_level: int = 0
        self.language: str = "en_us"

        # On initial imports, sql is not defined, so it is better to do it upon user construction.
        global sql
        if not sql:
            from util.asyncpg import sql as t_sql
            sql = t_sql

    async def set_profile_level(self, level):
        """Set the profile level."""
        await self.ensure_level()
        await self.update_level_in_db("profile", level)
        self.profile_level = level

    async def set_beg_level(self, level):
        """Set the beg level."""
        await self.ensure_level()
        await self.update_level_in_db("beg", level)
        self.beg_level = level

    async def set_rob_level(self, level):
        """Set the rob level."""
        await self.ensure_level()
        await self.update_level_in_db("rob", level)
        self.rob_level = level

    async def set_daily_level(self, level):
        """Set the daily level."""
        await self.ensure_level()
        await self.update_level_in_db("daily", level)
        self.daily_level = level

    async def ensure_level(self):
        """Ensure the user has a row in the levels table."""
        if self.profile_level or self.beg_level or self.rob_level or self.daily_level:
            return
        else:
            await sql.create_level_row(self.id)

    async def update_level_in_db(self, column_name, level):
        """Update the level for the user."""
        allowed_columns = ['profile', 'beg', 'rob', 'daily']
        if column_name in allowed_columns:
            await sql.update_level(self.id, column_name, level)

    @staticmethod
    async def get_xp_needed(level: int, column_name: str):
        """Returns money/experience needed for a certain level."""
        if column_name == "profile":
            return 250 * level
        return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)

    async def get_rob_percentage(self):
        """Get the percentage of being able to rob. (Every 1 is 5%)"""
        chance = int(6 + (self.rob_level // 10))  # first 10 levels is 6 for 30% chance
        if chance > 16:
            chance = 16
        return chance

    async def register_currency(self):
        """Registers the user to the currency system."""
        if self.money == -1:
            self.money = 100
            await sql.register_currency(self.id, self.money)

    async def update_balance(self, balance: int = None, add: int = None, remove: int = None):
        """Set balance of user in db and object."""
        if self.money == -1:
            await self.register_currency()
            # accounting for new registered users receiving 100 when updating balance.
            if balance:
                self.money = balance + self.money
        else:
            if balance:
                self.money = balance

        if add:
            self.money += add

        if remove:
            self.money -= remove

        # make sure money can never be negative.
        if self.money < -1:
            self.money = 0

        await sql.update_user_balance(self.id, str(self.money))

    async def get_shortened_balance(self) -> str:
        """Shorten an amount of money to its value places."""
        place_names = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion', 'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quatturodecillion', 'Quindecillion', 'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion', 'Centillion']
        try:
            place_values = int(log10(self.money) // 3)
        except:
            # This will have a math domain error when the balance is 0.
            return "0"
        try:
            return f"{self.money // (10 ** (3 * place_values))} {place_names[place_values]}"
        except:
            # user has money outside of the value places. resort to scientific notation.
            return f"{Decimal(self.money):.2E}"

    async def get_rob_amount(self, money):
        """
        The amount to rob a specific person based on their rob level.

        :param money: (The amount of money the person getting robbed has)
        """
        base_rob_percentage = 0.01
        max_rob_percentage = 0.21  # [(0.21-0.01) / 0.0005] = 400 as the max rob level.
        increment_per_level = 0.0005

        rob_percentage = base_rob_percentage + (self.rob_level * increment_per_level)

        # confirm rob percentage never goes above max (in case the rob level cap is increased)
        if rob_percentage > max_rob_percentage:
            rob_percentage = max_rob_percentage

        return randint(0, rob_percentage * money)

    async def get_daily_amount(self):
        """Get the amount the user should receive daily."""
        base_daily = 50
        return base_daily if not self.daily_level else base_daily * self.daily_level

    async def set_language(self, language):
        """Sets the user's language."""
        self.language = language
        await sql.delete_user_language(self.id)

        # user language is en_us by default. We do not want it in the db.
        if self.language == 'en_us':
            return

        await sql.set_user_language(self.id, language)



