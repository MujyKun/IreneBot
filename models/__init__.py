import logging
from datetime import date
from os import path, mkdir


log_folder_name = "Logs"
if not path.exists(log_folder_name):
    mkdir(log_folder_name)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=f'{log_folder_name}/{date.today()}-info.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


from .DbConn import DbConnection
from .PgConn import PgConnection
