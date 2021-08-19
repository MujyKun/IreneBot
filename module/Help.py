import asyncio

import discord
from discord.ext import commands
import itertools
from IreneUtility.Utility import Utility


ex: Utility


class Help(commands.Cog):
    def __init__(self, t_ex):
        """

        :param t_ex: Utility object
        """
        self.ex: Utility = t_ex
        global ex
        ex = self.ex

        self._original_help_command = ex.client.help_command

        ex.client.help_command = self.SubHelp()
        ex.client.help_command.cog = self

    # noinspection PyPep8
    class SubHelp(commands.MinimalHelpCommand):
        """
        Custom help command.
        """
        def __init__(self):
            super(Help.SubHelp, self).__init__()
            self.command_attrs["aliases"] = ["commands"]  # add commands as an alias for help.

        async def get_server_prefix(self):
            return await ex.get_server_prefix(self.context)

        async def send_pages(self):
            channel = self.get_destination()
            server_prefix = await self.get_server_prefix()
            for page in self.paginator.pages:
                await asyncio.sleep(0)
                embed = discord.Embed(title=f"Server Prefix is {server_prefix}", description=page)
                await channel.send(embed=embed)

        async def send_command_help(self, command):
            """%help (specific command)."""
            channel = self.get_destination()
            user = await ex.get_user(self.context.author.id)

            """
            We are now going to have manually updated information for our commands instead of directly through
            methods. This will make it easier to share accurate and precise information across all of the Bot's 
            Systems. If information is needed from a cog command, use the argument passed into the method.
            """
            unique_command = ex.get_unique_command(command.cog_name, command.qualified_name, language=user.language)
            # change the default prefix to the server prefix
            cmd_prefix = await self.get_server_prefix()

            if not unique_command:
                cmd_format = self.get_command_signature(command)
                cmd_format = cmd_prefix + cmd_format[1:len(cmd_format)]
                cmd_brief = command.help.replace(ex.keys.bot_prefix, cmd_prefix)
                embed = discord.Embed(description=f"{cmd_format}\n\n{cmd_brief}")

            else:
                syntax = "" if not unique_command.syntax else f"**Syntax**:\n{unique_command.syntax}\n\n"
                example_syntax = "" if not unique_command.example_syntax else \
                    f"**Example Syntax**:\n{unique_command.example_syntax}\n\n"
                desc = "" if not unique_command.description else f"**Description**:\n{unique_command.description}\n\n"
                notes = "" if not unique_command.notes else f"**Additional Notes**:\n{unique_command.notes}\n\n"
                aliases = "" if not unique_command.aliases else f"**Aliases**:\n{', '.join(unique_command.aliases)}\n\n"
                cog_name = "" if not unique_command.cog_name else f"**Cog Name**:\n{unique_command.cog_name}\n\n"
                perms_needed = "" if not unique_command.permissions_needed else \
                    f"**Permissions Needed**:\n{', '.join(unique_command.permissions_needed)}\n\n"
                cmd_brief = f"{syntax}{desc}{notes}{example_syntax}{aliases}{cog_name}{perms_needed}"
                cmd_brief = cmd_brief.replace(ex.keys.bot_prefix, cmd_prefix)
                embed = discord.Embed(description=cmd_brief)
                if unique_command.example_image_url:
                    embed.set_image(url=unique_command.example_image_url)
            await channel.send(embed=embed)

        async def send_cog_help(self, cog):
            """%help (specific cog)."""
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
                await asyncio.sleep(0)
                if command.hidden is False:
                    embed_empty = False
                    cmd_name = command.name
                    cmd_prefix = await self.get_server_prefix()
                    cmd_desc = command.short_doc.replace(ex.keys.bot_prefix, cmd_prefix)
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
            server_prefix = await ex.get_server_prefix(self.context)
            return f"Use ``{server_prefix}help [command]`` for more info on a command.\nYou can also use " \
                f"``{server_prefix}help [category]`` (CASE-SENSITIVE) for more info on a category.\nTo reset a " \
                f"server prefix, you may type ``{ex.keys.bot_prefix}setprefix``.\n\n " \
                f"**Support Server:** {ex.keys.bot_support_server_link}\n\n" \
                f"**[Link to Commands](https://irenebot.com/commands)**"

        async def send_bot_help(self, mapping):
            """
            THIS METHOD WAS COPY PASTED FROM D.PY V1.6.0

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

            no_category_t = f"\u200b{self.no_category}"

            def get_category(command, *, no_category=no_category_t):
                cog = command.cog
                return cog.qualified_name if cog is not None else no_category

            filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
            to_iterate = itertools.groupby(filtered, key=get_category)

            for category, t_commands in to_iterate:
                await asyncio.sleep(0)
                commands_list = sorted(t_commands, key=lambda c: c.name) if self.sort_commands else list(t_commands)
                self.add_bot_commands_formatting(commands_list, category)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

            await self.send_pages()

        async def send_group_help(self, group):
            """
            THIS METHOD WAS COPY PASTED FROM D.PY V1.6.0

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
                    await asyncio.sleep(0)
                    self.add_subcommand_formatting(command)

                note = self.get_ending_note()
                if note:
                    self.paginator.add_line()
                    self.paginator.add_line(note)

            await self.send_pages()
