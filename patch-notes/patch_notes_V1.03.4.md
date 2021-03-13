# **V1.03.4 Patch Notes**  

## **New Commands/Features:**  

A multi-player guessing game has been added for Idols! `%help guessinggame`  

You can now choose between server/global wide currency leaderboards. `%leaderboard (global/server)`  

Added `%mergeidol` and `mergegroup` for duplicate Idols when importing from other sources.  

`%choose` was added to select from a number of options Underscores is for several words as an option while a space is to indicate an option.  

Restricted channels, Idols, and Groups are now added to cache.  

Added `%displayemoji :emoji:` to display an emoji larger.   

If the bot is mentioned, it will give them information to help use the bot.  

Tempchannels now have a minimum deletion time of 1 minute due to rate-limiting.  

It is now possible to do `%aliases (group name/idol name)` to check the aliases of a specific idol or group.  

If the guild owner is a Super Patron, all users in that guild will get 2x the max amount of idol photos.  

Added Maintenance,DB,Images, and API Status to `%botinfo`.  

Added `p` as an alias for `%play`.  

Added `%killAPI` for Bot Mods to restart API  

Merged API with IreneBot to run under the same server.  

Added photos THE NINE and Day6  

Added hundreds of secret groups and idols not publicly seen.  

`%members` and `%groups` will NOT show idols that have 0 photos.  

Idol Photos can now be spammed without sleep timers.  


## **Bug/Issue/Backend Fixes:**  

Irene is not allowed to mute herself anymore.  

Moved tempchannel to general schema on DB.  

If the command is `%setprefix` or `%checkprefix`, the prefix will no longer be altered according to the server prefix.  

Created DB cache of patrons to fix issue of Patrons not loading right away.  

Fixed issue where if the guild owner was a normal patron, the entire server could use Music.  

Fixed bug that terminates temp channel cache.  

Swapped Jihan and Zoa from Weeekly  















