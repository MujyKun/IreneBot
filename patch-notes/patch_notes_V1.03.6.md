# **V1.03.6 Patch Notes**  

## **New Commands/Features:**  
Added Server-Side Idol & Group Aliases  

DataDog Analytics now available on https://irenebot.com/statistics  

`%botinfo` now contains Weverse Status and the amount of Guessing/Bias Games concurrently occurring.  

`%moveto` was readded for Bot Mods to move images to other idols.  

The DCAPP commands were completely removed.  

Added `%addalias` and `%removealias` for Servers and BotMods. Servers are local and BotMods create Global aliases.  

Added Local and Global Aliases to `%card (idol)`  

Advanced Results now show on Wolfram Requests.  

When the bot restarts, a message will be sent to all game channels letting the user know the bot will delete their game.  

Added Thousands of Photos for `GOT7`, `ATEEZ`, `BIG BANG`, `Block B`, `B1A4`, `T-ara`.  

Self-Assignable Roles were added (`%addrole`, `%removerole`, `%listroles`, `%sendrolemessage`, `%setrolechannel`). `%help SelfAssignRoles` for more info.  

Added Weverse Updates. (`%updates (community name)`, `%disablecomments (community name)`)  


## **Bug/Issue/Backend Fixes:**  
File Logging will no longer block certain commands.  

GuessingGame took too long loading photos -> Added Delay of 2 Seconds.  

Fixed issue where `%sendimages` tries to get information on nonexistant channel and can no longer update to a new channel.  

Fixed `%addemoji` displaying the wrong error message.  

Fixed Bias and Guessing Game causing errors in DMs.  

Fixed issue with BotMod DMs creating errors on list iteration when the list is updated.  

API crashing seemed to occur frequently. API restarts after x amount of errors in a row.  

Fixed Bug where `%help`, `%avatar`, `%profile` could not be used in DMs.  



