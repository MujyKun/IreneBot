from Utility import resources as ex
import math
import random


# noinspection PyBroadException,PyPep8
class Currency:
    @staticmethod
    async def register_user(user_id):
        """Register a user to the database if they are not already registered."""
        count = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.Currency WHERE UserID = $1", user_id))
        if not count:
            await ex.conn.execute("INSERT INTO currency.Currency (UserID, Money) VALUES ($1, $2)", user_id, "100")
            return True

    @staticmethod
    async def get_user_has_money(user_id):
        """Check if a user has money."""
        return not ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) FROM currency.Currency WHERE UserID = $1", user_id)) == 0

    async def get_balance(self, user_id):
        """Get current balance of a user."""
        if not (await self.register_user(user_id)):
            money = await ex.conn.fetchrow("SELECT money FROM currency.currency WHERE userid = $1", user_id)
            return int(ex.first_result(money))
        else:
            return 100

    @staticmethod
    async def shorten_balance(money):  # money must be passed in as a string.
        """Shorten an amount of money to it's value places."""
        place_names = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion', 'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quatturodecillion', 'Quindecillion', 'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion', 'Centillion']
        try:
            place_values = int(math.log10(int(money)) // 3)
        except:
            # This will have a math domain error when the amount of balance is 0.
            return "0"
        try:
            return f"{int(money) // (10 ** (3 * place_values))} {place_names[place_values]}"
        except:
            return "Too Fucking Much$"

    @staticmethod
    async def update_balance(user_id, new_balance):
        """Update a user's balance."""
        await ex.conn.execute("UPDATE currency.Currency SET Money = $1::text WHERE UserID = $2", str(new_balance), user_id)

    @staticmethod
    async def get_robbed_amount(author_money, user_money, level):
        """The amount to rob a specific person based on their rob level."""
        max_amount = int(user_money // 100)  # b value
        if max_amount > int(author_money // 2):
            max_amount = int(author_money // 2)
        min_amount = int((max_amount * level) // 100)
        if min_amount > max_amount:  # kind of ironic, but it is possible for min to surpass max in this case
            robbed_amount = random.randint(max_amount, min_amount)
        else:
            robbed_amount = random.randint(min_amount, max_amount)
        return robbed_amount

