from Utility import resources as ex
from module import logger as log


class CustomCommands:
    async def check_custom_command_name_exists(self, server_id, command_name):
        if server_id:
            custom_commands = ex.cache.custom_commands.get(server_id)
            if custom_commands:
                if command_name.lower() in custom_commands:
                    return True
        return False

    async def add_custom_command(self, server_id, command_name, message):
        await ex.conn.execute("INSERT INTO general.customcommands(serverid, commandname, message) VALUES ($1, $2, $3)", server_id, command_name, message)
        custom_commands = ex.cache.custom_commands.get(server_id)
        if custom_commands:
            custom_commands[command_name] = message
        else:
            ex.cache.custom_commands[server_id] = {command_name: message}

    async def remove_custom_command(self, server_id, command_name):
        await ex.conn.execute("DELETE FROM general.customcommands WHERE serverid = $1 AND commandname = $2", server_id, command_name)
        custom_commands = ex.cache.custom_commands.get(server_id)
        try:
            custom_commands.pop(command_name)
        except Exception as e:
            log.console(e)

    async def get_custom_command(self, server_id, command_name):
        commands = ex.cache.custom_commands.get(server_id)
        return commands.get(command_name)
