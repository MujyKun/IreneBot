# **V1.04.2 Patch Notes**


## **New Commands/Features:**


**Photos for:**
```TRI.BE (1149) | HOPPIPOLLA (2339) | The Boyz Sangyeon (206) | N.flying   (2425) | P1harmony    (1973) | Ariaz  (1153) | Lightsum  (1803) | Kingdom  (696) | ONEWE  (7510) | Cross Gene (714) | Wanna One  (4634) | ab6ix (18257)```

Added Twitter Subscription commands: ``%twitter code/group/idol/list/reset``  
- Limit of 2 accounts for non patrons.  
- Patrons get 5 times more account subscriptions than non patrons.  

Added VLIVE Subscription commands: ``%vlive code/group/idol/list``


Removed the concept of unregistered Idols/Groups and introduced the DataMod Role  
- `%addidol` and `%addgroup` are now exclusive to data moderators.  
- `%edit idol/group` command was added to edit any idol/group.  
- `All changes/additions to an idol/group are logged in a text channel.`  


DataMods, Translators, and Proofreaders are considered patrons and are synced for real-time changes.  

The bot now has several languages included in the bot that can be set using `%setlanguage` (thanks to the translators).  

Youtube, Archive, and Weverse modules have been removed from Irene.  

Added several reload commands for quick and easy Bot Owner changes.
- A module's loops are restarted when reloading.  
- Also added cache commands.  

Added spotify search to music.  
- Waiting for library owners to fix bug regarding youtube links not working.  
- Music may generally be broken as I have not updated some dependencies.  
- Music was actually recoded twice during this update. The first time included full youtube functionalities, 
  while the second one broke that adding Spotify.  

`%botinfo` now displays number of BlackJack games.  

Added UCubeBot for updates on united-cube.com  

The Bias Game list will now show **all** of the idols that have won.  

Added more shard details to the bot.
- Added command `%shard` with alias `shardinfo` to give information about the shard the current server is using.  


## **Bug/Issue/Backend Fixes/Changes:**

GG will no longer wait 2 seconds if uploading from host.  

Editing a banner/avatar will auto migrate to the host.  

Edit command can not modify a date.  

`addidoltogroup` & `removeidolfromgroup` now update the idol attributes as well.  

BlackJack was fixed and is now playable. There was an issue with the second player of the game
being compared when searching for a game.  

`%setlanguage` no longer gives a KeyError if the language was not found.  

Added stats for VLIVE and Twitter.  

Requirements are now entirely reliant on IreneUtility.  

Fixed Idol photos displaying a photo when a user limit was reached.  

Fixed DM message in GG.  

Added better logging in BJ.  

Fixed Music not displaying commands.

Fixed spam messages when using the help command from local cog checks.

Status messages will now change every 1 minute instead of 30 seconds (was too soon).  

Fixed group photos not being called correctly.  

Fixed Twitch not notifying when an account goes live.

Added hot-reloading. Irene can now reload all packages/libs as well as the cogs that are already in the Bot.  
- This actually was a lot harder to do than expected since IreneBot is dependent on IreneUtility.  

Added auto daily backups instead of weekly manual backups.
- Daily is kind of a stretch with how big the database is, but it'll be fine for now.  

`%approve` command was removed.  

Unscramble game now gives answer when skipping.  

Unscramble game will no longer cause an infinite loop.  

Removed unnecessary bolded unique inputs such as server link.  

Removed `nword` and `nwordleaderboard`
- No need for them anymore.  

`commands.json` was created to have accurate information on every single command.
- In the case the site is finished, this will allow for very accurate syncing between the commands of the bot and the sites without much manual change.  
- Usually this info would be stored in the DB, but for a manageable state without altering from code, we will have it stored on a file that is shared across dev/prod.  
- The help command is now based off this file.  

`%listbg` has been embedded to prevent mentions.  



### Weverse (Includes the wrapper and the bot)
- Added login and hook capabilities.  
- Fixed permission issues.  
- Added ability to load media.  
- Will no longer create old posts/media unless specified.  
- Added to Top.gg  
- Can now post announcements.  
- Added ^list on the bot to see which communities are following the current channel.  
- Fixed account language issues by also including Korean trigger phrases.  
- Will auto publish in announcement channels.  
- Weverse Wrapper can now get information on videos.  
- WeverseBot can now post videos.  
- WeverseBot will use an image host link if the image is greater than 8 mb, otherwise it'll upload to discord directly.  



### UCubeBot (Includes the wrapper and the bot)
- Created the bot off Weverse template.  
- Fixed invite link.  
- Added to Top.gg  
- Added ^list on the bot to see which communities are following the current channel.  
- Will auto publish in announcement channels.  
