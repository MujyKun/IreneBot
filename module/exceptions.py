class TooLarge(Exception):
    """The input was too long."""
    def __init__(self):
        super(TooLarge, self).__init__("That number was too large.")
