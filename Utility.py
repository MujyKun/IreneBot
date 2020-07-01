from module import keys, logger as log
from bs4 import BeautifulSoup as soup
import discord
import random
import asyncio
import aiohttp
import aiofiles
import os
import math
"""
Utility.py
Resource Center for Irene
Any potentially useful functions will end up here
"""


class Utility:
    def __init__(self):
        self.client = keys.client
        self.DBconn, self.c = self.get_db_connection()
        self.DBconn.autocommit = False
        self.session = aiohttp.ClientSession()

    ##################
    # ## DATABASE ## #
    ##################

    @staticmethod
    def get_db_connection():
        """Retrieve Database Connection and Cursor."""
        return keys.DBconn, keys.DBconn.cursor()

    def fetch_one(self):
        """Get the first result from a sql query."""
        try:
            results = self.c.fetchone()[0]
        except Exception as e:
            results = None
        return results

    def fetch_all(self):
        """Get all the results from a sql query."""
        try:
            results = self.c.fetchall()
        except Exception as e:
            log.console(e)
            results = []
            pass
        return results

    ##################
    # ## CURRENCY ## #
    ##################
    async def register_user(self, user_id):
        """Register a user to the database if they are not already registered."""
        self.c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
        count = self.fetch_one()
        if count == 0:
            self.c.execute("INSERT INTO currency.Currency (UserID, Money) VALUES (%s, %s)", (user_id, "100"))
            self.DBconn.commit()
            return True
        elif count == 1:
            return False

    async def get_user_has_money(self, user_id):
        """Check if a user has money."""
        self.c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
        return not self.fetch_one() == 0

    async def get_balance(self, user_id):
        """Get current balance of a user."""
        if not (await self.register_user(user_id)):
            self.c.execute("SELECT money FROM currency.currency WHERE userid = %s", (user_id,))
            return int(self.fetch_one())
        else:
            return 100

    @staticmethod
    async def shorten_balance(money):  # money must be passed in as a string.
        """Shorten an amount of money to it's value places."""
        place_names = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion', 'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quatturodecillion', 'Quindecillion', 'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion', 'Centillion']
        place_values = int(math.log10(int(money)) // 3)
        try:
            return f"{int(money) // (10 ** (3 * place_values))} {place_names[place_values]}"
        except Exception as e:
            return "Too Fucking Much$"

    async def update_balance(self, user_id, new_balance):
        """Update a user's balance."""
        self.c.execute("UPDATE currency.Currency SET Money = %s::text WHERE UserID = %s", (str(new_balance), user_id))
        self.DBconn.commit()

    @staticmethod
    async def get_robbed_amount(author_money, user_money, level):
        """The amount to rob a specific person based on their rob level."""
        max_amount = int(user_money // 100)  # b value
        if max_amount > int(author_money // 2):
            max_amount = int(author_money // 2)
        min_amount = int((max_amount * level) // 100)
        if min_amount > max_amount:  # kind of ironic, but it is possible for min to surpass max in this case
            robbed_amount = random.randint(max_amount, min_amount)
        else:
            robbed_amount = random.randint(min_amount, max_amount)
        return robbed_amount

    @staticmethod
    def remove_commas(amount):
        """Remove all commas from a string and make it an integer."""
        return int(amount.replace(',', ''))

    #######################
    # ## MISCELLANEOUS ## #
    #######################
    def get_all_command_names(self):
        """Retrieves a list with all the client's command names."""
        command_list = []
        for command in self.client.all_commands:
            command_list.append(command)
        return command_list

    def check_message_is_command(self, message):
        """Check if a message is a command."""
        for command_name in self.get_all_command_names():
            if command_name in message.content:
                if len(command_name) != 1:
                    return True
        return False

    @staticmethod
    async def send_ban_message(channel):
        """A message to send for a user that is banned from the bot."""
        await channel.send(
            f"> **You are banned from using Irene. Join <{keys.bot_support_server_link}>**")

    async def ban_user_from_bot(self, user_id):
        """Bans a user from using the bot."""
        self.c.execute("INSERT INTO general.blacklisted(userid) VALUES (%s)", (user_id,))
        self.DBconn.commit()

    async def unban_user_from_bot(self, user_id):
        """UnBans a user from the bot."""
        self.c.execute("DELETE FROM general.blacklisted WHERE userid = %s", (user_id,))
        self.DBconn.commit()

    async def check_if_bot_banned(self, user_id):
        """Check if the user can use the bot."""
        self.c.execute("SELECT COUNT(*) FROM general.blacklisted WHERE userid = %s", (user_id,))
        return self.fetch_one() == 1

    @staticmethod
    def check_nword(message_content):
        """Check if a message contains the NWord."""
        message_split = message_content.lower().split()
        return 'nigga' in message_split or 'nigger' in message_split and ':' not in message_split

    @staticmethod
    def check_if_mod(ctx, mode=0):  # as mode = 1, ctx is the author id.
        """Check if the user is a bot mod/owner."""
        if mode == 0:
            user_id = ctx.author.id
            return user_id in keys.mods_list or user_id == keys.owner_id
        else:
            return ctx in keys.mods_list or ctx == keys.owner_id

    @staticmethod
    def get_none_if_list_is_empty(new_list):
        """Returns none if a list is empty, otherwise, it will return the list."""
        if len(new_list) == 0:
            return None
        else:
            return new_list

    def get_ping(self):
        """Get the client's ping."""
        return int(self.client.latency * 1000)

    @staticmethod
    def get_int_index(original, index):
        """Retrieves the specific index of an integer. Ex: Calling index 0 for integer 51 will return 5."""
        entire_selection = ""
        counter = 0
        for value in str(original):
            if counter < index:
              entire_selection += value
            counter += 1
        return int(entire_selection)

    @staticmethod
    def get_random_color():
        """Retrieves a random hex color."""
        r = lambda: random.randint(0, 255)
        return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present

    async def create_embed(self, title="Irene", color=None, title_desc=None, footer_desc="Thanks for using Irene!"):
        """Create a discord Embed."""
        if color is None:
            color = self.get_random_color()
        if title_desc is None:
            embed = discord.Embed(title=title, color=color)
        else:
            embed = discord.Embed(title=title, color=color, description=title_desc)
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    async def check_reaction(self, msg, user_id, reaction_needed):
        """Wait for a user's reaction on a message."""
        def react_check(reaction_used, user_reacted):
            return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=react_check)
            return True
        except asyncio.TimeoutError:
            await msg.delete()
            return False

    @staticmethod
    async def get_cooldown_time(time):
        """Turn command cooldown of seconds into hours, minutes, and seconds."""
        time = round(time)
        time_returned = ""
        if time % 3600 != time:
            hours = int(time//3600)
            if hours != 0:
                time_returned += f"{int(time//3600)}h "
        if time % 3600 != 0:
            minutes = int((time % 3600) // 60)
            if minutes != 0:
                time_returned += f"{int((time% 3600) // 60)}m "
        if (time % 3600) % 60 < 60:
            seconds = (time % 3600) % 60
            if seconds != 0:
                time_returned += f"{int((time% 3600) % 60)}s"
        return time_returned

    @staticmethod
    def check_embed_exists(message):
        """Check if a message has embeds."""
        try:
            for embed_check in message.embeds:
                if len(embed_check) > 0:
                    return True
        except Exception as e:
            pass
        return False

    @staticmethod
    def check_message_not_empty(message):
        """Check if a message has content."""
        try:
            if len(message.clean_content) >= 1:
                return True
        except Exception as e:
            pass
        return False

    def get_message_prefix(self, message):
        """Get the prefix of a message."""
        try:
            if self.check_message_not_empty(message):
                return message.clean_content[0]
        except Exception as e:
            pass
        return None

    async def check_left_or_right_reaction_embed(self, msg, embed_lists, original_page_number=0, reaction1="\U00002b05", reaction2="\U000027a1"):
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
                await msg.clear_reactions()
                await msg.add_reaction(reaction1)
                await msg.add_reaction(reaction2)
                await change_page(c_page)
            except Exception as e:
                log.console(f"check_left_or_right_reaction_embed - {e}")
                await change_page(c_page)
        await change_page(original_page_number)

    @staticmethod
    async def set_embed_author_and_footer(embed, footer_message):
        """Sets the author and footer of an embed."""
        embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                         icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
        embed.set_footer(text=footer_message,
                         icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
        return embed

    @staticmethod
    async def get_language_code(language):
        """Returns a language code that is compatible with the papago framework."""
        language = language.lower()
        languages = ['ko', 'en', 'ja', 'zh-CN', 'zh-TW', 'es', 'fr', 'vi', 'th', 'id']
        ko_keywords = ['korean', 'ko', 'kr', 'korea', 'kor']
        eng_keywords = ['en', 'eng', 'english']
        ja_keywords = ['jp', 'jap', 'japanese', 'japan']
        zh_CN_keywords = ['chinese', 'ch', 'zh-cn', 'zhcn', 'c', 'china']
        es_keywords = ['es', 'espanol', 'spanish', 'sp']
        fr_keywords = ['french', 'fr', 'f', 'fren']
        vi_keywords = ['viet', 'vi', 'vietnamese', 'vietnam']
        th_keywords = ['th', 'thai', 'thailand']
        id_keywords = ['id', 'indonesian', 'indonesia', 'ind']
        if language in ko_keywords:
            return languages[0]
        elif language in eng_keywords:
            return languages[1]
        elif language in ja_keywords:
            return languages[2]
        elif language in zh_CN_keywords:
            return languages[3]
        elif language in es_keywords:
            return languages[5]
        elif language in fr_keywords:
            return languages[6]
        elif language in vi_keywords:
            return languages[7]
        elif language in th_keywords:
            return languages[8]
        elif languages in id_keywords:
            return languages[9]
        return None

    async def get_server_prefix(self, server_id):
        """Gets the prefix of a server by the server ID."""
        self.c.execute("SELECT prefix FROM general.serverprefix WHERE serverid = %s", (server_id,))
        prefix = self.fetch_one()
        if prefix is None:
            return keys.bot_prefix
        else:
            return prefix

    async def get_server_prefix_by_context(self, ctx):
        """Gets the prefix of a server by the context."""
        try:
            server_id = ctx.guild.id
        except Exception as e:
            return keys.bot_prefix
        self.c.execute("SELECT prefix FROM general.serverprefix WHERE serverid = %s", (server_id,))
        prefix = self.fetch_one()
        if prefix is None:
            return keys.bot_prefix
        else:
            return prefix

    async def get_bot_statuses(self):
        """Get the displayed messages for the bot."""
        self.c.execute("SELECT status FROM general.botstatus")
        statuses = self.fetch_all()
        if len(statuses) == 0:
            return None
        else:
            return statuses

    def get_user_count(self):
        """Get the amount of users that the bot is watching over."""
        counter = 0
        for guild in self.client.guilds:
            counter += guild.member_count
        return counter

    def get_server_count(self):
        """Returns the guild count the bot is connected to."""
        return len(self.client.guilds)

    def get_channel_count(self):
        """Returns the channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.channels)
        return count

    def get_text_channel_count(self):
        """Returns the text channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.text_channels)
        return count

    def get_voice_channel_count(self):
        """Returns the voice channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.client.guilds:
            count += len(guild.voice_channels)
        return count


    ###################
    # ## BLACKJACK ## #
    ###################
    async def check_in_game(self, user_id, ctx):  # this is meant for when it is accessed by commands outside of BlackJack.
        """Check if a user is in a game."""
        self.c.execute("SELECT COUNT(*) From blackjack.games WHERE player1 = %s OR player2 = %s", (user_id, user_id))
        check = self.fetch_one()
        if check == 1:
            await ctx.send(f"> **{ctx.author}, you are already in a pending/active game. Please type {await self.get_server_prefix_by_context(ctx)}endgame.**")
            return True
        else:
            return False

    async def add_bj_game(self, user_id, bid, ctx, mode):
        """Add the user to a blackjack game."""
        self.c.execute("INSERT INTO blackjack.games (player1, bid1, channelid) VALUES (%s, %s, %s)", (user_id, bid, ctx.channel.id))
        self.DBconn.commit()
        game_id = self.get_game_by_player(user_id)
        if mode != "bot":
            await ctx.send(f"> **There are currently 1/2 members signed up for BlackJack. To join the game, please type {await self.get_server_prefix_by_context(ctx)}joingame {game_id} (bid)** ")

    async def process_bj_game(self, ctx, amount, user_id):
        """pre requisites for joining a blackjack game."""
        if amount >= 0:
            if not await self.check_in_game(user_id, ctx):
                if amount > await self.get_balance(user_id):
                    await ctx.send(f"> **{ctx.author}, you can not bet more than your current balance.**")
                else:
                    return True
        else:
            await ctx.send(f"> **{ctx.author}, you can not bet a negative number.**")
        return False

    def get_game_by_player(self, player_id):
        """Get the current game of a player."""
        self.c.execute("SELECT gameid FROM blackjack.games WHERE player1 = %s OR player2 = %s", (player_id, player_id))
        return self.fetch_one()

    def get_game(self, game_id):
        """Get the game from its ID"""
        self.c.execute("SELECT gameid, player1, player2, bid1, bid2, channelid FROM blackjack.games WHERE gameid = %s", (game_id,))
        return self.c.fetchone()

    def add_player_two(self, game_id, user_id, bid):
        """Add a second player to a blackjack game."""
        self.c.execute("UPDATE blackjack.games SET player2 = %s, bid2 = %s WHERE gameid = %s ", (user_id, bid, game_id))
        self.DBconn.commit()

    def get_current_cards(self, user_id):
        """Get the current cards of a user."""
        self.c.execute("SELECT inhand FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
        in_hand = self.fetch_one()
        if in_hand is None:
            return []
        return in_hand.split(',')

    def check_player_standing(self, user_id):
        """Check if a player is standing."""
        self.c.execute("SELECT stand FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
        return self.fetch_one() == 1

    def set_player_stand(self, user_id):
        """Set a player to stand."""
        self.c.execute("UPDATE blackjack.currentstatus SET stand = %s WHERE userid = %s", (1, user_id))
        self.DBconn.commit()

    def delete_player_status(self, user_id):
        """Remove a player's status from a game."""
        self.c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
        self.DBconn.commit()

    def add_player_status(self, user_id):
        """Add a player's status to a game."""
        self.delete_player_status(user_id)
        self.c.execute("INSERT INTO blackjack.currentstatus (userid, stand, total) VALUES (%s, %s, %s)", (user_id, 0, 0))
        self.DBconn.commit()

    def get_player_total(self, user_id):
        """Get a player's total score."""
        self.c.execute("SELECT total FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
        return self.fetch_one()

    def get_card_value(self, card):
        """Get the value of a card."""
        self.c.execute("SELECT value FROM blackjack.cards WHERE id = %s", (card,))
        return self.fetch_one()

    def get_all_cards(self):
        """Get all the cards from a deck."""
        self.c.execute("SELECT id FROM blackjack.cards")
        card_tuple = self.fetch_all()
        all_cards = []
        for card in card_tuple:
            all_cards.append(card[0])
        return all_cards

    def get_available_cards(self, game_id):  # pass in a list of card ids
        """Get the cards that are not occupied."""
        all_cards = self.get_all_cards()
        available_cards = []
        game = self.get_game(game_id)
        player1_cards = self.get_current_cards(game[1])
        player2_cards = self.get_current_cards(game[2])
        for card in all_cards:
            if card not in player1_cards and card not in player2_cards:
                available_cards.append(card)
        return available_cards

    def get_card_name(self, card_id):
        """Get the name of a card."""
        self.c.execute("SELECT name FROM blackjack.cards WHERE id = %s", (card_id,))
        return self.fetch_one()

    def check_if_ace(self, card_id, user_id):
        """Check if the card is an ace and is not used."""
        aces = ["1", "14", "27", "40"]
        aces_used = self.get_aces_used(user_id)
        if card_id in aces and card_id not in aces_used:
            aces_used.append(card_id)
            self.set_aces_used(aces_used, user_id)
            return True
        return False

    def set_aces_used(self, card_list, user_id):
        """Mark an ace as used."""
        separator = ','
        cards = separator.join(card_list)
        self.c.execute("UPDATE blackjack.currentstatus SET acesused = %s WHERE userid = %s", (cards, user_id))
        self.DBconn.commit()

    def get_aces_used(self, user_id):
        """Get the aces that were changed from 11 to 1."""
        self.c.execute("SELECT acesused FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
        aces_used = self.fetch_one()
        if aces_used is None:
            return []
        return aces_used.split(',')

    def check_if_bot(self, user_id):
        """Check if the player is a bot. (The bot would be Irene)"""
        return str(self.get_int_index(keys.bot_id, 9)) in str(user_id)

    async def add_card(self, user_id):
        """Check status of a game, it's player, manages the bot that plays, and then adds a card."""
        end_game = False
        check = 0

        separator = ','
        current_cards = self.get_current_cards(user_id)
        game_id = self.get_game_by_player(user_id)
        game = self.get_game(game_id)
        channel = await self.client.fetch_channel(game[5])
        stand = self.check_player_standing(user_id)
        player1_score = self.get_player_total(game[1])
        player2_score = self.get_player_total(game[2])
        player1_cards = self.get_current_cards(game[1])
        if not stand:
            available_cards = self.get_available_cards(game_id)
            random_card = random.choice(available_cards)
            current_cards.append(str(random_card))
            cards = separator.join(current_cards)
            current_total = self.get_player_total(user_id)
            random_card_value = self.get_card_value(random_card)
            if current_total + random_card_value > 21:
                for card in current_cards:  # this includes the random card
                    if self.check_if_ace(card, user_id) and check != 1:
                        check = 1
                        current_total = (current_total + random_card_value) - 10
                if check == 0:  # if there was no ace
                    current_total = current_total + random_card_value
            else:
                current_total = current_total + random_card_value
            self.c.execute("UPDATE blackjack.currentstatus SET inhand = %s, total = %s WHERE userid = %s", (cards, current_total, user_id))
            self.DBconn.commit()
            if current_total > 21:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if player1_score > 21 and current_total >= 16:
                        end_game = True
                        self.set_player_stand(game[1])
                        self.set_player_stand(game[2])
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
                        self.set_player_stand(user_id)
                        self.set_player_stand(game[2])
                        end_game = True
            else:
                if user_id == game[2] and self.check_if_bot(game[2]):
                    if current_total < 16143478541328187392 and len(player1_cards) > 2:
                        await self.add_card(game[2])
                    if self.check_player_standing(game[1]) and current_total >= 16:
                        end_game = True
            if not self.check_if_bot(user_id):
                if self.check_if_bot(game[2]):
                    await self.send_cards_to_channel(channel, user_id, random_card, True)
                else:
                    await self.send_cards_to_channel(channel, user_id, random_card)
        else:
            await channel.send(f"> **You already stood.**")
            if self.check_game_over(game_id):
                await self.finish_game(game_id, channel)
        if end_game:
            await self.finish_game(game_id, channel)

    async def send_cards_to_channel(self, channel, user_id, card, bot_mode=False):
        """Send the cards to a specific channel."""
        if bot_mode:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=False)
        else:
            card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=True)
        total_score = str(self.get_player_total(user_id))
        if len(total_score) == 1:
            total_score = '0' + total_score  # this is to prevent being able to detect the number of digits by the spoiler
        card_name = self.get_card_name(card)
        if bot_mode:
            await channel.send(f"<@{user_id}> pulled {card_name}. Their current score is {total_score}", file=card_file)
        else:
            await channel.send(f"<@{user_id}> pulled ||{card_name}||. Their current score is ||{total_score}||", file=card_file)

    async def compare_channels(self, user_id, channel):
        """Check if the channel is the correct channel."""
        game_id = self.get_game_by_player(user_id)
        game = self.get_game(game_id)
        if game[5] == channel.id:
            return True
        else:
            await channel.send(f"> **{user_id}, that game ({game_id}) is not available in this text channel.**")
            return False

    async def start_game(self, game_id):
        """Start out the game of blackjack."""
        game = self.get_game(game_id)
        player1 = game[1]
        player2 = game[2]
        self.add_player_status(player1)
        self.add_player_status(player2)
        # Add Two Cards to both players [ Not in a loop because the messages should be in order on discord ]
        await self.add_card(player1)
        await self.add_card(player1)
        await self.add_card(player2)
        await self.add_card(player2)

    def check_game_over(self, game_id):
        """Check if the blackjack game is over."""
        game = self.get_game(game_id)
        player1_stand = self.check_player_standing(game[1])
        player2_stand = self.check_player_standing(game[2])
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
        game = self.get_game(game_id)
        player1_score = self.get_player_total(game[1])
        player2_score = self.get_player_total(game[2])
        if player2_score < 12 and self.check_if_bot(game[2]):
            await self.add_card(game[2])
        else:
            winner = self.determine_winner(player1_score, player2_score)
            player1_current_bal = await self.get_balance(game[1])
            player2_current_bal = await self.get_balance(game[2])
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
            self.delete_game(game_id)

    def delete_game(self, game_id):
        """Delete a blackjack game."""
        game = self.get_game(game_id)
        self.c.execute("DELETE FROM blackjack.games WHERE gameid = %s", (game_id,))
        self.c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (game[1],))
        self.c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (game[2],))
        log.console(f"Game {game_id} deleted.")

    def delete_all_games(self):
        """Delete all blackjack games."""
        self.c.execute("SELECT gameid FROM blackjack.games")
        all_games = self.fetch_all()
        for games in all_games:
            game_id = games[0]
            self.delete_game(game_id)
    ################
    # ## LEVELS ## #
    ################

    async def get_level(self, user_id, command):
        """Get the level of a command (rob/beg/daily)."""
        self.c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s AND {command} > %s", (user_id, 1))
        if self.fetch_one() == 0:
            level = 1
        else:
            self.c.execute(f"SELECT {command} FROM currency.Levels WHERE UserID = %s", (user_id,))
            level = self.fetch_one()
        return int(level)

    async def set_level(self, user_id, level, command):
        """Set the level of a user for a specific command."""
        def update_level():
            """Updates a user's level."""
            self.c.execute(f"UPDATE currency.Levels SET {command} = %s WHERE UserID = %s", (level, user_id))
            self.DBconn.commit()

        self.c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s", (user_id,))
        if self.fetch_one() == 0:
            self.c.execute("INSERT INTO currency.Levels VALUES(%s, NULL, NULL, NULL, NULL, 1)", (user_id,))
            self.DBconn.commit()
            update_level()
        else:
            update_level()

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

    #######################
    # ## GROUP MEMBERS ## #
    #######################
    @staticmethod
    def log_idol_command(message):
        """Log an idol photo that was called."""
        log.console(f"IDOL LOG: ChannelID = {message.channel.id} - {message.author} "
                    f"({message.author.id})|| {message.clean_content} ")

    async def get_all_images_count(self):
        """Get the amount of images the bot has."""
        self.c.execute("SELECT COUNT(*) FROM groupmembers.imagelinks")
        return self.fetch_one()

    def get_idol_called(self, member_id):
        """Get the amount of times an idol has been called."""
        self.c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
        counter = self.fetch_one()
        return counter

    @staticmethod
    async def check_if_folder(url):
        """Check if a url is a folder."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    return True
                return False

    async def get_idol_count(self, member_id):
        """Get the amount of photos for an idol."""
        self.c.execute("SELECT COUNT(*) FROM groupmembers.ImageLinks WHERE MemberID = %s", (member_id,))
        count = self.fetch_one()
        return count

    async def get_random_idol_id(self):
        """Get a random idol."""
        member_ids = await self.get_all_members()
        return (random.choice(member_ids))[0]

    async def get_all_members(self):
        """Get all idols."""
        self.c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.Member")
        return self.fetch_all()

    async def get_all_groups(self):
        """Get all groups."""
        self.c.execute("SELECT groupid, groupname, aliases FROM groupmembers.groups ORDER BY groupname")
        return self.fetch_all()

    async def get_members_in_group(self, group_name):
        """Get the members in a specific group."""
        self.c.execute(f"SELECT groupid FROM groupmembers.groups WHERE groupname = %s", (group_name,))
        group_id = self.fetch_one()
        all_members = await self.get_all_members()
        members_in_group = []
        for member in all_members:
            member_info = [member[0], member[2]]
            in_groups = member[3].split(',')
            if str(group_id) in in_groups:
                members_in_group.append(member_info)
        return members_in_group

    async def get_member(self, member_id):
        """Get an idol based on their ID."""
        self.c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.member WHERE id = %s", (member_id,))
        return self.c.fetchone()

    async def get_group_name(self, group_id):
        """Get a group's name based on their ID."""
        self.c.execute("SELECT groupname FROM groupmembers.groups WHERE groupid = %s", (group_id,))
        return self.fetch_one()

    async def get_group_id_from_member(self, member_id):
        """Get a group ID based on a member's ID."""
        member_info = await self.get_member(member_id)
        return ((member_info[3]).split(','))[0]

    async def send_names(self, ctx, mode, user_page_number):
        """Send the names of all idols in an embed with many pages."""
        async def check_mode(embed_temp):
            """Check if it is grabbing their full names or stage names."""
            if mode == "fullname":
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {await self.get_server_prefix_by_context(ctx)}members for Stage Names.")
            else:
                embed_temp = await self.set_embed_author_and_footer(embed_temp, f"Type {await self.get_server_prefix_by_context(ctx)}fullnames for Full Names.")
            return embed_temp
        is_mod = self.check_if_mod(ctx)
        embed_lists = []
        all_members = await self.get_all_members()
        all_groups = await self.get_all_groups()
        page_number = 1
        embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
        counter = 1
        for group in all_groups:
            names = []
            group_id = group[0]
            group_name = group[1]
            if group_name != "NULL" or is_mod:
                for member in all_members:
                    if mode == "fullname":
                        member_name = member[1]
                    else:
                        member_name = member[2]
                    member_in_group_ids = (member[3]).split(',')
                    for member_in_group_id in member_in_group_ids:
                        if int(member_in_group_id) == group_id:
                            if is_mod:
                                names.append(f"{member_name} ({member[0]}) | ")
                            else:
                                names.append(f"{member_name} | ")
                final_names = "".join(names)
                if len(final_names) == 0:
                    final_names = "None"
                if is_mod:
                    embed.insert_field_at(counter, name=f"{group_name} ({group_id})", value=final_names, inline=False)
                else:
                    embed.insert_field_at(counter, name=f"{group_name}", value=final_names, inline=False)
                if counter == 10:
                    page_number += 1
                    await check_mode(embed)
                    embed_lists.append(embed)
                    embed = discord.Embed(title=f"Idol List Page {page_number}", color=0xffb6c1)
                    counter = 0
                counter += 1
        # if counter did not reach 10, current embed needs to be saved.
        await check_mode(embed)
        embed_lists.append(embed)
        if user_page_number > len(embed_lists) or user_page_number < 1:
            user_page_number = 1
        msg = await ctx.send(embed=embed_lists[user_page_number-1])
        await self.check_left_or_right_reaction_embed(msg, embed_lists, user_page_number-1)

    async def set_embed_with_all_aliases(self, mode):
        """Send the names of all aliases in an embed with many pages."""
        check = False
        if mode == "Group":
            all_info = await self.get_all_groups()
        else:
            all_info = await self.get_all_members()
        embed_list = []
        count = 0
        page_number = 1
        embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=self.get_random_color())
        for info in all_info:
            id = info[0]
            name = info[1]
            aliases = info[2]
            if mode != "Group":
                stage_name = info[2]
                aliases = info[4]
                check = True
            if aliases is not None:
                if check:
                    embed.add_field(name=f"{name} ({stage_name}) [{id}]", value=aliases, inline=True)
                else:
                    embed.add_field(name=f"{name} [{id}]", value=aliases, inline=True)
                count += 1
            if count == 10:
                count = 0
                embed_list.append(embed)
                page_number += 1
                embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=self.get_random_color())
        if count != 0:
            embed_list.append(embed)
        return embed_list

    async def check_idol_post_reactions(self, message, user_msg):
        """Check the reactions on an idol post."""
        try:
            if message is not None:
                reload_image_emoji = "<:ReloadImage:694109526491922463>"
                dead_link_emoji = "<:DeadLink:695787733460844645>"
                await message.add_reaction(reload_image_emoji)
                await message.add_reaction(dead_link_emoji)
                message = await message.channel.fetch_message(message.id)

                def image_check(user_reaction, reaction_user):
                    """check the user that reacted to it and which emoji it was."""
                    user_check = (reaction_user == user_msg.author) or (reaction_user.id == keys.owner_id)
                    return user_check and (str(user_reaction.emoji) == dead_link_emoji or str(user_reaction.emoji) ==
                                           reload_image_emoji) and user_reaction.message.id == message.id

                async def reload_image(message1):
                    """Wait for a user to react, and reload the image if it's the reload emoji."""
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', check=image_check)
                        if str(reaction) == reload_image_emoji:
                            channel = message1.channel
                            try:
                                link = message1.embeds[0].url
                            except:
                                link = message1.content
                            await message1.delete()
                            # message1 = await channel.send(embed=embed)
                            count = 0
                            keep_going = True
                            while keep_going:
                                message1 = await channel.send(link)
                                await message1.delete()
                                count += 1
                                # how many times to resend the message.
                                if count == 3:
                                    keep_going = False
                            message1 = await channel.send(link)
                            await self.check_idol_post_reactions(message1, user_msg)
                        elif str(reaction) == dead_link_emoji:
                            try:
                                link = message1.embeds[0].url
                            except:
                                link = message1.content
                            self.c.execute("INSERT INTO groupmembers.DeadLinkFromUser VALUES(%s,%s)", (link, user.id))
                            self.DBconn.commit()
                            await message1.delete()

                    except Exception as e:
                        log.console(e)
                        pass
                await reload_image(message)
        except Exception as e:
            pass

    async def get_id_where_member_matches_name(self, name, mode=0):
        """Get member ids if the name matches."""
        all_members = await self.get_all_members()
        id_list = []
        for member in all_members:
            member_id = member[0]
            full_name = member[1].lower()
            stage_name = member[2].lower()
            aliases = member[4]
            if mode == 0:
                if name.lower() == full_name or name.lower() == stage_name:
                    id_list.append(member_id)
            else:
                if stage_name.lower() in name.lower() or full_name.lower() in name.lower():
                    id_list.append(member_id)

            if aliases is not None:
                for alias in aliases.split(','):
                    if mode == 0:
                        if alias == name.lower():
                            id_list.append(member_id)
                    else:
                        if alias in name.lower():
                            id_list.append(member_id)
        # remove any duplicates
        id_list = list(dict.fromkeys(id_list))
        return id_list

    async def get_id_where_group_matches_name(self, name, mode=0):
        """Get group ids for a specific name."""
        all_groups = await self.get_all_groups()
        id_list = []
        for group in all_groups:
            try:
                group_id = group[0]
                group_name = group[1].lower()
                aliases = group[2]
                if mode == 0:
                    if name.lower() == group_name.lower():
                        id_list.append(group_id)
                else:
                    if group_name.lower() in name.lower():
                        id_list.append(group_id)
                        name = (name.lower()).replace(group_name, "")
                if aliases is not None:
                    for alias in aliases.split(','):
                        if mode == 0:
                            if alias == name.lower():
                                id_list.append(group_id)
                        else:
                            if alias in name.lower():
                                id_list.append(group_id)
                                name = (name.lower()).replace(alias, "")
            except Exception as e:
                log.console(e)
        # remove any duplicates
        id_list = list(dict.fromkeys(id_list))
        if mode == 0:
            return id_list
        else:
            return id_list, name

    async def check_group_and_idol(self, message):
        """Check if a specific idol is being called from a reference to a group. ex: redvelvet irene"""
        group_ids, new_message = await self.get_id_where_group_matches_name(message, mode=1)
        member_list = []
        for group_id in group_ids:
            members_in_group = await self.get_members_in_group(await self.get_group_name(group_id))
            member_ids = await self.get_id_where_member_matches_name(new_message, 1)
            for member_id in member_ids:
                for group_member in members_in_group:
                    group_member_id = group_member[0]
                    if member_id == group_member_id:
                        member_list.append(member_id)
        return self.get_none_if_list_is_empty(member_list)

    async def get_random_photo_from_member(self, member_id):
        """Get a random photo from an idol."""
        self.c.execute("SELECT link FROM groupmembers.imagelinks WHERE memberid = %s", (member_id,))
        return (random.choice(self.fetch_all()))[0]

    async def update_member_count(self, member_id):
        """Update the amount of times an idol has been called."""
        self.c.execute("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
        count = self.fetch_one()
        if count == 0:
            self.c.execute("INSERT INTO groupmembers.Count VALUES(%s, %s)", (member_id, 1))
        else:
            self.c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
            count = self.fetch_one()
            count += 1
            self.c.execute("UPDATE groupmembers.Count SET Count = %s WHERE MemberID = %s", (count, member_id))
        self.DBconn.commit()

    @staticmethod
    def remove_custom_characters(file_name):
        """Only allow 0-9, a-z as a file name and remove any other characters."""
        allowed_characters = "abcdefghijklmnopqrstuvwxyz1234567890."
        for character in file_name:
            if character not in allowed_characters:
                file_name = file_name.replace(character, "z")
        return file_name

    async def send_google_drive_embed(self, photo_link, embed, channel, drive_id, member_id, group_id):
        """Does the processing for google drive photos/videos."""
        try:
            post_url = f"https://drive.google.com/file/d/{drive_id}/view?usp=sharing"
            async with self.session.get(post_url) as r:
                async with self.session.get(photo_link) as resp:
                    if resp.status == 200:
                        page_html = await r.text()
                        page_soup = soup(page_html, "html.parser")
                        title_loc = (page_soup.find("title"))
                        title_end = (str(title_loc.next).find(" - Google Drive"))
                        file_name = (title_loc.next[0:title_end])
                        file_name = self.remove_custom_characters(file_name)  # Important to have photo not outisde of embed.
                        file_location = f'temp/{file_name}'
                        fd = await aiofiles.open(file_location, mode='wb')
                        await fd.write(await resp.read())
                        await fd.close()
                        file_size = os.path.getsize(file_location)  # bytes (conversion binary)
                        if file_size < 8388608:  # 8 MB
                            photo = discord.File(file_location, file_name)
                            embed.set_image(url=f"attachment://{file_name}")
                            if not self.check_photo_animated(file_name):
                                msg = await channel.send(file=photo, embed=embed)
                            else:
                                msg = await channel.send(file=photo)
                        else:
                            embed.set_image(url=photo_link)
                            msg = await channel.send(embed=embed)
                        os.unlink(file_location)
                        return msg
                    elif resp.status == 404 or resp.status == 403:
                        log.console(f"REMOVING FROM IDOL {member_id} - {photo_link}")
                        self.c.execute("DELETE FROM groupmembers.imagelinks WHERE link = %s", (photo_link,))
                        self.c.execute("INSERT INTO groupmembers.deleted(link, memberid) VALUES (%s,%s)", (photo_link, 0))
                        self.DBconn.commit()
                        # send a new post
                        random_link = await self.get_random_photo_from_member(member_id)
                        await self.idol_post(channel, member_id, random_link, group_id)
                    else:
                        log.console(f"ERROR {resp.status} Member ID: {member_id}- {photo_link}")
        except Exception as e:
            log.console(e)

    @staticmethod
    def check_photo_animated(photo_name):
        """Check if the media is audio, a video, or a gif."""
        mp3 = photo_name.find('mp3')
        mp4 = photo_name.find('mp4')
        gif = photo_name.find('gif')
        if gif == -1 and mp4 == -1 and mp3 == -1:
            return False
        else:
            return True

    @staticmethod
    def check_link_origin(link):
        """Check where the media link came from."""
        tenor = link.find("tenor.com", 0)
        drive = link.find("drive", 0)
        if tenor != -1:
            return 'tenor'
        elif drive != -1:
            return 'drive'
        else:
            return 'other'

    async def get_idol_post_embed(self, group_id, member_info, photo_link):
        """The embed for an idol post."""
        if group_id is None:
            embed = discord.Embed(title=f"{member_info[1]} ({member_info[2]})", color=self.get_random_color(),
                                  url=photo_link)
        else:
            embed = discord.Embed(title=f"{await self.get_group_name(group_id)} ({member_info[2]})",
                                  color=self.get_random_color(), url=photo_link)
        return embed

    async def idol_post(self, channel, member_id, photo_link, group_id=None):
        """The main process for posting an idol's photo."""
        try:
            member_info = await self.get_member(member_id)
            link_origin = self.check_link_origin(photo_link)
            await self.update_member_count(member_id)
            if link_origin == 'drive':
                id_loc = photo_link.find("id=") + 3
                drive_id = photo_link[id_loc:len(photo_link)]
                embed = await self.get_idol_post_embed(group_id, member_info, photo_link)
                msg = await self.send_google_drive_embed(photo_link, embed, channel, drive_id, member_id, group_id)
                return msg
            if link_origin == 'tenor':
                msg = await channel.send(photo_link)
                return msg
            else:
                embed = await self.get_idol_post_embed(group_id, member_info, photo_link)
                embed.set_image(url=photo_link)
                msg = await channel.send(embed=embed)
                return msg
        except Exception as e:
            log.console(e)

    #################
    # ## LOGGING ## #
    #################

    async def get_servers_logged(self):
        """Get the servers that are being logged."""
        self.c.execute("SELECT serverid FROM logging.servers")
        server_ids = self.fetch_all()
        servers_logged = []
        for server in server_ids:
            if await self.check_if_logged(server_id = server):
                servers_logged.append(server)
        return servers_logged

    async def get_channels_logged(self):
        """Get all the channels that are being logged."""
        self.c.execute("SELECT channelid, server FROM logging.channels")
        channel_ids = self.fetch_all()
        channels_logged = []
        for channel in channel_ids:
            channel_id = channel[0]
            channel_guild = channel[1]  # not the server id, just the row id
            self.c.execute("SELECT serverid FROM logging.servers WHERE id = %s", (channel_guild,))
            channel_guild = self.fetch_one()
            if await self.check_if_logged(server_id=channel_guild):
                # No need to check if channel is logged because the list already confirms it is logged.
                channels_logged.append(channel_id)
        return channels_logged

    async def add_to_logging(self, server_id, channel_id):  # return true if status is on
        """Add a channel to be logged."""
        self.c.execute("SELECT COUNT(*) FROM logging.servers WHERE serverid = %s", (server_id,))
        if self.fetch_one() == 0:
            self.c.execute("INSERT INTO logging.servers (serverid, channelid, status, sendall) VALUES (%s, %s, %s, %s)", (server_id, channel_id, 1, 1))
            self.DBconn.commit()
        else:
            await self.set_logging_status(server_id, 1)
            self.c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (server_id,))
            if self.fetch_one() != channel_id:
                self.c.execute("UPDATE logging.servers SET channelid = %s WHERE serverid = %s", (channel_id, server_id))
        return True

    async def check_if_logged(self, server_id=None, channel_id=None):  # only one parameter should be passed in
        """Check if a server or channel is being logged."""
        if channel_id is not None:
            self.c.execute("SELECT COUNT(*) FROM logging.channels WHERE channelid = %s", (channel_id,))
            if self.fetch_one() == 1:
                return True
            else:
                return False
        elif server_id is not None:
            try:
                self.c.execute("SELECT status FROM logging.servers WHERE serverid = %s", (server_id,))
                if self.fetch_one() == 1:
                    return True
                else:
                    return False
            except Exception as e:
                return False

    async def set_logging_status(self, server_id, status):  # status can only be 0 or 1
        """Set a server's logging status."""
        self.c.execute("UPDATE logging.servers SET status = %s WHERE serverid = %s", (status, server_id))
        self.DBconn.commit()

    async def get_logging_id(self, server_id):
        """Get the ID in the table of a server."""
        self.c.execute("SELECT id FROM logging.servers WHERE serverid = %s", (server_id,))
        return self.fetch_one()

    async def check_logging_requirements(self, message):
        """Check if a message meets all the logging requirements."""
        try:
            if not message.author.bot:
                if await self.check_if_logged(server_id=message.guild.id):
                    if await self.check_if_logged(channel_id=message.channel.id):
                        return True
        except Exception as e:
            pass
        return False

    @staticmethod
    async def get_attachments(message):
        """Get the attachments of a message."""
        files = None
        if len(message.attachments) != 0:
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())
        return files

    async def get_log_channel_id(self, message):
        """Get the channel where logs are made on a server."""
        self.c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (message.guild.id,))
        return self.client.get_channel(self.fetch_one())

    ######################
    # ## DREAMCATCHER ## #
    ######################
    def get_dc_channels(self):
        """Get all the servers that receive DC APP Updates."""
        self.c.execute("SELECT serverid FROM dreamcatcher.dreamcatcher")
        return self.fetch_all()

    def get_video_and_bat_list(self, page_soup):
        """Get a list of all the .bat and video files."""
        video_list = (page_soup.findAll("div", {"class": "swiper-slide img-box video-box width"}))
        if len(video_list) == 0:
            video_list = (page_soup.findAll("div", {"class": "swiper-slide img-box video-box height"}))
        count_numbers = 0
        video_name_list = []
        bat_name_list = []
        for video in video_list:
            count_numbers += 1
            new_video_url = video.source["src"]
            bat_name = "{}DC.bat".format(count_numbers)
            bat_name_list.append(bat_name)
            ab = open("Videos\{}".format(bat_name), "a+")
            video_name = "{}DCVideo.mp4".format(count_numbers)
            info = 'ffmpeg -i "{}" -c:v libx264 -preset slow -crf 22 "Videos/{}"'.format(new_video_url,
                                                                                         video_name)
            video_name_list.append(video_name)
            ab.write(info)
            ab.close()
        return self.get_none_if_list_is_empty(video_name_list), self.get_none_if_list_is_empty(bat_name_list)

    @staticmethod
    def get_videos(video_name_list):
        """Return a list of discord.File that contains videos."""
        dc_videos = []
        try:
            if video_name_list is not None:
                for video_name in video_name_list:
                    dc_video = discord.File(fp='Videos/{}'.format(video_name),
                                            filename=video_name)
                    dc_videos.append(dc_video)
            else:
                return None
        except Exception as e:
            log.console(e)
            pass
        return dc_videos

    @staticmethod
    def get_photos(photo_name_list):
        """Return a list of discord.File that contains photos."""
        dc_photos = []
        try:
            if photo_name_list is not None:
                for file_name in photo_name_list:
                    dc_photo = discord.File(fp='DCApp/{}'.format(file_name),
                                            filename=file_name)
                    dc_photos.append(dc_photo)
            else:
                return None
        except Exception as e:
            log.console(e)
        return dc_photos

    async def get_embed(self, image_links, member_name):
        """Create the embed for a DC APP post."""
        embed_list = []
        for link in image_links:
            embed = discord.Embed(title=member_name, color=self.get_random_color(), url=link)
            embed.set_image(url=link)
            embed = await self.set_embed_author_and_footer(embed, "Thanks for using Irene.")
            embed_list.append(embed)
        return self.get_none_if_list_is_empty(embed_list)

    @staticmethod
    async def send_content(channel, dc_photos_embeds, dc_videos):
        """Send the DC APP post to the channels."""
        try:
            if dc_photos_embeds is not None:
                for dc_photo_embed in dc_photos_embeds:
                    await channel.send(embed=dc_photo_embed)
            if dc_videos is not None:
                for video in dc_videos:
                    await channel.send(file=video)
        except Exception as e:
            log.console(e)

    @staticmethod
    def delete_content():
        """Delete any videos or photos that were downloaded."""
        all_videos = os.listdir('Videos')
        for video in all_videos:
            try:
                os.unlink('Videos/{}'.format(video))
            except Exception as e:
                log.console(e)
                pass
        all_photos = os.listdir('DCApp')
        for photo in all_photos:
            try:
                os.unlink('DCApp/{}'.format(photo))
            except Exception as e:
                log.console(e)
                pass

    @staticmethod
    def get_member_name_and_id(username, member_list):
        """return the member name and id of a post."""
        member_id = None
        member_name = None
        if username == member_list[0]:
            member_name = "Gahyeon"
            member_id = 163
        if username == member_list[1]:
            member_name = "Siyeon"
            member_id = 159
        if username == member_list[2]:
            member_name = "Yoohyeon"
            member_id = 161
        if username == member_list[3]:
            member_name = "JIU"
            member_id = 157
        if username == member_list[4]:
            member_name = "SUA"
            member_id = 158
        if username == member_list[5]:
            member_name = "DC"
        if username == member_list[6]:
            member_name = "Dami"
            member_id = 162
        if username == member_list[7]:
            member_name = "Handong"
            member_id = 160
        return member_name, member_id

    def add_post_to_db(self, image_links, member_id, member_name, post_number, post_url):
        """Add a post's information to the database."""
        if image_links is not None:
            for link in image_links:
                try:
                    if member_id is not None:
                        self.c.execute("INSERT INTO groupmembers.imagelinks VALUES (%s,%s)", (link, member_id))
                    self.c.execute("INSERT INTO dreamcatcher.DCHDLinks VALUES (%s,%s,%s)", (link, member_name.lower(), post_number))
                    self.c.execute("UPDATE dreamcatcher.DCUrl SET url = %s WHERE member = %s", (post_url, "latest"))
                    self.c.execute("UPDATE dreamcatcher.DCUrl SET url = %s WHERE member = %s", (post_url, member_name.lower()))
                    self.DBconn.commit()
                except Exception as e:
                    log.console(e)
                    pass

    async def send_new_post(self, channel_id, channel, member_name, status_message, post_url):
        """Send the status information to a channel."""
        try:
            await channel.send(f">>> **New {member_name} Post\n<{post_url}>\nStatus Message: {status_message}**")
        except AttributeError:
            try:
                self.c.execute("DELETE from dreamcatcher.dreamcatcher WHERE serverid = %s", (channel_id,))
                self.DBconn.commit()
            except Exception as e:
                log.console(e)
        except Exception as e:
            await channel.send(f">>> **New {member_name} Post\n<{post_url}>**")

    @staticmethod
    async def open_bat_file(bat_list):
        """Open a bat file to process the video with ffmpeg."""
        for bat_name in bat_list:
            # open bat file
            check_bat = await asyncio.create_subprocess_exec("Videos\\{}".format(bat_name),
                                                             stderr=asyncio.subprocess.PIPE)
            await check_bat.wait()

    async def get_image_list(self, image_url, post_url, image_links):
        """Downloads Thumbnail Photos//This was before embeds were being used and was very inefficient. || Not Used"""
        photo_name_list = []
        new_count = -1
        final_image_list = []
        for image in image_url:
            new_count += 1
            new_image_url = image.img["src"]
            file_name = new_image_url[82:]
            async with self.session.get(new_image_url) as resp:
                fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                await fd.write(await resp.read())
                await fd.close()
                file_size = (os.path.getsize(f'DCApp/{file_name}'))
                if file_size <= 20000:
                    keep_going = True
                    loop_count = 0
                    while keep_going:
                        log.console(f"Stuck in a loop {loop_count}")
                        loop_count += 1
                        try:
                            os.unlink(f'DCApp/{file_name}')
                        except Exception as e:
                            log.console(e)
                        fd = await aiofiles.open('DCApp/{}'.format(file_name), mode='wb')
                        await fd.write(await resp.read())
                        await fd.close()
                        file_size = (os.path.getsize(f'DCApp/{file_name}'))
                        if file_size > 20000:
                            photo_name_list.append(file_name)
                            keep_going = False
                        if loop_count == 30:
                            try:
                                final_image_list.append(image_links[new_count])
                                os.unlink(f'DCApp/{file_name}')
                                keep_going = False
                            except Exception as e:
                                log.console(e)
                                keep_going = False
                elif file_size > 20000:
                    photo_name_list.append(file_name)
        return self.get_none_if_list_is_empty(photo_name_list), self.get_none_if_list_is_empty(final_image_list)

    @staticmethod
    async def download_dc_photos(image_url):
        """Return the list of HD links."""
        image_links = []
        for image in image_url:
            new_image_url = image.img["src"]
            dc_date = new_image_url[41:49]
            unique_id = new_image_url[55:87]
            file_format = new_image_url[93:]
            hd_link = f'https://file.candlemystar.com/post/{dc_date}{unique_id}{file_format}'
            image_links.append(hd_link)
            # do not download hd links so that they are sent to channels quicker.
            """
            async with session.get(hd_link) as resp:
                fd = await aiofiles.open(
                    'DreamHD/{}'.format(f"{unique_id[:8]}{file_format}"), mode='wb')
                await fd.write(await resp.read())
                await fd.close()
            """
        return image_links


resources = Utility()

