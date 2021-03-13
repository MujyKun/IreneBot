# **V1.03.5 Patch Notes**  

## **New Commands/Features:**  
Added Idol and Group information cards `%card (idol/group name)`  

Added Drop One, Save One (AKA Bias Game) `%help BiasGame`  

Added `%biasgame (male/female/all) (bracket size(4,8,16,32))`  

Added `%stopbg` to end a Bias Game  

Added Leaderboards to Bias Game Wins `%listbg`  

Renamed `%stopgame` from GuessingGame to `%stopgg`  

Added a maintenance reason when bot mods use `%maintenance`  

Idol and Group Avatars/Banners are now stored under `images.irenebot.com`  

Stray Kids, AleXa, Monsta X, Ateez Photos are currently processing and will be added soon.  

Added Custom Commands  

Added `%createcommand (command name) (message)` to create commands on a server.  

Added `%deletecommand (command name)` to delete a custom command.  

Added `%listcommands` to view the custom commands on a server.  

Bot Statuses were added to Cache.  

Added Bot Mod Command `%removestatus (status index)` to remove an already existing bot status.  

A special check has been put in place to check for group photos with the guessing game.  

Added ability to report guessing game photos as dead links OR group photos.  

Dead Image Links & the channel object is now stored as cache.  


## **Bug/Issue/Backend Fixes:**  
Removed `quickstart.py` from code as it has not been used for months.  

Fixed Infinite Loop of Custom Commands  

Fixed Prefix Issue with Custom Commands that allowed any prefix.  

Removed `%deletelink` , `%moveto` from Bot Mod commands.  

Fixed Music not playing.  

Fixed `%card` displaying fake group & idol relationships.  

Fixed issue where `.webm` links were not uploading to discord.  
















