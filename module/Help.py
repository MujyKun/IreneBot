import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self._original_help_command = client.help_command
        client.help_command = self.SubHelp()
        client.help_command.cog = self
        self.client = client

    class SubHelp(commands.MinimalHelpCommand):
        async def send_pages(self):
            channel = self.get_destination()
            for page in self.paginator.pages:
                embed = discord.Embed(description=page)
                await channel.send(embed=embed)

