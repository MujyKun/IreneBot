from discord.ext import commands
import time


class Cache(commands.Cog):
    def __init__(self):
        # maintenance mode
        self.maintenance_mode = False
        # maintenance reason
        self.maintenance_reason = None
        # current session
        self.session_id = None
        # current session commands used
        self.current_session = 0
        # total amount of commands used
        self.total_used = None
        # time format of current session for comparison
        self.session_time_format = None
        # API Calls made directly from the bot for Translations per minute
        self.bot_api_translation_calls = 0
        # API Calls made directly from the bot for Idols per minute
        self.bot_api_idol_calls = 0
        # N Words per minute
        self.n_words_per_minute = 0
        # commands used in the current minute
        self.commands_per_minute = 0
        # messages received per minute
        self.messages_received_per_minute = 0
        # errors per minute
        self.errors_per_minute = 0
        # wolfram calls per minute
        self.wolfram_per_minute = 0
        # Urban dictionary calls per minute
        self.urban_per_minute = 0
        """
        Command Counter
        {
        command_name : amount_of_times_used
        }
        """
        self.command_counter = {}
        # Photo Count of groups
        self.group_photos = {}  # { group_id: photo_count }
        # Photo Count of idols
        self.idol_photos = {}  # { idol_id: photo_count }
        # All custom server prefixes
        self.server_prefixes = {}  # { server_id: server_prefix }
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
        """
        Welcome Messages
        {
        server_id : {
            channel_id: channel_id,
            message: text,
            enabled: 0 or 1
            }
        }
        """
        self.welcome_messages = {}
        """
        Temp Channels
        {
        channel_id : seconds
        }
        """
        self.temp_channels = {}
        """
        NWord Counter
        {
        user_id : counter
        }
        """
        self.n_word_counter = {}

        # list of idol objects
        self.idols = []
        # list of group objects
        self.groups = []
        # dict of restricted idol photo channels
        """
        channelid : [server_id, sendall]
        """
        self.restricted_channels = {}
        """
        messageid : [dead_link, userid, idolid, is_guessing_game]
        """
        self.dead_image_cache = {}
        # Channel for all dead images to be sent to.
        self.dead_image_channel = None
        self.bot_statuses = []
        """
        server_id: {command_name:info, command_name:info}  
        """
        self.custom_commands = {}

        # Guessing Game Objects
        self.guessing_games = []
        # Bias Game Objects
        self.bias_games = []
        # Text channels to send Weverse updates to.
        self.weverse_channels = {}  # { community_name: [ [channel_id, role_id, comments_disabled] ] }

        self.assignable_roles = {}  #
        # { server_id:
        #    {channel_id: channel_id,
        #    roles: [role_id, role_name]
        # }}

        # Reminder dictionary
        self.reminders = {}   # { user_id: [ [remind_reason, remind_time] ] }
        self.timezones = {}   # { user_id: timezone }

        # bracket position for bias game stored due to annoyance when using previous x and y values.
        # counting starts from left to right, bottom to top
        self.stored_bracket_positions = {
            1: {'img_size': (50, 50), 'pos': (30, 515)},
            2: {'img_size': (50, 50), 'pos': (100, 515)},
            3: {'img_size': (50, 50), 'pos': (165, 515)},
            4: {'img_size': (50, 50), 'pos': (230, 515)},
            5: {'img_size': (50, 50), 'pos': (320, 515)},
            6: {'img_size': (50, 50), 'pos': (390, 515)},
            7: {'img_size': (50, 50), 'pos': (455, 515)},
            8: {'img_size': (50, 50), 'pos': (525, 515)},
            9: {'img_size': (75, 75), 'pos': (55, 380)},
            10: {'img_size': (75, 75), 'pos': (185, 380)},
            11: {'img_size': (75, 75), 'pos': (340, 380)},
            12: {'img_size': (75, 75), 'pos': (475, 380)},
            13: {'img_size': (100, 100), 'pos': (110, 225)},
            14: {'img_size': (100, 100), 'pos': (390, 225)},
            15: {'img_size': (134, 130), 'pos': (235, 55)}
        }


