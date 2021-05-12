# **V1.03.9 Patch Notes**  

## **New Commands/Features:**
API has public random photo endpoint.  

Wolfram requests are now paginated if it is long.  

MIRAE & Cherry Bullet were added to Weverse.  

Added a group filter for guessing games (`ggfilter`). These scores do not count towards the leaderboard.  

Added Language Packs (`setlanguage`) -> Currently only english available.  

Currency and BlackJack have been entirely recoded and have been re-enabled.  
-> Player VS Bot has been removed.  
-> Currency rates have been lowered. Once finalized, all currency from users will be wiped to zero to reduce the 
crazy inflation.  
-> BlackJack has been recoded to allow for custom cards with idols. (Instantly generated from Idol Avatars)  

Added API endpoint for guessing game (for other developers, not currently used on IreneBot.)  

Added API endpoint for members with photos (for other developers)  

Cleared Bias Game Photos so new avatars were properly regenerated.  

Created a new cog/module ONLY for a bot owner and moved all bot owner commands there to stop confusion of what a user 
can use in a module.  

A new check has been added for facial detection before going to the production db.  

Photos for BIBI, Lucy, DreamNote, Dal Shabet, Honey Popcorn, Bestie, Bonusbaby, Golden Child, Weki Meki, Loona,
Verivery, SHINee, SF9, AKMU, STAYC, and SISTAR were added this update.  

`%resetcache` was added to manually reset cache instead of having to wait 12 hours.  

Users must now be in the support server to play Guessing/Bias Game. This is important for accurate user feedback.  

Weverse messages no longer have a 5 second delay per channel.  
-> This is a test in production to see how affected the bot will be.  


## **Bug/Issue/Backend Fixes/Changes:**

IreneBot now requests from localhost instead of direct domain.  

Weverse account token was regenerated to load newer posts.  

Filtered Guessing Game list is no longer paginated if it is one page.  

Fixed Weverse Comments not posting (Weverse.io had changed their format  
-> still needs to be looked into more).  

Fixed guessing game end messsage being posted twice.  

Guessing and Bias Games are now properly removed from cache after any errors.  

Created more efficient language pack design by having a list of keyword and inputs to iterate over to not have several 
replace statements in a single command just to get all input set up properly. We can now also directly change input
from the Utility get_msg method itself.  

GG, BG, and BJ are now all concrete subclasses of an abstract Utility Game model and have been moved to the 
Utility models folder.  

Utility was made portable.  
-> Any instances created in the properties of Utility would be set in the client run.py  
-> Any utils accessing a client module were moved.  

N-Word is no longer hard-coded and is a list in an environment variable.  

`card`, `remindme`, and `ggfilter` have been either embedded, or removed user input on message in order to remove 
unintentional mentions.  

Fixed weverse messages coming back blank and not sending a lot of posts.  

A note is now left on guessing game on how to disable the ggfilter if there are no results.  

If an idol and group have the same name, all of the idols are put into a list and chosen randomly.  
-> ex: Weki Meki Lucy & the group Lucy.  
-> The issue was occurring so that only the idol would be posted and not the group.  

Fixed DEV branch to not be so unstable for production.  

Patreon Cache now loads during reset cache. This fixes the issue with patrons not being recognized.  

Patrons now have priority check when posting an idol photo.  

When the Bot restarts, Live Twitch channels are not sent to a channel again and it keeps track in the DB.  

Added a bare yield to majority for loops.  

`countmember` and `countgroup` were fixed.  

SQL is now in a separate part in the Utility. This means it will be much easier to switch libraries if ever needed be,
and it is just cleaner code in general.  

IreneAPI is now on its own repository.  

IreneUtility is now on its own repository **BUT THE VERSION NUMBERS MATCH TO EACH OTHER**  

A logging function has been created for skipped errors.  
-> Try Except Passes are now rendered into a third file as unimportant errors.  

Majority methods in Utility and across IreneBot are now documented better than they were before.  

Fixed issue where members that are in support server are not able to use gg or bg.  
-> Fixed by making our own member support server cache.  

IreneBot and IreneUtility have been redesigned in a way that will support type-casing a lot more.

Moved Keys to a separate object in Utility for proper type-casing support.  

Fixed commands not being responsive.  
-> Issue was two clients being created.  

Fixed broken help command.  
-> Utility object that temporarily created was pointing to the wrong check method.  

Removed possible negative numbers on currency by defaulting all balance amounts to 0 if less than 0.  

Guilds Table is now accurately updated when guilds join/leave and is reset completely everytime discord cache reloads.
