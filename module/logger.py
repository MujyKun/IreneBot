import logging
import datetime
from module import keys


def debug():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'Logs/{datetime.date.today()}-debug.log', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def info():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=f'Logs/{datetime.date.today()}-info.log', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def console(message):
    print(message)
    with open(f"Logs/{datetime.date.today()}-console.log", "a+", encoding='utf-8') as file:
        output = f"{datetime.datetime.now()} -- {message}\n"
        file.write(output)


def logfile(message):
    with open(f"Logs/{datetime.date.today()}-info.log", "a+", encoding='utf-8') as file:
        output = f"{datetime.datetime.now()} -- {message}\n"
        file.write(output)
