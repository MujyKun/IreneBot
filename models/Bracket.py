import asyncio
from math import log2
from IreneAPIWrapper.models import AbstractModel, Person
from typing import List, Dict, Optional
from random import shuffle


class Bracket:
    """Represents a tournament bracket."""

    def __init__(self, bracket_size):
        if bracket_size > 32:
            bracket_size = 32
        elif bracket_size < 4:
            bracket_size = 4
        self.size = 2 ** int(
            log2(bracket_size)
        )  # rounds down to the closest power of 2.
        self.rounds: Dict[int, List[PvP]] = {}
        self._chosen_pool = []
        self.final_winner: Optional[Person] = None

    @property
    def max_round(self):
        return 0 if not self.rounds else max(self.rounds.keys())

    def get_dict(self):
        """Get a dict with no objects to be sent over a route."""
        rounds_as_dict = {}
        for key, list_of_pvps in self.rounds.items():
            rounds_as_dict[key] = []
            for pvp in list_of_pvps:
                rounds_as_dict[key].append(pvp.get_dict())
        return rounds_as_dict

    async def get_known_pvps(self):
        return list(set([pvp for list_pvp in self.rounds.values() for pvp in list_pvp]))

    async def select_from_pool(self, pool: List[AbstractModel]) -> bool:
        if len(pool) < self.size:
            return False

        shuffle(pool)
        self._chosen_pool = pool[0 : self.size]

        self.rounds[self.max_round + 1] = await PvP.create(self._chosen_pool)
        return True

    async def next_round(self):
        """Go to the next round of the bracket.

        :returns: bool
            If the game is over.
        """
        c_round_pvp_list: List[PvP] = self.rounds[self.max_round]
        winners: List[AbstractModel] = [pvp.winner for pvp in c_round_pvp_list]

        next_round_list = []

        if len(winners) == 1:  # game is over
            self.final_winner = winners[0]
            return True

        already_used = []
        for idx, winner_one in enumerate(winners, start=0):
            if idx in already_used:
                continue

            already_used += [idx, idx + 1]

            winner_two = winners[idx + 1]
            next_round_list.append(PvP(winner_one, winner_two))

        self.rounds[self.max_round + 1] = next_round_list


class PvP:
    def __init__(self, player_one: AbstractModel, player_two: AbstractModel):
        self.player_one = player_one
        self.player_two = player_two
        self.winner = None
        self.img_url: Optional[str] = None

    def __eq__(self, other):
        return self.player_one == other.player_one and self.player_two == other.player_two

    def __hash__(self):
        return self.get_dict()

    def get_dict(self):
        return {
            "player_one": self.player_one.id,
            "player_two": self.player_two.id,
            "winner": self.winner.id,
        }

    @property
    def is_complete(self) -> bool:
        return self.winner is not None

    @staticmethod
    async def create(pool) -> list:
        """
        Creates PvP objects for a bracket based on a list of players.

        Should not be used if going to the next round of a bracket.
        Should only be used if starting out a bracket and there are no player standings.

        :returns: List[PvP]
        """
        pvp_list = []
        for idx, player in enumerate(pool, start=1):
            if idx > (len(pool) // 2):
                continue
            pvp_list.append(PvP(player, pool[0 - idx]))
        return pvp_list
