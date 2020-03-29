
# [IreneBot](https://discordapp.com/oauth2/authorize?client_id=520369375325454371&scope=bot&permissions=8)

## Irene Bot for Discord in Python V1.004

Upon signing up for the Google Drive API, make sure to put the credentials.json in the main folder.  
[ https://developers.google.com/drive ]  

When first getting the bot to work, make sure to use the %upload command to get the Google Drive API to properly work. Or you can just remove it.    
You will need to sign into your Google Account when it prompts you as a one time authorization.  
ImageUploader was not coded with aiohttp, so there will be blockage from other commands when these commands are in use.  
There are instructions left in quickstart.py for first time running. Make sure to follow the comments.  

Command Prefix is in run.py and is currently set to '%' by default.

Music will not run as an executable (it will not be able to find a module properly). It can run from an IDE just fine.

♥ - Requires Bot Owner  
♥♥♥ -- Entire Section Requires Bot Owner  
★ - Requires Guild Permissions  
★★★ - Entire Section Requires Permissions
## FILES

<table>

<tbody>

<tr>

<th>File</th>

<th>Purpose</th>

</tr>

<tr>

<td>run.exe</td>

<td>Main Run File - Startup</td>

</tr>

<tr>

<td>run.py</td>

<td>Main Program/Bot - Startup</td>

</tr>

<tr>

<td>Cards/..</td>

<td>All Cards In A Deck</td>

</tr>

<tr>

<td>music/..</td>

<td>Local Music Files</td>

</tr>

<tr>

<td>module/BlackJack.py</td>

<td>A 1v1 game of blackjack</td>

</tr>

<tr>

<td>module/Currency.py</td>

<td>Games that involve an economy</td>

</tr>

<tr>

<td>modules/DreamCatcher.py</td>

<td>Send Photos from the DC App to a certain text channel based on a loop.</td>

</tr>

<tr>

<td>module/ImageUploader.py</td>

<td>Commands for downloading photos from a text channel and uploading them to google drive.</td>

</tr>

<tr>

<td>module/Miscellaneous.py</td>

<td>Commands I didn't feel like making a section for</td>

</tr>

<tr>

<td>module/Music.py</td>

<td>Commands for Music</td>

</tr>

<tr>

<td>module/Twitter2.py</td>

<td>Commands for Twitter</td>

</tr>

<tr>

<td>module/currency.db</td>

<td>Database that includes the economy [Also has channel ids].</td>

</tr>

<tr>

<td>module/groupmembers.db</td>

<td>Contains information on idols aside from DreamCatcher</td>

</tr>

<tr>

<td>module/keys.py</td>

<td>All Keys/Tokens should be put here.</td>

</tr>

<tr>

<td>module/quickstart.py</td>

<td>Google Drive API</td>

</tr>

<tr>

<td>module/twitter.py</td>

<td>Connection to Twitter API</td>

</tr>

<tr>

<td>module/Cogs.py</td>

<td>Loading/Reloading/Unloading Cogs</td>

</tr>

<tr>

<td>module/Youtube.py</td>

<td>For Youtube Views/ETC</td>

</tr>

<tr>

<td>module/Games.py</td>

<td>For Games Unrelated to Currency.</td>

</tr>

</tr>

<tr>

<td>module/GroupMembers.py</td>

<td>Contains other groups aside from DreamCatcher.</td>

</tr>

<tr>

<td>module/logger.py</td>

<td>Logs to console and debugger</td>

</tr>

<tr>

<td>DCAPPDownloaded/</td>

<td>Folder for %download_all</td>

</tr>

<tr>

<td>DreamHD/</td>

<td>All HD photos from DC APP go here as they are posted.</td>

</tr>

</tbody>

</table>

## PLUGINS/LIBRARIES USED

<table>

<tbody>

<tr>

<th>Plugins/Libraries</th>

<th>pip install</th>

</tr>

<tr>

<td>Discord</td>

<td>pip install discord.py</td>

</tr>

<tr>

<td>aiohttp</td>

<td>pip install aiohttp</td>

</tr>

<tr>

<td>asyncio</td>

<td>pip install asyncio</td>

</tr>

<tr>

<td>bs4 (BeautifulSoup)</td>

<td>pip install bs4</td>

</tr>

<tr>

<td>aiofiles</td>

<td>pip install aiofiles</td>

</tr>

<tr>

<td>youtube_dl</td>

<td>pip install youtube_dl ---- (ffmpeg needed)</td>

</tr>

<tr>

<td>Google Client Library</td>

<td>pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib</td>

</tr>

<tr>

<td>Tweepy</td>

<td>pip install tweepy</td>

</tr>

<tr>

<td>PyNaCl</td>

<td>pip install PyNaCl</td>

</tr>

</tbody>

</table>

## COMMANDS

#### BlackJack:

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>addcards</td>

<td>Fill The CardValues Table with Cards</td>

<td>%addcards</td>

<td>♥</td>

</tr>

<tr>

<td>blackjack</td>

<td>Start a game of BlackJack</td>

<td>%blackjack (amount)</td>

<td>bj</td>

</tr>

<tr>

<td>endgame</td>

<td>End your current game</td>

<td>%endgame</td>

<td>eg</td>

</tr>

<tr>

<td>hit</td>

<td>Pick A Card</td>

<td>%hit</td>

<td></td>

</tr>

<tr>

<td>joingame</td>

<td>Join a game</td>

<td>%joingame (gameid) (bid)</td>

<td>jg</td>

</tr>

<tr>

<td>stand</td>

<td>Keep Your Cards</td>

<td>%stand</td>

<td></td>

</tr>

</tbody>

</table>

#### Cogs: ♥♥♥

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

</tr>

<tr>

<td>load</td>

<td>Command which Loads a Module. Remember to use dot path. e.g: cogs.owner</td>

<td>%load Module.(filename.py)</td>

</tr>

<tr>

<td>reload</td>

<td>Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner</td>

<td>%reload Module.(filename.py)</td>

</tr>

<tr>

<td>unload</td>

<td>Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner</td>

<td>%unload Module.(filename.py)</td>

</tr>

</tbody>

</table>

#### Currency:

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>balance</td>

<td>View balance of yourself or a user</td>

<td>%balance (@user)</td>

<td>b,bal,$</td>

</tr>

<tr>

<td>beg</td>

<td>Beg a homeless man for money</td>

<td>%beg</td>

<td></td>

</tr>

<tr>

<td>bet</td>

<td>Bet your money</td>

<td>%bet (amount)</td>

<td></td>

</tr>
<tr>

<td>daily</td>

<td>Gives 100 Dollars Every 24 Hours</td>

<td>%daily</td>

<td></td>

</tr>
<tr>

<td>give</td>

<td>Give a user money</td>

<td>%give (@user) (amount)</td>

<td></td>

</tr>

<tr>

<td>leaderboard</td>

<td>Shows Top 10 Users</td>

<td>%leaderboard</td>

<td>leaderboards</td>

</tr>

<tr>

<td>raffle</td>

<td>Join a Raffle</td>

<td>%raffle to start a raffle; %raffle (amount) to join; %raffle 0 balance to check current amount]</td>

