import datetime
from typing import Optional, Dict
from IreneAPIWrapper.models import StatsUpdater
from keys import get_keys

BOT_NAME = get_keys().bot_name.lower()


class Trackable:
    """
    An entity that is being tracked.

    :param name: str
        What is being tracked.
    :param frequency: int
        How often the object is tracked (in seconds).
    :param value: int
        The value to be set.
    """

    def __init__(self, name: str, value: int = 0, frequency: int = 60):
        if BOT_NAME not in name.lower():
            name = f"{BOT_NAME}2-{name.lower()}"
        self.name = name
        self.frequency = frequency
        self.value = value
        self._updated_last: Optional[datetime.timedelta] = None  # last update period.

    async def update(self):
        """Update the value of the entity."""
        if not self.ready_to_update:
            return

        # update to API.
        # call wrapper
        await StatsUpdater.update(key=self.name, value=self.value)

        self._updated_last = datetime.datetime.utcnow()

    @property
    def ready_to_update(self):
        """Check whether the value is ready to be sent to the API."""
        current_time = datetime.datetime.utcnow()
        self._updated_last = self._updated_last or current_time
        return (current_time - self._updated_last).total_seconds() > self.frequency


class StatsTracker:
    """
    Track the stats of :ref:`Trackable` objects throughout the bot.

    """

    def __init__(self, trackables: Dict[str, Trackable] = None):
        self.trackables: Dict[str, Trackable] = trackables or dict()

    async def update_to_api(self, logger=None):
        """Update all trackables to the API if they need to be."""
        for trackable in self.trackables.values():
            if trackable.ready_to_update:
                try:
                    await trackable.update()
                except Exception as e:
                    logger.warn(
                        f"Failed to update Stats key {trackable.name} to value {trackable.value} -> {e}"
                    )
