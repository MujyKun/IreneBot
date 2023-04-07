from typing import Dict
from datetime import datetime
from concurrent import futures


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


# groupmembers search
distance_between_words: Dict[str, Dict[str, float]] = dict()
requests_today = 0
user_requests: Dict[int, int] = {}
current_day = datetime.now().day


from .StatsTracker import StatsTracker, Trackable


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


from .CommandTypes import (
    UserCommand,
    Command,
    RegularCommand,
    MessageCommand,
    SubCommand,
    SlashCommand,
    get_cog_dicts,
)
from .Bracket import Bracket, PvP
from .Game import Game
from .BaseRoundGame import BaseRoundGame
from .BaseScoreGame import BaseScoreGame

from .bot import Bot
from .GuessingGame import GuessingGame
from .GroupGuessingGame import GroupGuessingGame
from .UnscrambleGame import UnscrambleGame
from .BiasGame import BiasGame
