from dotenv import load_dotenv
from os import getenv


class Keys:
    def __init__(self):
        self.keys = self.refresh_env()

    def __getitem__(self, item):
        return self.keys[item]

    def refresh_env(self):
        """Update the values in the .env file."""
        load_dotenv()
        self.__define_keys()

    def __define_keys(self):
        self.keys = dict({
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
            'database_port': getenv('PRT_DB'),
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



