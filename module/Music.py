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
files_in_process_of_queue = []


def check_live(video_info):
    # return None = video is downloaded
    # return a message = video is ignored
    def process_video():
        files_in_process_of_queue.append(ytdl.prepare_filename(video_info))
        return None

    try:
        if video_info['duration'] > 14400:
            return 'too_long'
    except Exception as e:
        pass
    try:
        if not video_info['is_live']:
            process_video()
        else:
            return 'live_video'
    except Exception as e:
        process_video()  # this error occurs from is_live not being found.

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
                file_location = f"music\\{song_file_name}"
                if file_location not in keep_files and file_location not in files_in_process_of_queue:
                    if file_location != "music":
                        os.remove(file_location)
        except Exception as e:
            log.console(e)

    def check_user_in_vc(self, ctx):
        return ctx.author in ctx.voice_client.channel.members

    def reset_queue_for_guild(self, guild_id):
        try:
            if queued[guild_id]:
                for song in queued[guild_id]:
                    player = song[0]
                    player.cleanup()
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
                player = song[0]
                youtube_channel = player.uploader
                song_name = player.title
                song_link = player.url
                if counter == 1:
                    song_desc = f"[{counter}] **NOW PLAYING:** [{youtube_channel} - {song_name}]({song_link})\n\n"
                else:
                    song_desc = f"[{counter}] [{youtube_channel} - {song_name}]({song_link}) \n\n"
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
                await ctx.send("> **The video player is now paused**")
            else:
                await ctx.send("> **The video player is already paused.**")
        else:
            await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")

    @commands.command(aliases=['unpause'])
    async def resume(self, ctx):
        """Resumes a paused song [Format: %resume]"""
        if self.check_user_in_vc(ctx):
            paused = ctx.voice_client.is_paused()
            if paused:
                ctx.voice_client.resume()
                await ctx.send(f'> **Now resuming: {((queued[ctx.guild.id])[0][0]).title}**')
            else:
                await ctx.send('> **The video player is not paused**')
        else:
            await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")

    @commands.command()
    async def skip(self, ctx):
        """Skips the current song. [Format: %skip]"""
        if self.check_user_in_vc(ctx):
            ctx.voice_client.stop()  # Will call error to remove the song.
            await ctx.send(f"> **Skipped.**")
        else:
            await ctx.send(f"> **{ctx.author}, we are not in the same voice channel.**")

    def remove_song_in_queue(self, client_guild_id):
        try:
            if len(queued[client_guild_id]) == 1:
                return self.reset_queue_for_guild(client_guild_id)
        except KeyError:
            pass
        try:
            (queued[client_guild_id][0][0]).cleanup()
            return queued[client_guild_id].pop(0)
        except KeyError:
            return None

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays audio to a voice channel. [Format: %play (title/url)"""
        try:
            if self.check_user_in_vc(ctx):
                async with ctx.typing():
                    players = await YTDLSource.from_url(url, loop=client.loop, stream=False, guild_id=ctx.guild.id, channel=ctx.channel)
                    if not ctx.voice_client.is_playing():
                        ctx.voice_client.play(players[0], after=self.start_next_song)
                        await ctx.send(f'> **Now playing: {players[0].title}**')
                    else:
                        # grabbing the latest player
                        if len(players) == 1:
                            await ctx.send(f"> **Added {players[0].title} to the queue.**")
                        else:
                            await ctx.send(f"> **Added {len(players)} songs to the queue.**")
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
                        voice_client.play(player, after=self.start_next_song)
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

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, guild_id=None, channel=None):
        players = []

        async def add_video(video):
            try:
                status = check_live(video)
                if status == 'too_long':
                    await channel.send(f"> **A video will not be added because it is over 4 hours long.**")
                else:
                    if status == 'live_video':
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                        file_name = video['url']
                        player = cls(discord.FFmpegPCMAudio(file_name, **ffmpeg_options), data=data)
                    else:
                        file_name = video['url'] if stream else ytdl.prepare_filename(video)
                        player = cls(discord.FFmpegPCMAudio(file_name, **ffmpeg_options), data=video)
                    players.append(player)
                    video_player_and_channel = [player, channel, file_name]
                    if guild_id in queued:
                        if queued[guild_id] is not None:
                            queued[guild_id].append(video_player_and_channel)
                    else:
                        queued[guild_id] = [video_player_and_channel]
                    try:
                        files_in_process_of_queue.remove(file_name)
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:  # several videos
            for video_entry in data['entries']:
                await add_video(video_entry)
        else:
            await add_video(data)  # only 1 video
        return players  # return added players
