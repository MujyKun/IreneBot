from functools import wraps


def disabled_command(func):
    """Decorator to disable a command."""

    @wraps(func)
    async def wrap_async_function(self=None, *args, **kwargs):
        ctx = args[0]
        await ctx.send("This feature may not work anymore and has been disabled.")
        raise Exception

    return wrap_async_function


from module import BlackJack, BotMod, Currency, GroupMembers, Help, keys, \
    Logging, Miscellaneous, Moderator, Music, Profile, status, Twitter, \
    events, LastFM, Interactions, Wolfram, GuessingGame, CustomCommands, BiasGame, \
    SelfAssignRoles, Reminder, Twitch, Gacha, BotOwner, UnScramble, blockingmonitor, Vlive, DataMod


