from module import logger as log


class TooLarge(Exception):
    """The input was too long."""
    def __init__(self):
        super(TooLarge, self).__init__("That number was too large.")


class ImproperFormat(Exception):
    """Invalid Format was given."""
    def __init__(self):
        super(ImproperFormat, self).__init__("An Invalid Format was given.")


class NoTimeZone(Exception):
    """No Timezone was found."""
    def __init__(self):
        super(NoTimeZone, self).__init__("The user did not have a timezone.")


class MaxAttempts(Exception):
    """Essentially StopIteration, but created for logging to file & console upon raising error."""
    def __init__(self, msg):
        super(MaxAttempts, self).__init__(f"Max Attempts reached. - {msg}")
        log.console(msg)


class ShouldNotBeHere(Exception):
    """Raised when safe-guarded code is created. If this exception is raised, the code reached a point it should not
    have"""
    def __init__(self, msg):
        super(ShouldNotBeHere, self).__init__(f"Code was reached when it shouldn't have been - {msg}")
        log.console(msg)
