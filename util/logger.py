import logging
import datetime
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor()


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


def print_to_console(message):
    message = message.replace("**", "")  # getting rid of bold in markdown
    print(message)
    with open(f"Logs/{datetime.date.today()}-console.log", "a+", encoding='utf-8') as file:
        output = f"{datetime.datetime.now()} -- {message}\n"
        file.write(output)


def console(message):
    # run in a separate thread to avoid blocking.
    (thread_pool.submit(print_to_console, f"{message}")).result()


def logfile(message):
    with open(f"Logs/{datetime.date.today()}-info.log", "a+", encoding='utf-8') as file:
        output = f"{datetime.datetime.now()} -- {message}\n"
        file.write(output)


def useless(message):
    """Submits Loggings Try-Except-Passes to Thread Pool."""
    (thread_pool.submit(loguseless, f"{message}")).result()


def loguseless(message):
    """Logs Try-Except-Passes. This will put the exceptions into a log file specifically for cases with no exception
    needed. """
    with open(f"Logs/{datetime.date.today()}-useless.log", "a+", encoding='utf-8') as file:
        output = f"{datetime.datetime.now()} -- {message}\n"
        file.write(output)

