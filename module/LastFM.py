import discord
from discord.ext import commands
from module import events, logger as log
from Utility import resources as ex
import typing


class LastFM(commands.Cog):
    def __init__(self):
        self.user_not_found = "That user was not found. Refer to `setfm` to link an account."
        self.user_does_not_exist = "That discord user does not have a Last FM account attached. Refer to `setfm`."

    @staticmethod
    def get_recent_tracks(response, limit):
        """Get limit amount of tracks"""
        image_url = False
        album_name = False
        list_of_tracks = response['recenttracks']['track']
        counter = 0
        tracks_and_titles = []
        for track in list_of_tracks:
            counter += 1
            if counter <= limit:
                title = f"**#{counter} **"
                try:
                    date = track['date']['#text']
                    album_name = track['album']['#text']
                    image_url = (track['image'][2])['#text']
                except Exception as e:
                    date = "Currently Playing"
                main_desc = f"""
                **[{track['name']} by {track['artist']['#text']}]({track['url']})**
                """
                if album_name:
                    main_desc += f"**Album: {album_name}**\n"
                main_desc += f"**Listened on {date}.**"
                tracks_and_titles.append([title, main_desc, image_url])
        return tracks_and_titles

    @staticmethod
    async def create_fm_embed(title, stats_info, inline=False, individual=False):
        """Create and return an embed that matches the format for FM tracks and artists."""
        embed = await ex.create_embed(title=title, color=ex.get_random_color())
        for name, value in stats_info:
            if not individual:
                embed.add_field(name=name, value=value, inline=inline)
            else:
                embed.description = value
        return embed

    async def set_user(self, ctx, org_user, time_period=None):
        """Returns the username that is sent to the LastFM API."""
        # this condition is set in place to make the parameters reversible
        if type(time_period) is discord.User:
            org_user = time_period
        if not time_period:
            if self.set_period(None, org_user) != "overall":
                org_user = None
        if not org_user:
            user = await ex.u_last_fm.get_fm_username(ctx.author.id)
        elif type(org_user) is str:
            return org_user
        elif type(org_user) is discord.User:
            user = await ex.u_last_fm.get_fm_username(org_user.id)
            if not user:
                user = org_user.name
        else:
            return
        return user

    @staticmethod
    def set_period(user, time_period):
        """Take several inputs of time and return the input that is allowed by Last FM"""
        # this condition is set in place to make the parameters reversible
        if type(time_period) is discord.User:
            time_period = user
        if not time_period:
            time_period = user
        weeks = ["7day", "7days", "week", "weekly"]
        month = ["1month", "4weeks", "4week", "month", "mo"]
        three_months = ["3month", "3months", "3mo"]
        six_months = ["6month", "6months", "6mo"]
        years = ["12month", "year", "12months", "12mo", "yr"]
        if time_period in weeks:
            return weeks[0]
        elif time_period in month:
            return month[0]
        elif time_period in three_months:
            return three_months[0]
        elif time_period in six_months:
            return six_months[0]
        elif time_period in years:
            return years[0]
        else:
            return 'overall'

    @commands.command()
    async def fm(self, ctx, user: typing.Union[discord.User, str] = None):
        """Get information about a Last FM account by a discord user or a Last FM username.
        [Format: %fm @user]."""
        try:
            user = await self.set_user(ctx, user)
            if user is not None:
                response = await ex.u_last_fm.get_fm_response('user.getinfo', user)
                user_info = response['user']
                title_desc = f"""Age: {user_info['age']}

                Country: {user_info['country']}

                Gender: {user_info['gender']}

                Name: {user_info['name']}

                Total PlayCount: {user_info['playcount']}

                Playlists: {user_info['playlists']}

                URL: {user_info['url']}                
                """
                title = f"{user}'s LastFM Account Info"
                embed = await ex.create_embed(title=title, color=ex.get_random_color(), title_desc=title_desc)
                await ctx.send(embed=embed)
            else:
                await events.Events.error(ctx, self.user_does_not_exist)
        except KeyError:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command()
    async def setfm(self, ctx, username):
        """Attach a Last FM username to your Discord Account.
        [Format: %setfm username]."""
        try:
            response = await ex.u_last_fm.set_fm_username(ctx.author.id, username)  # can be an Exception or True
            if response:
                await ctx.send(f"> **{username} (last.fm) is now attached to {ctx.author.display_name}.**")
            else:
                await events.Events.error(ctx, response)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command(aliases=['recents', 'rt'])
    async def recenttracks(self, ctx, user: typing.Union[discord.User, str] = None):
        """Get the recent tracks of a Last FM Account by a discord user or a Last FM username"""
        try:
            user = await self.set_user(ctx, user)
            response = await ex.u_last_fm.get_fm_response('user.getRecentTracks', user)
            tracks_and_titles = self.get_recent_tracks(response, limit=10)
            await ctx.send(embed=await self.create_fm_embed(f"{user} **Recent Tracks **", tracks_and_titles, inline=True))
        except KeyError as e:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command()
    async def recent(self, ctx, user: typing.Union[discord.User, str] = None):
        """Get the last listened track of a Last FM Account by a discord user or a Last FM username"""
        try:
            user = await self.set_user(ctx, user)
            response = await ex.u_last_fm.get_fm_response('user.getRecentTracks', user)
            tracks_and_titles = self.get_recent_tracks(response, limit=1)
            embed = await self.create_fm_embed(f"{user}'s **Most Recent Track**", tracks_and_titles, individual=True)
            image_url = tracks_and_titles[0][2]
            if image_url:
                embed.set_thumbnail(url=tracks_and_titles[0][2])
            await ctx.send(embed=embed)
        except KeyError:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command(aliases=['ta'])
    async def topartists(self, ctx, user: typing.Union[discord.User, str] = None, time_period: typing.Union[discord.User, str] = None):
        """See the top artists of a Last FM Account by a discord user or a Last FM username
        [Format: %topartists (username) (time period)]
        Time period options are ``overall | week | month | 3month | 6month | year``. Time period defaults to overall."""
        try:
            user, time_period = await self.set_user(ctx, user, time_period), self.set_period(user, time_period)
            response = await ex.u_last_fm.get_fm_response('user.getTopArtists', user, limit=10, time_period=time_period)
            list_of_artists = response['topartists']['artist']
            counter = 0
            artist_and_titles = []
            for artist in list_of_artists:
                counter += 1
                title = f"**#{counter} ({artist['playcount']} plays)**"
                artist_name = f"**[{artist['name']}]({artist['url']})**"
                artist_and_titles.append([title, artist_name])
            await ctx.send(embed=await self.create_fm_embed(f"{user} **Top Artists ({time_period})**", artist_and_titles))
        except KeyError:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command(aliases=['tt'])
    async def toptracks(self, ctx, user: typing.Union[discord.User, str] = None, time_period: typing.Union[discord.User, str] = None):
        """See the top tracks of a Last FM Account by a discord user or a Last FM username
        [Format: %toptracks (username) (time period)]
        Time period options are ``overall | week | month | 3month | 6month | year``.
        Time period defaults to overall."""
        try:
            user, time_period = await self.set_user(ctx, user, time_period), self.set_period(user, time_period)
            response = await ex.u_last_fm.get_fm_response('user.getTopTracks', user, limit=10, time_period=time_period)
            list_of_tracks = response['toptracks']['track']
            counter = 0
            tracks_and_titles = []
            for track in list_of_tracks:
                counter += 1
                title = f"**#{counter} ({track['playcount']} plays)**"
                artist_name = f"**[{track['name']} by {track['artist']['name']}]({track['url']})**"
                tracks_and_titles.append([title, artist_name])
            await ctx.send(embed=await self.create_fm_embed(f"{user} **Top Tracks ({time_period})**", tracks_and_titles))
        except KeyError:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(
                f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")

    @commands.command(aliases=["tal"])
    async def topalbums(self, ctx, user: typing.Union[discord.User, str] = None, time_period: typing.Union[discord.User, str] = None):
        """See the top albums of a Last FM Account by a discord user or a Last FM username
        [Format: %topalbums (username) (time period)]
        Time period options are ``overall | week | month | 3month | 6month | year``.
        Time period defaults to overall."""
        try:
            user, time_period = await self.set_user(ctx, user, time_period), self.set_period(user, time_period)
            response = await ex.u_last_fm.get_fm_response('user.getTopAlbums', user, limit=10, time_period=time_period)
            list_of_albums = response['topalbums']['album']
            counter = 0
            tracks_and_titles = []
            for album in list_of_albums:
                counter += 1
                title = f"**#{counter} ({album['playcount']} plays)**"
                artist_name = f"**[{album['name']} by {album['artist']['name']}]({album['url']})**"
                tracks_and_titles.append([title, artist_name])
            await ctx.send(embed=await self.create_fm_embed(f"{user} **Top Albums ({time_period})**", tracks_and_titles))
        except KeyError:
            await events.Events.error(ctx, self.user_not_found)
        except Exception as e:
            log.console(e)
            await ctx.send(
                f"> **Something went wrong.. Please {await ex.get_server_prefix_by_context(ctx)}report it.**")
