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
    member_count = sum([guild.member_count for guild in bot.guilds])
    return member_count

