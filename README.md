# IreneBot 
 Irene Bot for Discord in Python V1.0

Upon signing up for the Google Drive API, make sure to put the credentials.json in the main folder.
[ https://developers.google.com/drive ]


When first getting the bot to work, make sure to use the %upload command to get the Google Drive API to properly work. You will need to sign into your Google Account when it prompts you as a one time authorization.
ImageUploader was not coded with aiohttp, so there will be blockage from other commands when these commands are in use.
There are instructions left in quickstart.py for first time running. Make sure to follow the comments.


Command Prefix is in run.py and is currently set to '%' by default.
______
FILES
______
run.py - Main Program/Bot - Startup

Cards/.. - All Cards In A Deck

music/.. - Local Music Files

modules/BlackJack.py - A 1v1 game of blackjack

modules/Currency.py - Games that involve an economy

modules/DreamCatcher.py - Send Photos from the DC App to a certain text channel based on a loop. 

modules/ImageUploader.py - Commands for downloading photos from a text channel and uploading them to google drive.

modules/Miscellaneous.py - clear/kill/ping/speak/say/8ball/servers [Things I didn't feel like making a section for]

modules/Music.py - Commands for Music

modules/Twitter2.py - Commands for Twitter

modules/currency.db - Database that includes the economy.

modules/keys.py - All Keys/Tokens should be put here.

modules/quickstart.py - Google Drive API

modules/twitter.py - Connection to Twitter API
______
COMMANDS
________
BlackJack:

addcards   ----  Fill The CardValues Table with Cards [Format: %addcards]

blackjack  ----  Start a game of BlackJack [Format: %blackjack (amount)] [Aliases: bj]
  
  endgame   ----   End your current game [Format: %endgame] [Aliases: eg]
  
  hit       ----   Pick A Card [Format: %hit]
  
  joingame  ----   Join a game [Format: %joingame (gameid) (bid)] [Aliases: jg]
  
  stand     ----   Keep Your Cards [Format: %stand]
________
Currency:

  balance   ----   View your balance [Format: %balance (@user)][Aliases: b,bal,$]
  
  beg      ----    Beg a homeless man for money [Format: %beg]
  
  bet      ----    Bet your money [Format: %bet (amount)]
  
  give      ----   Give a user money [Format: %give (@user) (amount)]
  
  leaderboard ---- Shows Top 10 Users [Format: %leaderboard][Aliases: leaderboards]
  
  raffle    ----   Join a Raffle [Format: %raffle to start a raffle; %raffle (amount) to join; %raffle 0 balance to check current amount]
  
  rafflereset ---- Resets Raffle without giving people their money back[Format: %rafflereset]
  
  register    ---- Register yourself onto the database.
  
  resetall  ----   Resets Leaderboard [Format: %resetall] USE WITH CAUTION
  
  rob     ----     Rob a user [Format: %rob @user] - Command does not exist yet.
  
  roll    ----     No Description Yet- Command does not exist yet.
  
  rps      ----    Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]
________
DreamCatcher:

scrape   ----    Starts Loop Searching For New DC Post [Format: %scrape (post number to start at)] NOTE : This command must be used every run as it will not automatically start the loop [can easily be coded to be automatic] Starts scraping from post number 36582 by default

updates   ----   Send DC Updates to your current text channel [Format: %updates] | To Stop : [Format: %updates stop]
________
ImageUploader:

deletephotos ---- Delete All Photos in Photos Folder [Format: %deletephotos]

steal     ----   Downloads Images from Current Text Channel [Format: %steal (amount of messages)][Aliases: log]

upload    ----   Uploads All Images in the Photos Folder to Google Drive [Format: %upload (all/filename)]

view        ---- Shows amount of Images in the Photos Folder [Format: %view]
________
Miscellaneous:

_8ball   ----    Asks the 8ball a question. [Format: %8ball Question]

clear    ----    Prune Messages [Format: %clear (amount)][Aliases: prune]

kill     ----    Kills the bot [Format: %kill]

ping      ----   Shows Latency to Discord [Format: %ping]

say       ----   Owner to Bot Message

servers   ----   Extremely sloppy way of showing which servers the bot are in.

speak      ----  Owner to Bot TTS
________
Music:

join       ----  Joins a voice channel [Format: %join]

local     ----  Plays a file from the local filesystem

localfiles ----  Displays all music in the music folder [Format: %localfiles]

pause   ----     Pauses currently playing song [Format: %pause]

play     ----    Streams from a url (same as yt, but doesn't predownload)

queue    ----    Shows Current Queue [Format: %queue]

resume   ----    Resumes a paused song [Format: %resume]

stop     ----    Stops and disconnects the client from voice

volume    ----   Changes the player's volume - play,yt, and local all have  preset volumes when they start playing.

yt        ----   Play A Song From Youtube[Format: %play (url)]
________
Twitter:

deletetweet ---- Delete a Tweet by it's ID [Format: %deletetweet (id)]

recenttweets ---- Show Most Recents Tweets[Format: %recenttweets (amount)]

tweet     ----   Tweets a status update on Twitter [Format: %tweet (status)]
________
