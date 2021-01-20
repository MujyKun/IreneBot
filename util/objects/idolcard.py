import discord
from Utility import resources as ex


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
        idol_card = ex.u_objects.IdolCard(idol, user)
        if not rap_skill:
            idol_card.rap_skill = rap_skill
        if not vocal_skill:
            idol_card.vocal_skill = vocal_skill
        if not dance_skill:
            idol_card.dance_skill = dance_skill
        setattr(idol_card, f"{idol.skill}_skill", ex.u_gacha.random_skill_score(card_rarity))

        return idol_card
