
# [IreneBot](https://discordapp.com/oauth2/authorize?client_id=520369375325454371&scope=bot&permissions=1609956823)

## Irene Bot for Discord in Python V1.01.7

[![Discord Bots](https://top.gg/api/widget/520369375325454371.svg)](https://top.gg/bot/520369375325454371)
[![Discord Boats](https://discord.boats/api/widget/520369375325454371)](https://discord.boats/bot/520369375325454371)  


## [Discord Support Server](https://discord.gg/bEXm85V)

Commands from this documentation may not be present in the code (The code may be a bit behind with updating).  
Command Prefix is in modules/keys.py and is currently set to '%' by default. To change a server prefix, look at `%setprefix`.    
In order to check the prefix of your server, type `%checkprefix`.

In order to pull a photo of an idol, you can type an idol's stage name, full name, alias, their group name, or group alias name after the prefix.    
examples: `%irene` `%blackpink` `%red velvet`. You may also put an idol's stage name, full name, or alias after a group such as `%red velvet irene`. You can use this with many idols to get a random one. `%red velvet irene joy seulgi` This way, you will pull any of the idols as long as they are in that group.  
To find out more, look at the `GroupMembers` category. 

♥ - Requires Bot Owner  
♥♥♥ -- Entire Section Requires Bot Owner  
★ - Requires Guild Permissions  
★★★ - Entire Section Requires Permissions
😇 - Requires Bot Moderator

## PLUGINS/LIBRARIES USED
| Plugins/Libraries     | pip install                                                                              |
|-----------------------|------------------------------------------------------------------------------------------|
| Discord               | pip install discord.py                                                                   |
| aiohttp               | pip install aiohttp                                                                      |
| asyncio               | pip install asyncio                                                                      |
| bs4 (BeautifulSoup)   | pip install bs4                                                                          |
| aiofiles              | pip install aiofiles                                                                     |
| youtube_dl            | pip install youtube_dl ---- (ffmpeg needed)                                              |
| Google Client Library | pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib |
| Tweepy                | pip install tweepy                                                                       |
| PostgreSQL Driver     | pip install psycopg2                                                                     |
| pypapago (translator)    | pip install pypapago                                                                     |
| dbl (top.gg)   | pip install dbl                                                                    |
| discordboats [MODIFIED]  | pip install discordboats                                                                     |


## COMMANDS

#### Archive: ★★★
| Command               | Description                                                                                           | Format                               |
|-----------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|
| addchannel            | REQUIRES BOT OWNER PRESENCE TO ADD -- Make the current channel start archiving images to google drive | %addchannel (drive_folder_id) (name) |
| addhistory            | Add all of the previous images from a text channel to google drive.                                   | %addhistory (year) (month) (day)     |
| deletechannel         | Stop the current channel from being archived                                                          | %deletechannel                       |
| listchannels          | List the channels in your server that are being archived.                                             | %listchannels                        |


#### BlackJack:
| Command           | Description                                                                                           | Format                               | Aliases |
|-------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|---------|
| addcards          | Fill The CardValues Table with Cards                                                                  | %addcards                            | ♥       |
| blackjack         | Start a game of BlackJack                                                                             | %blackjack (amount)                  | bj      |
| endgame           | End your current game                                                                                 | %endgame                             | eg      |
| hit               | Pick A Card                                                                                           | %hit                                 |         |
| joingame          | Join a game                                                                                           | %joingame (gameid) (bid)             | jg      |
| rules          | View the rules of BlackJack.                                                                                           | %rules             |       |
| stand             | Keep Your Cards                                                                                       | %stand                               |         |


#### Cogs: ♥♥♥
| Command           | Description                                                               | Format                       |
|-------------------|---------------------------------------------------------------------------|------------------------------|
| load              | Command which Loads a Module. Remember to use dot path. e.g: cogs.owner   | %load Module.(filename.py)   |
| reload            | Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner | %reload Module.(filename.py) |
| unload            | Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner | %unload Module.(filename.py) |


#### Currency:
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| balance     | View balance of yourself or a user   | %balance (@user)       | b,bal,$           |
| beg         | Beg a homeless man for money         | %beg                   |                   |
| bet         | Bet your money                       | %bet (amount)          |                   |
| daily       | Gives 100 Dollars Every 24 Hours     | %daily                 |                   |
| give        | Give a user money                    | %give (@user) (amount) |                   |
| leaderboard | Shows Top 10 Users                   | %leaderboard           | leaderboards      |
| rob         | Rob a user - Max Value = 1000        | %rob @user             |                   |
| rps         | Play Rock Paper Scissors for Money   | %rps (r/p/s)(amount)   | rockpaperscissors |
| upgrade    | Upgrade a command to the next level with your money. | %upgrade rob/daily/beg              | levelup                  |


#### DreamCatcher: 
| Command      | Description                                                     | Format                                        | Aliases |
|--------------|-----------------------------------------------------------------|-----------------------------------------------|---------|
| dcstart      | Starts DC LOOP                                                  | %dcstart                                      | ♥       |
| dcstop       | Stops DC LOOP                                                   | %dcstop                                       | ♥       |
| download_all | Download All DC Photos from DC APP                              | %download_all                                 | ♥       |
| latest       | Grabs the highest resolution possible from MOST RECENT DC Posts. | %latest (member)                                      | ★       |
| updates      | Send DreamCatcher Updates to your current text channel          | To start %updates, To Stop : %updates stop | ★       |

  
#### GroupMembers:
| Command          | Description                                                                        | Format                                                                                                         | Aliases                |
|------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------|
| addalias         | Adds an alias to an idol/group.                                                              | %addalias (alias) (ID of idol/group) ("idol" or "group")                                                                                                      | 😇                      |
| addgroup         | Adds a group.                                                              | %addgroup (group name)                                                                                                      | 😇                      |
| addidol         | Adds an idol (Use underscores for spaces).                                                              | %addidol (full name) (stage name) (group id)                                                                                                      | 😇                     |
| addidoltogroup         | Adds idol to group.                                                              | %addidoltogroup (idol id) (group id)                                                                                                     | 😇                      |
| aliases          | Lists the aliases of idols that have one.                                           | %aliases                                                                                                       |                        |
| count            | Shows howmany times an idol has been called.                                       | %count (name)                                                                                                  |                        |
| countleaderboard | Shows leaderboards for how many times an idol has been called.                     | %clb                                                                                                           | highestcount, cb, clb |
| countgroup      | Shows how many images of a certain group there are.                               | %countgroup (group)                                                                                          |                        |
| countmember      | Shows how many images of a certain member there are.                               | %countmember (member)                                                                                          |                        |
| deletealias         | Remove alias from an idol/group.                                                               | %deletealias (alias) (ID of idol/group) ("idol" or "group")                                                                                                     | 😇, removealias                      |
| deletegroup         | Deletes a group.                                                              | %deletegroup (group id)                                                                                                    | 😇, removegroup                     |
| deleteidol         | Deletes an idol.                                                              | %deleteidol (idol id)                                                                                             | 😇, removeidol                      |
| deleteidolfromgroup         | Deletes idol from group                                                              | %deleteidolfromgroup (idol id) (group id)                                                                                             | 😇, removeidolfromgroup                      |
| fullnames        | Lists the full names of idols the bot has photos of                                | %fullnames (page number)                                                                                                    |   fullname                     |
| getlinks         | Add links of photos to database from linked Archives                               | %getlinks                                                                                                      | ♥                      |
| groups           | Lists the groups of idols the bot has photos of                                    | %groups                                                                                                        |                        |
| members          | Lists the names of idols the bot has photos of                                     | %members (page number)                                                                                                      |    member                    |
| randomidol          | Sends a photo of a random idol.                                     | %%                                                                                                       |                   %     |
| scandrive        | Scan DriveIDs Table and update other tables.                                       | %scandrive (name=NULL) (member_id=0)                                                                           | ♥                      |
| scrapelink      | Connection to site + put html to html_page.txt                                     | %scrapelinks                                                                                                   | ♥                      |
| sort             | Approve member links with a small sorting game.                                    | %sort -- checks next message                                                                                   | ♥                      |
| tenor            | Connection to tenor API // Sends Links of gifs to Database. Dashes (-) are spaces. | %tenor                                                                                                         | ♥                      |
#### Logging: ★★★  
| Command      | Description                                                                                          | Format        |
|--------------|------------------------------------------------------------------------------------------------------|---------------|
| logadd       | Start logging the current text channel.                                                              | %logadd       |
| logremove    | Stop logging the current text channel.                                                               | %logremove    |
| sendall      | Toggles sending all messages to log channel. If turned off, it only sends edited & deleted messages. | %sendall      |
| startlogging | Start sending log messages in the current server and channel.                                        | %startlogging |
| stoplogging  | Stop sending log messages in the current server.                                                     | %stoplogging  |

#### Miscellaneous:
| Command          | Description                                                    | Format                          | Aliases        |
|------------------|----------------------------------------------------------------|---------------------------------|----------------|
| _8ball           | Asks the 8ball a question.                                     | %8ball (Question)               | 8ball,8        |
| announce         | Sends a bot message to text channels                           | %announce (message)             | ♥              |
| addstatus       | Add a playing status to Irene.                                   | %addstatus (status)               | ♥              |
| botinfo       | Get information about the bot.                                   | %botinfo               |               |
| checkprefix       | Check the current prefix using the default prefix.                                   | %checkprefix               |               |
| clearnword       | Clear A User's Nword Counter                                   | %clearnword @user               | ♥              |
| flip             | Flips a Coin                                                   | %flip                           |                |
| getstatuses             | Get all statuses of Irene.                                                   | %getstatuses                           |                |
| invite           | Invite Link for Irene                                          | %invite                         |                |
| kill             | Kills the bot                                                  | %kill                           | ♥              |
| logging          | Start logging this channel/Stop logging this channel           | %logging (start/stop)           | ♥              |
| nword            | Checks how many times a user has said the N Word               | %nword @user                    |                |
| nwordleaderboard | Shows leaderboards for how many times the nword has been said. | %nwl                            | nwl            |
| ping             | Shows Latency to Discord                                       | %ping                           | pong           |
| random           | Choose a random number from a range (a,b)                      | %random a b [Ex: %random 1 100] | r,rand,randint |
| report          | Report an issue with Irene.                                    | %report (issue)              |               |
| say              | Owner to Bot Message                                           | %say (message)                  | ♥              |
| send              | Send a message to a text channel.                                             | %send (channelid) (message)                  | ♥              |
| servercount      | Shows how many servers Irene is on.                            | %servercount                    |                |
| serverinfo      | View information about the current server.                            | %serverinfo                   |                |
| servers          | Displays which servers Irene is in.  | %servers                        | ♥              |
| slap          | Slap someone                              | %slap @user                       |                |
| speak            | Owner to Bot TTS                                               | %speak (message)                | ♥              |
| suggest          | Suggest a feature for Irene                                    | %suggest (feature)              |               |
| support          | Support Discord Server for Irene                               | %support                        |                |
| translate          | Translate between languages using Papago                              | %translate English Korean this is a test phrase.                       |                |


#### Moderator: ★★★
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| addemoji         | Adds an emoji to the server.                                                                                                         | %addemoji (url) (emoji_name)    |               |
| ban              | Ban A User                                                                                                                           | %ban @user                      |               |
| clear            | Prune Messages                                                                                                                       | %clear (amount)                 |  prune        |
| kick             | Kick A User                                                                                                                          | %kick @user                     |               |
| setprefix      | Set the server prefix. If prefix was forgotten, type this command with the default prefix. | %setprefix $         |          | 
| tempchannel      | Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel. | %tempchannel [delay=-1]         | temp         |
| unban            | UnBan A User                                                                                                                         | %unban @user                    |               |
  
#### Profile:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| avatar         | Display a user's avatar.                                                                                                         | %avatar @user    |               |
| profile         | Display a user's profile.                                                                                                         | %profile @user    |               |


#### Twitter: ♥♥♥
| Command          | Description                                                                                                                          | Format                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| deletetweet      | Delete a Tweet by it's ID                                                                                                            | %deletetweet (id)               |
| recenttweets     | Show Most Recents Tweets                                                                                                             | %recenttweets (amount)          |
| tweet            | Tweets a status update on Twitter                                                                                                    | %tweet (status)                 |


#### Youtube: ♥♥♥

| Command          | Description                                                                                                                          | Format                                       |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| addurl           | Add url to youtube videos                                                                                                            | %addurl (link)                               |
| removeurl        | Remove url from youtube videos                                                                                                       | %removeurl (link)                            |
| scrapeyoutube    | Scrape Youtube Videos in DB                                                                                                          | %scrapeyoutube                               |
| startloop        | Starts scraping youtube videos.                                                                                                      | %startloop (seconds until it starts looping) |
| stoploop         | Stops scraping youtube videos                                                                                                        | %stoploop                                    |