<td></td>

</tr>

<tr>

<td>rafflereset</td>

<td>Resets Raffle without giving people their money back</td>

<td>%rafflereset</td>

<td>♥</td>

</tr>

<tr>

<td>register</td>

<td>Register yourself onto the database.</td>

<td>%register</td>

<td></td>

</tr>

<tr>

<td>resetall</td>

<td>Resets Leaderboard USE WITH CAUTION)</td>

<td>%resetall</td>

<td>♥</td>

</tr>

<tr>

<td>rob</td>

<td>Rob a user - Max Value = 1000</td>

<td>%rob @user</td>

<td></td>

</tr>

<tr>

<td>roll</td>

<td>No Description Yet</td>

<td>Command does not exist yet.</td>

<td></td>

</tr>

<tr>

<td>rps</td>

<td>Play Rock Paper Scissors for Money</td>

<td>%rps (r/p/s)(amount)</td>

<td>rockpaperscissors</td>

</tr>

</tbody>

</table>

#### DreamCatcher: 

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>
<tr>

<td>createlinks</td>

<td>Create HD links and store them in the database.</td>

<td>%createlinks (post number)</td>

<td>♥</td>

</tr>
<tr>

<td>dami</td>

<td>Pulls Dami Photo from DCAPP.</td>

<td>%dami</td>

<td></td>

</tr>
<tr>

<td>dcrandom</td>

<td>Pull Random Photo from DC APP</td>

<td>%dcrandom || %%</td>

<td>%</td>

</tr>
<tr>

<td>dcstart</td>

<td>Starts DC LOOP</td>

<td>%dcstart</td>

<td>♥</td>

</tr>

<tr>

<td>dcstop</td>

<td>Stops DC LOOP</td>

<td>%dcstop</td>

<td>♥</td>

</tr>
<tr>

<td>download_all</td>

<td>Download All DC Photos from DC APP</td>

<td>%download_all</td>

<td>♥</td>

</tr>
<tr>

<td>dreamcatcher</td>

<td>Pulls DreamCatcher Photo from DCAPP.</td>

<td>%dreamcatcher</td>

<td></td>

</tr>
<tr>

<td>gahyeon</td>

<td>Pulls Gahyeon Photo from DCAPP.</td>

<td>%gahyeon</td>

<td></td>

</tr>
<tr>

<td>handong</td>

