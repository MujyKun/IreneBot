import logging
from datetime import date
from os import path, mkdir

_log_level = "info"

_log_folder_name = "Logs"
if not path.exists(_log_folder_name):
    mkdir(_log_folder_name)

logger = logging.getLogger("disnake")
logger.setLevel(logging.INFO if _log_level == "info" else logging.DEBUG)
_handler = logging.FileHandler(
    filename=f"{_log_folder_name}/{date.today()}-{_log_level}.log", encoding="utf-8"
)
_handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(_handler)


for filename in listdir(_log_folder_name):
    if filename.endswith(".log"):
        full_path = path.join(_log_folder_name, filename)
        try:
            # Get file's modification time
            file_mtime = datetime.fromtimestamp(path.getmtime(full_path))
            if file_mtime < cutoff_date:
                remove(full_path)
                print(f"Deleted old log file: {filename}")
        except Exception as e:
            print(f"Error while checking/deleting {filename}: {e}")
