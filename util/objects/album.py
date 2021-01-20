import datetime
from Utility import resources as ex


class Album:
    def __init__(self, album_name, idol_cards,
                 rap_score=0, dance_score=0, vocal_score=0, popularity=0, income_rate=0, album_active_time=None):
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
        if not album_active_time:
            # This was reverted from the parameters due to GachaValues object not existing in Utility till
            # after run.py has fully loaded. Having this check will allow the bot to run fine.
            album_active_time = datetime.timedelta(hours=ex.u_objects.GachaValues.album_active_time_in_hours)
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
        max_income_rate = ex.u_objects.GachaValues.album_max_income_rate

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
            return ex.u_objects.GachaValues.album_three_skill_mult
        elif number_of_non_zero_skills == 2:
            return ex.u_objects.GachaValues.album_two_skill_mult
        else:
            return ex.u_objects.GachaValues.album_one_skill_mult

    async def calculate_rap_score(self):
        """Returns the total rap skills of all idols in the album"""
        return sum(idol_card.rap_skill for idol_card in self.idol_cards)

    async def calculate_dance_score(self):
        """Returns the total dance skills of all idols in the album"""
        return sum(idol_card.dance_skill for idol_card in self.idol_cards)

    async def calculate_vocal_score(self):
        """returns the total vocal skills of all idols in the album"""
        return sum(idol_card.vocal_skill for idol_card in self.idol_cards)
