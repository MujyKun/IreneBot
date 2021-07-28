import discord
from discord.ext import commands
from IreneUtility.util import u_logger as log
from IreneUtility.Utility import Utility
from ksoftapi import NoResults
import wavelink
from random import shuffle


class Music(commands.Cog):
    def __init__(self, ex):
        """
        :param ex: Utility object.
        """
        self.ex: Utility = ex

        self.ex.client.id = self.ex.keys.bot_id  # this is very important if the bot is not fully loaded.

        self.ex.client.loop.create_task(self.ex.u_music.start_nodes())

    async def cog_check(self, ctx):
        """A local check for this cog."""
        if ctx.invoked_with and ctx.invoked_with == 'help':
            return True

        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        log.console(f'Wavelink Node: {node.identifier} is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        controller = self.ex.u_music.get_controller(player)
        controller.next.set()

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, track, threshold):
        print(track, threshold)

    @commands.command(aliases=["connect"])
    async def join(self, ctx):
        """
        Makes the Bot join the current voice channel.

        [Format: %join [Voice Channel]]
        """
        await self.ex.u_music.connect_to_vc(ctx)

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, volume: int):
        """Change the player's volume.

        [Format: %volume <volume>]
        """
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return
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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return
        # destroy the player
        await self.ex.u_music.destroy_player(player)

        msg = await self.ex.get_msg(ctx, "music", "disconnected")
        return await ctx.send(msg)

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, source: str):
        """Play a song based on a search query.

        [Format: %play (query)]
        """
        node_available = False
        for node in self.ex.u_music.node_pool.nodes.values():
            if node.is_connected():
                node_available = True
                break

        if not node_available:
            msg = await self.ex.get_msg(ctx, "music", "no_nodes")
            return await ctx.send(msg)
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return

        source = await self.ex.u_music.search_query(source)

        if not source:
            # no tracks exist based on the search query.
            msg = await self.ex.get_msg(ctx, "music", "no_songs")
            return await ctx.send(msg)

        if not hasattr(player, "playlist"):
            # create an empty playlist.
            player.playlist = []
        try:
            if isinstance(source, (wavelink.YouTubePlaylist, list)):
                # add an entire playlist to the player playlist.
                if isinstance(source, wavelink.YouTubePlaylist):
                    list_of_tracks = source.tracks
                else:
                    list_of_tracks = source

                for track in list_of_tracks:
                    # every track in the playlist will have the Context it was created in.
                    track.info["ctx"] = ctx

                player.playlist = player.playlist + list_of_tracks
                length_of_tracks = len(list_of_tracks)
                result = f"{length_of_tracks} songs" if length_of_tracks > 1 else str(list_of_tracks[0])
                msg = await self.ex.get_msg(ctx, "music", "added_to_queue", ["result", f"{result}"])
                await ctx.send(msg)
            else:
                # add the Context that had the track created.
                source.info["ctx"] = ctx

                # add a single track to the player playlist.
                msg = await self.ex.get_msg(ctx, "music", "added_to_queue", ["result", str(source)])
                await ctx.send(msg)
                player.playlist.append(source)

            # start the player loop if it was not already started.
            await self.ex.u_music.start_player_loop(player)
            await self.ex.u_music.remove_partial_tracks(player)

        except Exception as e:
            await ctx.send(f"ERROR: {e}")
            log.console(e, method=self.play)

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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return
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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return
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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return

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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return

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
        try:
            player = await self.ex.u_music.connect_to_vc(ctx)
        except discord.NotFound:
            return

        if hasattr(player, "loop"):
            player.loop = not player.loop
        else:
            player.loop = True
        loop_status = "now looping" if player.loop else "no longer looping"
        msg = await self.ex.get_msg(ctx, "music", "player_status", ["result", loop_status])
        return await ctx.send(msg)
