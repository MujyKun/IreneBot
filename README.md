# [IreneBot V1.02.7](https://discordapp.com/oauth2/authorize?client_id=520369375325454371&scope=bot&permissions=1609956823)

## [Support Irene by becoming a Patron!](https://www.patreon.com/bePatron?u=38971435)  
**[Become a Patron!](https://www.patreon.com/bePatron?u=38971435)**

[![Discord Bots](https://top.gg/api/widget/520369375325454371.svg)](https://top.gg/bot/520369375325454371)
[![Discord Boats](https://discord.boats/api/widget/520369375325454371)](https://discord.boats/bot/520369375325454371)  


## [Discord Support Server](https://discord.gg/bEXm85V)

Command Prefix is currently set to `%` by default. To change a server prefix, look at `%setprefix`.    
In order to check the prefix of your server, type `%checkprefix`.

In order to pull a photo of an idol, you can type an idol's stage name, full name, alias, their group name, or group alias name after the prefix.    
examples: `%irene` `%blackpink` `%red velvet`. You may also put an idol's stage name, full name, or alias after a group such as `%red velvet irene`. You can use this with many idols to get a random one. `%red velvet irene joy seulgi` This way, you will pull any of the idols as long as they are in that group.  
To find out more, look at the `GroupMembers` category. 

♥ - Requires Bot Owner  
★ - Requires Guild Permissions  
😇 - Requires Bot Moderator
♥♥♥ -- Entire Section Requires Bot Owner  
★★★ - Entire Section Requires Guild Permissions  
😇😇😇 - Entire Section Requires Bot Moderator

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

#### BotMod: 😇😇😇  
| Command           | Description                                                                                           | Format                               | Aliases |
|-------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|---------|
| addalias         | Adds an alias to an idol/group. (Underscores are spaces)                                                              | %addalias (alias) (ID of idol/group) ("idol" or "group")                                                                                                      |                       |
| addgroup         | Adds a group.                                                              | %addgroup (group name)                                                                                                      |                       |
| addidol         | Adds an idol (Use underscores for spaces).                                                              | %addidol (full name) (stage name) (group id)                                                                                                      |                      |
| addidoltogroup         | Adds idol to group.                                                              | %addidoltogroup (idol id) (group id)                                                                                                     |                       |
| addinteraction       | Add a gif/photo to an interaction (ex: slap,kiss,lick,hug)                                   | %addinteraction (interaction) (url,url)               |               |
| addstatus       | Add a playing status to Irene.                                   | %addstatus (status)               |               |
| botban       | Bans a user from Irene.                                   | %botban (user id)               |               |
| botunban       | UnBans a user from Irene.                                   | %botunban (user id)               |               |
| deletealias         | Remove alias from an idol/group. (Underscores are spaces)                                                               | %deletealias (alias) (ID of idol/group) ("idol" or "group")                                                                                                     |  removealias                      |
| deletegroup         | Deletes a group.                                                              | %deletegroup (group id)                                                                                                    | removegroup                     |
| deleteidol         | Deletes an idol.                                                              | %deleteidol (idol id)                                                                                             | removeidol                      |
| deleteidolfromgroup         | Deletes idol from group                                                              | %deleteidolfromgroup (idol id) (group id)                                                                                             | removeidolfromgroup                      |
| deleteinteraction       | Delete a url from an interaction                                   | %deleteinteraction (url,url)               |               |
| deletelink       | Removes a link from an idol.                                   | %deletelink (link)               |               |
| getstatuses             | Get all statuses of Irene.                                                   | %getstatuses                           |                |
| kill             | Kills the bot                                                  | %kill                           |               |
| moveto             | Moves a link to another idol. (Cannot be used for adding new links) | %moveto (idol id) (link)                           |               |
| repost             | Reposts a certain post from the DC APP to all channels.                                                  | %repost (post_number)                           |               |

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
| aliases          | Lists the aliases of idols that have one.                                           | %aliases                                                                                                       |                        |
| count            | Shows howmany times an idol has been called.                                       | %count (name)                                                                                                  |                        |
| countleaderboard | Shows leaderboards for how many times an idol has been called.                     | %clb                                                                                                           | highestcount, cb, clb |
| countgroup      | Shows how many images of a certain group there are.                               | %countgroup (group)                                                                                          |                        |
| countmember      | Shows how many images of a certain member there are.                               | %countmember (member/all)                                                                                          |                        |
| fullnames        | Lists the full names of idols the bot has photos of                                | %fullnames (page number)                                                                                                    |   fullname                     |
| getlinks         | Add links of photos to database from linked Archives                               | %getlinks                                                                                                      | ♥                      |
| groups           | Lists the groups of idols the bot has photos of                                    | %groups                                                                                                        |                        |
| members          | Lists the names of idols the bot has photos of                                     | %members (page number)                                                                                                      |    member                    |
| randomidol          | Sends a photo of a random idol.                                     | %%                                                                                                       |                   %     |
| scandrive        | Scan DriveIDs Table and update other tables.                                       | %scandrive (name=NULL) (member_id=0)                                                                           | ♥                      |
| scrapelink      | Connection to site + put html to html_page.txt                                     | %scrapelinks                                                                                                   | ♥                      |
| sendimages      | All idol photo commands from the server will post idol photos in a specific text channel. To undo, type it again.                                     | %sendimages #text-channel                                                                                                   | ★                      |
| sort             | Approve member links with a small sorting game.                                    | %sort -- checks next message                                                                                   | ♥                      |
| stopimages             | Stops Irene from posting/recognizing idol photos in a specific text channel. To undo, type it again.                                    | %stopimages #text-channel                                                                                  | ★                     |
| tenor            | Connection to tenor API // Sends Links of gifs to Database. Dashes (-) are spaces. | %tenor                                                                                                         | ♥                      |

#### Interactions:
| Command          | Description                                                    | Format                          | Aliases        |
|------------------|----------------------------------------------------------------|---------------------------------|----------------|
| hug          | Hug someone                              | %hug @user                       |                |
| kiss          | Kiss someone                              | %kiss @user                       |                |
| lick          | Lick someone                              | %lick @user                       |                |
| pat          | Pat someone                              | %pat @user                       |                |
| punch          | Punch someone                              | %punch @user                       |                |
| slap          | Slap someone                              | %slap @user                       |                |
| spit          | Spit on someone                              | %spit @user                       |                |


#### Logging: ★★★  
| Command      | Description                                                                                          | Format        |
|--------------|------------------------------------------------------------------------------------------------------|---------------|
| logadd       | Start logging a text channel.                                                              | %logadd #text-channel       |
| logremove    | Stop logging a text channel.                                                               | %logremove #text-channel    |
| sendall      | Toggles sending all messages to log channel. If turned off, it only sends edited & deleted messages. | %sendall      |
| startlogging | Start sending log messages in the current server and channel.                                        | %startlogging |
| stoplogging  | Stop sending log messages in the current server.                                                     | %stoplogging  |

#### Miscellaneous:
| Command          | Description                                                    | Format                          | Aliases        |
|------------------|----------------------------------------------------------------|---------------------------------|----------------|
| _8ball           | Asks the 8ball a question.                                     | %8ball (Question)               | 8ball,8        |
| addpatreon         | Adds a patreon.                           | %addpatreon (userid,userid,userid)             | ♥              |
| announce         | Sends a bot message to text channels                           | %announce (message)             | ♥              |
| botinfo       | Get information about the bot.                                   | %botinfo               |               |
| checkprefix       | Check the current prefix using the default prefix.                                   | %checkprefix               |               |
| clearnword       | Clear A User's Nword Counter                                   | %clearnword @user               | ♥              |
| flip             | Flips a Coin                                                   | %flip                           |                |
| invite           | Invite Link for Irene                                          | %invite                         |                |
| logging          | Start logging this channel/Stop logging this channel           | %logging (start/stop)           | ♥              |
| nword            | Checks how many times a user has said the N Word               | %nword @user                    |                |
| nwordleaderboard | Shows leaderboards for how many times the nword has been said. | %nwl                            | nwl            |
| patreon             | Displays Patreon Information.                                       | %patreon                           |            |
| ping             | Shows Latency to Discord                                       | %ping                           | pong           |
| random           | Choose a random number from a range (a,b)                      | %random a b [Ex: %random 1 100] | r,rand,randint |
| removepatreon         | Removes a patreon.                           | %removepatreon (userid,userid,userid)             | ♥              |
| report          | Report an issue with Irene.                                    | %report (issue)              |               |
| send              | Send a message to a text channel.                                             | %send (channelid) (message)                  | ♥              |
| servercount      | Shows how many servers Irene is on.                            | %servercount                    |                |
| serverinfo      | View information about the current server.                            | %serverinfo                   |                |
| servers          | Displays which servers Irene is in.  | %servers                        | ♥              |
| speak            | Owner to Bot TTS                                               | %speak (message)                | ♥              |
| suggest          | Suggest a feature for Irene                                    | %suggest (feature)              |               |
| support          | Support Discord Server for Irene                               | %support                        |                |
| translate          | Translate between languages using Papago                              | %translate English Korean this is a test phrase.                       |                |


#### Moderator: ★★★
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| addemoji         | Adds an emoji to the server. (Manage Messages & Emojis)                                                                                                        | %addemoji (url) (emoji_name)    |               |
| ban              | Ban A User (Ban Members)                                                                                                                           | %ban @user                      |               |
| clear            | Prune Messages (LIMIT 1000) (Manage Messages)                                                                                                                      | %clear (amount)                 |  prune        |
| kick             | Kick A User. (Kick Members)                                                                                                                          | %kick @user                     |               |
| say              | Make Irene say a message. (Manage Messages)                                          | %say (message)                  |               |
| setprefix      | Set the server prefix. If prefix was forgotten, type this command with the default prefix. (Manage Messages) | %setprefix $         |          | 
| tempchannel      | Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel. (Manage Messages)| %tempchannel [delay=-1]         | temp         |
| unban            | UnBan A User (Ban Members)                                                                                                                      | %unban @user                    |               |
 
#### Music:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| join         | Joins a voice channel                              | %join    |               |
| move         | Makes a song the next song to play without skipping the current song.                              | %move (song number)    | skipto              |
| pause         | Pauses currently playing song                                                                         | %pause    |               |
| play         | Plays audio to a voice channel.                                               | %play (title/url)    |               |
| queue         | Shows Current Queue                                              | %queue (page number)    |   list, q            |
| remove         | Remove a song from the queue.                                                 | %remove (song number)    |            |
| resume         | Resumes a paused song                                                 | %resume    |      unpause         |
| shuffle         | Shuffles the playlist.                                                        | %shuffle    |               |
| skip         | Skips the current song.                                                                      | %skip    |               |
| stop         | Disconnects from voice channel and resets queue.                                                   | %stop    |  leave             |
| volume         | Changes the player's volume - Songs default to 10.                                                 | %volume (1-100)    |               |
 
#### Profile:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| avatar         | Display a user's avatar.                                                                                                         | %avatar @user    |               |
| profile         | Display a user's profile.                                                                                                         | %profile @user    |               |


#### LastFM:
| Command          | Description                                                                        | Format                                                                                                         | Aliases                |
|------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------|
| fm          | Get information about a Last FM account by a discord user or a Last FM username.   | %fm (username or @user)             |                        |
| recenttracks            | Get the recent tracks of a Last FM Account by a discord user or a Last FM username | %recenttracks (username or @user)         |  rt, recents                      |
| recent            | Get the last listened track of a Last FM Account by a discord user or a Last FM username        | %recent (username or @user)            |                        |
| topalbums            | See the top albums of a Last FM Account by a discord user or a Last FM username                                       | %topalbums (username or @user)       |   tal                     |
| topartists            | See the top artists of a Last FM Account by a discord user or a Last FM username.                                       | %topartists (username or @user)  |  ta                      |
| toptracks            | See the top tracks of a Last FM Account by a discord user or a Last FM username                                       | %toptracks (username or @user)  | tt                        |


#### Testing ♥♥♥
| Command          | Description                                                                                                                          | Format                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| testcommands      | Tests all commands (Use this while in a voice channel)                                                                                                            | %testcommands               |

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


## GROUPS / IDOLS

**You can scroll to the right.**  

| (G)I-DLE    | 4Minute    | After School | AOA         | APink        | APRIL       | B2ST      | BLACKPINK    | BTS         | Cherry Bullet | CLC         | DIA         | DreamCatcher | EVERGLOW    | ELRIS       | EXID        | f(x)        | fromis9      | GFRIEND     | Girl's Day  | Gugudan     | IOI          | ITZY         | IZONE        | Kara       | Laboum      | LOONA        | Lovelyz     | MAMAMOO      | MINX         | Miss A       | MyDoll Girls | Oh My Girl  | Orange Caramel | Pentagon  | Pink Fantasy | Pristin     | Red Velvet  | Rocket Punch | SNH48      | SNSD        | SOLO         | T-ara      | THE NINE      | Triple H  | Trouble Maker | TWICE         | Weki Meki   | WJSN         | Wonder Girls |
|-------------|------------|--------------|-------------|--------------|-------------|-----------|--------------|-------------|---------------|-------------|-------------|--------------|-------------|-------------|-------------|-------------|--------------|-------------|-------------|-------------|--------------|--------------|--------------|------------|-------------|--------------|-------------|--------------|--------------|--------------|--------------|-------------|----------------|-----------|--------------|-------------|-------------|--------------|------------|-------------|--------------|------------|---------------|-----------|---------------|---------------|-------------|--------------|--------------|
| Miyeon      | Jihyun     | E-Young      | Jimin       | Chorong      | Chaekyung   | Hyunseung | Rose         | Jimin       | Kokoro        | Seungyeon   | Chaeyeon    | Handong      | Aisha       | Bella       | Hyerin      | Victoria    | Saerom       | Eunha       | Yura        | Sejeong     | Kyulkyung    | Chaeryeong   | Yuri         | Gyuri      | Yujeong     | Olivia Hye   | Baby Soul   | Moonbyul     | Yoohyeon     | Suzy         | Yumin        | Seunghee    | Nana           | EDawn     | SangA        | Kyulkyung   | Irene       | Yunkyung     | Kiki       | Tiffany     | Kyulkyung    | Hyomin     | Zhao Xiaotang | EDawn     | HyunA         | Dahyun        | Yoojung     | Eunseo       | Yeeun        |
| Yuqi        | Gayoon     | Nana         | Yuna        | Bomi         | Chaewon     | Doojoon   | Jisoo        |             | Haeyoon       | Seunghee    | Jooeun      | Gahyeon      | E:U         | Hyeseong    | Solji       | Amber       | Nagyung      | Umji        | Hyeri       | Mina        | Sohye        | Yuna         | Wonyoung     | Seungyeon  | Soyeon      | Heejin       | Jiae        | Solar        | Siyeon       |              | Haruhi       | Jiho        | Raina          | Jinho     | Aini         | Nayoung     | Wendy       | Yeonhee      |            | Hyoyeon     | Jiyoon       |            | Liu Yuxin     | HyunA     | Hyunseung     | Momo          | Doyeon      | Bona         | HyunA        |
| Soyeon      | Jiyoon     | Raina        | Hyejeong    | Eunji        | Naeun       | Junhyung  | Lisa         |             | Yuju          | Yujin       | Huihyeon    | Yoohyeon     | Mia         | Karin       | LE          | Luna        | Gyuri        | Sowon       | Minah       |             | Sejeong      | Yeji         | Chaewon      | Youngji    | ZN          | Hyunjin      | Jisoo       | Wheein       | JiU          |              | Yugyung      | Binnie      | Lizzy          | Hui       | Daewang      |             | Seulgi      | Suyun        |            | Yuri        | Yeeun        |            | Yu Shuxin     | Hui       |               | Tzuyu         |             | Soobin       | Yubin        |
| Minnie      | Sohyun     | Kaeun        | Seolhyun    | Naeun        | Jinsol      | Yoseob    | Jennie       |             | Bora          | Sorn        | Eunice      | Siyeon       | Onda        | Sohee       | Hani        | Krystal     | Chaeyoung    | SinB        | Sojin       |             | Yoojung      | Lia          | Yena         | Hara       | Haein       | Haseul       | Mijoo       | Hwasa        | Dami         |              | Gahyun       | Mimi        |                | Hongseok  | Yechan       |             | Joy         | Sohee        |            | Sooyoung    | EDawn        |            | Yu Yan        |           |               | Chaeyoung     |             | Cheng Xiao   | Sunmi        |
| Soojin      | HyunA      | Lizzy        | Choa        | Namjoo       | Rachel      | Kikwang   |              |             | Jiwon         | Yeeun       | Yebin       | JiU          | Sihyeon     | Yukyung     | Jeonghwa    | Sulli       | Jiwon        | Yerin       |             |             | Doyeon       | Ryujin       | Sakura       |            | Solbin      | Yeojin       | Jin         |              | SuA          |              | Heesun       | Yooa        |                | Shinwon   | SeeA         |             | Yeri        | Juri         |            | Yoona       | Jennie       |            | Xie Keyin     |           |               | Mina          |             | EXY          | Hyelim       |
| Shuhua      |            | UEE          | Mina        | Hayoung      | Yena        | Dongwoon  |              |             | Remi          | Elkie       | Eunchae     | Dami         | Yiren       |             |             |             | Jiheon       | Yuju        |             |             | Chaeyeon     |              | Hitomi       |            | Yulhee      | Vivi         | Sujeong     |              |              |              | Momoka       | Arin        |                | Yeo One   | Yubeen       |             |             | Dahyun       |            | Seohyun     | Suzy         |            | An Qi         |           |               | Jihyo         |             | Seola        |              |
|             |            | Jungah       | Chanmi      |              |             |           |              |             | Chaerin       | Eunbin      | Somyi       | SuA          |             |             |             |             | Seoyeon      |             |             |             | Yeonjung     |              | Hyewon       |            |             | Kim Lip      | Yein        |              |              |              | Miu          | JinE        |                | Yanan     | Harin        |             |             |              |            | Jessica     | Somi         |            | Kong Xueer    |           |               | Sana          |             | Xuan Yi      |              |
|             |            | Jooyeon      |             |              |             |           |              |             | May           |             |             |              |             |             |             |             | Jisun        |             |             |             | Nayoung      |              | Yujin        |            |             | Jinsoul      | Kei         |              |              |              | Miku         | Hyojung     |                | Yuto      | Arang        |             |             |              |            | Taeyeon     | Chungha      |            | Lu Keran      |           |               | Jeongyeon     |             | Yeonjung     |              |
|             |            | So Young     |             |              |             |           |              |             | Mirae         |             |             |              |             |             |             |             | Hayoung      |             |             |             | Mina         |              | Minju        |            |             | Choerry      |             |              |              |              | Eseul        |             |                | Kino      | Heesun       |             |             |              |            | Sunny       | IU           |            | Kiki          |           |               | Nayeon        |             | Luda         |              |
|             |            | Bekah        |             |              |             |           |              |             | Linlin        |             |             |              |             |             |             |             |              |             |             |             | Somi         |              | Nako         |            |             | Yves         |             |              |              |              |              |             |                | Wooseok   |              |             |             |              |            |             | BIBI         |            |               |           |               |               |             | Dawon        |              |
|             |            | Kahi         |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             | Chungha      |              | Eunbi        |            |             | Chuu         |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Tiffany      |            |               |           |               |               |             | Mei Qi       |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              | Chaeyeon     |            |             | Gowon        |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Hyoyeon      |            |               |           |               |               |             | Yeoreum      |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Yuri         |            |               |           |               |               |             | Dayoung      |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Sooyoung     |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Yoona        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Seohyun      |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Jessica      |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Taeyeon      |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Sunny        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Amber        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Luna         |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Sulli        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | HyunA        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Yubin        |            |               |           |               |               |             |              |              |
|             |            |              |             |              |             |           |              |             |               |             |             |              |             |             |             |             |              |             |             |             |              |              |              |            |             |              |             |              |              |              |              |             |                |           |              |             |             |              |            |             | Sunmi        |            |               |           |               |               |             |              |              |
| 6282 Photos | 223 Photos | 341 Photos   | 6422 Photos | 12143 Photos | 6261 Photos | 35 Photos | 64950 Photos | 8453 Photos | 10117 Photos  | 7669 Photos | 1246 Photos | 14542 Photos | 6307 Photos | 3955 Photos | 4148 Photos | 5062 Photos | 34283 Photos | 6120 Photos | 2457 Photos | 2097 Photos | 12597 Photos | 23991 Photos | 20720 Photos | 276 Photos | 3301 Photos | 71414 Photos | 8358 Photos | 20540 Photos | 14103 Photos | 21699 Photos | 1190 Photos  | 8892 Photos | 51 Photos      | 20 Photos | 14579 Photos | 2109 Photos | 7970 Photos | 6058 Photos  | 535 Photos | 4399 Photos | 33913 Photos | 351 Photos | 583 Photos    | 87 Photos | 88 Photos     | 453898 Photos | 2097 Photos | 14801 Photos | 493 Photos   |