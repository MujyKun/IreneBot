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
<ul style="list-style-type:square;">
	<li>run.exe - Main Run File - Startup</li>
	<li>run.py - Main Program/Bot - Startup</li>
	<li>Cards/.. - All Cards In A Deck</li>
	<li>music/.. - Local Music Files</li>
	<li>modules/BlackJack.py - A 1v1 game of blackjack</li>
	<li>modules/Currency.py - Games that involve an economy</li>
	<li>modules/DreamCatcher.py - Send Photos from the DC App to a certain text channel based on a loop.</li>
	<li>modules/ImageUploader.py - Commands for downloading photos from a text channel and uploading them to google drive.</li>
	<li>modules/Miscellaneous.py - clear/kill/ping/speak/say/8ball/servers/admincommands [Things I didn't feel like making a section for]</li>
	<li>modules/Music.py - Commands for Music</li>
	<li>modules/Twitter2.py - Commands for Twitter</li>
	<li>modules/currency.db - Database that includes the economy [Also has channel ids].</li>
	<li>modules/keys.py - All Keys/Tokens should be put here.</li>
	<li>modules/quickstart.py - Google Drive API</li>
	<li>modules/twitter.py - Connection to Twitter API</li>
	<li>modules/Cogs.py - Loading/Reloading/Unloading Cogs</li>
</ul>
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
</table>
<h2>
COMMANDS
</h2>
<h4>
BlackJack:
</h4>
<ul>
	<li>addcards   ----  Fill The CardValues Table with Cards [Format: %addcards]</li>
	<li>blackjack  ----  Start a game of BlackJack [Format: %blackjack (amount)] [Aliases: bj]</li>
	<li>endgame   ----   End your current game [Format: %endgame] [Aliases: eg]</li>
	<li>hit       ----   Pick A Card [Format: %hit]</li>
	<li>joingame  ----   Join a game [Format: %joingame (gameid) (bid)] [Aliases: jg]</li>
	<li>stand     ----   Keep Your Cards [Format: %stand]</li>
</ul>
<h4>
Cogs:
</h4>

<ul>
	<li>load ---- Command which Loads a Module. Remember to use dot path. e.g: cogs.owner</li>
	<li>reload ---- Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner</li>
	<li>unload ---- Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner</li>
</ul>
<h4>
Currency:
</h4>
<ul>
	<li>balance   ----   View your balance [Format: %balance (@user)][Aliases: b,bal,$]</li>
	<li>beg      ----    Beg a homeless man for money [Format: %beg]</li>
	<li>bet      ----    Bet your money [Format: %bet (amount)]</li>
	<li>give      ----   Give a user money [Format: %give (@user) (amount)]</li>
	<li>leaderboard ---- Shows Top 10 Users [Format: %leaderboard][Aliases: leaderboards]</li>
	<li>raffle    ----   Join a Raffle [Format: %raffle to start a raffle; %raffle (amount) to join; %raffle 0 balance to check current amount]</li>
	<li>rafflereset ---- Resets Raffle without giving people their money back[Format: %rafflereset]</li>
	<li>register    ---- Register yourself onto the database.</li>
	<li>resetall  ----   Resets Leaderboard [Format: %resetall] USE WITH CAUTION</li>
	<li>rob     ----     Rob a user [Format: %rob @user] - Command does not exist yet.</li>
	<li>roll    ----     No Description Yet- Command does not exist yet.</li>
	<li>rps      ----    Play Rock Paper Scissors for Money [Format: %rps (r/p/s)(amount)][Aliases: rockpaperscissors]</li>
</ul>
<h4>
DreamCatcher:
</h4>
<ul>
	<li>scrape   ----    Starts Loop Searching For New DC Post [Format: %scrape (post number to start at)] NOTE : This command must be used every run as it will not automatically start the loop [can easily be coded to be automatic] Starts scraping from post number 36582 by default</li>
	<li>updates   ----   Send DC Updates to your current text channel [Format: %updates] | To Stop : [Format: %updates stop]</li>
</ul>
<h4>
ImageUploader:
</h4>
<ul>
	<li>deletephotos ---- Delete All Photos in Photos Folder [Format: %deletephotos]</li>
	<li>steal     ----   Downloads Images from Current Text Channel [Format: %steal (amount of messages)][Aliases: log]</li>
	<li>upload    ----   Uploads All Images in the Photos Folder to Google Drive [Format: %upload (all/filename)]</li>
	<li>view        ---- Shows amount of Images in the Photos Folder [Format: %view]</li>
</ul>
<h4>
Miscellaneous:
</h4>
<ul>
	<li>_8ball   ----    Asks the 8ball a question. [Format: %8ball Question]</li>
	<li>clear    ----    Prune Messages [Format: %clear (amount)][Aliases: prune]</li>
	<li>kill     ----    Kills the bot [Format: %kill]</li>
	<li>ping      ----   Shows Latency to Discord [Format: %ping]</li>
	<li>say       ----   Owner to Bot Message</li>
	<li>servers   ----   Extremely sloppy way of showing which servers the bot are in.</li>
	<li>speak      ----  Owner to Bot TTS</li>
</ul>
<h4>
Music:
</h4>
<ul>
	<li>join       ----  Joins a voice channel [Format: %join]</li>
	<li>local     ----  Plays a file from the local filesystem</li>
	<li>localfiles ----  Displays all music in the music folder [Format: %localfiles]</li>
	<li>pause   ----     Pauses currently playing song [Format: %pause]</li>
	<li>play     ----    Streams from a url (same as yt, but doesn't predownload)</li>
	<li>queue    ----    Shows Current Queue [Format: %queue]</li>
	<li>resume   ----    Resumes a paused song [Format: %resume]</li>
	<li>stop     ----    Stops and disconnects the client from voice</li>
	<li>volume    ----   Changes the player's volume - play,yt, and local all have  preset volumes when they start playing.</li>
	<li>yt        ----   Play A Song From Youtube[Format: %play (url)]</li>
</ul>
<h4>
Twitter:
</h4>
<ul>
	<li>deletetweet ---- Delete a Tweet by it's ID [Format: %deletetweet (id)]</li>
	<li>recenttweets ---- Show Most Recents Tweets[Format: %recenttweets (amount)]</li>
	<li>tweet     ----   Tweets a status update on Twitter [Format: %tweet (status)]</li>
</ul>
</body>