<td>Pulls Handong Photo from DCAPP.</td>

<td>%handong</td>

<td></td>

</tr>
<tr>

<td>jiu</td>

<td>Pulls JiU Photo from DCAPP.</td>

<td>%jiu</td>

<td></td>

</tr>
<tr>

<td>latest</td>

<td>Grabs the highest resolution possible from MOST RECENT DC Post.</td>

<td>%latest</td>

<td>★</td>

</tr>
<tr>

<td>siyeon</td>

<td>Pulls Siyeon Photo from DCAPP.</td>

<td>%siyeon</td>

<td></td>

</tr>
<tr>

<td>sua</td>

<td>Pulls SuA Photo from DCAPP.</td>

<td>%sua</td>

<td></td>

</tr>
<tr>

<td>updates</td>

<td>Send DreamCatcher Updates to your current text channel</td>

<td>To start :%updates | To Stop : %updates stop</td>

<td>★</td>

</tr>
<tr>

<td>yoohyeon</td>

<td>Pulls Yoohyeon Photo from DCAPP.</td>

<td>%yoohyeon</td>

<td></td>

</tr>
</tbody>

</table>  
  
#### GroupMembers:
<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>addalias</td>

<td>Add alias to a member</td>

<td>%addalias <alias> <member></td>

<td>♥</td>

</tr>

<tr>

<td>addmemberurl</td>

<td>Adds URL to GroupMembers database</td>

<td>%addmemberurl <link="NULL", member="NULL", group="NULL", group2="NULL", group3="NULL", stage_name="NULL", *, aliases="NULL"></td>

<td>♥</td>

</tr>

<tr>

<td>aliases</td>

<td>Lists the aliases of idols that have one</td>

<td>%aliases</td>

<td></td>

</tr>

<tr>

<td>fullnames</td>

<td>Lists the full names of idols the bot has photos of</td>

<td>%fullnames</td>

<td></td>

</tr>

<tr>

<td>getlinks</td>

<td>Add links of photos to database from linked Archives</td>

<td>%getlinks <link="NULL", member="NULL", group="NULL", group2="NULL", group3="NULL", stage_name="NULL", aliases="NULL"></td>

<td>♥</td>

</tr>

<tr>

<td>groups</td>

<td>Lists the groups of idols the bot has photos of</td>

<td>%groups</td>

<td></td>

</tr>

<tr>

<td>members</td>

<td>Lists the names of idols the bot has photos of</td>

<td>%members</td>

<td></td>

</tr>

<tr>

<td>removealias</td>

<td>Add alias to a member</td>

<td>%addalias <alias> <idol's full name></td>

<td>♥</td>

</tr>

<tr>

<td>scrapelinks</td>

<td>Connection to site + put html to html_page.txt</td>

<td>%scrapelinks <url></td>

<td>♥</td>

</tr>

<tr>

<td>sort</td>

<td>Approve member links with a small sorting game.</td>

<td>%sort -- checks next message <member's name, delete, deleteall, stop></td>

<td>♥</td>

</tr>

<tr>

<td>tenor</td>

<td>Connection to tenor API // Sends Links of gifs to Database. Dashes (-) are spaces.</td>

<td>%tenor <key-word> <amount of gifs></td>

<td>♥</td>

</tr>

</tbody>

</table>


#### ImageUploader: ♥♥♥

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>deletephotos</td>

<td>Delete All Photos in Photos Folder</td>

<td>%deletephotos</td>

<td></td>

</tr>

<tr>

<td>steal</td>

<td>Downloads Images from Current Text Channel</td>

<td>%steal</td>

<td>log</td>

</tr>

<tr>

<td>upload</td>

<td>Uploads All Images in the Photos Folder to Google Drive</td>

<td>%upload (all/filename)</td>

<td></td>

</tr>

<tr>

<td>view</td>

<td>Shows amount of Images in the Photos Folder</td>

<td>%view</td>

<td></td>

</tr>

</tbody>

</table>

#### Miscellaneous:

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>_8ball</td>

<td>Asks the 8ball a question.</td>

<td>%8ball (Question)</td>

<td>8ball,8</td>

</tr>
<tr>

<td>addemoji</td>

<td>Adds an emoji to the server.</td>

<td>%addemoji (url) (emoji_name)</td>

<td>★</td>

</tr>
<tr>

<td>announce</td>

<td>Sends a bot message to certain text channels</td>

<td>%announce (message)</td>

<td>♥</td>

</tr>
<tr>

<td>ban</td>

<td>Ban A User</td>

<td>%ban @user</td>

<td>★</td>

</tr>
<tr>

<td>clear</td>

<td>Prune Messages</td>

<td>%clear (amount)</td>

<td>★ prune</td>

</tr>
<tr>

<td>flip</td>

<td>Flips a Coin</td>

