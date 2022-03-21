import logging
from datetime import date
from os import path, mkdir

_log_level = "info"

_log_folder_name = "Logs"
if not path.exists(_log_folder_name):
    mkdir(_log_folder_name)

logger = logging.getLogger('dislash')
logger.setLevel(logging.INFO if _log_level == "info" else logging.DEBUG)
_handler = logging.FileHandler(filename=f'{_log_folder_name}/{date.today()}-info.log', encoding='utf-8')
_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(_handler)
