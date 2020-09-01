# **V1.03.0 Patch Notes**  

## **New Commands/Features:**  

Edited Commands can now be register commands if the message and edit time are within 60 seconds.  

`%addemoji` now takes in emoji AND url input. It can also add several emojis at once now and the emoji name is OPTIONAL and no longer required.  

During August 2020, ALL photos were migrated from external sites DIRECTLY to Irene's Google Drive. This means it is much easier to now upload images to Irene manually and automatically without worrying about Storage. [Consider being a patron to help with costs](https://www.patreon.com/mujykun)  

`%dcnotify @role` -> Notify a role when there is a new DCAPP post.  

`%disableinteraction (interaction)` -> You can now disable and re-enable interactions on a specific server.  

`%sayembed (json)` -> You can use JSON to send an embed message in a channel with Irene following the format from https://embedbuilder.nadekobot.me/  


Irene Public API (api.irenebot.com) now has a translate endpoint. This confirms a stable translation system with `%translate`.  

With the above being said, All DC APP Posts are now auto translated directly from KR to EN.  

Irene now uses a Sharded Client.  

ModMail was created for Irene's Bot Mods ( this feature may get extended to normal servers in the future ).  

## **How ModMail Works**:  
`%createdm (userid)` -> The user will receive a dm from Irene if possible and all the messages that are sent TO and FROM Irene during this time will go back and forth with Irene as the "middle man"  

`%closedm <userid>` -> Will close the EARLIEST DM in a text channel or close a dm directly with the user in the current text channel.  

It is possible to have several users in one DM Channel, but all of the users will get the same messages but they will not be able to see each other's messages.  

## **Bug/Issue Fixes:**  
`%dcstart` & `%dcstop` now create a new instance and both rely on each other separate from the main dc loop.  

`%startloop` & `%stoploop` now create a new instance and both rely on each other separate from the ain youtube loop.  

`%scrapeyoutube` now leaves a message.  

`%help (module/cog)` now **ONLY** shows commands you have access to.  

Group Idol Photos can no longer be posted in temp channels due to overload  

Rate limit non patrons | Requests stall for 1.5 seconds for ALL users | Non patrons will only be able to call 150 photos a day | Patrons can send unlimited photos.  

All reactions are removed from an idol post after it runs out of time (60 seconds).  

Fixed issue where non patrons exceeding 150 photos would spam them after every message. Now only says the patron message after idol photo commands.  

For pages, instead of removing ALL reactions, Irene only removes the USER'S reaction.  

Reload Idol Image now only reloads once instead of three times.  

Phrase notifications no longer search for the word inside a word (ex: sue in is'sue's) It has to be an independent word in order to notify the user.  



