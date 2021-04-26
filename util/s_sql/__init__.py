conn = None


# do not import at top of file. we need conn as the db connection in sub folders without circular import issues.
from util.s_sql import s_biasgame, s_blackjack, s_cache, s_customcommands, s_database, s_gacha, s_groupmembers, \
    s_guessinggame, s_lastfm, s_logging, s_miscellaneous, s_moderator, s_patreon, s_reminder, \
    s_selfassignroles, s_twitch, s_twitter, s_weverse, s_currency, s_levels, s_user, s_session, s_general


