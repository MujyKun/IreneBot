import discord
from discord.ext import commands
from module.keys import client, bot_prefix
from Utility import resources as ex


class Help(commands.Cog):
    def __init__(self):
        self._original_help_command = client.help_command
        client.help_command = self.SubHelp()
        client.help_command.cog = self

    class SubHelp(commands.MinimalHelpCommand):
        async def check_server_prefix(self):
            try:
                channel = self.get_destination()
                server_id = channel.guild.id
                server_prefix = await ex.get_server_prefix(server_id)
            except Exception as e:
                server_prefix = await client.get_prefix(self.context.message)
            return server_prefix

        async def send_pages(self):
            channel = self.get_destination()
            server_prefix = await self.check_server_prefix()
            for page in self.paginator.pages:
                embed = discord.Embed(title=f"Server Prefix is {server_prefix}", description=page)
                await channel.send(embed=embed)

        async def send_command_help(self, command):
            channel = self.get_destination()
            cmd_format = self.get_command_signature(command)
            # change the default prefix to the server prefix
            cmd_prefix = await self.check_server_prefix()
            cmd_format = cmd_prefix + cmd_format[1:len(cmd_format)]
            cmd_brief = command.help.replace(await client.get_prefix(self.context.message), cmd_prefix)
            embed = discord.Embed(description=f"{cmd_format}\n\n{cmd_brief}")
            await channel.send(embed=embed)

        async def send_cog_help(self, cog):
            channel = self.get_destination()
            open_msg = self.get_opening_note()
            cog_name = cog.qualified_name
            entire_msg = f"{open_msg}\n\n**{cog_name} Commands**"
            for command in cog.get_commands():
                if command.hidden is False:
                    cmd_name = command.name
                    cmd_prefix = await self.check_server_prefix()
                    cmd_desc = command.short_doc.replace(await client.get_prefix(self.context.message), cmd_prefix)
                    cmd_msg = f"\n{cmd_prefix}{cmd_name} - {cmd_desc}"
                    entire_msg += cmd_msg
            embed = discord.Embed(description=entire_msg)
            await channel.send(embed=embed)

        def get_opening_note(self):
            # method is not async // duplicated code for prefix
            try:
                ex.c.execute("SELECT prefix FROM general.serverprefix WHERE serverid = %s", (self.context.guild.id,))
                server_prefix = ex.fetch_one()
                if len(server_prefix) == 0:
                    server_prefix = bot_prefix
            except Exception as e:
                server_prefix = bot_prefix
            return f"Use ``{server_prefix}help [command]`` for more info on a command.\nYou can also use ``{server_prefix}help [category]`` (CASE-SENSITIVE) for more info on a category.\nTo reset a server prefix, you may type ``{bot_prefix}setprefix``."

