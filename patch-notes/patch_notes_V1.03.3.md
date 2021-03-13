# **V1.03.3 Patch Notes**  

## **New Commands/Features:**  
Added `%welcome` messages.  

`%sayembed` can now go to a specific channel.  

For random idols, it now confirms the idol has a photo before attempting to send one.  

Idol Photo Storage now deletes at 20,000 photos instead of 10,000 (will be increased in near future)  

`%members` and `%fullnames` can now take in group names to display the members ex: `%members blackpink red velvet`  

Added Seventeen Photos  

Irene was moved to discord.py version 1.5.0  

Added Temp Channels and NWord Counter to Cache  

Set up a new host that is prepared for migration (This will occur in the near future.)  

Added Analytics for every individual command.  

Added Analytics with dates for every session and how many commands are used during that session.  

Removed `%announce` command.  

Added Maintenance Mode (Bot Mod Access).  

## **Bug/Issue Fixes:**  
Server Logging was fixed.  

Fixed error messages that occurred when new servers invited Irene without enough permissions.  

Confirm the user has access to the text channel before sending them a notification about a phrase.  

Lowered Amount of Calls to API at once for proper rate-limiting.  

Fixed bug that didn't add `%randomidol` to the member's idol count until after the reaction timer expired.  

Fixed property bug when adding `%addnoti` to cache.  

Fixed help message of `dcnotify`.  

Idol Photos send an error message in DMs letting the user know they should not use it in DMs.  

Added errors for embeds not loading when sending Idol Photos.  

Fixed DCAPP delay when sending to servers - Issue was translating for every server.  

Fixed Intents from new discord.py version and on developer page for discord.  

Fixed some code inefficiency in numerous places.  












