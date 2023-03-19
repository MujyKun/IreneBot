from main import Bot


def get_bot_ping(bot: Bot) -> int:
    """Get bot client ping in milliseconds."""
    return int(bot.latency * 1000)


def get_server_count(bot: Bot) -> int:
    """Returns the guild count the bot is connected to."""
    return len(bot.guilds)


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
