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
