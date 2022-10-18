import disnake.ext.commands
from typing import TYPE_CHECKING, Dict
from . import PlayerScore, add_to_cache

if TYPE_CHECKING:
    from . import Bot

from datetime import datetime


class Game:
    def __init__(self, bot, user, ctx=None, inter=None):
        self.start_time = datetime.now()
        self.end_time = None
        self.ctx: disnake.ext.commands.Context = ctx
        self.inter: disnake.AppCmdInter = inter
        self.bot: Bot = bot
        self.host_user = user
        self._complete = False
        self.players: Dict[int, PlayerScore] = {}
        add_to_cache(self)

    @property
    def is_complete(self):
        is_complete = self._complete
        if is_complete and not self.end_time:
            self.end_time = datetime.now()
        return is_complete

    async def start(self):
        """Start the game."""
        ...

    async def stop(self):
        self._complete = True

    async def get_message(self, key, *custom_args):
        """Get a message using the host user."""
        from cogs.helper import (
            get_message,
        )  # need to import here to avoid circular imports.

        return await get_message(self.host_user, key, *custom_args)

    async def send_message(
        self, *custom_args, key=None, msg=None, view=None, delete_after=None
    ):
        """Send a message using the Context and AppCmdInter objects in the game."""
        from cogs.helper import (
            send_message,
        )  # need to import here to avoid circular imports.

        return await send_message(
            *custom_args,
            key=key,
            ctx=self.ctx,
            inter=self.inter,
            user=self.host_user,
            msg=msg,
            view=view,
            delete_after=delete_after,
        )
