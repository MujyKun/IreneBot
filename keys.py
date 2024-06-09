from typing import Optional, List

from dotenv import load_dotenv
from os import getenv
from util import logger


def make_int(var):
    # noinspection PyBroadException,PyPep8
    if not var:
        return None
    try:
        return int(var)
    except Exception as exc:
        logger.warn(
            f"{exc} (Exception) -> Failed to turn {var} of type {type(var)} into an integer. -> module.keys.make_int"
        )
        return None


def make_list(var: str, make_integer=False):
    if not var:
        return []
    split_list = var.split(",")
    if make_integer:
        return [make_int(val) for val in split_list]
    return split_list


def get_emoji(string):
    """Manages string input with unicode chars and turns them into Unicode Strings."""
    if len(string) != 0:
        if string[0] == "<":
            return string
        else:
            string = chr(int(string, 16))
    return string


class Keys:
    def __init__(self):
        # Bot Info
        self.prod_bot_token: str = ""
        self.prod_bot_token: str = ""
        self.dev_bot_token: str = ""
        self.bot_id: int = 0
        self.bot_owner_id: int = 0
        self.bot_name: str = ""
        self.bot_prefix: str = ""

        # Database Server (DB) (Preferred PostgreSQL)
        self.db_host: str = ""
        self.db_name: str = ""
        self.db_user: str = ""
        self.db_pass: str = ""

        # Support Server
        self.support_server_id: int = 0

        # URLS
        self.bot_invite_url: str = ""
        self.bot_website_url: str = ""
        self.bot_image_host_url: str = ""
        self.support_server_invite_url: str = ""
        self.embed_icon_url: str = ""
        self.embed_footer_url: str = ""
        self.api_url: str = ""

        # Channel IDS (CID)
        self.add_idol_channel_id: int = 0
        self.add_group_channel_id: int = 0
        self.data_mod_channel_id: int = 0
        self.bug_channel_id: int = 0
        self.suggest_channel_id: int = 0

        # PORTS
        self.db_port: int = 0
        self.site_port: str = ""
        self.api_port: int = 5454

        # Role IDS (RID)
        self.patron_role_id: int = 0
        self.super_patron_role_id: int = 0
        self.translator_role_id: int = 0
        self.proofreader_role_id: int = 0
        self.data_mod_role_id: int = 0

        # Directories (DIR) (Include / at end)
        self.avatar_directory: str = ""
        self.banner_directory: str = ""
        self.biasgame_directory: str = ""
        self.blackjack_directory: str = ""

        # Restrictions (LIM  LIMIT) (RMD = REMINDER)
        self.post_limit: int = 0
        self.no_vote_limit: int = 0
        self.auto_send_limit: int = 0
        self.reminder_limit: int = 0
        self.tiktok_limit: int = 0

        # Reactions/Emotes - Accepts xxxxxxxx and discord supported emojis (never include the U at the start)
        self.trash_emoji: str = ""
        self.checkmark_emoji: str = ""
        self.f_emoji: str = ""
        self.caution_emoji: str = ""
        self.previous_emoji: str = ""
        self.next_emoji: str = ""

        # Spotify (SPO)
        self.spotify_id: str = ""
        self.spotify_secret: str = ""

        # Oxford Dictionary (OX)
        self.oxford_id: str = ""
        self.oxford_key: str = ""

        # Urban Dictionary (URB)
        self.urban_host: str = ""
        self.urban_key: str = ""

        # Tenor (TNR)
        self.tenor_key: str = ""

        # Top.gg (TOP)
        self.top_key: str = ""
        self.top_webhook_key: str = ""

        # Discord Boats (BOATS)
        self.boats_key: str = ""

        # Papago (PAP)
        self.papago_id: str = ""
        self.papago_secret: str = ""

        # LastFM (FM)
        self.fm_key: str = ""
        self.fm_secret: str = ""
        self.fm_url: str = ""
        self.fm_agent: str = ""

        # Patreon (PAT)
        self.patreon_link: str = ""

        # Wolfram
        self.wolfram_id: str = ""

        # KSoftAPI Lyrics (LYR)
        self.lyrics_key: str = ""

        # DataDog (DD)
        self.datadog_api_key: str = ""
        self.datadog_app_key: str = ""

        # Twitch (TWCH)
        self.twitch_id: str = ""
        self.twitch_secret: str = ""

        # IreneAPI
        self.api_token: str = ""

        self.bot_owner_only_servers: List[int] = []

        self.refresh_env()

    def get_keys(self, *args) -> dict:
        """Return search_word list of key arguments as search_word dictionary.

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
        keys = dict(
            {
                # Bot Info
                "prod_bot_token": getenv("PROD_BOT_TOKEN"),
                "dev_bot_token": getenv("DEV_BOT_TOKEN"),
                "bot_id": make_int(getenv("BOT_ID")),
                "bot_owner_id": make_int(getenv("BOT_OWNER_ID")),
                "bot_name": getenv("BOT_NAME"),
                "bot_prefix": getenv("BOT_DEFAULT_PREFIX"),
                # Database Server (DB) (Preferred PostgreSQL)
                "db_host": getenv("DB_HOST"),
                "db_name": getenv("DB_NAME"),
                "db_user": getenv("DB_USER"),
                "db_pass": getenv("DB_PASS"),
                # Support Server
                "support_server_id": make_int(getenv("SUPPORT_SERVER_ID")),
                # URLS
                "bot_invite_url": getenv("BOT_INVITE_URL"),
                "bot_website_url": getenv("BOT_WEBSITE_URL"),
                "bot_image_host_url": getenv("BOT_IMAGE_HOST_URL"),
                "support_server_invite_url": getenv("SUPPORT_SERVER_INVITE_URL"),
                "embed_icon_url": getenv("EMBED_ICON_URL"),
                "embed_footer_url": getenv("EMBED_FOOTER_URL"),
                "api_url": getenv("API_URL"),
                # Channel IDS (CID)
                "add_idol_channel_id": make_int(getenv("ADD_IDOL_CID")),
                "add_group_channel_id": make_int(getenv("ADD_GROUP_CID")),
                "data_mod_channel_id": make_int(getenv("DM_LOG_CID")),
                "bug_channel_id": make_int(getenv("BUG_CID")),
                "suggest_channel_id": make_int(getenv("SUGGEST_CID")),
                # PORTS
                "db_port": make_int(getenv("PRT_DB")),
                "site_port": getenv("PRT_SITE"),
                "api_port": make_int(getenv("PRT_API")),
                # Role IDS (RID)
                "patron_role_id": make_int(getenv("RID_PAT")),
                "super_patron_role_id": make_int(getenv("RID_SUPER_PAT")),
                "translator_role_id": make_int(getenv("RID_TL")),
                "proofreader_role_id": make_int(getenv("RID_PR")),
                "data_mod_role_id": make_int(getenv("RID_DM")),
                # Directories (DIR) (Include / at end)
                "avatar_directory": getenv("DIR_AVATARS"),
                "banner_directory": getenv("DIR_BANNERS"),
                "biasgame_directory": getenv("DIR_BG"),
                "blackjack_directory": getenv("DIR_BJ"),
                # Restrictions (LIM  LIMIT) (TWT  Twitter) (RMD = REMINDER)
                "post_limit": make_int(getenv("LIM_POST")),
                "no_vote_limit": make_int(getenv("LIM_NO_VOTE")),
                "auto_send_limit": make_int(getenv("LIM_AUTO_SEND")),
                "reminder_limit": make_int(getenv("LIM_RMD")),
                "tiktok_limit": make_int(getenv("LIM_TIKTOK")),
                # Reactions/Emotes - Accepts xxxxxxxx and discord supported emojis (never include the U at the start)
                "trash_emoji": get_emoji(getenv("TRASH_EM")),
                "checkmark_emoji": get_emoji(getenv("CHECKMARK_EM")),
                "f_emoji": get_emoji(getenv("F_EM")),
                "caution_emoji": get_emoji(getenv("CAUTION_EM")),
                "previous_emoji": get_emoji(getenv("PREVIOUS_EM")),
                "next_emoji": get_emoji(getenv("NEXT_EM")),
                # Spotify (SPO)
                "spotify_id": getenv("SPO_ID"),
                "spotify_secret": getenv("SPO_SECRET"),
                # Oxford Dictionary (OX)
                "oxford_id": getenv("OX_ID"),
                "oxford_key": getenv("OX_KEY"),
                # Urban Dictionary (URB)
                "urban_host": getenv("URB_HOST"),
                "urban_key": getenv("URB_KEY"),
                # Tenor (TNR)
                "tenor_key": getenv("TNR_KEY"),
                # Top.gg (TOP)
                "top_key": getenv("TOP_KEY"),
                "top_webhook_key": getenv("TOP_WEBHOOK_KEY"),
                # Discord Boats (BOATS)
                "boats_key": getenv("BOATS_KEY"),
                # Papago (PAP)
                "papago_id": getenv("PAP_ID"),
                "papago_secret": getenv("PAP_SECRET"),
                # LastFM (FM)
                "fm_key": getenv("FM_KEY"),
                "fm_secret": getenv("FM_SECRET"),
                "fm_url": getenv("FM_URL"),
                "fm_agent": getenv("FM_AGENT"),
                # Patreon (PAT)
                "patreon_link": getenv("PAT_LINK"),
                # Wolfram
                "wolfram_id": getenv("WOLFRAM_ID"),
                # KSoftAPI Lyrics (LYR)
                "lyrics_key": getenv("LYR_KEY"),
                # DataDog (DD)
                "datadog_api_key": getenv("DD_API_KEY"),
                "datadog_app_key": getenv("DD_APP_KEY"),
                # Twitch (TWCH)
                "twitch_id": getenv("TWCH_ID"),
                "twitch_secret": getenv("TWCH_SECRET"),
                # IreneAPI
                "api_token": getenv("API_TOKEN"),
                "bot_owner_only_servers": make_list(
                    getenv("BOT_OWNER_ONLY_SERVERS"), make_integer=True
                ),
            }
        )

        for key, val in keys.items():
            if val is not None and type(self.__getattribute__(key)) != type(val):
                logger.warn(
                    f"Environment variable {key} has type {type(val)}"
                    f" when type {type(self.__getattribute__(key))} was expected."
                )
            self.__setattr__(key, val)

        no_vals = [key for key, value in keys.items() if not value]
        logger.warn(
            f"Could not find an environment value for keys: {', '.join(no_vals)}."
        )

    @property
    def role_update_kwargs(self):
        """Get the function kwargs for checking the status of a member's roles
        (ex: Patron, Translator)

        Primarily used for functions `bot._ensure_role` and `bot._check_role_update`.
        Is a property since the env variables can be updated dynamically.
        """
        return [
            {
                "role_to_find": self.patron_role_id,
                "async_callable_name": "set_patron",
                "attr_flag": "is_patron",
                "type_desc": "Patron",
            },
            {
                "role_to_find": self.super_patron_role_id,
                "async_callable_name": "set_super_patron",
                "attr_flag": "is_super_patron",
                "type_desc": "Super Patron",
            },
            {
                "role_to_find": self.translator_role_id,
                "async_callable_name": "set_translator",
                "attr_flag": "is_translator",
                "type_desc": "Translator",
            },
            {
                "role_to_find": self.proofreader_role_id,
                "async_callable_name": "set_proofreader",
                "attr_flag": "is_proofreader",
                "type_desc": "Proofreader",
            },
            {
                "role_to_find": self.data_mod_role_id,
                "async_callable_name": "set_data_mod",
                "attr_flag": "is_data_mod",
                "type_desc": "Data Mod",
            },
        ]


_keys: Optional[Keys] = None


def get_keys():
    global _keys
    if not _keys:
        _keys = Keys()
    return _keys
