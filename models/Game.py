from dislash import SlashInteraction

class Game:
    def __init__(self, inter: SlashInteraction):
        self.host_id: int = inter.author.id
        self.channel = inter.channel
        self.inter = inter
        self.force_ended = False
        # TODO: self.host_bot_user

    async def end_game(self):
        """Stops the game."""

    async def process_game(self):
        """Starts processing the game."""