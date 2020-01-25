<h1>IreneBot</h1> 
<h2>Irene Bot for Discord in Python V1.001</h2>

<p>Upon signing up for the Google Drive API, make sure to put the credentials.json in the main folder.
<br>[ https://developers.google.com/drive ]<br><br>
When first getting the bot to work, make sure to use the %upload command to get the Google Drive API to properly work.<br>You will need to sign into your Google Account when it prompts you as a one time authorization.<br>
ImageUploader was not coded with aiohttp, so there will be blockage from other commands when these commands are in use.<br>
There are instructions left in quickstart.py for first time running. Make sure to follow the comments.<br><br>
Command Prefix is in run.py and is currently set to '%' by default.</p>
<body>
<h2>
FILES
</h2>
<table>
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
		<td>modules/BlackJack.py</td>
		<td>A 1v1 game of blackjack</td>
	</tr>
	<tr>
		<td>modules/Currency.py</td>
		<td>Games that involve an economy</td>
	</tr>
	<tr>
		<td>modules/DreamCatcher.py</td>
		<td>Send Photos from the DC App to a certain text channel based on a loop.</td>
	</tr>
	<tr>
		<td>modules/ImageUploader.py</td>
		<td>Commands for downloading photos from a text channel and uploading them to google drive.</td>
	</tr>
	<tr>
		<td>modules/Miscellaneous.py</td>
		<td>Commands I didn't feel like making a section for</td>
	</tr>
	<tr>
		<td>modules/Music.py</td>
		<td>Commands for Music</td>
	</tr>
	<tr>
		<td>modules/Twitter2.py</td>
		<td>Commands for Twitter</td>
	</tr>
	<tr>
		<td>modules/currency.db </td>
		<td>Database that includes the economy [Also has channel ids].</td>
	</tr>
	<tr>
		<td>modules/keys.py</td>
		<td>All Keys/Tokens should be put here.</td>
	</tr>
	<tr>
		<td>modules/quickstart.py</td>
		<td>Google Drive API</td>
	</tr>
	<tr>
		<td>modules/twitter.py</td>
		<td>Connection to Twitter API</td>
	</tr>
	<tr>
		<td>modules/Cogs.py</td>
		<td>Loading/Reloading/Unloading Cogs</td>
	</tr>
</table>
<h2>
PLUGINS/LIBRARIES USED
</h2>
<table>
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
</table>
<h2>
COMMANDS
</h2>
<h4>
BlackJack:
</h4>
<table>
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
		<td>	</td>
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
		<td>	</td>
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
		<td>	</td>
	</tr>
</table>

<h4>
Cogs:
</h4>
<table>
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
		<td>unload</td>
		<td>Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner</td>
		<td>%reload Module.(filename.py)</td>
	</tr>
	<tr>
		<td>reload</td>
		<td>Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner</td>
		<td>%unload Module.(filename.py)</td>
	</tr>
</table>

<h4>
Currency:
</h4>
<table>
	<tr>
		<th>Command</th>
		<th>Description</th>
		<th>Format</th>
		<th>Aliases</th>
	</tr>
	<tr>
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
		<td>	</td>
	</tr>
	<tr>
		<td>bet</td>
		<td>Bet your money</td>
		<td>%bet (amount)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>give</td>
		<td>Give a user money</td>
		<td>%give (@user) (amount)</td>
		<td>	</td>
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
		<td>	</td>
	</tr>
	<tr>
		<td>rafflereset</td>
		<td>Resets Raffle without giving people their money back</td>
		<td>%rafflereset</td>
		<td>	</td>
	</tr>
	<tr>
		<td>register</td>
		<td>Register yourself onto the database.</td>
		<td>%register</td>
		<td>	</td>
	</tr>
	<tr>
		<td>resetall</td>
		<td>Resets Leaderboard USE WITH CAUTION)</td>
		<td>%resetall</td>
		<td>	</td>
	</tr>
	<tr>
		<td>rob</td>
		<td>Rob a user</td>
		<td>%rob @user</td>
		<td>Command does not exist yet.</td>
	</tr>
	<tr>
		<td>roll</td>
		<td>No Description Yet</td>
		<td>Command does not exist yet.</td>
		<td>	</td>
	</tr>
	<tr>
		<td>rps</td>
		<td>Play Rock Paper Scissors for Money</td>
		<td>%rps (r/p/s)(amount)</td>
		<td>rockpaperscissors</td>
	</tr>
