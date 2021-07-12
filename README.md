# [IreneBot V1.04.2](https://discordapp.com/oauth2/authorize?client_id=520369375325454371&scope=bot&permissions=1609956823)

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
| blackjack         | Start a game of BlackJack                                                                             | %blackjack (amount)                  | bj      |
| stopbj           | End your current blackjack game                                                                                 | %stopbj                             |       |
| joingame          | Join a game                                                                                           | %joingame (@user) (bid)             | jg      |
| rules          | View the rules of BlackJack.                                                                                           | %rules             |       |

#### BotMod: 😇😇😇  
| Command           | Description                                                                                           | Format                               | Aliases |
|-------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|---------|
| addidoltogroup         | Adds idol to group.                                                              | %addidoltogroup (idol id) (group id)                                                                                                     |                       |
| addinteraction       | Add a gif/photo to an interaction (ex: slap,kiss,lick,hug)                                   | %addinteraction (interaction) (url,url)               |               |
| addstatus       | Add a playing status to Irene.                                   | %addstatus (status)               |               |
| botban       | Bans a user from Irene.                                   | %botban (user id)               |               |
| botunban       | UnBans a user from Irene.                                   | %botunban (user id)               |               |
| botwarn   | Warns a user from Irene's DMs                                   | %botwarn (user id) (reason)               |               |
| closedm       | Closes a DM either by the User ID or by the current channel.                                   | %closedm (user id)               |               |
| createdm       | Create a DM with a user with the bot as a middle man. One user per mod channel.                                   | %createdm (user id)               |               |
| deletegroup         | Deletes a group.                                                              | %deletegroup (group id)                                                                                                    | removegroup                     |
| deleteidol         | Deletes an idol.                                                              | %deleteidol (idol id)                                                                                             | removeidol                      |
| deleteidolfromgroup         | Deletes idol from group                                                              | %deleteidolfromgroup (idol id) (group id)                                                                                             | removeidolfromgroup                      |
| deleteinteraction       | Delete a url from an interaction                                   | %deleteinteraction (url,url)               |               |
| fixlinks        | Fix thumbnails and banners of idols and groups and put them on the host. | %fixlinks |               |
| getstatuses             | Get all statuses of Irene.                                                   | %getstatuses                           |                |
| kill             | Kills the bot                                                  | %kill                           |               |
| killapi             | Restarts the API                                                  | %killapi                           |               |
| maintenance             | Enable/Disable Maintenance Mode. | %maintenance (reason)                          |               |
| mergeidol | Merges a duplicate Idol with it's original | %mergeidol (original idol id) (duplicate idol id) | |
| mergegroup | Merges a duplicate Group with it's original | %mergegroup (original group id) (duplicate group id) | |
| moveto | Moves an image to another idol. | %moveto (idol id) (url) | |
| removestatus             | Remove a status based on it's index. The index can be found using %getstatuses | %removestatus (status index)                           |               |
| weverseauth      | Updates Weverse Authentication Token without restarting bot. Only use this in DMs or a private channel for security purposes. | %weverseauth (token)                           |               |

#### BlockingManager: ♥♥♥
| Command           | Description                                                                                           | Format                               | Aliases |
|-------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|---------|
| bmon start         | Starts the blocking manager.                                                              | %bmon start                                                                                                     |                       |
| bmon stop       | Stops the blocking manager.                                   | %bmon stop               |               |

#### BiasGame:
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| biasgame | Start a bias game in the current channel. The host of the game can use `stopbg` to stop playing. | %biasgame (male/female/all) (bracket size (4,8,16,32)) | bg |
| stopbg | Force-end a bias game if you are a moderator or host of the game. This command is meant for any issues or if a game happens to be stuck. | %stopbg | ★/Host |
| listbg | List a user's bias game leaderboards. | %listbg (user) | |

#### Currency:
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| balance     | View balance of yourself or a user   | %balance (@user)       | b,bal,$           |
| beg         | Beg a homeless man for money         | %beg                   |                   |
| bet         | Bet your money                       | %bet (amount)          |                   |
| daily       | Gives 100 Dollars Every 24 Hours     | %daily                 |                   |
| give        | Give a user money                    | %give (@user) (amount) |                   |
| leaderboard | Shows Top 10 Users Server/Global Wide  | %leaderboard (server/global)           | leaderboards, lb      |
| rob         | Rob a user - Max Value = 1000        | %rob @user             |                   |
| rps         | Play Rock Paper Scissors for Money   | %rps (r/p/s)(amount)   | rockpaperscissors |
| upgrade    | Upgrade a command to the next level with your money. | %upgrade rob/daily/beg              | levelup                  |

