from discord.ext import commands, tasks
import time


class Cache(commands.Cog):
    def __init__(self):
        # Photo Count of groups
        self.group_photos = {}  # { group_id: photo_count }
        # All channels DCAPP updates go to
        self.dc_app_channels = {}  # { channel_id: role_id }
        # All custom server prefixes
        self.server_prefixes = {}  # { server_id: server_prefix }
        # DC members
        self.dc_member_list = ["jiu", "sua", "siyeon", "handong", "yoohyeon", "dami", "gahyeon", "dc"]  # dc members
        # list of patrons
        self.patrons = {}  # { user_id: is_super_patron ( True or False ) }
        """
        reset timer for idol photos (keeps track of command usage)
        {
            reset_time: date
            userid: [commands_used, time_since_last_command]
        }"""
        self.commands_used = {"reset_time": time.time()}
        # phrases that will notify users [guild_id, user_id, phrase]
        self.user_notifications = []
        # mod mail user and channel {user_id: channel_id}
        self.mod_mail = {}
        # user ids banned from bot [user_id]
        self.bot_banned = []
        # server to channels being logged
        """
        {
        server_id : {
                    send_all: 0 or 1,
                    logging_channel: channel_id,
                    channels: [channel_id, channel_id]
                    },
        ...
        }
        
        """
        self.logged_channels = {}
        # just a list of channels that are being logged with no correlation to the servers.
        # this exists to check if a channel is logged much quicker.
        self.list_of_logged_channels = []
