# **V1.04.1 Patch Notes**  

## **New Commands/Features:**
We now have a group guessing game!  
-> Created command `%groupguessinggame` (Aliases: `%ggg`, `%groupgg`) to guess the names of groups instead of idol names.  

Added `%commands` as an alias for `%help`.  

Created a command `%sendidol [idol id] [#text channel]` to automatically post a photo of an   
idol after every 12 hours in a channel.  
-> Patrons get 3x more idols in a text channel than non-patrons do.  
-> not specifying an idol id will remove all idols in the channel.  
-> To remove an idol, you may repeat the command you used to add them.  

Added `skip` to unscramble game  

Added amount of unscramble games to `botinfo`  

**Photos have been added for:**  
**First Batch:**
-> `Chungha`,`HyunA`,`Sunmi`,`Lee Hi`,`Yerin Baek`,`Ailee`,`BoA`,`Heize`,`Rothy`  
`After School (All Members)`,`DIA (All Members)`,`Kara (All Members)`,`PurpleBeck (All Members)`,  
`4Minute (All Members)`,`Cravity (All Members)`  

**Second Batch:**
-> `ONEUS (22583)`, `ONF (6295)`, `Victon (10758)`, `CIIPHER (688)`, `WEi (1495)`, `ELRIS (11436)`, `lunarsolar (1102)`,
`Ghost9 (97)`, `Super Junior (9316)`, `BTOB (12882)`, `NU'EST (11567)`  

Automatic Twitter Updates were added. (They have been temporarily disabled)  

The facial recognition for all of Irene's photos are now done! This means data is more accurate for the guessing games!  

Weverse has been disabled. We are now reliant on discord announcement channels in the support server!  

Added letteamor, everglow, ftisland, woo!ah!, ikon, blackpink, and just b to Weverse.  

Although currently unusable by regular users, Weverse media now has a toggle (`%disablemedia (community_name)`)  


## **Bug/Issue/Backend Fixes/Changes:**

Added Active Unscramble games as a metric.  

Recoded process for receiving an idol photo. It was way too complex.  

Metrics Added:  
-> # of Unscramble Games  
-> # of Text Channels with automatic idol photos  
-> # of idol photos sent every 12 hours

Server Prefixes and Bot ID are no longer bolded from language packs.  

It is now possible for Irene to upload straight from host  
(it will upload images from host when the image is < 8 mb, otherwise  
it will use the image host url). The reason for this is to ensure discord  
actually loads the photo from Irene's image host (it's rare but sometimes it does not).  

GuessingGame answer is now properly displayed on console and logs for debugging.  

When the bot boots up, it is now automatically in maintenance mode.  

All pending asyncio tasks are now closed safely on bot exit.  

Irene's logging system are now VERY specific with tracebacks displaying the method and class name of the occurrence.  
-> Now using Aiofiles  

Added a blocking manager to Irene to detect cases where Irene is stalling.  

Fixed profile level resetting.
-> This issue was caused by messages being sent when cache was not fully loaded.  

Fixed BlackJack game not announcing proper winner.  

Fixed BiasGame repeating end message twice.  

Params for API:  
-> Added Min and Max face count for an image  
-> Added ability to filter if you want videos  
-> Removed group photos param  
-> Now accept form data sent in as params  
-> Redirect param remains as is  

Added dev mode to Irene. This way we can run a production version of the bot without messing up important data.  


