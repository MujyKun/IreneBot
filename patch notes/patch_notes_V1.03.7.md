# **V1.03.7 Patch Notes**  

## **New Commands/Features:**  
`%card now display member names with the id instead of full name, group ids on idol cards, and the idol's guessing game difficulty.`  

Using `%setrolechannel` again will remove the channel as a role channel.  

Weverse **should not** duplicate posts anymore in channels, although it may occur every now and then.  

`%addidol` and `%addgroup` are now public and a form was created to assist with easy creation of an idol/group.  

Added `%approve` (bot owner command) to approve a user's idol or group.  

Guessing Games now have 3 difficulties (easy/medium/hard). Idol difficulties were manually chosen. Higher difficulties contain idols from lower difficulties.  

Can now view information on a certain group or idol by their id `%card (idol/group id)`  

Added Photos for CIX, The Boyz, NCT, Treausre, Enhypen, and Aespa.  

Added reminders `%remindme`, `%listreminders`, `%removereminder`, `%gettimezone`, `settimezone`.  

Top.gg Voting is now required for more than 2 idol photos every 12 hours (excluding games)  

Added leaderboards for guessing game difficulty  

Profile now contains user timezone if they have it set.  

Added ID of idol to photos.  


## **Bug/Issue/Backend Fixes:**  
Image links are now specific to their file id which means discord may be able to load them faster.  

On this update, guessing game was made to be in separate tasks, removed this as it was causing crashses.  

`%removerole` now detects roles with several words as a name.  

Guessing Game and Bias game no longer us recursion.  

Music Playing has been fixed and also now properly recognizes users in voice chat without disconnecting.  

Fixed issue where roles were not being added to weverse updates.  

PyCharm warnings were cleared up  

Utility.py (the brain of Irene) ~3000 lines were refactored into about 17-19 subclasses to reduce clutter.  

Fixed profile not loading because of timezone.  

**Hotfixes:**  
Fixed Reminder Timezones, inability to remove reminders, remove reminders once the message has been sent,
majority fm commands not being unpacked correctly, user phrases not properly being removed, %say not adjusting to current text channel properly if not specifying one.  



