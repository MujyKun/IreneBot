from discord.ext import commands
from module import logger as log, keys
from Utility import resources as ex


# noinspection PyPep8
class CustomCommands(commands.Cog):
    @staticmethod
    async def process_custom_commands(message):
        # custom server commands
        if not message.content or message.author.bot:
            return

        if await ex.u_miscellaneous.check_if_bot_banned(message.author.id):
            return

        guild_id = await ex.get_server_id(message)
        current_message_prefix = message.content[0:len(keys.bot_prefix)]
        if current_message_prefix == keys.bot_prefix:
            message_without_prefix = message.content[len(keys.bot_prefix):len(message.content)].lower()
            if await ex.u_custom_commands.check_custom_command_name_exists(guild_id, message_without_prefix):
                await message.channel.send(await ex.u_custom_commands.get_custom_command(guild_id, message_without_prefix))

    @commands.command(aliases=['addcommand'])
    @commands.has_guild_permissions(manage_messages=True)
    async def createcommand(self, ctx, command_name, *, message):
        """Create a custom command. [Format: %createcommand (command name) (message)]"""
        try:
            command_name = command_name.lower()
            msg_is_cmd = await ex.u_miscellaneous.check_message_is_command(command_name, is_command_name=True)
            if msg_is_cmd:
                return await ctx.send(f"> {command_name} is already a bot command and can not be added.")
            if await ex.u_custom_commands.check_custom_command_name_exists(ctx.guild.id, command_name):
                return await ctx.send(f"> {command_name} is already a custom command and can not be added.")
            else:
                await ex.u_custom_commands.add_custom_command(ctx.guild.id, command_name, message)
                return await ctx.send(f"> {command_name} has been added as a command.")
        except Exception as e:
            await ctx.send(f"> An unexpected error occurred -> {e}. Please {await ex.get_server_prefix_by_context(ctx)}report it.")
            log.console(e)

    @commands.command(aliases=['removecommand'])
    @commands.has_guild_permissions(manage_messages=True)
    async def deletecommand(self, ctx, command_name):
        """Delete a custom command. [Format: %deletecommand (command name)]"""
        try:
            await ex.u_custom_commands.remove_custom_command(ctx.guild.id, command_name.lower())
            return await ctx.send(f"> If the `{command_name}` exists, it was removed.")
        except Exception as e:
            await ctx.send(f"> An unexpected error occurred -> {e}. Please {await ex.get_server_prefix_by_context(ctx)}report it.")
            log.console(e)

    @commands.command()
    async def listcommands(self, ctx):
        """List all the custom commands for this server. [Format: %listcommands]"""
        try:
            async def get_new_embed(desc):
                return await ex.create_embed(f"Custom Commands for {ctx.guild.name} ({ctx.guild.id})", color=ex.get_random_color(),
                                             title_desc=desc)
            custom_commands = ex.cache.custom_commands.get(ctx.guild.id)
            embed_list = []
            embed_message = ""

            if not custom_commands:
                return await ctx.send("> There are no custom commands for your server.")

            for command in custom_commands:
                added_to_list = False
                message = f"**{command}** -> {custom_commands.get(command)}\n"
                if len(message) > 1000:
                    embed_list.append(await get_new_embed(message))
                    added_to_list = True

                if not added_to_list:
                    embed_message += message
                    if len(embed_message) >= 950:
                        embed_list.append(await get_new_embed(embed_message))
                        embed_message = ""
            if embed_message:
                embed_list.append(await get_new_embed(embed_message))
            if embed_list:
                msg = await ctx.send(embed=embed_list[0])
                if len(embed_list) > 1:
                    await ex.check_left_or_right_reaction_embed(msg, embed_list)

        except Exception as e:
            await ctx.send(f"> An unexpected error occurred -> {e}. Please {await ex.get_server_prefix_by_context(ctx)}report it.")
            log.console(e)

