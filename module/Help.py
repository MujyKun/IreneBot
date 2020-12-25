import discord
from discord.ext import commands
from module.keys import bot_prefix, bot_support_server_link
from Utility import resources as ex
import itertools


class Help(commands.Cog):
    def __init__(self):
        self._original_help_command = ex.client.help_command
        ex.client.help_command = self.SubHelp()
        ex.client.help_command.cog = self

    class SubHelp(commands.MinimalHelpCommand):
        async def get_server_prefix(self):
            return await ex.get_server_prefix_by_context(self.context)

        async def send_pages(self):
            channel = self.get_destination()
            server_prefix = await self.get_server_prefix()
            for page in self.paginator.pages:
                embed = discord.Embed(title=f"Server Prefix is {server_prefix}", description=page)
                await channel.send(embed=embed)

        async def send_command_help(self, command):
            """%help (specific command)"""
            channel = self.get_destination()
            cmd_format = self.get_command_signature(command)
            # change the default prefix to the server prefix
            cmd_prefix = await self.get_server_prefix()
            cmd_format = cmd_prefix + cmd_format[1:len(cmd_format)]
            cmd_brief = command.help.replace(await ex.client.get_prefix(self.context.message), cmd_prefix)
            embed = discord.Embed(description=f"{cmd_format}\n\n{cmd_brief}")
            await channel.send(embed=embed)

        async def send_cog_help(self, cog):
            """%help (specific cog)"""
            channel = self.get_destination()
            open_msg = await self.get_opening_note()
            cog_name = cog.qualified_name
            page_number = 1
            entire_msg = f"{open_msg}\n\n**{cog_name} Commands - Page {page_number}**"
            embed_list = []
            embed_empty = False
            # filter the commands to check if the commands can be used by the user.
            cog_commands = await self.filter_commands(cog.get_commands())
            for command in cog_commands:
                if command.hidden is False:
                    embed_empty = False
                    cmd_name = command.name
                    cmd_prefix = await self.get_server_prefix()
                    cmd_desc = command.short_doc.replace(await ex.client.get_prefix(self.context.message), cmd_prefix)
                    cmd_msg = f"\n{cmd_prefix}{cmd_name} - {cmd_desc}"
                    entire_msg += cmd_msg
                    if len(entire_msg) >= 1500:
                        embed_list.append(discord.Embed(description=entire_msg))
                        page_number += 1
                        entire_msg = f"{open_msg}\n\n**{cog_name} Commands - Page {page_number}**"
                        embed_empty = True

            if not embed_empty:
                embed_list.append(discord.Embed(description=entire_msg))
            msg = await channel.send(embed=embed_list[0])
            if len(embed_list) > 1:
                await ex.check_left_or_right_reaction_embed(msg, embed_list)

        async def get_opening_note(self):
            """Was changed to async. Gets the opening message of a help command."""
            server_prefix = await ex.get_server_prefix_by_context(self.context)
            return f"Use ``{server_prefix}help [command]`` for more info on a command.\nYou can also use ``{server_prefix}help [category]`` (CASE-SENSITIVE) for more info on a category.\nTo reset a server prefix, you may type ``{bot_prefix}setprefix``.\n\n **Support Server:** {bot_support_server_link}"

        async def send_bot_help(self, mapping):
            """
            THIS METHOD WAS COPY PASTED FROM D.PY V1.3.3
            THE ONLY ALTERED CODE WAS CHANGING get_opening_note to be awaited.
            get_opening_note was not originally async.
            """
            ctx = self.context
            bot = ctx.bot

            if bot.description:
                self.paginator.add_line(bot.description, empty=True)

            note = await self.get_opening_note()
            if note:
                self.paginator.add_line(note, empty=True)
            no_category = '\u200b{0.no_category}'.format(self)

            def get_category(command, *, no_category=no_category):
                cog = command.cog
                return cog.qualified_name if cog is not None else no_category

            filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
            to_iterate = itertools.groupby(filtered, key=get_category)

            for category, commands in to_iterate:
                commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
                self.add_bot_commands_formatting(commands, category)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

            await self.send_pages()

        async def send_group_help(self, group):
            """
            THIS METHOD WAS COPY PASTED FROM D.PY V1.3.3
            THE ONLY ALTERED CODE WAS CHANGING get_opening_note to be awaited.
            get_opening_note was not originally async.
            """
            self.add_command_formatting(group)

            filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
            if filtered:
                note = await self.get_opening_note()
                if note:
                    self.paginator.add_line(note, empty=True)

                self.paginator.add_line('**%s**' % self.commands_heading)
                for command in filtered:
                    self.add_subcommand_formatting(command)

                note = self.get_ending_note()
                if note:
                    self.paginator.add_line()
                    self.paginator.add_line(note)

            await self.send_pages()
