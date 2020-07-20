import discord
from discord.ext import commands, tasks
from module import keys, logger as log
import asyncio
import youtube_dl
from Utility import resources as ex
import random
import os
client = keys.client


youtube_dl.utils.bug_reports_message = lambda: ''

# A song does not directly go to the queue if it's in a playlist.
# instead, it piles up in this process and is all sent to the queue at once.


def get_video_title(video):
    if check_if_player(video):
        return video.title
    else:
        return video.get('title')


def check_if_player(player):
    return isinstance(player, YTDLSource)


async def download_video(video):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(video.get('webpage_url'), download=True))
    file_name = ytdl.prepare_filename(video)
    return YTDLSource(discord.FFmpegPCMAudio(file_name, **ffmpeg_options), data=data)


def check_live(video):
    # return None = video is downloaded
    # return a message = video is ignored
    try:
        if video['duration'] > 14400:
            return 'too_long'
    except Exception as e:
        pass
    try:
        if not video['is_live']:
            return None
        else:
            return 'live_video'
    except Exception as e:
        return None  # this error occurs from is_live not being found.

# https://github.com/ytdl-org/youtube-dl/blob/2391941f283a1107b01f9df76a8b0e521a5abe3b/youtube_dl/YoutubeDL.py#L143
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'music/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'nooverwrites': True,
    'match_filter': check_live,
    'verbose': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queued = {}


