from util import exceptions, logger as log, local_cache
from typing import TYPE_CHECKING
from discord.ext.commands import Context
from Weverse.weverseasync import WeverseAsync
import discord
import random
import asyncio
import os
import tweepy



# do not import in runtime. This is used for type-hints.
if TYPE_CHECKING:
    import util
    from aiohttp import ClientSession

"""
Utility.py
Resource Center for Irene -> Essentially serves as a client for Irene.
Any potentially useful/repeated functions will end up here
All categorized utility methods will be placed as objects prefixed with u_ as a property.
"""


# noinspection PyBroadException,PyPep8
class Utility:
    def __init__(self):
        # A lot of these properties may be created via client side
        # in order to make Utility more portable when needed and client friendly.
        self.test_bot = None  # this is changed on the client side in run.py
        self.client: discord.AutoShardedClient = None  # discord.py client
        self.session: ClientSession = None  # aiohttp client session
        self.conn = None  # db connection
        self.discord_cache_loaded = False  # d.py library cache finished loading
        self.irene_cache_loaded = False  # IreneBot cache finished loading
        self.cache = local_cache.Cache()  # instance for loaded cache
        self.temp_patrons_loaded = False
        self.running_loop = None  # current asyncio running loop
        self.thread_pool = None  # ThreadPoolExecutor for operations that block the event loop.
        self.keys = None  # access to keys file
        self.sql: util.sql.SQL = None  # abstract class hidden as concrete sql class -> manages queries

        self.api: tweepy.API = None
        self.loop_count = 0
        self.recursion_limit = 10000
        self.api_issues = 0  # api issues in a given minute
        self.max_idol_post_attempts = 10  # 100 was too much
        self.twitch_guild_follow_limit = 2
        self.weverse_client: WeverseAsync = None

        self.exceptions = exceptions  # custom error handling
        self.twitch_token = None  # access tokens are set everytime the token is refreshed.

        self.events = None  # Client-Sided Events class
        """
        IMPORTANT: This design implementation is a hack for circular imports.
        The intended use is to allow a singular object to manage the entire Utility.
        """
        # SubClass Objects -- Instances given in client's run.py
        self.u_database: util.database.DataBase = None
        self.u_cache: util.cache.Cache = None
        self.u_miscellaneous: util.miscellaneous.Miscellaneous = None
        self.u_blackjack: util.blackjack.BlackJack = None
        self.u_group_members: util.groupmembers.GroupMembers = None
        self.u_logging: util.logging.Logging = None
        self.u_twitter: util.twitter.Twitter = None
        self.u_last_fm: util.lastfm.LastFM = None
        self.u_patreon: util.patreon.Patreon = None
        self.u_moderator: util.moderator.Moderator = None
        self.u_custom_commands: util.customcommands.CustomCommands = None
        self.u_bias_game: util.biasgame.BiasGame = None
        self.u_data_dog: util.datadog.DataDog = None
        self.u_weverse: util.weverse.Weverse = None
        self.u_self_assign_roles: util.selfassignroles.SelfAssignRoles = None
        self.u_reminder: util.reminder.Reminder = None
        self.u_guessinggame: util.guessinggame.GuessingGame = None
        self.u_twitch: util.twitch.Twitch = None
        self.u_gacha: util.gacha.Gacha = None

        # Util Directory that contains needed objects as attributes.
        self.u_objects: util.objects = None

    def define_properties(self, keys, events):
        """
        Define client-sided properties in Utility.

        :param keys: Access to the keys file.
        :param events: Access to the client-sided events class
        """
        self.keys = keys

        self.client = keys.client  # set discord client

        self.session = keys.client_session  # set aiohttp client session

        # set weverse client
        self.weverse_client = WeverseAsync(authorization=keys.weverse_auth_token, web_session=self.session,
                                           verbose=True, loop=asyncio.get_event_loop())

        # create twitter auth
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.events = events

    async def get_user(self, user_id):
        """Creates a user if not created and adds it to the cache, then returns the user object.

        :rtype: util.objects.User
        """
        user = self.cache.users.get(user_id)
        if not user:
            user = self.u_objects.User(user_id)
            self.cache.users[user_id] = user
        return user

    @staticmethod
    def first_result(record):
        """Returns the first item of a record if there is one."""
        if record:
            return record[0]

    @staticmethod
    def remove_commas(amount):
        """Remove all commas from a string and make it an integer."""
        return int(amount.replace(',', ''))

    async def kill_api(self):
        """restart the api"""
        source_link = "http://127.0.0.1:5123/restartAPI"
        async with self.session.get(source_link):
            log.console("Restarting API.")

    @staticmethod
    async def get_server_id(ctx):
        """Get the server id by context or message."""
        # make sure ctx.guild exists in the case discord.py cache isn't loaded.
        if ctx.guild:
            return ctx.guild.id

    async def get_dm_channel(self, user_id=None, user=None):
        try:
            if user_id:
                # user = await self.client.fetch_user(user_id)
                user = self.client.get_user(user_id)
                if not user:
                    user = await self.client.fetch_user(user_id)
            dm_channel = user.dm_channel
            if not dm_channel:
                await user.create_dm()
                dm_channel = user.dm_channel
            return dm_channel
        except discord.errors.HTTPException as e:
            log.console(f"{e} - get_dm_channel 1")
            return
        except AttributeError:
            return
        except Exception as e:
            log.console(f"{e} - get_dm_channel 2")
            return

    @staticmethod
    async def check_interaction_enabled(ctx=None, server_id=None, interaction=None):
        """Check if the interaction is disabled in the current server, RETURNS False when it is disabled."""
        if not server_id and not interaction:
            server_id = await Utility.get_server_id(ctx)
            interaction = ctx.command.name
        interactions = await resources.u_miscellaneous.get_disabled_server_interactions(server_id)
        if not interactions:
            return True
        interaction_list = interactions.split(',')
        if interaction in interaction_list:
            # normally we would alert the user that the command is disabled, but discord.py uses this function.
            return False
        return True

    def check_if_mod(self, ctx, mode=0):  # as mode = 1, ctx is the author id.
        """Check if the user is a bot mod/owner."""
        if not mode:
            user_id = ctx.author.id
            return user_id in self.keys.mods_list or user_id == self.keys.owner_id
        else:
            return ctx in self.keys.mods_list or ctx == self.keys.owner_id

    def get_ping(self):
        """Get the client's ping."""
        return int(self.client.latency * 1000)

    @staticmethod
    def get_random_color():
        """Retrieves a random hex color."""
        r = lambda: random.randint(0, 255)
        return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present

    async def create_embed(self, title="Irene", color=None, title_desc=None, footer_desc="Thanks for using Irene!"):
        """Create a discord Embed."""
        if not color:
            color = self.get_random_color()
        if not title_desc:
            embed = discord.Embed(title=title, color=color)
        else:
            embed = discord.Embed(title=title, color=color, description=title_desc)
        embed.set_author(name="Irene", url=self.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def wait_for_reaction(self, msg, user_id, reaction_needed):
        """Wait for a user's reaction on a message."""
        def react_check(reaction_used, user_reacted):
            return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

        try:
            # noinspection PyUnusedLocal
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=react_check)
            return True
        except asyncio.TimeoutError:
            await msg.delete()
            return False

    async def set_embed_author_and_footer(self, embed, footer_message):
        """Sets the author and footer of an embed."""
        embed.set_author(name="Irene", url=self.keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_message,
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def check_left_or_right_reaction_embed(self, msg, embed_lists, original_page_number=0, reaction1=None,
                                                 reaction2=None):
        """This method is used for going between pages of embeds."""
        reaction1 = self.keys.previous_emoji
        reaction2 = self.keys.next_emoji
        await msg.add_reaction(reaction1)  # left arrow by default
        await msg.add_reaction(reaction2)  # right arrow by default

        def reaction_check(user_reaction, reaction_user):
            """Check if the reaction is the right emoji and right user."""
            return ((user_reaction.emoji == '➡') or (
                        user_reaction.emoji == '⬅')) and reaction_user != msg.author and user_reaction.message.id == msg.id

        async def change_page(c_page):
            """Waits for the user's reaction and then changes the page based on their reaction."""
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=reaction_check)
                if reaction.emoji == '➡':
                    c_page += 1
                    if c_page >= len(embed_lists):
                        c_page = 0  # start from the beginning of the list
                    await msg.edit(embed=embed_lists[c_page])

                elif reaction.emoji == '⬅':
                    c_page -= 1
                    if c_page < 0:
                        c_page = len(embed_lists) - 1  # going to the end of the list
                    await msg.edit(embed=embed_lists[c_page])

                # await msg.clear_reactions()
                # await msg.add_reaction(reaction1)
                # await msg.add_reaction(reaction2)
                # only remove user's reaction instead of all reactions
                try:
                    await reaction.remove(user)
                except:
                    pass
                await change_page(c_page)
            except Exception as e:
                log.console(f"check_left_or_right_reaction_embed - {e}")
                await change_page(c_page)
        await change_page(original_page_number)

    async def get_server_prefix(self, server_id):
        """Gets the prefix of a server by the server ID."""
        prefix = self.cache.server_prefixes.get(server_id)
        if not prefix:
            return self.keys.bot_prefix
        else:
            return prefix

    async def get_server_prefix_by_context(self, ctx):  # this can also be passed in as a message
        """Gets the prefix of a server by the context."""
        try:
            prefix = await self.get_server_prefix(ctx.guild.id)
            return prefix
        except:
            return self.keys.bot_prefix

    @staticmethod
    def check_file_exists(file_name):
        return os.path.isfile(file_name)

    async def stop_game(self, ctx, games):
        """Delete an ongoing game."""
        is_moderator = await self.u_miscellaneous.check_if_moderator(ctx)
        game = self.find_game(ctx.channel, games)
        if game:
            if ctx.author.id == game.host or is_moderator:
                games.remove(game)
                return await game.end_game()
            else:
                return await ctx.send("> You must be a moderator or the host of the game in order to end the game.")
        return await ctx.send("> No game is currently in session.")

    @staticmethod
    def find_game(channel, games):
        """Return a game from a list of game objects if it exists in the channel."""
        for game in games:
            if game.channel == channel:
                return game

    async def check_user_in_support_server(self, ctx):
        """Checks if a user is in the support server.
        If the support server is not in cache, it will count as if the user is in the server.
        d.py cache must be fully loaded before this is properly checked.
        """
        if not self.discord_cache_loaded:
            return True

        support_server = self.client.get_guild(self.keys.bot_support_server_id)
        if not support_server:
            return True
        if support_server.get_member(ctx.author.id):
            return True
        user = await self.get_user(ctx.author.id)
        msg = await self.replace(self.cache.languages[user.language]['utility']['join_support_server_feature'],
                           [['bot_name', self.keys.bot_name], ['support_server_link', self.keys.bot_support_server_link]])
        await ctx.send(msg)

    @staticmethod
    async def replace(text: str, inputs_to_change: list) -> str:
        """
        Replace custom text from language packs for several keywords at once.
        :param text: The text that requires replacing.
        :param inputs_to_change: A list of lists with the 0th index as the keyword to replace, and the 1st index
        as the content.
        :return:
        """
        # convert the input to a list of lists if it is not already.
        if not isinstance(inputs_to_change[0], list):
            inputs_to_change = [[inputs_to_change[0], inputs_to_change[1]]]

        # custom input is always surrounded by curly braces {}
        for input_list in inputs_to_change:
            # make sure braces do not already exist in the input
            keyword = input_list[0]
            custom_input = str(input_list[1])

            keyword = keyword.replace("{", "")
            keyword = keyword.replace("}", "")
            text = text.replace("{" + keyword + "}", custom_input)

        return text

    async def get_msg(self, user, module, keyword) -> str:
        """Get a msg from a user's language.

        :param user: User ID, Irene User object, or Context object
        :param module: Module name (Case Sensitive)
        :param keyword: Key attached to the string
        :return: message string from language pack.
        """
        # allow ctx as input to the user
        if isinstance(user, Context):
            user = user.author.id

        # allow user id as input to the user.
        if not isinstance(user, self.u_objects.User):
            user = await self.get_user(user)

        return self.cache.languages[user.language][module][keyword]


resources = Utility()
