import discord.ext.commands

class Game:
    def __init__(self, ctx):
        self.host_ctx: discord.ext.commands.Context = ctx
        self.host_id: int = ctx.author.id
        self.host_user = None
        self.channel = ctx.channel
        self.force_ended = False

    async def end_game(self):
        """Ends game."""

    async def process_game(self):
        """Starts processing the game."""
