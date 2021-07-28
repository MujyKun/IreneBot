import discord
from discord.ext import commands, tasks
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
from ksoftapi import NoResults
import wavelink
from random import shuffle
import re


class Music(commands.Cog):
    def __init__(self, ex):
        """
        :param ex: Utility object.
        """
        self.ex: Utility = ex
        self.ex.wavelink = wavelink.Client(bot=self.ex.client)
        self.URL_REGEX = re.compile(r'https?://(?:www\.)?.+')

        # Modified version of wavelink to not have to wait till d.py cache loads.

        # IMPORTANT: THIS BOT ID MUST BE ACCURATE FOR THE MUSIC PLAYER TO WORK
        # IMPORTANT: THIS BOT ID MUST BE ACCURATE FOR THE MUSIC PLAYER TO WORK
        # IMPORTANT: THIS BOT ID MUST BE ACCURATE FOR THE MUSIC PLAYER TO WORK

        # The Bot ID is used across the nodes.
        self.ex.wavelink.bot_user_id = self.ex.keys.bot_id
        self.ex.client.loop.create_task(self.ex.u_music.start_nodes())

    async def cog_check(self, ctx):
        """A local check for this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    @commands.command(aliases=["connect"])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """
        Makes the Bot join the current voice channel.

        [Format: %join [Voice Channel]]
        """
        await self.ex.u_music.connect_to_vc(ctx, channel)

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, volume: int):
        """Change the player's volume.

        [Format: %volume <volume>]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        volume = 100 if volume > 100 else volume
        volume = 0 if volume < 0 else volume
        await player.set_volume(volume)

        msg = await self.ex.get_msg(ctx, "music", "volume_status", ["result", volume])
        return await ctx.send(msg)

    @commands.command(aliases=["leave", "disconnect"])
    async def stop(self, ctx):
        """
        Makes the bot leave the current voice channel.

        [Format: %stop]
        [Aliases: leave, disconnect]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        # destroy the player
        await self.ex.u_music.destroy_player(player)

        msg = await self.ex.get_msg(ctx, "music", "disconnected")
        return await ctx.send(msg)

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, query: str):
        """Play a song based on a search query.

        [Format: %play (query)]
        """
        query = query.strip('<>')
        if not self.URL_REGEX.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.ex.wavelink.get_tracks(query)

        if not tracks:
            # no tracks exist based on the search query.
            msg = await self.ex.get_msg(ctx, "music", "no_songs")
            return await ctx.send(msg)

        player = self.ex.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            # connect to voice channel.
            await ctx.invoke(self.join)

        if not hasattr(player, "playlist"):
            # create an empty playlist.
            player.playlist = []

        if isinstance(tracks, wavelink.TrackPlaylist):
            # add an entire playlist to the player playlist.
            list_of_tracks = tracks.tracks

            for track in list_of_tracks:
                # every track in the playlist will have the Context it was created in.
                track.info["ctx"] = ctx

            player.playlist = player.playlist + list_of_tracks
            msg = await self.ex.get_msg(ctx, "music", "added_to_queue", ["result", f"{len(list_of_tracks)} songs"])
            await ctx.send(msg)
        else:
            track = tracks[0]
            # add the Context that had the track created.
            track.info["ctx"] = ctx

            # add a single track to the player playlist.
            msg = await self.ex.get_msg(ctx, "music", "added_to_queue", ["result", str(track)])
            await ctx.send(msg)
            player.playlist.append(tracks[0])

        # start the player loop if it was not already started.
        await self.ex.u_music.start_player_loop(player)

    @commands.command()
    async def pause(self, ctx):
        """Pause the player.

        [Format: %pause]
        """
        await self.ex.u_music.toggle_pause(ctx, pause=True)

    @commands.command(aliases=["unpause"])
    async def resume(self, ctx):
        """Resume a paused player.

        [Format: %resume]
        [Aliases: unpause]
        """
        await self.ex.u_music.toggle_pause(ctx, pause=False)

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song on the player.

        [Format: %skip]
        """
        controller = self.ex.u_music.get_controller(ctx)
        controller.skipped = True
        controller.next.set()

    @commands.command()
    async def lyrics(self, ctx, *, song_query: str):
        """
        Get the lyrics of a song (From https://api.ksoft.si)

        [Format: %lyrics (song)]
        """
        if not self.ex.keys.lyric_client:
            log.console(f"There is no API Key currently set for the Lyrics and the Developer is working on it.")
            return await ctx.send(await self.ex.get_msg(ctx, "music", "no_api_key"))
        try:
            results = await self.ex.keys.lyric_client.music.lyrics(song_query)
        except NoResults:
            log.console(f"No lyrics were found for {song_query}.")
            return await ctx.send(await self.ex.get_msg(ctx, "music", "no_lyrics"))
        except Exception as e:
            await ctx.send(await self.ex.get_msg(ctx, "general", "main_error"))
            log.console(e)
        else:
            song = results[0]

            split_amount = 1500

            possible_pages = (len(song.lyrics) // split_amount) or 1
            embed_list = []
            for page_count in range(possible_pages + 1):
                start_index = split_amount * page_count
                end_index = split_amount + start_index

                if end_index > len(song.lyrics):
                    end_index = len(song.lyrics)

                try:
                    page = song.lyrics[start_index:end_index]
                except IndexError:
                    continue

                if not len(page):
                    continue

                embed = await self.ex.create_embed(title=f"{song.name} by {song.artist}",
                                                   color=self.ex.get_random_color(),
                                                   title_desc=page,
                                                   footer_desc="Thanks for using Irene! Lyrics API is from ksoft.si.")
                embed_list.append(embed)

            msg = await ctx.send(embed=embed_list[0])
            if len(embed_list) > 1:
                return await self.ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command()
    async def shuffle(self, ctx):
        """
        Shuffle the current playlist.

        [Format: %shuffle]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        if hasattr(player, "playlist"):
            shuffle(player.playlist)

        msg = await self.ex.get_msg(ctx, "music", "shuffled")
        return await ctx.send(msg)

    @commands.command(aliases=["q", "list"])
    async def queue(self, ctx):
        """
        Displays the currently queued songs in the player.

        [Format: %queue]
        [Aliases: q, list]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        embed_list = await self.ex.u_music.create_queue_embed(player)

        if not embed_list:
            msg = await self.ex.get_msg(ctx, "music", "empty_queue")
            return await ctx.send(msg)

        msg = await ctx.send(embed=embed_list[0])
        if len(embed_list) > 1:
            await self.ex.check_left_or_right_reaction_embed(msg, embed_list)

    @commands.command()
    async def remove(self, ctx, song_number: int):
        """
        Remove a song from the queue.

        [Format: %remove (song number)]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        if hasattr(player, "playlist"):
            try:
                player.playlist.pop(song_number - 1)
            except IndexError:
                msg = await self.ex.get_msg(ctx, "general", "out_of_range")
                return await ctx.send(msg)
        else:
            msg = await self.ex.get_msg(ctx, "music", "empty_queue")
            return await ctx.send(msg)

    @commands.command(aliases=["skipto"])
    async def move(self, ctx, song_number: int):
        """
        Make a song the next to play without skipping the current song.

        [Format: %move (song number)]
        [Aliases: skipto]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)
        if hasattr(player, "playlist"):
            try:
                track: wavelink.Track = player.playlist.pop(song_number - 1)
                player.playlist.insert(0, track)
                msg = await self.ex.get_msg(ctx, "music", "moved_song", [["title", track.title],
                                                                         ["artist", track.author]])
                return await ctx.send(msg)
            except IndexError:
                msg = await self.ex.get_msg(ctx, "general", "out_of_range")
                return await ctx.send(msg)
        else:
            msg = await self.ex.get_msg(ctx, "music", "empty_queue")
            return await ctx.send(msg)

    @commands.command()
    async def loop(self, ctx):
        """Loop the current playlist and any songs added.

        [Format: %loop]
        """
        player = self.ex.wavelink.get_player(ctx.guild.id)

        if hasattr(player, "loop"):
            player.loop = not player.loop
        else:
            player.loop = True
        loop_status = "now looping" if player.loop else "no longer looping"
        msg = await self.ex.get_msg(ctx, "music", "player_status", ["result", loop_status])
        return await ctx.send(msg)