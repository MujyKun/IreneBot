from dotenv import load_dotenv
from os import getenv
from models import logger


class Keys:
    def __init__(self):
        # Bot Info
        self.prod_bot_token: str = ''
        self.prod_bot_token: str = ''
        self.dev_bot_token: str = ''
        self.bot_id: int = 0
        self.bot_owner_id: int = 0
        self.bot_name: str = ''
        self.bot_prefix: str = ''

        # Database Server (DB) (Preferred PostgreSQL)
        self.db_host: str = ''
        self.db_name: str = ''
        self.db_user: str = ''
        self.db_pass: str = ''

        # Support Server
        self.support_server_id: str = ''

        # URLS
        self.bot_invite_url: str = ''
        self.bot_website_url: str = ''
        self.bot_image_host_url: str = ''
        self.support_server_invite_url: str = ''
        self.embed_icon_url: str = ''
        self.embed_footer_url: str = ''
        self.vlive_base_url: str = ''

        # Channel IDS (CID)
        self.add_idol_channel_id: int = 0
        self.add_group_channel_id: int = 0
        self.twitter_channel_id: int = 0
        self.data_mod_channel_id: int = 0

        # PORTS
        self.db_port: int = 0
        self.site_port: str = ''
        self.api_port: int = 0

        # Role IDS (RID)
        self.patron_role_id: int = 0
        self.super_patron_role_id: int = 0
        self.translator_role_id: int = 0
        self.proofreader_role_id: int = 0
        self.data_mod_role_id: int = 0

        # Directories (DIR) (Include / at end)
        self.avatar_directory: str = ''
        self.banner_directory: str = ''
        self.biasgame_directory: str = ''
        self.blackjack_directory: str = ''

        # Restrictions (LIM  LIMIT) (TWT  Twitter) (RMD = REMINDER)
        self.post_limit: int = 0
        self.no_vote_limit: int = 0
        self.auto_send_limit: int = 0
        self.twitter_update_limit: int = 0
        self.reminder_limit: int = 0

        # Reactions/Emotes - Accepts xxxxxxxx and discord supported emojis (never include the U at the start)
        self.trash_emoji: str = ''
        self.checkmark_emoji: str = ''
        self.f_emoji: str = ''
        self.caution_emoji: str = ''
        self.previous_emoji: str = ''
        self.next_emoji: str = ''

        # Twitter (TWT) Bot Information
        self.twitter_account_id: str = ''
        self.twitter_username: str = ''
        self.twitter_consumer_key: str = ''
        self.twitter_consumer_secret: str = ''
        self.twitter_access_key: str = ''
        self.twitter_access_secret: str  = ''

        # Spotify (SPO)
        self.spotify_id: str = ''
        self.spotify_secret: str = ''

        # Oxford Dictionary (OX)
        self.oxford_id: str = ''
        self.oxford_key: str = ''

        # Urban Dictionary (URB)
        self.urban_host: str = ''
        self.urban_key: str = ''

        # Tenor (TNR)
        self.tenor_key: str = ''

        # Top.gg (TOP)
        self.top_key: str = ''
        self.top_webhook_key: str = ''

        # Discord Boats (BOATS)
        self.boats_key: str = ''

        # Papago (PAP)
        self.papago_id: str = ''
        self.papago_secret: str = ''

        # LastFM (FM)
        self.fm_key: str = ''
        self.fm_secret: str = ''
        self.fm_url: str = ''
        self.fm_agent: str = ''

        # Patreon (PAT)
        self.patreon_link: str = ''

        # Wolfram
        self.wolfram_id: str = ''

        # KSoftAPI Lyrics (LYR)
        self.lyrics_key: str = ''

        # DataDog (DD)
        self.datadog_api_key: str = ''
        self.datadog_app_key: str = ''

        # Twitch (TWCH)
        self.twitch_id: str = ''
        self.twitch_secret: str = ''
        self.refresh_env()

    def get_keys(self, *args) -> dict:
        """Return a list of key arguments as a dictionary.

        :param args: List of key arguments
        :return dict: Dictionary with the values of the key arguments passed in.
        """
        keys = dict()

        for arg in args:
            keys[arg] = self.__dict__[arg]

        return keys

    def refresh_env(self):
        """Update the values in the .env file."""
        load_dotenv()
        self.__define_keys()

    def __define_keys(self):
        keys = dict({
            # Bot Info
            'prod_bot_token': getenv('PROD_BOT_TOKEN'),
            'dev_bot_token': getenv('DEV_BOT_TOKEN'),
            'bot_id': getenv('BOT_ID'),
            'bot_owner_id': getenv('BOT_OWNER_ID'),
            'bot_name': getenv('BOT_NAME'),
            'bot_prefix': getenv('BOT_DEFAULT_PREFIX'),

            # Database Server (DB) (Preferred PostgreSQL)
            'db_host': getenv('DB_HOST'),
            'db_name': getenv('DB_NAME'),
            'db_user': getenv('DB_USER'),
            'db_pass': getenv('DB_PASS'),

            # Support Server
            'support_server_id': getenv('SUPPORT_SERVER_ID'),

            # URLS
            'bot_invite_url': getenv('BOT_INVITE_URL'),
            'bot_website_url': getenv('BOT_WEBSITE_URL'),
            'bot_image_host_url': getenv('BOT_IMAGE_HOST_URL'),
            'support_server_invite_url': getenv('SUPPORT_SERVER_INVITE_URL'),
            'embed_icon_url': getenv('EMBED_ICON_URL'),
            'embed_footer_url': getenv('EMBED_FOOTER_URL'),
            'vlive_base_url': getenv('VLIVE_BASE_URL'),

            # Channel IDS (CID)
            'add_idol_channel_id': getenv('ADD_IDOL_CID'),
            'add_group_channel_id': getenv('ADD_GROUP_CID'),
            'twitter_channel_id': getenv('TWITTER_CID'),
            'data_mod_channel_id': getenv('DM_LOG_CID'),

            # PORTS
            'db_port': getenv('PRT_DB'),
            'site_port': getenv('PRT_SITE'),
            'api_port': getenv('PRT_API'),

            # Role IDS (RID)
            'patron_role_id': getenv('RID_PAT'),
            'super_patron_role_id': getenv('RID_SUPER_PAT'),
            'translator_role_id': getenv('RID_TL'),
            'proofreader_role_id': getenv('RID_PR'),
            'data_mod_role_id': getenv('RID_DM'),

            # Directories (DIR) (Include / at end)
            'avatar_directory': getenv('DIR_AVATARS'),
            'banner_directory': getenv('DIR_BANNERS'),
            'biasgame_directory': getenv('DIR_BG'),
            'blackjack_directory': getenv('DIR_BJ'),

            # Restrictions (LIM  LIMIT) (TWT  Twitter) (RMD = REMINDER)
            'post_limit': getenv('LIM_POST'),
            'no_vote_limit': getenv('LIM_NO_VOTE'),
            'auto_send_limit': getenv('LIM_AUTO_SEND'),
            'twitter_update_limit': getenv('LIM_TWT_UPDATE'),
            'reminder_limit': getenv('LIM_RMD'),

            # Reactions/Emotes - Accepts xxxxxxxx and discord supported emojis (never include the U at the start)
            'trash_emoji': getenv('TRASH_EM'),
            'checkmark_emoji': getenv('CHECKMARK_EM'),
            'f_emoji': getenv('F_EM'),
            'caution_emoji': getenv('CAUTION_EM'),
            'previous_emoji': getenv('PREVIOUS_EM'),
            'next_emoji': getenv('NEXT_EM'),

            # Twitter (TWT) Bot Information
            'twitter_account_id': getenv('TWT_ACCOUNT_ID'),
            'twitter_username': getenv('TWT_USERNAME'),
            'twitter_consumer_key': getenv('TWT_CONSUMER_KEY'),
            'twitter_consumer_secret': getenv('TWT_CONSUMER_SECRET'),
            'twitter_access_key': getenv('TWT_ACCESS_KEY'),
            'twitter_access_secret': getenv('TWT_ACCESS_SECRET'),

            # Spotify (SPO)
            'spotify_id': getenv('SPO_ID'),
            'spotify_secret': getenv('SPO_SECRET'),

            # Oxford Dictionary (OX)
            'oxford_id': getenv('OX_ID'),
            'oxford_key': getenv('OX_KEY'),

            # Urban Dictionary (URB)
            'urban_host': getenv('URB_HOST'),
            'urban_key': getenv('URB_KEY'),

            # Tenor (TNR)
            'tenor_key': getenv('TNR_KEY'),

            # Top.gg (TOP)
            'top_key': getenv('TOP_KEY'),
            'top_webhook_key': getenv('TOP_WEBHOOK_KEY'),

            # Discord Boats (BOATS)
            'boats_key': getenv('BOATS_KEY'),

            # Papago (PAP)
            'papago_id': getenv('PAP_ID'),
            'papago_secret': getenv('PAP_SECRET'),

            # LastFM (FM)
            'fm_key': getenv('FM_KEY'),
            'fm_secret': getenv('FM_SECRET'),
            'fm_url': getenv('FM_URL'),
            'fm_agent': getenv('FM_AGENT'),

            # Patreon (PAT)
            'patreon_link': getenv('PAT_LINK'),

            # Wolfram
            'wolfram_id': getenv('WOLFRAM_ID'),

            # KSoftAPI Lyrics (LYR)
            'lyrics_key': getenv('LYR_KEY'),

            # DataDog (DD)
            'datadog_api_key': getenv('DD_API_KEY'),
            'datadog_app_key': getenv('DD_APP_KEY'),

            # Twitch (TWCH)
            'twitch_id': getenv('TWCH_ID'),
            'twitch_secret': getenv('TWCH_SECRET'),
        })

        for key, val in keys.items():
            self.__setattr__(key, val)

        no_vals = [key for key, value in keys.items() if not value]
        logger.warn(f"Could not find an environment value for keys: {', '.join(no_vals)}.")
