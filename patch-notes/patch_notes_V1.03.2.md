# **V1.03.2 Patch Notes**  

## **New Commands/Features:**  
Group Photo Count Updated for Docs  

`%download_all` was removed.  

Irene now has majority features cached: (group photo counts, dc app channels and role ids, patrons, commands used, user notification, mod mail, users banned from bot, logged servers, logged channels, and server prefixes)  

Irene now grabs media from the API endpoint (https://api.irenebot.com/photos/{member_id}) instead of doing it directly in Irene.  

Translation API for Irene was made private due to excessive usage outside of Irene.  

$10 Patrons created to have access to the API endpoint for idol photos and translation.  

Pressing the dead link reaction on an idol photo will edit the message saying only to use it when it's needed. This message is removed as a patron.  

Idol photos now have a footer message to let them know it is possible to be a patron.  

Emojis are no longer pre-downloaded and it's data is read directly online. (Emojis Folder deleted.)  

Every 1000 Photos called will result in a deletion of those 1000 from `images.irenebot.com`.  

8+ MB Photos can now be loaded since they are stored on `images.irenebot.com`  

Irene now sleeps for 1 second if the request was made within 2 seconds of another request instead of 1.5s.  

Lyrics can now have several pages.  

`%botwarn` was added for Bot Mods to warn abusive users.  



## **Bug/Issue Fixes:**  
`%addemoji` now gives an error for reaching the emoji limit.  

Fixed Bug that didn't allow idol photo requests of group to idols (ex: `%red velvet irene`)  

Fixed Cache not properly updating Patron List.  

Fixed `%groups` not displaying photo count.  

Fixed `%startlogging` issue that stopped users from logging their servers.  

Added Photo Links to Idol Photo Titles.  


