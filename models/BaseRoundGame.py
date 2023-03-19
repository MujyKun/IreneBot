from . import Game
from datetime import datetime


class BaseRoundGame(Game):
    def __init__(self, bot, user, max_rounds, ctx=None, inter=None):
        super(BaseRoundGame, self).__init__(bot, user, ctx=ctx, inter=inter)
        self.max_rounds = max_rounds
        self.rounds = 0

    @property
    def is_complete(self):
        is_complete = self._complete or self.rounds >= self.max_rounds
        if is_complete and not self.end_time:
            self.end_time = datetime.now()
        return is_complete
