def add_to_cache(obj):
    if isinstance(obj, GroupGuessingGame):
        gggs.append(obj)
    elif isinstance(obj, GuessingGame):
        ggs.append(obj)
    elif isinstance(obj, UnscrambleGame):
        uss.append(obj)
    elif isinstance(obj, BiasGame):
        bgs.append(obj)
    else:
        others.append(obj)
    all_games.append(obj)


ggs = []  # GuessingGame
gggs = []  # GroupGuessingGame
uss = []  # UnscrambleGame
bgs = []  # BiasGame
bjs = []  # BlackJack
others = []  # etc
all_games = []

from dataclasses import dataclass
from IreneAPIWrapper.models import User, UserStatus
import disnake


@dataclass
class PlayerScore(UserStatus):
    user: User
    disnake_user: disnake.User
    status: UserStatus

    def __str__(self):
        return f"{self.disnake_user.display_name} -> {self.status.score}."


from .Bracket import Bracket, PvP
from .Game import Game
from .BaseRoundGame import BaseRoundGame
from .BaseScoreGame import BaseScoreGame

from .bot import Bot
from .GuessingGame import GuessingGame
from .GroupGuessingGame import GroupGuessingGame
from .UnscrambleGame import UnscrambleGame
from .BiasGame import BiasGame