class Music(commands.Cog):
    @tasks.loop(seconds=30, minutes=1, hours=0, reconnect=True)
    async def check_voice_clients(self):
        if ex.client.loop.is_running():
            try:
                voice_clients = client.voice_clients
                for voice_client in voice_clients:
                    if voice_client.is_connected():
                        if len(voice_client.channel.members) == 1:
                            if voice_client.is_playing():
                                try:
                                    songs_queued = queued[voice_client.guild.id]
                                    if len(songs_queued) > 0:
                                        channel = songs_queued[0][1]
                                        msg = f"> **There are no users in this voice channel. Resetting queue and leaving.**"
                                        await channel.send(msg)
                                except Exception as e:
                                    pass
                                self.reset_queue_for_guild(voice_client.guild.id)
                                voice_client.stop()
                            await voice_client.disconnect()
                keep_files = []
                for key in queued:
                    file_name = (queued[key][0][2])
                    keep_files.append(file_name)
                all_music = os.listdir("music")
                for song_file_name in all_music:
                    file_location = f"music/{song_file_name}"
                    if file_location not in keep_files:
                        if file_location != "music":
                            try:
                                os.remove(file_location)
                            except Exception as e:
                                pass
            except Exception as e:
                log.console(e)

    def check_user_in_vc(self, ctx):
        try:
            return ctx.author in ctx.voice_client.channel.members
        except AttributeError:
            return False  # NoneType object has no attribute channel

    def reset_queue_for_guild(self, guild_id):
        try:
            if queued[guild_id]:
                for song in queued[guild_id]:
                    player = song[0]
                    file_name = song[2]
                    if check_if_player(player):
                        player.cleanup()
                    try:
                        os.remove(file_name)
                    except Exception as e:
                        pass

                queued.pop(guild_id, None)
        except Exception as e:
            pass

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffles the playlist."""
        try:
            if self.check_user_in_vc(ctx):
                # this is in a list so that it can be added to the beginning later
                currently_playing = [queued[ctx.guild.id][0]]
                number_of_songs_in_queue = len(queued[ctx.guild.id])
                if number_of_songs_in_queue > 1:
                    other_songs = queued[ctx.guild.id][1:number_of_songs_in_queue]
                    random.shuffle(other_songs)
                    queued[ctx.guild.id] = currently_playing + other_songs
                await ctx.send(f"> **{ctx.author}, the current queue was shuffled.**")
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except AttributeError:
            await ctx.send(f"> **There is no list to shuffle or I am not in a voice channel.**")

    @commands.command(aliases=['list', 'q'])
    async def queue(self, ctx, page_number=1):
        """Shows Current Queue [Format: %queue]"""
        try:
            embed_page_number = 1
            current_songs = queued[ctx.guild.id]
            embed_list = []
            counter = 1
            set_of_songs = ""
            for song in current_songs:
                if check_if_player(song[0]):
                    player = song[0]
                    youtube_channel = player.uploader
                    song_name = player.title
                    song_link = player.url
                    duration = player.duration
                else:
                    video = song[0]
                    youtube_channel = video.get('uploader')
                    song_name = video.get('title')
                    song_link = video.get('webpage_url')
                    duration = video.get('duration')
                try:
                    duration = await ex.get_cooldown_time(duration)
                except Exception as e:
                    duration = "N/A"
                if counter == 1:
                    song_desc = f"[{counter}] **NOW PLAYING:** [{youtube_channel} - {song_name}]({song_link}) - {duration}\n\n"
                else:
                    song_desc = f"[{counter}] [{youtube_channel} - {song_name}]({song_link}) - {duration}\n\n"
                set_of_songs += song_desc
                if counter % 10 == 0:
                    embed = discord.Embed(title=f"{ctx.guild.name}'s Music Playlist Page {embed_page_number}",
                                          description=set_of_songs, color=ex.get_random_color())
                    embed = await ex.set_embed_author_and_footer(embed, footer_message="Thanks for using Irene.")
                    set_of_songs = ""
                    embed_list.append(embed)
                    embed_page_number += 1
                counter += 1
            # if there are not more than 10 songs in queue.
            embed = discord.Embed(title=f"{ctx.guild.name}'s Music Playlist Page {embed_page_number}",
                                  description=set_of_songs, color=ex.get_random_color())
            embed = await ex.set_embed_author_and_footer(embed, footer_message="Thanks for using Irene.")
            embed_list.append(embed)
            if page_number > len(embed_list):
                page_number = 1
            elif page_number <= 0:
                page_number = 1
            msg = await ctx.send(embed=embed_list[page_number - 1])
            await ex.check_left_or_right_reaction_embed(msg, embed_list, page_number - 1)
        except KeyError as e:
            await ctx.send(f"> **There are no songs queued in this server.**")
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel [Format: %join]"""
        try:
            channel = ctx.message.author.voice.channel
            await ctx.send(f"> **{ctx.author}, I joined {channel.name}.**")
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)
            await channel.connect()
        except AttributeError:
            await ctx.send(f"> **{ctx.author}, you are not in a voice channel.**")
        except Exception as e:
            log.console(e)

    @commands.command()
    async def pause(self, ctx):
        """Pauses currently playing song [Format: %pause]"""
        if self.check_user_in_vc(ctx):
            paused = ctx.voice_client.is_paused()
            if not paused:
                ctx.voice_client.pause()
                await ctx.send("> **The player is now paused.**")

        else:
            await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")

    @commands.command(aliases=['unpause'])
    async def resume(self, ctx):
        """Resumes a paused song [Format: %resume]"""
        if self.check_user_in_vc(ctx):
            paused = ctx.voice_client.is_paused()
            if paused:
                ctx.voice_client.resume()
                video = (queued[ctx.guild.id])[0][0]
                if check_if_player(video):
                    title = video.title
                else:
                    title = video.get('title')
                await ctx.send(f'> **Now resuming: {title}**')
            else:
                await ctx.send('> **The video player is not paused**')
        else:
            await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")

    @commands.command(aliases=['skipto'])
    async def move(self, ctx, song_number: int):
        """Makes a song the next song to play without skipping the current song. [Format: %move (song number)] """
        try:
            if self.check_user_in_vc(ctx):
                song_number = song_number - 1  # account for starting from 0
                if song_number == 0:
                    await ctx.send(f"> **You can not move the song currently playing.**")
                else:
                    try:
                        title = get_video_title(queued[ctx.guild.id][song_number][0])
                        # inserts song information at index 1 and removes the old position.
                        queued[ctx.guild.id].insert(1, queued[ctx.guild.id].pop(song_number))
                        await ctx.send(f"> **{title} will now be the next song to play.**")
                    except Exception as e:
                        await ctx.send(f"> **That song number was not found. Could not move it.**")
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except Exception as e:
            pass


    @commands.command()
    async def remove(self, ctx, song_number:int):
        """Remove a song the queue. [Format: %remove (song number)] """
        try:
            if self.check_user_in_vc(ctx):
                song_number = song_number - 1  # account for starting from 0
                try:
                    title = get_video_title(queued[ctx.guild.id][song_number][0])
                    queued[ctx.guild.id].pop(song_number)
                    await ctx.send(f"> **Removed {title} from the queue.**")
                except Exception as e:
                    await ctx.send(f"> **That song number was not found. Could not remove it.**")
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except Exception as e:
            pass


    @commands.command()
    async def skip(self, ctx):
        """Skips the current song. [Format: %skip]"""
        try:
            if self.check_user_in_vc(ctx):
                ctx.voice_client.stop()  # Will call error to remove the song.
                player = queued[ctx.guild.id][0][0]
                title = get_video_title(player)
                await ctx.send(f"> **Skipped {title}**")
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except Exception as e:
            pass

    def remove_song_in_queue(self, client_guild_id):
        try:
            if len(queued[client_guild_id]) == 1:
                return self.reset_queue_for_guild(client_guild_id)
        except KeyError:
            pass
        try:
            try:
                (queued[client_guild_id][0][0]).cleanup()
            except Exception as e:
                pass
            try:
                os.remove(queued[client_guild_id][0][2])
            except Exception as e:
                pass
            return queued[client_guild_id].pop(0)
        except KeyError:
            return None

    @commands.command()
    async def play(self, ctx, *, url=None):
        """Plays audio to a voice channel. [Format: %play (title/url)"""
        if url is None:
            if ctx.voice_client.is_paused:
                ctx.voice_client.resume()
                await ctx.send(f"> **The video player is now resumed**")
            else:
                await ctx.send("> The player is not paused. Please enter a title or link to play audio.")
        else:
            try:
                if self.check_user_in_vc(ctx):
                    async with ctx.typing():
                        msg = await ctx.send(f"> **Gathering information about the video/playlist, this may take a few minutes if it is a long playlist.**")
                        videos, first_video_live = await YTDLSource.from_url(url, loop=client.loop, stream=False, guild_id=ctx.guild.id, channel=ctx.channel)
                        if not ctx.voice_client.is_playing():
                            if not first_video_live:
                                player = await download_video(videos[0])
                                video_title = videos[0].get('title')
                            else:
                                player = videos[0]
                                video_title = player.title
                            try:
                                ctx.voice_client.play(player, after=self.start_next_song)
                                # THIS IS VERY IMPORTANT
                                # This makes the front of the queue always a player.
                                # This is useful so that no code is changed for going to the next song (music rework)
                                queued[ctx.guild.id][0][0] = player
                            except Exception as e:  # Already Playing Audio
                                return await ctx.send(f"> **Added {video_title} to the queue.**")
                            await ctx.send(f'> **Now playing: {video_title}**')
                        else:
                            # grabbing the latest player
                            if len(videos) == 1:
                                if not first_video_live:
                                    title = videos[0].get('title')
                                else:
                                    title = videos[0].title
                                await ctx.send(f"> **Added {title} to the queue.**")
                            else:
                                await ctx.send(f"> **Added {len(videos)} songs to the queue.**")
                        await msg.delete()
                else:
                    await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
            except IndexError:
                pass
            except Exception as e:
                log.console(e)

    def start_next_song(self, error):
        if error is None:
            all_voice_clients = client.voice_clients
            for voice_client in all_voice_clients:
                if not voice_client.is_playing() and not voice_client.is_paused():
                    client_guild_id = voice_client.guild.id
                    self.remove_song_in_queue(client_guild_id)
                    try:
                        player = queued[client_guild_id][0][0]
                        channel = queued[client_guild_id][0][1]
                        live = queued[client_guild_id][0][3]
                        try:
                            if not live:  # we know it's video information and not a player because it is not live.
                                download_a_video = download_video(player)
                                player = asyncio.run_coroutine_threadsafe(download_a_video, client.loop)
                                try:
                                    player = player.result()
                                    queued[client_guild_id][0][0] = player  # making front of queue a player
                                except Exception as e:
                                    log.console(e)
                            voice_client.play(player, after=self.start_next_song)
                        except Exception as e:
                            log.console(e)
                        send_channel_song = channel.send(f'> **Now playing: **{player.title}')
                        # used because async function cannot be used.
                        # https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function
                        send_channel = asyncio.run_coroutine_threadsafe(send_channel_song, client.loop)
                        try:
                            send_channel.result()
                        except Exception as e:
                            log.console(e)
                            pass
                    except IndexError as e:
                        pass
                    except Exception as e:
                        log.console(e)

    @commands.command()
    async def volume(self, ctx, volume: int = 10):
        """Changes the player's volume - Songs default to 10. [Format: %volume (1-100)]"""
        try:
            if self.check_user_in_vc(ctx):
                if volume < 1 or volume > 100:
                    await ctx.send(f"> **{ctx.author}, please choose a volume from 1 to 100.**")
                else:
                    if ctx.voice_client is None:
                        return await ctx.send(f"> **{ctx.author}, you are not connected to a voice channel.**")

                    ctx.voice_client.source.volume = volume / 100
                    await ctx.send("> **Changed volume to {}%**".format(volume))
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except AttributeError:
            await ctx.send(f"> **{ctx.author}, I am not in a voice channel.**")
        except Exception as e:
            log.console(e)

    @commands.command(aliases=["leave"])
    async def stop(self, ctx):
        """Disconnects from voice channel and resets queue. [Format: %stop]"""
        try:
            if self.check_user_in_vc(ctx):
                voice_channel_name = ctx.voice_client.channel.name
                self.reset_queue_for_guild(ctx.guild.id)
                await ctx.voice_client.disconnect()
                await ctx.send(f"**{ctx.author}, I left {voice_channel_name} and reset the queue.**")
            else:
                await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")
        except AttributeError:
            pass
        except Exception as e:
            log.console(e)

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("> **You are not connected to a voice channel.**")
                raise commands.CommandError("Author not connected to a voice channel.")


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)
        self.source = source
        self.data = data
        self.title = data.get('title')
        self.uploader = data.get('uploader')
        self.url = data.get('webpage_url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, guild_id=None, channel=None):
        videos = []

        async def add_video(video):
            try:
                live = False
                status = check_live(video)
                if status == 'too_long':
                    await channel.send(f"> **A video will not be added because it is over 4 hours long.**")
                else:
                    if status == 'live_video':
                        live = True
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                        file_name = video['url']
                        video = cls(discord.FFmpegPCMAudio(file_name, **ffmpeg_options), data=data)
                    else:
                        file_name = video['url'] if stream else ytdl.prepare_filename(video)
                    videos.append(video)
                    video_and_channel = [video, channel, file_name, live]
                    if guild_id in queued:
                        if queued[guild_id] is not None:
                            queued[guild_id].append(video_and_channel)
                    else:
                        queued[guild_id] = [video_and_channel]
                return live
            except Exception as e:
                return False

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        first_video_live = False
        if 'entries' in data:  # several videos
            counter = 0
            for video_entry in data['entries']:
                if counter == 0:
                    first_video_live = await add_video(video_entry)
                else:
                    await add_video(video_entry)
                counter += 1
        else:
            first_video_live = await add_video(data)  # only 1 video
        return videos, first_video_live  # return added players
