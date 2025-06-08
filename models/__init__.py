from typing import Dict
from datetime import datetime
from concurrent import futures


# groupmembers search
distance_between_words: Dict[str, Dict[str, float]] = dict()
requests_today = 0
user_requests: Dict[int, int] = {}
current_day = datetime.now().day


PUNISHMENTS = {
    'mute': 'been muted',
    'ban': 'been banned',
    'delete': 'had their message deleted'
}


from .StatsTracker import StatsTracker, Trackable


from dataclasses import dataclass
from IreneAPIWrapper.models import User, UserStatus
import disnake


from .CommandTypes import (
    UserCommand,
    Command,
    RegularCommand,
    MessageCommand,
    SubCommand,
    SlashCommand,
    get_cog_dicts,
)

from .bot import Bot
