import disnake.ext.commands
from typing import TYPE_CHECKING, Dict
from . import PlayerScore

if TYPE_CHECKING:
    from . import Bot

from datetime import datetime


class Game:
    def __init__(self, bot, user, max_rounds, ctx=None, inter=None):
        self.start_time = datetime.now()
        self.end_time = None
        self.ctx: disnake.ext.commands.Context = ctx
        self.inter: disnake.AppCmdInter = inter
        self.bot: Bot = bot
        self.host_user = user
        self.max_rounds = max_rounds
        self._complete = False
        self.rounds = 0
        self.players: Dict[int, PlayerScore] = {}

    @property
    def is_complete(self):
        is_complete = self._complete or self.rounds >= self.max_rounds
        if is_complete and not self.end_time:
            self.end_time = datetime.now()
        return is_complete

    async def start(self):
        """Start the game."""
        ...

    async def send_message(self, msg):
        """Send a message using the Context and AppCmdInter objects in the game."""
        from cogs.helper import (
            send_message,
        )  # need to import here to avoid circular imports.

        await send_message(msg=msg, ctx=self.ctx, inter=self.inter)
