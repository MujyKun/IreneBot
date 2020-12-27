from Utility import resources as ex


class Moderator:
    @staticmethod
    async def add_welcome_message_server(channel_id, guild_id, message, enabled):
        """Adds a new welcome message server."""
        await ex.conn.execute(
            "INSERT INTO general.welcome(channelid, serverid, message, enabled) VALUES($1, $2, $3, $4)", channel_id,
            guild_id, message, enabled)
        ex.cache.welcome_messages[guild_id] = {"channel_id": channel_id, "message": message, "enabled": enabled}

    @staticmethod
    async def check_welcome_message_enabled(server_id):
        """Check if a welcome message server is enabled."""
        return ex.cache.welcome_messages[server_id]['enabled'] == 1

    @staticmethod
    async def update_welcome_message_enabled(server_id, enabled):
        """Update a welcome message server's enabled status"""
        await ex.conn.execute("UPDATE general.welcome SET enabled = $1 WHERE serverid = $2", int(enabled), server_id)
        ex.cache.welcome_messages[server_id]['enabled'] = int(enabled)

    @staticmethod
    async def update_welcome_message_channel(server_id, channel_id):
        """Update the welcome message channel."""
        await ex.conn.execute("UPDATE general.welcome SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        ex.cache.welcome_messages[server_id]['channel_id'] = channel_id

    @staticmethod
    async def update_welcome_message(server_id, message):
        await ex.conn.execute("UPDATE general.welcome SET message = $1 WHERE serverid = $2", message, server_id)
        ex.cache.welcome_messages[server_id]['message'] = message
