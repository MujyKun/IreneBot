from Utility import resources as ex


class Logging:
    #################
    # ## LOGGING ## #
    #################

    async def get_servers_logged(self):
        """Get the servers that are being logged."""
        return [server_id for server_id in self.cache.logged_channels]

    async def get_channels_logged(self):
        """Get all the channels that are being logged."""
        return self.cache.list_of_logged_channels

    async def add_to_logging(self, server_id, channel_id):  # return true if status is on
        """Add a channel to be logged."""
        if (self.first_result(
                await self.conn.fetchrow("SELECT COUNT(*) FROM logging.servers WHERE serverid = $1", server_id))) == 0:
            await self.conn.execute(
                "INSERT INTO logging.servers (serverid, channelid, status, sendall) VALUES ($1, $2, $3, $4)", server_id,
                channel_id, 1, 1)
            server = self.cache.logged_channels.get(server_id)
            if server is None:
                self.cache.logged_channels[server_id] = {"send_all": 1, "logging_channel": channel_id, "channels": []}
            else:
                self.cache.list_of_logged_channels.append(channel_id)
                server['channels'].append(channel_id)
        else:
            await self.set_logging_status(server_id, 1)
            current_channel_id = self.first_result(
                await self.conn.fetchrow("SELECT channelid FROM logging.servers WHERE serverid = $1", server_id))
            if current_channel_id != channel_id:
                await self.conn.execute("UPDATE logging.servers SET channelid = $1 WHERE serverid = $2", channel_id,
                                        server_id)
        return True

    async def check_if_logged(self, server_id=None, channel_id=None):  # only one parameter should be passed in
        """Check if a server or channel is being logged."""
        if channel_id:
            return channel_id in self.cache.list_of_logged_channels
        elif server_id:
            return server_id in self.cache.logged_channels

    async def get_send_all(self, server_id):
        return (self.cache.logged_channels.get(server_id))['send_all']

    async def set_logging_status(self, server_id, status):  # status can only be 0 or 1
        """Set a server's logging status."""
        await self.conn.execute("UPDATE logging.servers SET status = $1 WHERE serverid = $2", status, server_id)
        if not status:
            self.cache.logged_channels.pop(server_id, None)
        else:
            logged_server = await self.conn.fetchrow(
                "SELECT id, serverid, channelid, sendall FROM logging.servers WHERE serverid = $1", server_id)
            channels = await self.conn.fetch("SELECT channelid FROM logging.channels WHERE server = $1",
                                             logged_server[0])
            for channel in channels:
                self.cache.list_of_logged_channels.append(channel[0])
            self.cache.logged_channels[logged_server[1]] = {
                "send_all": logged_server[3],
                "logging_channel": logged_server[2],
                "channels": [channel[0] for channel in channels]
            }

    async def get_logging_id(self, server_id):
        """Get the ID in the table of a server."""
        return self.first_result(
            await self.conn.fetchrow("SELECT id FROM logging.servers WHERE serverid = $1", server_id))

    async def check_logging_requirements(self, message):
        """Check if a message meets all the logging requirements."""
        try:
            if not message.author.bot:
                if await self.check_if_logged(server_id=message.guild.id):
                    if await self.check_if_logged(channel_id=message.channel.id):
                        return True
        except Exception as e:
            pass
        return False

    @staticmethod
    async def get_attachments(message):
        """Get the attachments of a message."""
        files = None
        if message.attachments:
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())
        return files

    async def get_log_channel_id(self, message):
        """Get the channel where logs are made on a server."""
        return self.client.get_channel((self.cache.logged_channels.get(message.guild.id))['logging_channel'])


