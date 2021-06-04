# **V1.04.1 Patch Notes**  

## **New Commands/Features:**

Added `%commands` as an alias for `%help`.  

Created a command `%sendidol [idol id] [#text channel]` to automatically post a photo of an   
idol after every 12 hours in a channel.  
-> Patrons get 3x more idols in a text channel than non-patrons do.  
-> not specifying an idol id will remove all idols in the channel.  
-> To remove an idol, you may repeat the command you used to add them.  

Added `skip` to unscramble game  

Added amount of unscramble games to `botinfo`  

Photos have been added for:
-> `Chungha`,`HyunA`,`Sunmi`,`Lee Hi`,`Yerin Baek`,`Ailee`,`BoA`,`Heize`,`Rothy`  
`After School (All Members)`,`DIA (All Members)`,`Kara (All Members)`,`PurpleBeck (All Members)`,  
`4Minute (All Members)`,`Cravity (All Members)`


## **Bug/Issue/Backend Fixes/Changes:**

Added Active Unscramble games as a metric.  

Recoded process for receiving an idol photo. It was way too complex.  

Amount of unscramble games is now put as a metric.  

Server Prefixes and Bot ID are no longer bolded from language packs.  

It is now possible for Irene to upload straight from host  
(it will upload images from host when the image is < 8 mb, otherwise  
it will use the image host url). The reason for this is to ensure discord  
actually loads the photo from Irene's image host (it's rare but sometimes it does not).  