<td>%flip</td>

<td></td>

</tr>
<tr>

<td>kick</td>

<td>Kick A User</td>

<td>%kick @user</td>

<td>★</td>

</tr>
<tr>

<td>kill</td>

<td>Kills the bot</td>

<td>%kill</td>

<td>♥</td>

</tr>

<tr>

<td>logging</td>

<td>Start logging this channel/Stop logging this channel</td>

<td>%logging (start/stop)</td>

<td>♥</td>

</tr>
<tr>

<td>nword</td>

<td>Checks how many times a user has said the N Word</td>

<td>%nword @user</td>

<td></td>
</tr>
<tr>

<td>ping</td>

<td>Shows Latency to Discord</td>

<td>%ping</td>

<td>pong</td>

</tr>
<tr>

<td>random</td>

<td>Choose a random number from a range (a,b)</td>

<td>%random a b [Ex: %random 1 100]</td>

<td>r,rand,randint</td>

</tr>
<tr>

<td>say</td>

<td>Owner to Bot Message</td>

<td>%say (message)</td>

<td>♥</td>

</tr>

<tr>

<td>servers</td>

<td>Extremely sloppy way of showing which servers the bot are in.</td>

<td>%servers</td>

<td>♥</td>

</tr>

<tr>

<td>speak</td>

<td>Owner to Bot TTS</td>

<td>%speak (message)</td>

<td>♥</td>

</tr>
<tr>

<td>tempchannel</td>

<td>Makes Current Channel a temporary channel deleting messages after a certain time period. If delay is -1, it will remove the channel.</td>

<td>%tempchannel [delay=-1]</td>

<td>★ temp</td>

</tr>
<tr>

<td>unban</td>

<td>UnBan A User</td>

<td>%unban @user</td>

<td>★</td>

</tr>
</tbody>

</table>

#### Music [Currently Disabled]:

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>join</td>

<td>Joins a voice channel</td>

<td>%join</td>

<td></td>

</tr>

<tr>

<td>local</td>

<td>Plays a file from the local filesystem</td>

<td>%local (filename)</td>

<td></td>

</tr>

<tr>

<td>localfiles</td>

<td>Displays all music in the music folder</td>

<td>%localfiles</td>

<td></td>

</tr>

<tr>

<td>pause</td>

<td>Pauses currently playing song</td>

<td>%pause</td>

<td></td>

</tr>

<tr>

<td>play</td>

<td>Streams from a url (same as yt, but doesn't predownload)</td>

<td>%play (link)</td>

<td></td>

</tr>

<tr>

<td>queue</td>

<td>Shows Current Queue [Broken atm]</td>

<td>%queue</td>

<td></td>

</tr>

<tr>

<td>resume</td>

<td>Resumes a paused song</td>

<td>%resume</td>

<td></td>

</tr>

<tr>

<td>stop</td>

<td>Stops and disconnects the client from voice</td>

<td>%stop</td>

<td></td>

</tr>

<tr>

<td>volume</td>

<td>Changes the player's volume - play,yt, and local all have preset volumes when they start playing.</td>

<td>%volume (amount)</td>

<td></td>

</tr>

<tr>

<td>yt</td>

<td>Play A Song From Youtube</td>

<td>%yt (url)</td>

<td></td>

</tr>

</tbody>

</table>

#### Twitter: ♥♥♥

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>deletetweet</td>

<td>Delete a Tweet by it's ID</td>

<td>%deletetweet (id)</td>

<td></td>

</tr>

<tr>

<td>recenttweets</td>

<td>Show Most Recents Tweets</td>

<td>%recenttweets (amount)</td>

<td></td>

</tr>

<tr>

<td>tweet</td>

<td>Tweets a status update on Twitter</td>

<td>%tweet (status)</td>

<td></td>

</tr>

</tbody>

</table>

#### Youtube: ♥♥♥

<table>

<tbody>

<tr>

<th>Command</th>

<th>Description</th>

<th>Format</th>

<th>Aliases</th>

</tr>

<tr>

<td>addurl</td>

<td>Add url to youtube videos</td>

<td>%addurl (link)</td>

<td></td>

</tr>

<tr>

<td>removeurl</td>

<td>Remove url from youtube videos</td>

<td>%removeurl (link)</td>

<td></td>

</tr>

<tr>

<td>scrapeyoutube</td>

<td>Scrape Youtube Videos in DB</td>

<td>%scrapeyoutube</td>

<td></td>

</tr>

<tr>

<td>startloop</td>

<td>Starts scraping youtube videos. </td>

<td>%startloop (seconds until it starts looping)</td>

<td></td>

</tr>

<tr>

<td>stoploop</td>

<td>Stops scraping youtube videos</td>

<td>%stoploop</td>

<td></td>

</tr>

</tbody>

</table>
