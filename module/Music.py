import discord
import os
from discord.ext import commands
import youtube_dl
import asyncio

client = 0


def setup(client1):
    client1.add_cog(Music(client1))
    global client
    client = client1


youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def queue(self, ctx):
        """Shows Current Queue [Format: %queue]"""
        song_loop = ""
        for song in music_list:
            song_loop = '{}\n'.format(song)
        await ctx.send(">>> **There are {} songs in queue.\n{} **".format(len(music_list), song_loop))

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel [Format: %join]"""
        channel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def localfiles(self, ctx):
        """Displays all music in the music folder [Format: %localfiles]"""
        all_music = os.listdir('music')
        print(all_music)
        song_list = ""
        for song in all_music:
            song_list += "{}\n".format(song)
        await ctx.send(">>> There are **{}** songs.\n{}".format(len(all_music), song_list))

    @commands.command()
    async def pause(self, ctx):
        """Pauses currently playing song [Format: %pause]"""
        SongPlaying = ctx.voice_client.is_playing()
        Paused = ctx.voice_client.is_paused()
        if Paused != True:
            ctx.voice_client.pause()
            await ctx.send("> **The video player is now paused**")
        else:
            if SongPlaying == True:
                await ctx.send("> **The video player is already paused.**")
            else:
                await ctx.send("> **There is no song currently playing.**")

    @commands.command()
    async def resume(self, ctx):
        """Resumes a paused song [Format: %resume]"""
        Paused = ctx.voice_client.is_paused()
        if Paused == True:
            ctx.voice_client.resume()
            await ctx.send('> **Now resuming:**')
        else:
            await ctx.send('> **The video player is not paused**')

    @commands.command()
    async def local(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        newquery = "music/{}".format(query)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(newquery))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        ctx.voice_client.source.volume = 20 / 100
        await ctx.send('> **Now playing:** {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Play A Song From Youtube[Format: %yt (url)]"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 10 / 100
        await ctx.send('> **Now playing: **{}'.format(player.title))

    @commands.command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 20 / 100
        await ctx.send('> **Now playing: **{}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("> **Not connected to a voice channel.**")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("> **Changed volume to **{}%".format(volume))

    @commands.command(aliases=["leave"])
    async def stop(self, ctx):
        """Stops and disconnects the client from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @local.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("> **You are not connected to a voice channel.**")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

#Source Code : https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py#L107