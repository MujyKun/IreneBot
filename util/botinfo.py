from main import Bot


def get_bot_ping(bot: Bot) -> int:
    """Get bot client ping in milliseconds."""
    return int(bot.latency * 1000)


def get_server_count(bot: Bot) -> int:
    """Returns the guild count the bot is connected to."""
    return len(bot.guilds)


def get_today_user_requests():
    """Returns the GroupMember search requests from today."""
    from models import requests_today

    return requests_today


def get_numbers_of_distance_words():
    """Returns the number of distance words in key cache. Used for GroupMembers search."""
    from models import distance_between_words

    return len(distance_between_words)


def get_distance_words_active_threads():
    """Returns the number of active threads used in GroupMembers search"""
    from models import request_executor

    return len(request_executor._threads) - request_executor._work_queue.qsize()


def get_channel_count(bot: Bot) -> int:
    """Returns the channel count from all the guilds the bot is connected to."""
    return sum([len(guild.channels) for guild in bot.guilds])


def get_text_channel_count(bot: Bot) -> int:
    """Returns the text channel count from all the guilds the bot is connected to."""
    return sum([len(guild.text_channels) for guild in bot.guilds])


def get_voice_channel_count(bot: Bot) -> int:
    """Returns the voice channel count from all the guilds the bot is connected to."""
    return sum([len(guild.voice_channels) for guild in bot.guilds])


def get_user_count(bot: Bot) -> int:
    """Get the amount of users that the bot is watching over."""
    return len(bot.users)


def get_count_active_games():
    """Get a list of active games for each game type."""
    return [
        len(get_gg(finished=False)),
        len(get_ggg(finished=False)),
        len(get_bg(finished=False)),
        len(get_us(finished=False)),
        len(get_other_games(finished=False)),
    ]


def get_count_unfinished_games():
    """Get a list of total unfinished games for each game type."""
    return [
        len(get_gg()),
        len(get_ggg()),
        len(get_bg()),
        len(get_us()),
        len(get_other_games()),
    ]


def get_count_total_games():
    """Get a list of total amounts for each game type."""
    from models import ggs, gggs, uss, bgs, bjs, others, all_games

    return [len(ggs), len(gggs), len(bgs), len(uss), len(others), len(all_games)]


def get_gg(finished=True):
    from models import ggs

    return [gg for gg in ggs if gg.is_complete is finished]


def get_bg(finished=True):
    from models import bgs

    return [bg for bg in bgs if bg.is_complete is finished]


def get_us(finished=True):
    from models import uss

    return [us for us in uss if us.is_complete is finished]


def get_ggg(finished=True):
    from models import gggs

    return [ggg for ggg in gggs if ggg.is_complete is finished]


def get_other_games(finished=True):
    from models import others

    return [other for other in others if other.is_complete is finished]