</table>

<h4>
DreamCatcher:
</h4>
<table>
	<tr>
		<th>Command</th>
		<th>Description</th>
		<th>Format</th>
		<th>Aliases</th>
	</tr>
	<tr>
		<td>latest</td>
		<td>Grabs the highest resolution possible from MOST RECENT DC Post. Must have uploaded at least 1 post while running in order for it to work.</td>
		<td>%latest</td>
		<td>	</td>
	</tr>
	<tr>
		<td>scrape</td>
		<td>Starts Loop Searching For New DreamCatcher Post. This command must be used every run as it will not automatically start the loop on purpose.</td>
		<td>%scrape (post number to start at)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>updates</td>
		<td>Send DreamCatcher Updates to your current text channel</td>
		<td>To start :%updates | To Stop : %updates stop</td>
		<td>	</td>
	</tr>
</table>

<h4>
ImageUploader:
</h4>
<table>
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
		<td>	</td>
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
		<td>	</td>
	</tr>
	<tr>
		<td>view</td>
		<td>Shows amount of Images in the Photos Folder</td>
		<td>%view</td>
		<td>	</td>
	</tr>
</table>

<h4>
Miscellaneous:
</h4>
<table>
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
		<td>announce</td>
		<td>Sends a bot message to certain text channels</td>
		<td>%announce (message)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>clear</td>
		<td>Prune Messages</td>
		<td>%clear (amount)</td>
		<td>prune</td>
	</tr>
	<tr>
		<td>kill</td>
		<td>Kills the bot</td>
		<td>%kill</td>
		<td>	</td>
	</tr>
	<tr>
		<td>logging</td>
		<td>Start logging this channel/Stop logging this channel</td>
		<td>%logging (start/stop)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>ping</td>
		<td>Shows Latency to Discord</td>
		<td>%ping</td>
		<td>	</td>
	</tr>
	<tr>
		<td>say</td>
		<td>Owner to Bot Message</td>
		<td>%say (message)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>servers</td>
		<td>Extremely sloppy way of showing which servers the bot are in.</td>
		<td>%servers</td>
		<td>	</td>
	</tr>
	<tr>
		<td>speak</td>
		<td>Owner to Bot TTS</td>
		<td>%speak (message)</td>
		<td>	</td>
	</tr>
</table>

<h4>
Music:
</h4>
<table>
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
		<td>	</td>
	</tr>
	<tr>
		<td>local</td>
		<td>Plays a file from the local filesystem</td>
		<td>%local (filename)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>localfiles</td>
		<td>Displays all music in the music folder</td>
		<td>%localfiles</td>
		<td>	</td>
	</tr>
	<tr>
		<td>pause</td>
		<td>Pauses currently playing song</td>
		<td>%pause</td>
		<td>	</td>
	</tr>
	<tr>
		<td>play</td>
		<td>Streams from a url (same as yt, but doesn't predownload)</td>
		<td>%play (link)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>queue</td>
		<td>Shows Current Queue [Broken atm]</td>
		<td>%queue</td>
		<td>	</td>
	</tr>
	<tr>
		<td>resume</td>
		<td>Resumes a paused song</td>
		<td>%resume</td>
		<td>	</td>
	</tr>
	<tr>
		<td>stop</td>
		<td>Stops and disconnects the client from voice</td>
		<td>%stop</td>
		<td>	</td>
	</tr>
	<tr>
		<td>volume</td>
		<td>Changes the player's volume - play,yt, and local all have  preset volumes when they start playing.</td>
		<td>%volume (amount)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>yt</td>
		<td>Play A Song From Youtube</td>
		<td>%yt (url)</td>
		<td>	</td>
	</tr>
</table>

<h4>
Twitter:
</h4>
<table>
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
		<td>	</td>
	</tr>
	<tr>
		<td>recenttweets</td>
		<td>Show Most Recents Tweets</td>
		<td>%recenttweets (amount)</td>
		<td>	</td>
	</tr>
	<tr>
		<td>tweet</td>
		<td>Tweets a status update on Twitter</td>
		<td>%tweet (status)</td>
		<td>	</td>
	</tr>
</table>

</body>
