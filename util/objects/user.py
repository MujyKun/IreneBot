class User:
    """Represents a discord user."""
    def __init__(self, user_id: int):
        self.id = user_id
        self.mod_mail_channel_id: int = None
        self.bot_banned: bool = False
        self.idol_cards: list = []
        self.gacha_albums: list = []
        self.patron: bool = False
        self.super_patron: bool = False
        self.notifications: list = []  # [ [guild_id, phrase], ... ]
        self.reminders: list = []  # [ [remind_id, remind_reason, remind_time], ... ]
        self.timezone: str = None