#### CustomCommands:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| createcommand | Create a custom command. | %createcommand (command name) (message) | addcommand, ★ |
| deletecommand | Delete a custom command.  | %deletecommand (command name) | removecommand, ★ |
| listcommands | List all the custom commands for the current server. | %listcommands | |
  
#### GroupMembers:
| Command          | Description                                                                        | Format                                                                                                         | Aliases                |
|------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------|
| addidol         | Adds an idol using the syntax from https://irenebot.com/addidol.html | %addidol (json)                                                                                                      |                      |
| addgroup         | Adds a group using the syntax from https://irenebot.com/addgroup.html | %addgroup (json)                                                                                                      |                       |
| aliases          | Lists the aliases of idols or groups that have one. Underscores are spaces and commas are to split idol or group names                                        | %aliases (name of idol or group) [page number] ex: %aliases irene,seulgi,red_velvet                                                                                                       |                        |
| card | Displays an Idol/Group's profile card. | %card (Idol/Group Name/ID) | |
| count            | Shows howmany times an idol has been called.                                       | %count (name)                                                                                                  |                        |
| countleaderboard | Shows leaderboards for how many times an idol has been called.                     | %clb                                                                                                           | highestcount, cb, clb |
| countgroup      | Shows how many images of a certain group there are.                               | %countgroup (group)                                                                                          |                        |
| countmember      | Shows how many images of a certain member there are.                               | %countmember (member/all)                                                                                          |                        |
| fullnames        | Lists the full names of idols the bot has photos of                                | %fullnames (page number/group names)                                                                                                    |   fullname                     |
| groups           | Lists the groups of idols the bot has photos of                                    | %groups                                                                                                        |                        |
| members          | Lists the names of idols the bot has photos of                                     | %members (page number/group names)                                                                                                      |    member                    |
| randomidol          | Sends a photo of a random idol.                                     | %%                                                                                                       |                   %     |
| sendidol      | Request for an idol photo to be sent to a certain text channel every 12 hours. Not specifying an idol will remove all of them. You may add or remove by putting in an idol id. Requires Manage Messages  | %sendidol [idol_id] [#text-channel]                                                                                                   | ★                      |
| sendimages      | All idol photo commands from the server will post idol photos in a specific text channel. To undo, type it again.                                     | %sendimages #text-channel                                                                                                   | ★                      |
| stopimages             | Stops Irene from posting/recognizing idol photos in a specific text channel. To undo, type it again.                                    | %stopimages #text-channel                                                                                  | ★                     |

#### GuessingGame:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| guessinggame | Start an idol guessing game in the current channel. The host of the game can use `stop` to end the game or `skip` to skip the current round without affecting the round number. | %guessinggame (Male/Female/All) (easy/medium/hard) (# of rounds - default 20) (timeout for each round - default 20s) | gg |
| groupguessinggame | Start a group guessing game in the current channel. The host of the game can use `stop` to end the game or `skip` to skip the current round without affecting the round number. | %groupguessinggame (Male/Female/All) (easy/medium/hard) (# of rounds - default 20) (timeout for each round - default 20s) | ggg, groupgg |
| ggfilter | Add a filter for your guessing game. Only the groups you select will appear on the guessing game. Use the command with no group ids to enable/disable the filter. Filtered idols do not count for a real score. | %ggfilter [group_id_one, group_id_two, ...] | |
| ggfilteredlist | View the current groups you currently have filtered. | %ggfilteredlist | ggfilterlist, filterlist |
| ggleaderboard | Shows leaderboards for guessing game. | %ggleaderboard (easy/medium/hard) (server/global)| ggl, gglb |
| stopgg | Force-end a guessing game if you are a moderator or host of the game. This command is meant for any issues or if a game happens to be stuck. Must be game host or access to manage messages. | %stopgg | ★/Host|

#### Interactions:
| Command          | Description                                                    | Format                          | Aliases        |
|------------------|----------------------------------------------------------------|---------------------------------|----------------|
| choke         | Choke someone                              | %choke @user                       |                |
| cuddle         | Cuddle someone                              | %cuddle @user                       |                |
| hug          | Hug someone                              | %hug @user                       |                |
| kiss          | Kiss someone                              | %kiss @user                       |                |
| lick          | Lick someone                              | %lick @user                       |                |
| pat          | Pat someone                              | %pat @user                       |                |
| punch          | Punch someone                              | %punch @user                       |                |
| pullhair         | Pull the hair of someone                              | %pullhair @user                       |                |
| slap          | Slap someone                              | %slap @user                       |                |
| spit          | Spit on someone                              | %spit @user                       |                |
| stab          | Stab someone                              | %stab @user                       |                |
| stepon          | Step on someone                              | %stepon @user                       |                |


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
| 8ball           | Asks the 8ball a question.                                     | %8ball (Question)               | 8        |
| addnoti         | Receive a DM whenever a phrase or word is said in the current server. | %addnoti (phrase/word)    |               |
| botinfo       | Get information about the bot.                                   | %botinfo               |               |
| checkprefix       | Check the current prefix using the default prefix.                                   | %checkprefix               |               |
| choose | Choose between a selection of options. Underscores are spaces between words. Spaces separate choices. | %choose option1 option2 | |
| displayemoji | Display an Emoji | %displayemoji :emoji | |
| flip             | Flips a Coin                                                   | %flip                           |                |
| invite           | Invite Link for Irene                                          | %invite                         |                |
| listnoti          | list all your notification phrases that exist in the current server.| %listnoti     |               |
| patreon             | Displays Patreon Information.                                       | %patreon                           |   patron         |
| ping             | Shows Latency to Discord                                       | %ping                           | pong           |
| random           | Choose a random number from a range (a,b)                      | %random a b [Ex: %random 1 100] | r,rand,randint |
| removenoti         | Remove a phrase/word when it said in the current server.| %removenoti (phrase/word)             | deletenoti              |
| report          | Report an issue with Irene.                                    | %report (issue)              |               |
| servercount      | Shows how many servers Irene is on.                            | %servercount                    |                |
| serverinfo      | View information about the current server.                            | %serverinfo                   |                |
| setlanguage          | Changes language of Irene. Available Choices: en_us  | %setlanguage (language choice)                         |               |
| shard          | Gives shard info about the current server.  | %shard | shardinfo              |
| stopgames          | End all games that you are hosting or that may exist in the text channel.  | %stopgames |  stopgame, endgame, endgames             |
| suggest          | Suggest a feature for Irene                                    | %suggest (feature)              |               |
| support          | Support Discord Server for Irene                               | %support                        |                |
| translate          | Translate between languages using Papago                              | %translate English Korean this is a test phrase.                       |   t, trans             |
| vote          | Link to Voting for Irene on Top.gg | %vote                       |                |

#### Moderator: ★★★
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| addalias         | Adds an alias to an idol/group. (Underscores are spaces)                                                              | %addalias (alias) (ID of idol/group) ("idol" or "group")                                                                                                      |                       |
| addemoji         | Adds an emoji to the server. Several emojis can be added if split with a comma. Emoji Name is optional. (Manage Messages & Emojis)                                                                                                        | %addemoji (emoji,emoji,emoji,url) (emoji_name)    |    yoink           |
| ban              | Ban A User (Ban Members)                                                                                                                           | %ban @user                      |               |
| clear            | Prune Messages (LIMIT 1000) (Manage Messages)                                                                                                                      | %clear (amount)                 |  prune        |
| deletealias         | Remove alias from an idol/group. (Underscores are spaces)                                                               | %deletealias (alias) (ID of idol/group) ("idol" or "group")                                                                                                     |  removealias                      |
| disableinteraction            | Disable an interaction on your server. Redo to enable again (Manage Messages)                                                                                                                      | %disableinteraction (interaction)                 |  |
| kick             | Kick A User. (Kick Members)                                                                                                                          | %kick @user                     |               |
| mute             | Mute A User. (Manage Messages & Manage Roles)                                                                                                                          | %mute @user (reason)                     |               |
| say              | Make Irene say a message. (Manage Messages)                                          | %say #[text-channel] (message)                  |               |
| sayembed              | Make Irene say an embed message. (Manage Messages)                                          | %sayembed #text-channel (json formatted message from https://embedbuilder.nadekobot.me/)                  |               |
| setprefix      | Set the server prefix. If prefix was forgotten, type this command with the default prefix. (Manage Messages) | %setprefix $         |          | 
| tempchannel      | Makes Current Channel a temporary channel deleting messages after a certain time period (greater than 1 minute). If delay is -1, it will remove the channel. (Manage Messages)| %tempchannel [delay=-1]         | temp         |
| togglegames      | Choose to enable/disable games in a text channel. (Manage Messages)| %togglegames [#channel]         |          |
| unban            | UnBan A User (Ban Members)                                                                                                                      | %unban @user                    |               |
| unmute            | UnMute A User (Manage Messages & Manage Roles)                                                                                                                      | %unmute @user                   |               |
| welcome            | Set a welcome message or disable welcome in the current channel. Use %user where they should be mentioned. Use %guild_name if the server name should be added. (Manage Messages)  | %welcome (Welcome %user to %guild_name!)                    |               |
| welcomerole            | The role to give a user when they first join the server. Use command without role to delete the welcome role set to the guild. (Manage Messages)  | %welcomerole @role                    |               |

#### Music:  
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| join         | Joins a voice channel                              | %join    |               |
| move         | Makes a song the next song to play without skipping the current song.                              | %move (song number)    | skipto              |
| pause         | Pauses currently playing song                                                                         | %pause    |               |
| play         | Plays audio to a voice channel.                                               | %play (title/url)    |      p         |
| queue         | Shows Current Queue                                              | %queue (page number)    |   list, q            |
| remove         | Remove a song from the queue.                                                 | %remove (song number)    |            |
| resume         | Resumes a paused song                                                 | %resume    |      unpause         |
| shuffle         | Shuffles the playlist.                                                        | %shuffle    |               |
| skip         | Skips the current song.                                                                      | %skip    |               |
| stop         | Disconnects from voice channel and resets queue.                                                   | %stop    |  leave             |
| volume         | Changes the player's volume - Songs default to 10.                                                 | %volume (1-100)    |               |
| lyrics        | Grab the lyrics of a song   | %lyrics (song) |

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
| recent            | Get the last listened track of a Last FM Account by a discord user or a Last FM username        | %recent (username or @user)            |  np                      |
| topalbums            | See the top albums of a Last FM Account by a discord user or a Last FM username                                       | %topalbums (username or @user)       |   tal                     |
| topartists            | See the top artists of a Last FM Account by a discord user or a Last FM username.                                       | %topartists (username or @user)  |  ta                      |
| toptracks            | See the top tracks of a Last FM Account by a discord user or a Last FM username                                       | %toptracks (username or @user)  | tt                        |
| setfm            | Attach a LastFM username to your discord account.                                       | %setfm (LastFM username)  |                         |


#### Wolfram: 

| Command          | Description                                                                                                                          | Format                                       |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| w           | Send a request to Wolfram.                                                                                                            | %wolfram (query)                               |


#### Twitter: ♥♥♥
| Command          | Description                                                                                                                          | Format                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| deletetweet      | Delete a Tweet by it's ID                                                                                                            | %deletetweet (id)               |
| recenttweets     | Show Most Recents Tweets                                                                                                             | %recenttweets (amount)          |
| tweet            | Tweets a status update on Twitter                                                                                                    | %tweet (status)                 |

#### UnScramble:
| Command          | Description                                                                                                                          | Format                          | Aliases        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|----------------|
| unscramble | Start an idol unscrambing game in the current channel. The host of the game can use `stop` to end the game | %unscramble (Male/Female/All) (easy/medium/hard) (# of rounds - default 20) (timeout for each round - default 20s) | us |
| usleaderboard | Shows leaderboards for unscramble game. | %uslb (easy/medium/hard) (server/global)| usl, uslb |
| stopus | Force-end an unscramble game if you are a moderator or host of the game. This command is meant for any issues or if a game happens to be stuck. Must be game host or access to manage messages. | %stopus | ★/Host|


#### Youtube: ♥♥♥

| Command          | Description                                                                                                                          | Format                                       |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| addurl           | Add url to youtube videos                                                                                                            | %addurl (link)                               |
| removeurl        | Remove url from youtube videos                                                                                                       | %removeurl (link)                            |
| scrapeyoutube    | Scrape the views from the Youtube Videos in the DB                                                                                                          | %scrapeyoutube                               |
| startloop        | Starts scraping youtube videos.                                                                                                      | %startloop (seconds until it starts looping) |
| stoploop         | Stops scraping youtube videos                                                                                                        | %stoploop                                    |


#### Weverse (This is now disabled for normal users, but join the support server and follow the announcement channels to your text channels):
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| weverseupdates | Receive Weverse Updates of a specific Weverse community in the current text channel. Use again to disable for a specific community. Available Communities -> [TXT, BTS, GFRIEND, SEVENTEEN, ENHYPEN, NU'EST, CL, P1Harmony, Weeekly, SUNMI, HENRY, Dreamcatcher, CherryBullet, MIRAE, TREASURE, LETTEAMOR, EVERGLOW, FTISLAND, woo!ah!, IKON, JUST B, BLACKPINK] | %weverseupdates (community name) [role to notify] | weverse |
| disablecomments | Disable updates for comments on a community. | %disablecomments (community name) |  |
| disablemedia | Disable updates for media on a community. | %disablecomments (community name) |  |


#### SelfAssignRoles:
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| addrole | Add a role to be self-assignable. | %addrole (@role) (custom role name) |  |
| listroles | List all the self-assignable roles in a server. | %listroles |  |
| removerole | Remove a self-assignable role based on the role name given. | %removerole (custom role name) |  |
| sendrolemessage | Sends the default role message in the current channel. Is not needed for the roles to work. | %sendrolemessage |  |
| setrolechannel | Set the channel for self-assignable roles to be used in. This will automatically delete future messages. Use sendrolemessage before using this command.| %setrolechannel #text-channel |  |

#### Reminder:
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| gettimezone | Display a user's current timezone and local time. | %gettimezone @user | gettz, time |
| listreminders | Lists out all of your reminders. | %listreminders | listreminds, reminders, reminds |
| remindme | Create a reminder to do a task at a certain time. | %remindme to ______ at 9PM or %remindme to ____ in 6hrs 30mins  | remind |
| removereminder | Remove one of your reminders. | %removereminder (reminder index) | removeremind |
| settimezone | Set your local timezone with a timezone abbreviation and country code. | %settimezone (timezone name ex: PST) (country code ex: US) | settz |

#### Twitch: ★★★
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| addtwitch | Adds a Twitch username to keep track of. Maximum 2 Twitch channels per server. | %addtwitch (twitch username) | |
| listtwitch | List the twitch channels the server follows.| %listtwitch | |
| removetwitch | Removes a twitch username that is being kept track of. | %removetwitch (twitch username) | |
| settwitchchannel | Set the discord channel that the twitch announcements will be posted on. | %settwitchchannel [#text channel] | |
| settwitchrole | Set the discord role that will be mentioned on twitch announcements. If a discord role is set, everyone will not be mentioned. Use the command without a role to mention everyone. |%settwitchrole [@role] | |

#### BotOwner: ♥♥♥
| Command               | Description                                                                                           | Format                               |
|-----------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------|
| addcards          | Fill The CardValues Table with Cards                                                                  | %addcards                            |       |
| addpatreon         | Adds a patreon.                           | %addpatreon (userid,userid,userid)             |               |
| approve       | Approve a query id for an unregistered group or idol. | %approve (query id) ('idol' or 'group') |    |
| generateplayingcards       | Generate custom playing cards with idol avatars. | %generateplayingcards  |               |
| removepatreon         | Removes a patreon.                           | %removepatreon (userid,userid,userid)             |               |
| resetcache          | Reset the cache.  | %resetcache                        |              |
| scandrive        | Scan DriveIDs Table and update other tables.                                       | %scandrive (name=NULL) (member_id=0)                                                                           |                       |
| send              | Send a message to a text channel.                                             | %send (channelid) (message)                  |               |
| speak            | Owner to Bot TTS                                               | %speak (message)                |              |
| uploadfromhost            | Toggles whether images are uploaded from host or not.            | %uploadfromhost |              |

#### Vlive: ★★★
| Command     | Description                          | Format                 | Aliases           |
|-------------|--------------------------------------|------------------------|-------------------|
| vliveupdates code | Follow a VLIVE channel based on the channel code. | %vliveupdates code (vlive channel code) [role id] | vlive code |
| vliveupdates group | Follow a VLIVE channel belonging to a Group ID If they have one. | %vliveupdates group (group id) [role id] | vlive group |
| vliveupdates idol | Follow a VLIVE channel belonging to an Idol ID If they have one. | %vliveupdates idol (idol id) [role id] | vlive idol |
| vliveupdates list | Lists the VLIVE channels currently being followed in the text channel. | %vliveupdates list | vlive list |

#### DataMod: 😇😇😇
| Command          | Description                                                                        | Format                                                                                                         | Aliases                |
|------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------|
| addidol         | Adds an idol using the syntax from https://irenebot.com/addidol.html | %addidol (json)                                                                                                      |                      |
| addgroup         | Adds a group using the syntax from https://irenebot.com/addgroup.html | %addgroup (json)                                                                                                      |                       |
