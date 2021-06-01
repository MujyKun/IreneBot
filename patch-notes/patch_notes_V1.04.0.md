# **V1.04.0 Patch Notes**  

## **New Commands/Features:**
Added ability to toggle games using `%togglegames`.  

Added Unscramble Game! `%help UnScramble`  

Added photos for `PIXY`, `WJSN`, `Pentagon`, `PLAYBACK`, `PURPLE KISS`, `9MUSES`, `A.C.E`, `REDSQUARE`,  
`3YE`, `P.O.P`, `Maka Maka`, `Ikon`, `Winner`, `Brave Girls`, `KARD`, `Ladies Code`

Added `np` as an alias for `%recent`  

Added default roles when a user joins a server using `%welcomerole`.  

Group names are now an allowed input for `%ggfilter` but are not as accurate as group ids.  

Former full name and former stage name are now correct answers for a guessing game.  

Irene now uses its own translation system if Weverse does not have a translation.  

Guessing Game can now report images using `dead` or `report` instead of `skip`.  
-> The reason for this is due to constantly waiting for a dead link reaction, whereas `dead` or `report`  
will ask for a double confirmation.  
-> Skip will now be used as an actual skip/pass without the option to report.  

`%endgame` was renamed to `%stopbj`.  

New command `%stopgames` (Aliases: `%endgames`/`%stopgame`/`%endgame`) was added to stop ALL games in the current text channel  
or that the user is a host of.  

## **Bug/Issue/Backend Fixes/Changes:**
Fixed Session ID not appearing on %botinfo.  

Fixed Twitch Notifications  

Fixed NWL dictionary changed size during iteration (created a copy).  

Made NWL faster to work with millions of users a lot quicker.  

`%choose` was embedded to avoid unnecessary/accidental mentions.  

`%botinfo` now works as expected.  

Fixed patron status disappearing after 12 hours.  

Created Official Documentation for Weverse and adjusted IreneBot to any code changes.  

Created a new image host server, this way discord will be able to download images from months ago in history if  
they do not exist without making a direct API call.  
-> Will make a call to api if image does not exist.  
-> Limits 25k photos existing at once  
-> Deletes random file if there are more than 25k photos.  

ALL WJSN photos were deleted and replaced.  

Added requirement for more specific youtube urls.  

Added Metrics For:  
-> Amount of Text channels with games disabled.  
-> Amount of dead images.  
-> Amount of User Objects.  
-> Amount of welcome roles.  
-> Amount of playing cards.  
-> Amount of members in support server.  
-> Amount of users with gg filter enabled.  

Bias game should no longer say it was force-closed when it ended normally.  

Added more appropriate error message for `%addidol` and `%addgroup` since users found it confusing.  

