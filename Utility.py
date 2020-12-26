from module import keys, logger as log, cache, exceptions
from discord.ext import tasks
from PIL import Image
from datadog import initialize, api
from Weverse.weverseasync import WeverseAsync
import datetime
import discord
import random
import asyncio
import os
import math
import tweepy
import json
import time
import aiofiles
import re
import pytz
import parsedatetime
import locale

"""
Utility.py
Resource Center for Irene -> Essentially serves as a client for Irene.
Any potentially useful/repeated functions will end up here
"""


class Utility:
    def __init__(self):
        self.test_bot = None  # this is changed in run.py
        self.client = keys.client
        self.session = keys.client_session
        self.conn = None  # db connection
        self.discord_cache_loaded = False
        self.cache = cache.Cache()
        self.temp_patrons_loaded = False
        self.running_loop = None  # current asyncio running loop
        self.thread_pool = None  # ThreadPoolExecutor for operations that block the event loop.
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.loop_count = 0
        self.recursion_limit = 10000
        self.api_issues = 0
        self.weverse_client = WeverseAsync(authorization=keys.weverse_auth_token, web_session=self.session,
                                           verbose=True, loop=asyncio.get_event_loop())
        self.exceptions = exceptions

        # SubClass Objects
        self.u_database = None
        self.u_cache = None
        self.u_currency = None
        self.u_miscellaneous = None
        self.u_blackjack = None
        self.u_levels = None
        self.u_group_members = None
        self.u_logging = None
        self.u_twitter = None
        self.u_last_fm = None
        self.u_patreon = None
        self.u_moderator = None
        self.u_custom_commands = None
        self.u_bias_game = None
        self.u_data_dog = None
        self.u_weverse = None
        self.u_self_assign_roles = None
        self.u_reminder = None

    @staticmethod
    def first_result(record):
        """Returns the first item of a record if there is one."""
        if not record:
            return
        else:
            return record[0]

    @staticmethod
    def remove_commas(amount):
        """Remove all commas from a string and make it an integer."""
        return int(amount.replace(',', ''))

    async def kill_api(self):
        """restart the api"""
        source_link = "http://127.0.0.1:5123/restartAPI"
        async with self.session.get(source_link) as resp:
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
            dm_channel = user.dm_channel
            if not dm_channel:
                await user.create_dm()
                dm_channel = user.dm_channel
            return dm_channel
        except discord.errors.HTTPException as e:
            log.console(f"{e} - get_dm_channel 1")
            return None
        except Exception as e:
            log.console(f"{e} - get_dm_channel 2")
            return None

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

    @staticmethod
    def check_if_mod(ctx, mode=0):  # as mode = 1, ctx is the author id.
        """Check if the user is a bot mod/owner."""
        if not mode:
            user_id = ctx.author.id
            return user_id in keys.mods_list or user_id == keys.owner_id
        else:
            return ctx in keys.mods_list or ctx == keys.owner_id

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
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def wait_for_reaction(self, msg, user_id, reaction_needed):
        """Wait for a user's reaction on a message."""
        def react_check(reaction_used, user_reacted):
            return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=react_check)
            return True
        except asyncio.TimeoutError:
            await msg.delete()
            return False

    async def check_left_or_right_reaction_embed(self, msg, embed_lists, original_page_number=0, reaction1=keys.previous_emoji, reaction2=keys.next_emoji):
        """This method is used for going between pages of embeds."""
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
                except Exception as e:
                    pass
                await change_page(c_page)
            except Exception as e:
                log.console(f"check_left_or_right_reaction_embed - {e}")
                await change_page(c_page)
        await change_page(original_page_number)

    @staticmethod
    async def set_embed_author_and_footer(embed, footer_message):
        """Sets the author and footer of an embed."""
        embed.set_author(name="Irene", url=keys.bot_website,
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_message,
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def get_server_prefix(self, server_id):
        """Gets the prefix of a server by the server ID."""
        prefix = self.cache.server_prefixes.get(server_id)
        if not prefix:
            return keys.bot_prefix
        else:
            return prefix

    async def get_server_prefix_by_context(self, ctx):  # this can also be passed in as a message
        """Gets the prefix of a server by the context."""
        try:
            prefix = await self.get_server_prefix(ctx.guild.id)
            return prefix
        except Exception as e:
            return keys.bot_prefix

    ###################
    # ## BLACKJACK ## #
    ###################

    async def check_in_game(self, user_id, ctx):  # this is meant for when it is accessed by commands outside of BlackJack.
        """Check if a user is in a game."""
        check = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) From blackjack.games WHERE player1 = $1 OR player2 = $1", user_id))
        if check:
            await ctx.send(f"> **{ctx.author}, you are already in a pending/active game. Please type {await self.get_server_prefix_by_context(ctx)}endgame.**")
            return True

    async def add_bj_game(self, user_id, bid, ctx, mode):
        """Add the user to a blackjack game."""
        await self.conn.execute("INSERT INTO blackjack.games (player1, bid1, channelid) VALUES ($1, $2, $3)", user_id, str(bid), ctx.channel.id)
        game_id = await self.get_game_by_player(user_id)
        if mode != "bot":
            await ctx.send(f"> **There are currently 1/2 members signed up for BlackJack. To join the game, please type {await self.get_server_prefix_by_context(ctx)}joingame {game_id} (bid)** ")

    async def process_bj_game(self, ctx, amount, user_id):
        """pre requisites for joining a blackjack game."""
        if amount >= 0:
            if not await self.check_in_game(user_id, ctx):
                if amount > await self.u_currency.get_balance(user_id):
                    await ctx.send(f"> **{ctx.author}, you can not bet more than your current balance.**")
                else:
                    return True
        else:
            await ctx.send(f"> **{ctx.author}, you can not bet a negative number.**")
        return False

    async def get_game_by_player(self, player_id):
        """Get the current game of a player."""
        return self.first_result(await self.conn.fetchrow("SELECT gameid FROM blackjack.games WHERE player1 = $1 OR player2 = $1", player_id))

    async def get_game(self, game_id):
        """Get the game from its ID"""
        return await self.conn.fetchrow("SELECT gameid, player1, player2, bid1, bid2, channelid FROM blackjack.games WHERE gameid = $1", game_id)

    async def add_player_two(self, game_id, user_id, bid):
        """Add a second player to a blackjack game."""
        await self.conn.execute("UPDATE blackjack.games SET player2 = $1, bid2 = $2 WHERE gameid = $3 ", user_id, str(bid), game_id)

    async def get_current_cards(self, user_id):
        """Get the current cards of a user."""
        in_hand = self.first_result(await self.conn.fetchrow("SELECT inhand FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if in_hand is None:
            return []
        return in_hand.split(',')

    async def check_player_standing(self, user_id):
        """Check if a player is standing."""
        return self.first_result(await self.conn.fetchrow("SELECT stand FROM blackjack.currentstatus WHERE userid = $1", user_id)) == 1

    async def set_player_stand(self, user_id):
        """Set a player to stand."""
        await self.conn.execute("UPDATE blackjack.currentstatus SET stand = $1 WHERE userid = $2", 1, user_id)

    async def delete_player_status(self, user_id):
        """Remove a player's status from a game."""
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", user_id)

    async def add_player_status(self, user_id):
        """Add a player's status to a game."""
        await self.delete_player_status(user_id)
        await self.conn.execute("INSERT INTO blackjack.currentstatus (userid, stand, total) VALUES ($1, $2, $2)", user_id, 0)

    async def get_player_total(self, user_id):
        """Get a player's total score."""
        return self.first_result(await self.conn.fetchrow("SELECT total FROM blackjack.currentstatus WHERE userid = $1", user_id))

    async def get_card_value(self, card):
        """Get the value of a card."""
        return self.first_result(await self.conn.fetchrow("SELECT value FROM blackjack.cards WHERE id = $1", card))

    async def get_all_cards(self):
        """Get all the cards from a deck."""
        card_tuple = await self.conn.fetch("SELECT id FROM blackjack.cards")
        all_cards = []
        for card in card_tuple:
            all_cards.append(card[0])
        return all_cards

    async def get_available_cards(self, game_id):  # pass in a list of card ids
        """Get the cards that are not occupied."""
        all_cards = await self.get_all_cards()
        available_cards = []
        game = await self.get_game(game_id)
        player1_cards = await self.get_current_cards(game[1])
        player2_cards = await self.get_current_cards(game[2])
        for card in all_cards:
            if card not in player1_cards and card not in player2_cards:
                available_cards.append(card)
        return available_cards

    async def get_card_name(self, card_id):
        """Get the name of a card."""
        return self.first_result(await self.conn.fetchrow("SELECT name FROM blackjack.cards WHERE id = $1", card_id))

    async def check_if_ace(self, card_id, user_id):
        """Check if the card is an ace and is not used."""
        aces = ["1", "14", "27", "40"]
        aces_used = await self.get_aces_used(user_id)
        if card_id in aces and card_id not in aces_used:
            aces_used.append(card_id)
            await self.set_aces_used(aces_used, user_id)
            return True
        return False

    async def set_aces_used(self, card_list, user_id):
        """Mark an ace as used."""
        separator = ','
        cards = separator.join(card_list)
        await self.conn.execute("UPDATE blackjack.currentstatus SET acesused = $1 WHERE userid = $2", cards, user_id)

    async def get_aces_used(self, user_id):
        """Get the aces that were changed from 11 to 1."""
        aces_used = self.first_result(await self.conn.fetchrow("SELECT acesused FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if aces_used is None:
            return []
        return aces_used.split(',')

    def check_if_bot(self, user_id):
        """Check if the player is a bot. (The bot would be Irene)"""
        return str(self.u_miscellaneous.get_int_index(keys.bot_id, 9)) in str(user_id)

    async def add_card(self, user_id):
        """Check status of a game, it's player, manages the bot that plays, and then adds a card."""
        end_game = False
        check = 0

        separator = ','
        current_cards = await self.get_current_cards(user_id)
        game_id = await self.get_game_by_player(user_id)
        game = await self.get_game(game_id)
        channel = await self.client.fetch_channel(game[5])
        stand = await self.check_player_standing(user_id)
        player1_score = await self.get_player_total(game[1])
        player2_score = await self.get_player_total(game[2])
        player1_cards = await self.get_current_cards(game[1])
        if not stand:
            available_cards = await self.get_available_cards(game_id)
            random_card = random.choice(available_cards)
            current_cards.append(str(random_card))
            cards = separator.join(current_cards)
            current_total = await self.get_player_total(user_id)
            random_card_value = await self.get_card_value(random_card)
            if current_total + random_card_value > 21:
                for card in current_cards:  # this includes the random card
                    if await self.check_if_ace(card, user_id) and check != 1:
                        check = 1
                        current_total = (current_total + random_card_value) - 10
                if check == 0:  # if there was no ace
                    current_total = current_total + random_card_value
            else:
                current_total = current_total + random_card_value
            await self.conn.execute("UPDATE blackjack.currentstatus SET inhand = $1, total = $2 WHERE userid = $3", cards, current_total, user_id)
            if current_total > 21:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if player1_score > 21 and current_total >= 16:
                        end_game = True
                        await self.set_player_stand(game[1])
                        await self.set_player_stand(game[2])
                    elif player1_score > 21 and current_total < 16:
                        await self.add_card(game[2])
                    elif player1_score < 22 and current_total > 21:
                        pass
                    else:
                        end_game = True
                elif self.check_if_bot(game[2]) and not self.check_if_bot(user_id):  # if user_id is not the bot
                    if player2_score < 16:
                        await self.add_card(game[2])
                    else:
                        await self.set_player_stand(user_id)
                        await self.set_player_stand(game[2])
                        end_game = True
            else:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if current_total < 16143478541328187392 and len(player1_cards) > 2:
                        await self.add_card(game[2])
                    if await self.check_player_standing(game[1]) and current_total >= 16:
                        end_game = True
            if not self.check_if_bot(user_id):
                if self.check_if_bot(game[2]):
                    await self.send_cards_to_channel(channel, user_id, random_card, True)
                else:
                    await self.send_cards_to_channel(channel, user_id, random_card)
        else:
            await channel.send(f"> **You already stood.**")
            if await self.check_game_over(game_id):
                await self.finish_game(game_id, channel)
        if end_game:
            await self.finish_game(game_id, channel)

    async def send_cards_to_channel(self, channel, user_id, card, bot_mode=False):
        """Send the cards to a specific channel."""
        if bot_mode:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=False)
        else:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=True)
        total_score = str(await self.get_player_total(user_id))
        if len(total_score) == 1:
            total_score = '0' + total_score  # this is to prevent being able to detect the number of digits by the spoiler
        card_name = await self.get_card_name(card)
        if bot_mode:
            await channel.send(f"<@{user_id}> pulled {card_name}. Their current score is {total_score}", file=card_file)
        else:
            await channel.send(f"<@{user_id}> pulled ||{card_name}||. Their current score is ||{total_score}||", file=card_file)

    async def compare_channels(self, user_id, channel):
        """Check if the channel is the correct channel."""
        game_id = await self.get_game_by_player(user_id)
        game = await self.get_game(game_id)
        if game[5] == channel.id:
            return True
        else:
            await channel.send(f"> **{user_id}, that game ({game_id}) is not available in this text channel.**")
            return False

    async def start_game(self, game_id):
        """Start out the game of blackjack."""
        game = await self.get_game(game_id)
        player1 = game[1]
        player2 = game[2]
        await self.add_player_status(player1)
        await self.add_player_status(player2)
        # Add Two Cards to both players [ Not in a loop because the messages should be in order on discord ]
        await self.add_card(player1)
        await self.add_card(player1)
        await self.add_card(player2)
        await self.add_card(player2)

    async def check_game_over(self, game_id):
        """Check if the blackjack game is over."""
        game = await self.get_game(game_id)
        player1_stand = await self.check_player_standing(game[1])
        player2_stand = await self.check_player_standing(game[2])
        if player1_stand and player2_stand:
            return True
        else:
            return False

    @staticmethod
    def determine_winner(score1, score2):
        """Check which player won the blackjack game."""
        if score1 == score2:
            return 'tie'
        elif score1 == 21:
            return 'player1'
        elif score2 == 21:
            return 'player2'
        elif score1 > 21 or score2 > 21:
            if score1 > 21 and score2 > 21:
                if score1 - 21 < score2 - 21:
                    return 'player1'
                else:
                    return 'player2'
            elif score1 > 21 and score2 < 21:
                return 'player2'
            elif score1 < 21 and score2 > 21:
                return 'player1'
        elif score1 < 21 and score2 < 21:
            if score1 - score2 > 0:
                return 'player1'
            else:
                return 'player2'
        else:
            return None

    async def announce_winner(self, channel, winner, loser, winner_points, loser_points, win_amount):
        """Send a message to the channel of who won the game."""
        if self.check_if_bot(winner):
            await channel.send(f"> **<@{keys.bot_id}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")
        elif self.check_if_bot(loser):
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{keys.bot_id}> with {loser_points}.**")
        else:
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")

    async def announce_tie(self, channel, player1, player2, tied_points):
        """Send a message to the channel of a tie."""
        if self.check_if_bot(player1) or self.check_if_bot(player2):
            await channel.send(f"> **<@{player1}> and <@{keys.bot_id}> have tied with {tied_points}**")
        else:
            await channel.send(f"> **<@{player1}> and <@{player2}> have tied with {tied_points}**")

    async def finish_game(self, game_id, channel):
        """Finish off a blackjack game and terminate it."""
        game = await self.get_game(game_id)
        player1_score = await self.get_player_total(game[1])
        player2_score = await self.get_player_total(game[2])
        if player2_score < 12 and self.check_if_bot(game[2]):
            await self.add_card(game[2])
        else:
            winner = self.determine_winner(player1_score, player2_score)
            player1_current_bal = await self.u_currency.get_balance(game[1])
            player2_current_bal = await self.u_currency.get_balance(game[2])
            if winner == 'player1':
                await self.update_balance(game[1], player1_current_bal + int(game[4]))
                if not self.check_if_bot(game[2]):
                    await self.update_balance(game[2], player2_current_bal - int(game[4]))
                await self.announce_winner(channel, game[1], game[2], player1_score, player2_score, game[4])
            elif winner == 'player2':
                if not self.check_if_bot(game[2]):
                    await self.update_balance(game[2], player2_current_bal + int(game[3]))
                await self.update_balance(game[1], player1_current_bal - int(game[3]))
                await self.announce_winner(channel, game[2], game[1], player2_score, player1_score, game[3])
            elif winner == 'tie':
                await self.announce_tie(channel, game[1], game[2], player1_score)
            await self.delete_game(game_id)

    async def delete_game(self, game_id):
        """Delete a blackjack game."""
        game = await self.get_game(game_id)
        await self.conn.execute("DELETE FROM blackjack.games WHERE gameid = $1", game_id)
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[1])
        await self.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[2])
        log.console(f"Game {game_id} deleted.")

    async def delete_all_games(self):
        """Delete all blackjack games."""
        all_games = await self.conn.fetch("SELECT gameid FROM blackjack.games")
        for games in all_games:
            game_id = games[0]
            await self.delete_game(game_id)
    ################
    # ## LEVELS ## #
    ################

    async def get_level(self, user_id, command):
        """Get the level of a command (rob/beg/daily)."""
        count = self.first_result(await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1 AND {command} > $2", user_id, 1))
        if not count:
            level = 1
        else:
            level = self.first_result(await self.conn.fetchrow(f"SELECT {command} FROM currency.Levels WHERE UserID = $1", user_id))
        return int(level)

    async def set_level(self, user_id, level, command):
        """Set the level of a user for a specific command."""
        async def update_level():
            """Updates a user's level."""
            await self.conn.execute(f"UPDATE currency.Levels SET {command} = $1 WHERE UserID = $2", level, user_id)

        count = self.first_result(await self.conn.fetchrow(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = $1", user_id))
        if not count:
            await self.conn.execute("INSERT INTO currency.Levels VALUES($1, NULL, NULL, NULL, NULL, 1)", user_id)
            await update_level()
        else:
            await update_level()

    @staticmethod
    async def get_xp(level, command):
        """Returns money/experience needed for a certain level."""
        if command == "profile":
            return 250 * level
        return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)

    @staticmethod
    async def get_rob_percentage(level):
        """Get the percentage of being able to rob. (Every 1 is 5%)"""
        chance = int(6 + (level // 10))  # first 10 levels is 6 for 30% chance
        if chance > 16:
            chance = 16
        return chance





    #################
    # ## LAST FM ## #
    #################

    @staticmethod
    def create_fm_payload(method, user=None, limit=None, time_period=None):
        """Creates the payload to be sent to Last FM"""
        payload = {
            'api_key': keys.last_fm_api_key,
            'method': method,
            'format': 'json'
        }
        if user:
            payload['user'] = user
        if limit:
            payload['limit'] = limit
        if time_period:
            payload['period'] = time_period
        return payload

    async def get_fm_response(self, method, user=None, limit=None, time_period=None):
        """Receives the response from Last FM"""
        async with self.session.get(keys.last_fm_root_url, headers=keys.last_fm_headers, params=self.create_fm_payload(method, user, limit, time_period)) as response:
            return await response.json()

    async def get_fm_username(self, user_id):
        """Gets Last FM username from the DB."""
        return self.first_result(await self.conn.fetchrow("SELECT username FROM lastfm.users WHERE userid = $1", user_id))

    async def set_fm_username(self, user_id, username):
        """Sets Last FM username to the DB."""
        try:
            if not await self.get_fm_username(user_id):
                await self.conn.execute("INSERT INTO lastfm.users(userid, username) VALUES ($1, $2)", user_id, username)
            else:
                await self.conn.execute("UPDATE lastfm.users SET username = $1 WHERE userid = $2", username, user_id)
            return True
        except Exception as e:
            log.console(e)
            return e

    #################
    # ## PATREON ## #
    #################
    async def get_patreon_users(self):
        """Get the permanent patron users"""
        return await self.conn.fetch("SELECT userid from patreon.users")

    async def get_patreon_role_members(self, super_patron=False):
        """Get the members in the patreon roles."""
        support_guild = self.client.get_guild(int(keys.bot_support_server_id))
        # API call will not show role.members
        if not super_patron:
            patreon_role = support_guild.get_role(int(keys.patreon_role_id))
        else:
            patreon_role = support_guild.get_role(int(keys.patreon_super_role_id))
        return patreon_role.members

    async def check_if_patreon(self, user_id, super_patron=False):
        """Check if the user is a patreon.
        There are two ways to check if a user ia a patreon.
        The first way is getting the members in the Patreon/Super Patreon Role.
        The second way is a table to check for permanent patreon users that are directly added by the bot owner.
        -- After modifying -> We take it straight from cache now.
        """
        if user_id in self.cache.patrons:
            if super_patron:
                return self.cache.patrons.get(user_id) == super_patron
            return True

    async def add_to_patreon(self, user_id):
        """Add user as a permanent patron."""
        try:
            user_id = int(user_id)
            await self.conn.execute("INSERT INTO patreon.users(userid) VALUES($1)", user_id)
            self.cache.patrons[user_id] = True
        except Exception as e:
            pass

    async def remove_from_patreon(self, user_id):
        """Remove user from being a permanent patron."""
        try:
            user_id = int(user_id)
            await self.conn.execute("DELETE FROM patreon.users WHERE userid = $1", user_id)
            self.cache.patrons.pop(user_id, None)
        except Exception as e:
            pass

    async def reset_patreon_cooldown(self, ctx):
        """Checks if the user is a patreon and resets their cooldown."""
        # Super Patrons also have the normal Patron role.
        if await self.check_if_patreon(ctx.author.id):
            ctx.command.reset_cooldown(ctx)

    ###################
    # ## MODERATOR ## #
    ###################
    async def add_welcome_message_server(self, channel_id, guild_id, message, enabled):
        """Adds a new welcome message server."""
        await self.conn.execute(
            "INSERT INTO general.welcome(channelid, serverid, message, enabled) VALUES($1, $2, $3, $4)", channel_id,
            guild_id, message, enabled)
        self.cache.welcome_messages[guild_id] = {"channel_id": channel_id, "message": message, "enabled": enabled}

    async def check_welcome_message_enabled(self, server_id):
        """Check if a welcome message server is enabled."""
        return self.cache.welcome_messages[server_id]['enabled'] == 1

    async def update_welcome_message_enabled(self, server_id, enabled):
        """Update a welcome message server's enabled status"""
        await self.conn.execute("UPDATE general.welcome SET enabled = $1 WHERE serverid = $2", int(enabled), server_id)
        self.cache.welcome_messages[server_id]['enabled'] = int(enabled)

    async def update_welcome_message_channel(self, server_id, channel_id):
        """Update the welcome message channel."""
        await self.conn.execute("UPDATE general.welcome SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        self.cache.welcome_messages[server_id]['channel_id'] = channel_id

    async def update_welcome_message(self, server_id, message):
        await self.conn.execute("UPDATE general.welcome SET message = $1 WHERE serverid = $2", message, server_id)
        self.cache.welcome_messages[server_id]['message'] = message

    ########################
    # ## CUSTOM COMMANDS## #
    ########################

    async def check_custom_command_name_exists(self, server_id, command_name):
        if server_id:
            custom_commands = self.cache.custom_commands.get(server_id)
            if custom_commands:
                if command_name.lower() in custom_commands:
                    return True
        return False

    async def add_custom_command(self, server_id, command_name, message):
        await self.conn.execute("INSERT INTO general.customcommands(serverid, commandname, message) VALUES ($1, $2, $3)", server_id, command_name, message)
        custom_commands = self.cache.custom_commands.get(server_id)
        if custom_commands:
            custom_commands[command_name] = message
        else:
            self.cache.custom_commands[server_id] = {command_name: message}

    async def remove_custom_command(self, server_id, command_name):
        await self.conn.execute("DELETE FROM general.customcommands WHERE serverid = $1 AND commandname = $2", server_id, command_name)
        custom_commands = self.cache.custom_commands.get(server_id)
        try:
            custom_commands.pop(command_name)
        except Exception as e:
            log.console(e)

    async def get_custom_command(self, server_id, command_name):
        commands = self.cache.custom_commands.get(server_id)
        return commands.get(command_name)
    ###################
    # ## BIAS GAME ## #
    ###################

    async def create_bias_game_image(self, first_idol_id, second_idol_id):
        """Uses thread pool to create bias game image to prevent IO blocking."""
        result = (self.thread_pool.submit(self.merge_images, first_idol_id, second_idol_id)).result()
        return f"{keys.bias_game_location}{first_idol_id}_{second_idol_id}.png"

    def merge_images(self, first_idol_id, second_idol_id):
        """Merge Idol Images if the merge doesn't exist already."""
        file_name = f"{first_idol_id}_{second_idol_id}.png"
        if not self.check_file_exists(f"{keys.bias_game_location}{file_name}"):
            # open the images.
            versus_image = Image.open(f'{keys.bias_game_location}versus.png')
            first_idol_image = Image.open(f'{keys.idol_avatar_location}{first_idol_id}_IDOL.png')
            second_idol_image = Image.open(f'{keys.idol_avatar_location}{second_idol_id}_IDOL.png')

            # define the dimensions
            idol_image_width = 150
            idol_image_height = 150
            first_image_area = (0, 0)
            second_image_area = (versus_image.width - idol_image_width, 0)
            image_size = (idol_image_width, idol_image_height)

            # resize the idol images
            first_idol_image = first_idol_image.resize(image_size)
            second_idol_image = second_idol_image.resize(image_size)

            # add the idol images onto the VS image.
            versus_image.paste(first_idol_image, first_image_area)
            versus_image.paste(second_idol_image, second_image_area)

            # save the versus image.
            versus_image.save(f"{keys.bias_game_location}{file_name}")

    @staticmethod
    def check_file_exists(file_name):
        return os.path.isfile(file_name)

    async def create_bias_game_bracket(self, all_games, user_id, bracket_winner):
        result = (self.thread_pool.submit(self.create_bracket, all_games, user_id, bracket_winner)).result()
        return f"{keys.bias_game_location}{user_id}.png"

    def create_bracket(self, all_games, user_id, bracket_winner):
        def get_battle_images(idol_1_id, idol_2_id):
            return Image.open(f'{keys.idol_avatar_location}{idol_1_id}_IDOL.png'), Image.open(f'{keys.idol_avatar_location}{idol_2_id}_IDOL.png')

        def resize_images(first_img, second_img, first_img_size, second_img_size):
            return first_img.resize(first_img_size), second_img.resize(second_img_size)

        def paste_image(first_idol_img, second_idol_img, first_img_area, second_img_area):
            bracket.paste(first_idol_img, first_img_area)
            bracket.paste(second_idol_img, second_img_area)

        bracket = Image.open(f'{keys.bias_game_location}bracket8.png')
        count = 1
        for c_round in all_games:
            if len(c_round) <= 4:
                for battle in c_round:
                    first_idol, second_idol = battle[0], battle[1]
                    first_idol_info = self.cache.stored_bracket_positions.get(count)
                    second_idol_info = self.cache.stored_bracket_positions.get(count + 1)

                    # get images
                    first_idol_image, second_idol_image = get_battle_images(first_idol.id, second_idol.id)

                    # resize images
                    first_idol_image, second_idol_image = resize_images(first_idol_image, second_idol_image, first_idol_info.get('img_size'), second_idol_info.get('img_size'))

                    # paste image to bracket
                    paste_image(first_idol_image, second_idol_image, first_idol_info.get('pos'), second_idol_info.get('pos'))

                    count = count + 2

        # add winner
        idol_info = self.cache.stored_bracket_positions.get(count)
        idol_image = Image.open(f'{keys.idol_avatar_location}{bracket_winner.id}_IDOL.png')
        idol_image = idol_image.resize(idol_info.get('img_size'))
        bracket.paste(idol_image, idol_info.get('pos'))
        bracket.save(f"{keys.bias_game_location}{user_id}.png")

    #######################
    # ## GENERAL GAMES ## #
    #######################

    async def stop_game(self, ctx, games):
        """Delete an ongoing game."""
        is_moderator = await self.u_miscellaneous.check_if_moderator(ctx)
        game = self.find_game(ctx.channel, games)
        if game:
            if ctx.author.id == game.host or is_moderator:
                # these are passed by reference, so can directly remove from them.
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

    #################
    # ## DATADOG ## #
    #################
    @staticmethod
    def initialize_data_dog():
        """Initialize The DataDog Class"""
        initialize()

    def send_metric(self, metric_name, value):
        """Send a metric value to DataDog."""
        # some values at 0 are important such as active games, this was put in place to make sure they are updated at 0.
        metrics_at_zero = ['bias_games', 'guessing_games', 'commands_per_minute', 'n_words_per_minute',
                           'bot_api_idol_calls', 'bot_api_translation_calls', 'messages_received_per_min',
                           'errors_per_minute', 'wolfram_per_minute', 'urban_per_minute']
        if metric_name in metrics_at_zero and not value:
            value = 0
        else:
            if not value:
                return
        if self.test_bot:
            metric_name = 'test_bot_' + metric_name
        else:
            metric_name = 'irene_' + metric_name
        api.Metric.send(metric=metric_name, points=[(time.time(), value)])

    #################
    # ## WEVERSE ## #
    #################
    async def add_weverse_channel(self, channel_id, community_name):
        """Add a channel to get updates for a community"""
        community_name = community_name.lower()
        await self.conn.execute("INSERT INTO weverse.channels(channelid, communityname) VALUES($1, $2)", channel_id, community_name)
        await self.add_weverse_channel_to_cache(channel_id, community_name)

    async def add_weverse_channel_to_cache(self, channel_id, community_name):
        """Add a weverse channel to cache."""
        community_name = community_name.lower()
        channels = self.cache.weverse_channels.get(community_name)
        if channels:
            channels.append([channel_id, None, False])
        else:
            self.cache.weverse_channels[community_name] = [[channel_id, None, False]]

    async def check_weverse_channel(self, channel_id, community_name):
        """Check if a channel is already getting updates for a community"""
        channels = self.cache.weverse_channels.get(community_name.lower())
        if channels:
            for channel in channels:
                if channel_id == channel[0]:
                    return True
        return False

    async def get_weverse_channels(self, community_name):
        """Get all of the channel ids for a specific community name"""
        return self.cache.weverse_channels.get(community_name.lower())

    async def delete_weverse_channel(self, channel_id, community_name):
        """Delete a community from a channel's updates."""
        community_name = community_name.lower()
        await self.conn.execute("DELETE FROM weverse.channels WHERE channelid = $1 AND communityname = $2", channel_id, community_name)
        channels = await self.get_weverse_channels(community_name)
        for channel in channels:
            if channel[0] == channel_id:
                if channels:
                    channels.remove(channel)
                else:
                    self.cache.weverse_channels.pop(community_name)

    async def add_weverse_role(self, channel_id, community_name, role_id):
        """Add a weverse role to notify."""
        await self.conn.execute("UPDATE weverse.channels SET roleid = $1 WHERE channelid = $2 AND communityname = $3", role_id, channel_id, community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, role_id)

    async def delete_weverse_role(self, channel_id, community_name):
        """Remove a weverse role from a server (no longer notifies a role)."""
        await self.conn.execute("UPDATE weverse.channels SET roleid = NULL WHERE channel_id = $1 AND communityname = $2", channel_id, community_name.lower())
        await self.replace_cache_role_id(channel_id, community_name, None)

    async def replace_cache_role_id(self, channel_id, community_name, role_id):
        """Replace the server role that gets notified on Weverse Updates."""
        channels = self.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[1] = role_id

    async def change_weverse_comment_status(self, channel_id, community_name, comments_disabled, updated=False):
        """Change a channel's subscription and whether or not they receive updates on comments."""
        comments_disabled = bool(comments_disabled)
        community_name = community_name.lower()
        if updated:
            await self.conn.execute("UPDATE weverse.channels SET commentsdisabled = $1 WHERE channelid = $2 AND communityname = $3", int(comments_disabled), channel_id, community_name)
        channels = self.cache.weverse_channels.get(community_name)
        for channel in channels:
            cache_channel_id = channel[0]
            if cache_channel_id == channel_id:
                channel[2] = comments_disabled

    async def set_comment_embed(self, notification, embed_title):
        """Set Comment Embed for Weverse."""
        artist_comments = await self.weverse_client.fetch_artist_comments(notification.community_id, notification.contents_id)
        if not artist_comments:
            return
        comment = artist_comments[0]
        embed_description = f"**{notification.message}**\n\n" \
            f"Content: **{comment.body}**\n" \
            f"Translated Content: **{await self.weverse_client.translate(comment.id, is_comment=True, p_obj=comment, community_id=notification.community_id)}**"
        embed = await self.create_embed(title=embed_title, title_desc=embed_description)
        return embed

    async def set_post_embed(self, notification, embed_title):
        """Set Post Embed for Weverse."""
        post = self.weverse_client.get_post_by_id(notification.contents_id)
        if post:
            # artist = self.weverse_client.get_artist_by_id(notification.artist_id)
            embed_description = f"**{notification.message}**\n\n" \
                f"Artist: **{post.artist.name} ({post.artist.list_name[0]})**\n" \
                f"Content: **{post.body}**\n" \
                f"Translated Content: **{await self.weverse_client.translate(post.id, is_post=True, p_obj=post, community_id=notification.community_id)}**"
            embed = await self.create_embed(title=embed_title, title_desc=embed_description)
            message = "\n".join([await self.download_weverse_post(photo.original_img_url, photo.file_name) for photo in post.photos])
            return embed, message
        return None, None

    async def download_weverse_post(self, url, file_name):
        """Downloads an image url and returns image host url."""
        async with self.session.get(url) as resp:
            fd = await aiofiles.open(keys.weverse_image_folder + file_name, mode='wb')
            await fd.write(await resp.read())
        return f"https://images.irenebot.com/weverse/{file_name}"

    async def set_media_embed(self, notification, embed_title):
        """Set Media Embed for Weverse."""
        media = self.weverse_client.get_media_by_id(notification.contents_id)
        if media:
            embed_description = f"**{notification.message}**\n\n" \
                f"Title: **{media.title}**\n" \
                f"Content: **{media.body}**\n"
            embed = await self.create_embed(title=embed_title, title_desc=embed_description)
            message = media.video_link
            return embed, message
        return None, None

    async def send_weverse_to_channel(self, channel_info, message_text, embed, is_comment, community_name):
        channel_id = channel_info[0]
        role_id = channel_info[1]
        comments_disabled = channel_info[2]
        if not (is_comment and comments_disabled):
            try:
                channel = self.client.get_channel(channel_id)
                if not channel:
                    # fetch channel instead (assuming discord.py cache did not load)
                    channel = await self.client.fetch_channel(channel_id)
            except Exception as e:
                # remove the channel from future updates as it cannot be found.
                return await self.delete_weverse_channel(channel_id, community_name.lower())
            try:
                await channel.send(embed=embed)
                if message_text:
                    # Since an embed already exists, any individual content will not load
                    # as an embed -> Make it it's own message.
                    if role_id:
                        message_text = f"<@&{role_id}>\n{message_text}"
                    await channel.send(message_text)
            except Exception as e:
                # no permission to post
                return

    #########################
    # ## SelfAssignRoles ## #
    #########################
    async def add_self_role(self, role_id, role_name, server_id):
        """Adds a self-assignable role to a server."""
        role_info = [role_id, role_name]
        await self.conn.execute("INSERT INTO selfassignroles.roles(roleid, rolename, serverid) VALUES ($1, $2, $3)", role_id, role_name, server_id)
        roles = await self.get_assignable_server_roles(server_id)
        if roles:
            roles.append(role_info)
        else:
            cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info:
                self.cache.assignable_roles[server_id] = {}
                cache_info = self.cache.assignable_roles.get(server_id)
            cache_info['roles'] = [role_info]

    async def get_self_role(self, message_content, server_id):
        """Returns a discord.Object that can be used for adding or removing a role to a member."""
        roles = await self.get_assignable_server_roles(server_id)
        if roles:
            for role in roles:
                role_id = role[0]
                role_name = role[1]
                if role_name.lower() == message_content.lower():
                    return discord.Object(role_id), role_name
        return None, None

    async def check_self_role_exists(self, role_id, role_name, server_id):
        """Check if a role exists as a self-assignable role in a server."""
        cache_info = self.cache.assignable_roles.get(server_id)
        if cache_info:
            roles = cache_info.get('roles')
            if roles:
                for role in roles:
                    c_role_id = role[0]
                    c_role_name = role[1]
                    if c_role_id == role_id or c_role_name == role_name:
                        return True
        return False

    async def remove_self_role(self, role_name, server_id):
        """Remove a self-assignable role from a server."""
        await self.conn.execute("DELETE FROM selfassignroles.roles WHERE rolename = $1 AND serverid = $2", role_name, server_id)
        cache_info = self.cache.assignable_roles.get(server_id)
        if cache_info:
            roles = cache_info.get('roles')
            if roles:
                for role in roles:
                    if role[1].lower() == role_name.lower():
                        roles.remove(role)

    async def modify_channel_role(self, channel_id, server_id):
        """Add or Change a server's self-assignable role channel."""
        def update_cache():
            cache_info = self.cache.assignable_roles.get(server_id)
            if not cache_info:
                self.cache.assignable_roles[server_id] = {'channel_id': channel_id}
            else:
                cache_info['channel_id'] = channel_id

        amount_of_results = self.first_result(await self.conn.fetchrow("SELECT COUNT(*) FROM selfassignroles.channels WHERE serverid = $1", server_id))
        if amount_of_results:
            update_cache()
            return await self.conn.execute("UPDATE selfassignroles.channels SET channelid = $1 WHERE serverid = $2", channel_id, server_id)
        await self.conn.execute("INSERT INTO selfassignroles.channels(channelid, serverid) VALUES($1, $2)", channel_id, server_id)
        update_cache()

    async def get_assignable_server_roles(self, server_id):
        """Get all the self-assignable roles from a server."""
        results = self.cache.assignable_roles.get(server_id)
        if results:
            return results.get('roles')

    async def check_for_self_assignable_role(self, message):
        """Main process for processing self-assignable roles."""
        try:
            author = message.author
            server_id = await self.get_server_id(message)
            if await self.check_self_assignable_channel(server_id, message.channel):
                if message.content:
                    prefix = message.content[0]
                    if len(message.content) > 1:
                        msg = message.content[1:len(message.content)]
                    else:
                        return
                    role, role_name = await self.get_self_role(msg, server_id)
                    await self.process_member_roles(message, role, role_name, prefix, author)
        except Exception as e:
            log.console(e)

    async def check_self_assignable_channel(self, server_id, channel):
        """Check if a channel is a self assignable role channel."""
        if server_id:
            cache_info = self.cache.assignable_roles.get(server_id)
            if cache_info:
                channel_id = cache_info.get('channel_id')
                if channel_id:
                    if channel_id == channel.id:
                        return True

    @staticmethod
    async def check_member_has_role(member_roles, role_id):
        """Check if a member has a role"""
        for role in member_roles:
            if role.id == role_id:
                return True

    async def process_member_roles(self, message, role, role_name, prefix, author):
        """Adds or removes a (Self-Assignable) role from a member"""
        if role:
            if prefix == '-':
                if await self.check_member_has_role(author.roles, role.id):
                    await author.remove_roles(role, reason="Self-Assignable Role", atomic=True)
                    return await message.channel.send(f"> {author.display_name}, You no longer have the {role_name} role.", delete_after=10)
                else:
                    return await message.channel.send(f"> {author.display_name}, You do not have the {role_name} role.", delete_after=10)
            elif prefix == '+':
                if await self.check_member_has_role(author.roles, role.id):
                    return await message.channel.send(f"> {author.display_name}, You already have the {role_name} role.", delete_after=10)
                await author.add_roles(role, reason="Self-Assignable Role", atomic=True)
                return await message.channel.send(f"> {author.display_name}, You have been given the {role_name} role.", delete_after=10)
            await message.delete()

    ##################
    # ## REMINDER ## #
    ##################

    @staticmethod
    async def determine_time_type(user_input):
        """Determine if time is relative time or absolute time
        relative time: remind me to _____ in 6 days
        absolute time: remind me to _____ at 6PM"""
        # TODO: add "on", "tomorrow", and "tonight" as valid inputs

        in_index = user_input.rfind(" in ")
        at_index = user_input.rfind(" at ")
        if in_index == at_index:
            return None, None
        if in_index > at_index:
            return True, in_index
        return False, at_index

    @staticmethod
    async def process_reminder_reason(user_input, cutoff_index):
        """Return the reminder reason that comes before in/at"""
        user_input = user_input[0: cutoff_index]
        user_words = user_input.split()
        if user_words[0].lower() == "me":
            user_words.pop(0)
        if user_words[0].lower() == "to":
            user_words.pop(0)
        return " ".join(user_words)

    async def process_reminder_time(self, user_input, type_index, is_relative_time, user_id):
        """Return the datetime of the reminder depending on the time format"""
        remind_time = user_input[type_index + len(" in "): len(user_input)]

        if is_relative_time:
            if await self.process_relative_time_input(remind_time) > 2 * 3.154e7:  # 2 years in seconds
                raise exceptions.TooLarge
            return datetime.datetime.now() + datetime.timedelta(seconds=await self.process_relative_time_input(remind_time))

        return await self.process_absolute_time_input(remind_time, user_id)

    @staticmethod
    async def process_relative_time_input(time_input):
        """Returns the relative time of the input in seconds"""
        year_aliases = ["years", "year", "yr", "y"]
        month_aliases = ["months", "month", "mo"]
        week_aliases = ["weeks", "week", "wk"]
        day_aliases = ["days", "day", "d"]
        hour_aliases = ["hours", "hour", "hrs", "hr", "h"]
        minute_aliases = ["minutes", "minute", "mins", "min", "m"]
        second_aliases = ["seconds", "second", "secs", "sec", "s"]
        time_units = [[year_aliases, 31536000], [month_aliases, 2592000], [week_aliases, 604800], [day_aliases, 86400],
                      [hour_aliases, 3600], [minute_aliases, 60], [second_aliases, 1]]

        remind_time = 0  # in seconds
        input_elements = re.findall(r"[^\W\d_]+|\d+", time_input)

        all_aliases = [alias for time_unit in time_units for alias in time_unit[0]]
        if not any(alias in input_elements for alias in all_aliases):
            raise exceptions.ImproperFormat

        for time_element in input_elements:
            try:
                int(time_element)
            except Exception as e:
                # purposefully creating an error to locate which elements are words vs integers.
                for time_unit in time_units:
                    if time_element in time_unit[0]:
                        remind_time += time_unit[1] * int(input_elements[input_elements.index(time_element) - 1])
        return remind_time

    async def process_absolute_time_input(self, time_input, user_id):
        """Returns the absolute date time of the input"""
        user_timezone = await self.get_user_timezone(user_id)
        if not user_timezone:
            raise exceptions.NoTimeZone
        cal = parsedatetime.Calendar()
        try:
            datetime_obj, _ = cal.parseDT(datetimeString=time_input, tzinfo=pytz.timezone(user_timezone))
            reminder_datetime = datetime_obj.astimezone(pytz.utc)
            return reminder_datetime
        except:
            raise exceptions.ImproperFormat

    async def get_user_timezone(self, user_id):
        """Returns the user's timezone"""
        return self.cache.timezones.get(user_id)

    async def set_user_timezone(self, user_id, timezone):
        """Set user timezone"""
        user_timezone = self.cache.timezones.get(user_id)
        self.cache.timezones[user_id] = timezone
        if user_timezone:
            await self.conn.execute("UPDATE reminders.timezones SET timezone = $1 WHERE userid = $2", timezone, user_id)
        else:
            await self.conn.execute("INSERT INTO reminders.timezones(userid, timezone) VALUES ($1, $2)", user_id, timezone)

    async def remove_user_timezone(self, user_id):
        """Remove user timezone"""
        try:
            self.cache.timezones.pop(user_id)
            await self.conn.execute("DELETE FROM reminders.timezones WHERE userid = $1", user_id)
        except:
            pass

    @staticmethod
    async def process_timezone_input(input_timezone, input_country_code=None):
        """Convert timezone abbreviation and country code to standard timezone name"""

        try:
            input_timezone = input_timezone.upper()
            input_country_code = input_country_code.upper()
        except:
            pass

        # Format if user inputs number timezones
        if any(char.isdigit() for char in input_timezone):
            try:
                timezone_offset = (re.findall(r"[+-]\d+", input_timezone))[0]
                UTC_offset = f"-{timezone_offset[1]}" if timezone_offset[0]=="+" else f"+{timezone_offset[1]}"
                input_timezone = 'Etc/GMT' + UTC_offset
            except:
                pass

        # Filter for all timezones which are equivalent to the user inputted timezone
        matching_timezones = None
        try:
            matching_timezones = set(
                filter(lambda x: datetime.datetime.now(pytz.timezone(x)).strftime("%Z") ==
                                 datetime.datetime.now(pytz.timezone(input_timezone)).strftime("%Z"),
                       pytz.common_timezones))
        except pytz.exceptions.UnknownTimeZoneError:
            matching_timezones = set(
                filter(lambda x: datetime.datetime.now(pytz.timezone(x)).strftime("%Z") == input_timezone,
                       pytz.common_timezones))
        except:
            pass

        # Find the timezones which share both same timezone input and the same country code
        if input_country_code:
            try:
                country_timezones = set(pytz.country_timezones[input_country_code])
                possible_timezones = matching_timezones.intersection(country_timezones)
            except:
                possible_timezones = matching_timezones
        else:
            possible_timezones = matching_timezones

        if not possible_timezones:
            return None

        return random.choice(list(possible_timezones))

    async def get_locale_time(self, m_time, user_timezone=None):
        """ Return a string containing locale date format. For now, enforce all weekdays to be en_US format"""
        # Set locale to server locale
        time_format = '%I:%M:%S%p %Z'
        locale.setlocale(locale.LC_ALL, '')

        if not user_timezone:
            return m_time.strftime('%a %x %I:%M:%S%p %Z')

        # Use weekday format of server
        weekday = m_time.strftime('%a')

        locale.setlocale(locale.LC_ALL, self.cache.locale_by_timezone[user_timezone])  # Set to user locale
        locale_date = m_time.strftime('%x')
        locale.setlocale(locale.LC_ALL, '')  # Reset locale back to server locale

        local_time = m_time.astimezone(pytz.timezone(user_timezone))
        local_time = local_time.strftime(time_format)
        return f"{weekday} {locale_date} {local_time}"

    async def set_reminder(self, remind_reason, remind_time, user_id):
        """Add reminder date to cache and db."""
        await self.conn.execute("INSERT INTO reminders.reminders(userid, reason, timestamp) VALUES ($1, $2, $3)", user_id, remind_reason, remind_time)
        remind_id = self.first_result(await self.conn.fetchrow("SELECT id FROM reminders.reminders WHERE userid=$1 AND reason=$2 AND timestamp=$3 ORDER BY id DESC", user_id, remind_reason, remind_time))
        user_reminders = self.cache.reminders.get(user_id)
        remind_info = [remind_id, remind_reason, remind_time]
        if user_reminders:
            user_reminders.append(remind_info)
        else:
            self.cache.reminders[user_id] = [remind_info]

    async def get_reminders(self, user_id):
        """Get the reminders of a user"""
        return self.cache.reminders.get(user_id)

    async def remove_user_reminder(self, user_id, reminder_id):
        """Remove a reminder from the cache and the database."""
        try:
            # remove from cache
            reminders = self.cache.reminders.get(user_id)
            if reminders:
                for reminder in reminders:
                    current_reminder_id = reminder[0]
                    if current_reminder_id == reminder_id:
                        reminders.remove(reminder)
        except Exception as e:
            log.console(e)
        await self.conn.execute("DELETE FROM reminders.reminders WHERE id = $1", reminder_id)

    async def get_all_reminders_from_db(self):
        """Get all reminders from the db (all users)"""
        return await self.conn.fetch("SELECT id, userid, reason, timestamp FROM reminders.reminders")

    async def get_all_timezones_from_db(self):
        """Get all timezones from the db (all users)"""
        return await self.conn.fetch("SELECT userid, timezone FROM reminders.timezones")



resources = Utility()
