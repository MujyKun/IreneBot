from Utility import resources as ex
import random
import math
from scipy.special import erf, erfinv

class Gacha:

    @staticmethod
    async def random_album_popularity():
        """Returns a random popularity between 0 and 1 that follows the PDF
        f(y) = exp( -a * (y - c)^2 ) where a is the curvature and c is the bell center.
        This is a truncated normal distribution.
        The random variable transformation g(x) : x -> y needs to be used where x is a uniform distribution
        and y is the f(x) distribution. g(x) = Fy^-1( F(x) ) where Fx = x and Fy = erf( sqrt(a)*(y - c) )
        which are the corresponding CDFs of x and y. Solving we find that
        g(x) = erfinv(x) / sqrt(a) + c."""
        center_popularity = 0.8

        curvature = 40
        lower_bound = -1
        upper_bound = erf(math.sqrt(curvature) * (1 - center_popularity))
        x = random.uniform(lower_bound, upper_bound)
        y = erfinv(x) / math.sqrt(curvature) + center_popularity
        return y

    @staticmethod
    async def random_skill_score(card_rarity):
        """Return a random skill score for rap/dance/vocal for the gacha card between 1 and 99
        dependent on the rarity of the card."""
        if card_rarity == "common":
            random.randint(1, 20)
        elif card_rarity == "uncommon":
            random.randint(21, 40)
        elif card_rarity == "rare":
            random.randint(41, 60)
        elif card_rarity == "epic":
            random.randint(61, 80)
        elif card_rarity == "legendary":
            random.randint(81, 99)
        else:
            raise ex.exceptions.ShouldNotBeHere(f"random_skill_score received the card rarity: {card_rarity} "
                                                f"which is not a valid card_rarity.")
    @staticmethod
    async def get_all_skill_scores(idol_skill_type, card_rarity):
        """Returns the rap, dance, and vocal scores of an idol"""
        skill_types = {"rap": 0, "dance": 1, "vocal": 2}

        all_skills = [0, 0, 0]
        all_skills[skill_types.get(idol_skill_type)] = await Gacha.random_skill_score(card_rarity)
        return all_skillsl