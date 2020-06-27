import discord
import random
import asyncio
from module import logger as log
from module import keys
import aiohttp
import aiofiles
from bs4 import BeautifulSoup as soup
import os
import math
import re

"""
Utility.py
Resource Center for Irene
Any potentially useful functions will end up here
"""
session = aiohttp.ClientSession()  # This is only used for calling idol photos to improve performance.
##################
# ## DATABASE ## #
##################


def get_db_connection():
    return keys.DBconn, keys.DBconn.cursor()


client = keys.client
DBconn, c = get_db_connection()
DBconn.autocommit = False


def fetch_one():
    try:
        results = c.fetchone()[0]
    except Exception as e:
        results = None
    return results


def fetch_all():
    try:
        results = c.fetchall()
    except Exception as e:
        log.console(e)
        results = []
        pass
    return results

##################
# ## CURRENCY ## #
##################


async def register_user(user_id):
    c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
    count = fetch_one()
    if count == 0:
        c.execute("INSERT INTO currency.Currency (UserID, Money) VALUES (%s, %s)", (user_id, "100"))
        DBconn.commit()
        return True
    elif count == 1:
        return False


async def get_user_has_money(user_id):
    c.execute("SELECT COUNT(*) FROM currency.Currency WHERE UserID = %s", (user_id,))
    return not fetch_one() == 0


async def get_balance(user_id):
    if not (await register_user(user_id)):
        c.execute("SELECT money FROM currency.currency WHERE userid = %s", (user_id,))
        return int(fetch_one())
    else:
        return 100


async def shorten_balance(money):  # money must be passed in as a string.
    place_names = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion', 'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quatturodecillion', 'Quindecillion', 'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion', 'Centillion']
    place_values = int(math.log10(int(money)) // 3)
    try:
        return f"{int(money) // (10 ** (3 * place_values))} {place_names[place_values]}"
    except Exception as e:
        return "Too Fucking Much$"


async def update_balance(user_id, new_balance):
    c.execute("UPDATE currency.Currency SET Money = %s::text WHERE UserID = %s", (str(new_balance), user_id))
    DBconn.commit()


async def get_robbed_amount(author_money, user_money, level):
    max_amount = int(user_money // 100)  # b value
    if max_amount > int(author_money // 2):
        max_amount = int(author_money // 2)
    min_amount = int((max_amount * 100) // 100)
    if min_amount > max_amount:  # kind of ironic, but it is possible for min to surpass max in this case
        robbed_amount = random.randint(max_amount, min_amount)
    else:
        robbed_amount = random.randint(min_amount, max_amount)
    return robbed_amount


def remove_commas(amount):
    return int(amount.replace(',', ''))

#######################
# ## MISCELLANEOUS ## #
#######################


async def ban_user_from_bot(user_id):
    c.execute("INSERT INTO general.blacklisted(userid) VALUES (%s)", (user_id,))
    DBconn.commit()


async def unban_user_from_bot(user_id):
    c.execute("DELETE FROM general.blacklisted WHERE userid = %s", (user_id,))
    DBconn.commit()


async def check_if_bot_banned(user_id):
    c.execute("SELECT COUNT(*) FROM general.blacklisted WHERE userid = %s", (user_id,))
    return fetch_one() == 1


def check_nword(message_content):
    message_split = message_content.lower().split()
    return 'nigga' in message_split or 'nigger' in message_split and ':' not in message_split


def check_if_mod(ctx, mode=0):  # as mode = 1, ctx is the author id.
    if mode == 0:
        user_id = ctx.author.id
        return user_id in keys.mods_list or user_id == keys.owner_id
    else:
        return ctx in keys.mods_list or ctx == keys.owner_id


def get_none_if_list_is_empty(new_list):
    if len(new_list) == 0:
        return None
    else:
        return new_list


def get_ping():
    return int(client.latency * 1000)


def get_int_index(original, index):
    entire_selection = ""
    counter = 0
    for value in str(original):
        if counter < index:
          entire_selection += value
        counter += 1
    return int(entire_selection)


def get_random_color():
    r = lambda: random.randint(0, 255)
    return int(('%02X%02X%02X' % (r(), r(), r())), 16)  # must be specified to base 16 since 0x is not present


async def create_embed(title="Irene", color=None, title_desc=None, footer_desc="Thanks for using Irene!"):
    if color is None:
        color = get_random_color()
    if title_desc is None:
        embed = discord.Embed(title=title, color=color)
    else:
        embed = discord.Embed(title=title, color=color, description=title_desc)
    embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                     icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
    embed.set_footer(text=footer_desc, icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
    return embed


async def check_reaction(msg, user_id, reaction_needed):
    def react_check(reaction_used, user_reacted):
        return (user_reacted.id == user_id) and (reaction_used.emoji == reaction_needed)

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60, check=react_check)
        return True
    except asyncio.TimeoutError:
        await msg.delete()
        return False


async def get_cooldown_time(time):
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


def check_embed_exists(message):
    try:
        for embed_check in message.embeds:
            if len(embed_check) > 0:
                return True
    except Exception as e:
        pass
    return False


def check_message_not_empty(message):
    try:
        if len(message.clean_content) >= 1:
            return True
    except Exception as e:
        pass
    return False


def get_message_prefix(message):
    try:
        if check_message_not_empty(message):
            return message.clean_content[0]
    except Exception as e:
        pass
    return None


async def check_left_or_right_reaction_embed(msg, embed_lists, original_page_number=0, reaction1="\U00002b05", reaction2="\U000027a1"):
    await msg.add_reaction(reaction1)  # left arrow by default
    await msg.add_reaction(reaction2)  # right arrow by default

    def reaction_check(user_reaction, reaction_user):
        return ((user_reaction.emoji == '➡') or (
                    user_reaction.emoji == '⬅')) and reaction_user != msg.author and user_reaction.message.id == msg.id

    async def change_page(c_page):
        try:
            reaction, user = await client.wait_for('reaction_add', check=reaction_check)
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


async def set_embed_author_and_footer(embed, footer_message):
    embed.set_author(name="Irene", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                     icon_url='https://cdn.discordapp.com/emojis/693392862611767336.gif?v=1')
    embed.set_footer(text=footer_message,
                     icon_url='https://cdn.discordapp.com/emojis/683932986818822174.gif?v=1')
    return embed


async def get_language_code(language):
    language = language.lower()
    languages = ['ko', 'en', 'ja', 'zh-CN', 'zh-TW', 'es', 'fr', 'vi', 'th', 'id']
    ko_keywords = ['korean', 'ko', 'kr', 'korea', 'kor']
    eng_keywords = ['en', 'eng', 'english']
    ja_keywords = ['jp', 'jap', 'japanese', 'japan']
    zhCN_keywords = ['chinese', 'ch', 'zh-cn', 'zhcn', 'c', 'china']
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
    elif language in zhCN_keywords:
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


async def get_server_prefix(server_id):
    c.execute("SELECT prefix FROM general.serverprefix WHERE serverid = %s", (server_id,))
    prefix = fetch_one()
    if prefix is None:
        return keys.bot_prefix
    else:
        return prefix


async def get_server_prefix_by_context(ctx):
    try:
        server_id = ctx.guild.id
    except Exception as e:
        return keys.bot_prefix
    c.execute("SELECT prefix FROM general.serverprefix WHERE serverid = %s", (server_id,))
    prefix = fetch_one()
    if prefix is None:
        return keys.bot_prefix
    else:
        return prefix


async def get_bot_statuses():
    c.execute("SELECT status FROM general.botstatus")
    statuses = fetch_all()
    if len(statuses) == 0:
        return None
    else:
        return statuses


def get_user_count():
    counter = 0
    for guild in client.guilds:
        counter += guild.member_count
    return counter


def get_server_count():
    return len(client.guilds)


def get_channel_count():
    count = 0
    for guild in client.guilds:
        count += len(guild.channels)
    return count


def get_text_channel_count():
    count = 0
    for guild in client.guilds:
        count += len(guild.text_channels)
    return count


def get_voice_channel_count():
    count = 0
    for guild in client.guilds:
        count += len(guild.voice_channels)
    return count


###################
# ## BLACKJACK ## #
###################


async def check_in_game(user_id, ctx):  # this is meant for when it is accessed by commands outside of BlackJack.
    c.execute("SELECT COUNT(*) From blackjack.games WHERE player1 = %s OR player2 = %s", (user_id, user_id))
    check = fetch_one()
    if check == 1:
        await ctx.send(f"> **{ctx.author}, you are already in a pending/active game. Please type {await get_server_prefix_by_context(ctx)}endgame.**")
        return True
    else:
        return False


async def add_bj_game(user_id, bid, ctx, mode):
    c.execute("INSERT INTO blackjack.games (player1, bid1, channelid) VALUES (%s, %s, %s)", (user_id, bid, ctx.channel.id))
    DBconn.commit()
    game_id = get_game_by_player(user_id)
    if mode != "bot":
        await ctx.send(f"> **There are currently 1/2 members signed up for BlackJack. To join the game, please type {await get_server_prefix_by_context(ctx)}joingame {game_id} (bid)** ")


async def process_bj_game(ctx, amount, user_id):
    if amount >= 0:
        if not await check_in_game(user_id, ctx):
            if amount > await get_balance(user_id):
                await ctx.send(f"> **{ctx.author}, you can not bet more than your current balance.**")
            else:
                return True
    else:
        await ctx.send(f"> **{ctx.author}, you can not bet a negative number.**")
    return False


def get_game_by_player(player_id):
    c.execute("SELECT gameid FROM blackjack.games WHERE player1 = %s OR player2 = %s", (player_id, player_id))
    return fetch_one()


def get_game(game_id):
    c.execute("SELECT gameid, player1, player2, bid1, bid2, channelid FROM blackjack.games WHERE gameid = %s", (game_id,))
    return c.fetchone()


def add_player_two(game_id, user_id, bid):
    c.execute("UPDATE blackjack.games SET player2 = %s, bid2 = %s WHERE gameid = %s ", (user_id, bid, game_id))
    DBconn.commit()


def get_current_cards(user_id):
    c.execute("SELECT inhand FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
    in_hand = fetch_one()
    if in_hand is None:
        return []
    return in_hand.split(',')


def check_player_standing(user_id):
    c.execute("SELECT stand FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
    return fetch_one() == 1


def set_player_stand(user_id):
    c.execute("UPDATE blackjack.currentstatus SET stand = %s WHERE userid = %s", (1, user_id))
    DBconn.commit()


def delete_player_status(user_id):
    c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
    DBconn.commit()


def add_player_status(user_id):
    delete_player_status(user_id)
    c.execute("INSERT INTO blackjack.currentstatus (userid, stand, total) VALUES (%s, %s, %s)", (user_id, 0, 0))
    DBconn.commit()


def get_player_total(user_id):
    c.execute("SELECT total FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
    return fetch_one()


def get_card_value(card):
    c.execute("SELECT value FROM blackjack.cards WHERE id = %s", (card,))
    return fetch_one()


def get_all_cards():
    c.execute("SELECT id FROM blackjack.cards")
    card_tuple = fetch_all()
    all_cards = []
    for card in card_tuple:
        all_cards.append(card[0])
    return all_cards


def get_available_cards(game_id):  # pass in a list of card ids
    all_cards = get_all_cards()
    available_cards = []
    game = get_game(game_id)
    player1_cards = get_current_cards(game[1])
    player2_cards = get_current_cards(game[2])
    for card in all_cards:
        if card not in player1_cards and card not in player2_cards:
            available_cards.append(card)
    return available_cards


def get_card_name(card_id):
    c.execute("SELECT name FROM blackjack.cards WHERE id = %s", (card_id,))
    return fetch_one()


def check_if_ace(card_id, user_id):
    aces = ["1", "14", "27", "40"]
    aces_used = get_aces_used(user_id)
    if card_id in aces and card_id not in aces_used:
        aces_used.append(card_id)
        set_aces_used(aces_used, user_id)
        return True
    return False


def set_aces_used(card_list, user_id):
    separator = ','
    cards = separator.join(card_list)
    c.execute("UPDATE blackjack.currentstatus SET acesused = %s WHERE userid = %s", (cards, user_id))
    DBconn.commit()


def get_aces_used(user_id):
    c.execute("SELECT acesused FROM blackjack.currentstatus WHERE userid = %s", (user_id,))
    aces_used = fetch_one()
    if aces_used is None:
        return []
    return aces_used.split(',')


def check_if_bot(user_id):
    return str(get_int_index(keys.bot_id, 9)) in str(user_id)


async def add_card(user_id):
    end_game = False
    check = 0

    separator = ','
    current_cards = get_current_cards(user_id)
    game_id = get_game_by_player(user_id)
    game = get_game(game_id)
    channel = await client.fetch_channel(game[5])
    stand = check_player_standing(user_id)
    player1_score = get_player_total(game[1])
    player2_score = get_player_total(game[2])
    player1_cards = get_current_cards(game[1])
    if not stand:
        available_cards = get_available_cards(game_id)
        random_card = random.choice(available_cards)
        current_cards.append(str(random_card))
        cards = separator.join(current_cards)
        current_total = get_player_total(user_id)
        random_card_value = get_card_value(random_card)
        if current_total + random_card_value > 21:
            for card in current_cards:  # this includes the random card
                if check_if_ace(card, user_id) and check != 1:
                    check = 1
                    current_total = (current_total + random_card_value) - 10
            if check == 0:  # if there was no ace
                current_total = current_total + random_card_value
        else:
            current_total = current_total + random_card_value
        c.execute("UPDATE blackjack.currentstatus SET inhand = %s, total = %s WHERE userid = %s", (cards, current_total, user_id))
        DBconn.commit()
        if current_total > 21:
            if user_id == game[2] and check_if_bot(game[2]):
                if player1_score > 21 and current_total >= 16:
                    end_game = True
                    set_player_stand(game[1])
                    set_player_stand(game[2])
                elif player1_score > 21 and current_total < 16:
                    await add_card(game[2])
                elif player1_score < 22 and current_total > 21:
                    pass
                else:
                    end_game = True
            elif check_if_bot(game[2]) and not check_if_bot(user_id):  # if user_id is not the bot
                if player2_score < 16:
                    await add_card(game[2])
                else:
                    set_player_stand(user_id)
                    set_player_stand(game[2])
                    end_game = True
        else:
            if user_id == game[2] and check_if_bot(game[2]):
                if current_total < 16143478541328187392 and len(player1_cards) > 2:
                    await add_card(game[2])
                if check_player_standing(game[1]) and current_total >= 16:
                    end_game = True
        if not check_if_bot(user_id):
            if check_if_bot(game[2]):
                await send_cards_to_channel(channel, user_id, random_card, True)
            else:
                await send_cards_to_channel(channel, user_id, random_card)
    else:
        await channel.send(f"> **You already stood.**")
        if check_game_over(game_id):
            await finish_game(game_id, channel)
    if end_game:
        await finish_game(game_id, channel)


async def send_cards_to_channel(channel, user_id, card, bot_mode=False):
    if bot_mode:
        card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=False)
    else:
        card_file = discord.File(fp=f'Cards/{card}.jpg', filename=f'{card}.jpg', spoiler=True)
    total_score = str(get_player_total(user_id))
    if len(total_score) == 1:
        total_score = '0' + total_score  # this is to prevent being able to detect the number of digits by the spoiler
    card_name = get_card_name(card)
    if bot_mode:
        await channel.send(f"<@{user_id}> pulled {card_name}. Their current score is {total_score}", file=card_file)
    else:
        await channel.send(f"<@{user_id}> pulled ||{card_name}||. Their current score is ||{total_score}||", file=card_file)


async def compare_channels(user_id, channel):
    game_id = get_game_by_player(user_id)
    game = get_game(game_id)
    if game[5] == channel.id:
        return True
    else:
        await channel.send(f"> **{user_id}, that game ({game_id}) is not available in this text channel.**")
        return False


async def start_game(game_id):
    game = get_game(game_id)
    player1 = game[1]
    player2 = game[2]
    add_player_status(player1)
    add_player_status(player2)
    # Add Two Cards to both players [ Not in a loop because the messages should be in order on discord ]
    await add_card(player1)
    await add_card(player1)
    await add_card(player2)
    await add_card(player2)


def check_game_over(game_id):
    game = get_game(game_id)
    player1_stand = check_player_standing(game[1])
    player2_stand = check_player_standing(game[2])
    if player1_stand and player2_stand:
        return True
    else:
        return False


def determine_winner(score1, score2):
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


async def announce_winner(channel, winner, loser, winner_points, loser_points, win_amount):
    if check_if_bot(winner):
        await channel.send(f"> **<@{keys.bot_id}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")
    elif check_if_bot(loser):
        await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{keys.bot_id}> with {loser_points}.**")
    else:
        await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")


async def announce_tie(channel, player1, player2, tied_points):
    if check_if_bot(player1) or check_if_bot(player2):
        await channel.send(f"> **<@{player1}> and <@{keys.bot_id}> have tied with {tied_points}**")
    else:
        await channel.send(f"> **<@{player1}> and <@{player2}> have tied with {tied_points}**")


async def finish_game(game_id, channel):
    game = get_game(game_id)
    player1_score = get_player_total(game[1])
    player2_score = get_player_total(game[2])
    if player2_score < 12 and check_if_bot(game[2]):
        await add_card(game[2])
    else:
        winner = determine_winner(player1_score, player2_score)
        player1_current_bal = await get_balance(game[1])
        player2_current_bal = await get_balance(game[2])
        if winner == 'player1':
            await update_balance(game[1], player1_current_bal + int(game[4]))
            if not check_if_bot(game[2]):
                await update_balance(game[2], player2_current_bal - int(game[4]))
            await announce_winner(channel, game[1], game[2], player1_score, player2_score, game[4])
        elif winner == 'player2':
            if not check_if_bot(game[2]):
                await update_balance(game[2], player2_current_bal + int(game[3]))
            await update_balance(game[1], player1_current_bal - int(game[3]))
            await announce_winner(channel, game[2], game[1], player2_score, player1_score, game[3])
        elif winner == 'tie':
            await announce_tie(channel, game[1], game[2], player1_score)
        delete_game(game_id)


def delete_game(game_id):
    game = get_game(game_id)
    c.execute("DELETE FROM blackjack.games WHERE gameid = %s", (game_id,))
    c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (game[1],))
    c.execute("DELETE FROM blackjack.currentstatus WHERE userid = %s", (game[2],))
    log.console(f"Game {game_id} deleted.")


def delete_all_games():
    c.execute("SELECT gameid FROM blackjack.games")
    all_games = fetch_all()
    for games in all_games:
        game_id = games[0]
        delete_game(game_id)
################
# ## LEVELS ## #
################


async def get_level(user_id, command):
    c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s AND {command} > %s", (user_id, 1))
    if fetch_one() == 0:
        level = 1
    else:
        c.execute(f"SELECT {command} FROM currency.Levels WHERE UserID = %s", (user_id,))
        level = fetch_one()
    return int(level)


async def set_level(user_id, level, command):
    def update_level():
        c.execute(f"UPDATE currency.Levels SET {command} = %s WHERE UserID = %s", (level, user_id))
        DBconn.commit()

    c.execute(f"SELECT COUNT(*) FROM currency.Levels WHERE UserID = %s", (user_id,))
    if fetch_one() == 0:
        c.execute("INSERT INTO currency.Levels VALUES(%s, NULL, NULL, NULL, NULL, 1)", (user_id,))
        DBconn.commit()
        update_level()
    else:
        update_level()


async def get_xp(level, command):
    """Returns money/experience needed for a certain level."""
    if command == "profile":
        return 250 * level
    return int((2 * 350) * (2 ** (level - 2)))  # 350 is base value (level 1)


async def get_rob_percentage(level):
    chance = int(6 + (level // 10))  # first 10 levels is 6 for 30% chance
    if chance > 16:
        chance = 16
    return chance

#######################
# ## GROUP MEMBERS ## #
#######################


async def get_all_images_count():
    c.execute("SELECT COUNT(*) FROM groupmembers.imagelinks")
    return fetch_one()


def get_idol_called(member_id):
    c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
    counter = fetch_one()
    return counter


async def check_if_folder(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return True
            return False


async def get_idol_count(member_id):
    c.execute("SELECT COUNT(*) FROM groupmembers.ImageLinks WHERE MemberID = %s", (member_id,))
    count = fetch_one()
    return count


async def get_random_idol_id():
    member_ids = await get_all_members()
    return (random.choice(member_ids))[0]


async def get_all_members():
    c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.Member")
    return fetch_all()


async def get_all_groups():
    c.execute("SELECT groupid, groupname, aliases FROM groupmembers.groups ORDER BY groupname")
    return fetch_all()


async def get_members_in_group(group_name):
    c.execute(f"SELECT groupid FROM groupmembers.groups WHERE groupname = %s", (group_name,))
    group_id = fetch_one()
    all_members = await get_all_members()
    members_in_group = []
    for member in all_members:
        member_info = [member[0], member[2]]
        in_groups = member[3].split(',')
        if str(group_id) in in_groups:
            members_in_group.append(member_info)
    return members_in_group


async def get_member(member_id):
    c.execute("SELECT id, fullname, stagename, ingroups, aliases FROM groupmembers.member WHERE id = %s", (member_id,))
    return c.fetchone()


async def get_group_name(group_id):
    c.execute("SELECT groupname FROM groupmembers.groups WHERE groupid = %s", (group_id,))
    return fetch_one()


async def get_group_id_from_member(member_id):
    member_info = await get_member(member_id)
    return ((member_info[3]).split(','))[0]


async def send_names(ctx, mode, user_page_number):
    async def check_mode(embed_temp):
        if mode == "fullname":
            embed_temp = await set_embed_author_and_footer(embed_temp, f"Type {await get_server_prefix_by_context(ctx)}members for Stage Names.")
        else:
            embed_temp = await set_embed_author_and_footer(embed_temp, f"Type {await get_server_prefix_by_context(ctx)}fullnames for Full Names.")
        return embed_temp
    is_mod = check_if_mod(ctx)
    embed_lists = []
    all_members = await get_all_members()
    all_groups = await get_all_groups()
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
    await check_left_or_right_reaction_embed(msg, embed_lists, user_page_number-1)


async def set_embed_with_all_aliases(mode):
    check = False
    if mode == "Group":
        all_info = await get_all_groups()
    else:
        all_info = await get_all_members()
    embed_list = []
    count = 0
    page_number = 1
    embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=get_random_color())
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
            embed = discord.Embed(title=f"{mode} Aliases Page {page_number}", description="", color=get_random_color())
    if count != 0:
        embed_list.append(embed)
    return embed_list


async def check_idol_post_reactions(message, user_msg):
    try:
        if message is not None:
            reload_image_emoji = "<:ReloadImage:694109526491922463>"
            dead_link_emoji = "<:DeadLink:695787733460844645>"
            await message.add_reaction(reload_image_emoji)
            await message.add_reaction(dead_link_emoji)
            message = await message.channel.fetch_message(message.id)

            def image_check(user_reaction, reaction_user):
                user_check = (reaction_user == user_msg.author) or (reaction_user.id == keys.owner_id)
                return user_check and (str(user_reaction.emoji) == dead_link_emoji or str(user_reaction.emoji) ==
                                       reload_image_emoji) and user_reaction.message.id == message.id

            async def reload_image(message1):
                try:
                    reaction, user = await client.wait_for('reaction_add', check=image_check)
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
                        await check_idol_post_reactions(message1, user_msg)
                    elif str(reaction) == dead_link_emoji:
                        try:
                            link = message1.embeds[0].url
                        except:
                            link = message1.content
                        c.execute("INSERT INTO groupmembers.DeadLinkFromUser VALUES(%s,%s)", (link, user.id))
                        DBconn.commit()
                        await message1.delete()

                except Exception as e:
                    log.console(e)
                    pass
            await reload_image(message)
    except Exception as e:
        pass


async def get_id_where_member_matches_name(name, mode=0):
    all_members = await get_all_members()
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


async def get_id_where_group_matches_name(name, mode=0):
    all_groups = await get_all_groups()
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


async def check_group_and_idol(message):
    group_ids, new_message = await get_id_where_group_matches_name(message, mode=1)
    member_list = []
    for group_id in group_ids:
        members_in_group = await get_members_in_group(await get_group_name(group_id))
        member_ids = await get_id_where_member_matches_name(new_message, 1)
        for member_id in member_ids:
            for group_member in members_in_group:
                group_member_id = group_member[0]
                if member_id == group_member_id:
                    member_list.append(member_id)
    return get_none_if_list_is_empty(member_list)


async def get_random_photo_from_member(member_id):
    c.execute("SELECT link FROM groupmembers.imagelinks WHERE memberid = %s", (member_id,))
    return (random.choice(fetch_all()))[0]


async def update_member_count(member_id):
    c.execute("SELECT COUNT(*) FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
    count = fetch_one()
    if count == 0:
        c.execute("INSERT INTO groupmembers.Count VALUES(%s, %s)", (member_id, 1))
    else:
        c.execute("SELECT Count FROM groupmembers.Count WHERE MemberID = %s", (member_id,))
        count = fetch_one()
        count += 1
        c.execute("UPDATE groupmembers.Count SET Count = %s WHERE MemberID = %s", (count, member_id))
    DBconn.commit()


def remove_custom_characters(file_name):
    allowed_characters = "abcdefghijklmnopqrstuvwxyz1234567890."
    for character in file_name:
        if character not in allowed_characters:
            file_name = file_name.replace(character, "z")
    return file_name


async def send_google_drive_embed(photo_link, embed, channel, drive_id, member_id, group_id):
    try:
        post_url = f"https://drive.google.com/file/d/{drive_id}/view?usp=sharing"
        async with session.get(post_url) as r:
            async with session.get(photo_link) as resp:
                if resp.status == 200:
                    page_html = await r.text()
                    page_soup = soup(page_html, "html.parser")
                    title_loc = (page_soup.find("title"))
                    title_end = (str(title_loc.next).find(" - Google Drive"))
                    file_name = (title_loc.next[0:title_end])
                    file_name = remove_custom_characters(file_name)  # Important to have photo not outisde of embed.
                    file_location = f'temp/{file_name}'
                    fd = await aiofiles.open(file_location, mode='wb')
                    await fd.write(await resp.read())
                    await fd.close()
                    file_size = os.path.getsize(file_location)  # bytes (conversion binary)
                    if file_size < 8388608:  # 8 MB
                        photo = discord.File(file_location, file_name)
                        embed.set_image(url=f"attachment://{file_name}")
                        if not check_photo_animated(file_name):
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
                    c.execute("DELETE FROM groupmembers.imagelinks WHERE link = %s", (photo_link,))
                    c.execute("INSERT INTO groupmembers.deleted(link, memberid) VALUES (%s,%s)", (photo_link, 0))
                    DBconn.commit()
                    # send a new post
                    random_link = await get_random_photo_from_member(member_id)
                    await idol_post(channel, member_id, random_link, group_id)
                else:
                    log.console(f"ERROR {resp.status} Member ID: {member_id}- {photo_link}")
    except Exception as e:
        log.console(e)


def check_photo_animated(photo_name):
    mp3 = photo_name.find('mp3')
    mp4 = photo_name.find('mp4')
    gif = photo_name.find('gif')
    if gif == -1 and mp4 == -1 and mp3 == -1:
        return False
    else:
        return True


def check_link_origin(link):
    tenor = link.find("tenor.com", 0)
    drive = link.find("drive", 0)
    if tenor != -1:
        return 'tenor'
    elif drive != -1:
        return 'drive'
    else:
        return 'other'


async def get_idol_post_embed(group_id, member_info, photo_link):
    if group_id is None:
        embed = discord.Embed(title=f"{member_info[1]} ({member_info[2]})", color=get_random_color(),
                              url=photo_link)
    else:
        embed = discord.Embed(title=f"{await get_group_name(group_id)} ({member_info[2]})",
                              color=get_random_color(), url=photo_link)
    return embed


async def idol_post(channel, member_id, photo_link, group_id=None):
    try:
        member_info = await get_member(member_id)
        link_origin = check_link_origin(photo_link)
        await update_member_count(member_id)
        if link_origin == 'drive':
            id_loc = photo_link.find("id=") + 3
            drive_id = photo_link[id_loc:len(photo_link)]
            embed = await get_idol_post_embed(group_id, member_info, photo_link)
            msg = await send_google_drive_embed(photo_link, embed, channel, drive_id, member_id, group_id)
            return msg
        if link_origin == 'tenor':
            msg = await channel.send(photo_link)
            return msg
        else:
            embed = await get_idol_post_embed(group_id, member_info, photo_link)
            embed.set_image(url=photo_link)
            msg = await channel.send(embed=embed)
            return msg
    except Exception as e:
        log.console(e)


#################
# ## LOGGING ## #
#################


async def get_servers_logged():
    c.execute("SELECT serverid FROM logging.servers")
    server_ids = fetch_all()
    servers_logged = []
    for server in server_ids:
        if await check_if_logged(server_id = server):
            servers_logged.append(server)
    return servers_logged


async def get_channels_logged():
    c.execute("SELECT channelid, server FROM logging.channels")
    channel_ids = fetch_all()
    channels_logged = []
    for channel in channel_ids:
        channel_id = channel[0]
        channel_guild = channel[1]  # not the server id, just the row id
        c.execute("SELECT serverid FROM logging.servers WHERE id = %s", (channel_guild,))
        channel_guild = fetch_one()
        if await check_if_logged(server_id=channel_guild):
            # No need to check if channel is logged because the list already confirms it is logged.
            channels_logged.append(channel_id)
    return channels_logged


async def add_to_logging(server_id, channel_id):  # return true if status is on
        c.execute("SELECT COUNT(*) FROM logging.servers WHERE serverid = %s", (server_id,))
        if fetch_one() == 0:
            c.execute("INSERT INTO logging.servers (serverid, channelid, status, sendall) VALUES (%s, %s, %s, %s)", (server_id, channel_id, 1, 1))
            DBconn.commit()
        else:
            await set_logging_status(server_id, 1)
            c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (server_id,))
            if fetch_one() != channel_id:
                c.execute("UPDATE logging.servers SET channelid = %s WHERE serverid = %s", (channel_id, server_id))
        return True


async def check_if_logged(server_id=None, channel_id=None):  # only one parameter should be passed in
    if channel_id is not None:
        c.execute("SELECT COUNT(*) FROM logging.channels WHERE channelid = %s", (channel_id,))
        if fetch_one() == 1:
            return True
        else:
            return False
    elif server_id is not None:
        try:
            c.execute("SELECT status FROM logging.servers WHERE serverid = %s", (server_id,))
            if fetch_one() == 1:
                return True
            else:
                return False
        except Exception as e:
            return False


async def set_logging_status(server_id, status):  # status can only be 0 or 1
    c.execute("UPDATE logging.servers SET status = %s WHERE serverid = %s", (status, server_id))
    DBconn.commit()


async def get_logging_id(server_id):
    c.execute("SELECT id FROM logging.servers WHERE serverid = %s", (server_id,))
    return fetch_one()


async def check_logging_requirements(message):
    try:
        if not message.author.bot:
            if await check_if_logged(server_id=message.guild.id):
                if await check_if_logged(channel_id=message.channel.id):
                    return True
    except Exception as e:
        pass
    return False


async def get_attachments(message):
    files = None
    if len(message.attachments) != 0:
        files = []
        for attachment in message.attachments:
            files.append(await attachment.to_file())
    return files


async def get_log_channel_id(message):
    c.execute("SELECT channelid FROM logging.servers WHERE serverid = %s", (message.guild.id,))
    return client.get_channel(fetch_one())

######################
# ## DREAMCATCHER ## #
######################


def get_dc_channels():
    c.execute("SELECT serverid FROM dreamcatcher.dreamcatcher")
    return fetch_all()


def get_video_and_bat_list(page_soup):
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
    return get_none_if_list_is_empty(video_name_list), get_none_if_list_is_empty(bat_name_list)


def get_videos(video_name_list):
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


def get_photos(photo_name_list):
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


async def get_embed(image_links, member_name):
    embed_list = []
    for link in image_links:
        embed = discord.Embed(title=member_name, color=get_random_color(), url=link)
        embed.set_image(url=link)
        embed = await set_embed_author_and_footer(embed, "Thanks for using Irene.")
        embed_list.append(embed)
    return get_none_if_list_is_empty(embed_list)


async def send_content(channel, dc_photos_embeds, dc_videos):
    try:
        if dc_photos_embeds is not None:
            for dc_photo_embed in dc_photos_embeds:
                await channel.send(embed=dc_photo_embed)
        if dc_videos is not None:
            for video in dc_videos:
                await channel.send(file=video)
    except Exception as e:
        log.console(e)


def delete_content():
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


def get_member_name_and_id(username, member_list):
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


def add_post_to_db(image_links, member_id, member_name, post_number, post_url):
    if image_links is not None:
        for link in image_links:
            try:
                if member_id is not None:
                    c.execute("INSERT INTO groupmembers.imagelinks VALUES (%s,%s)", (link, member_id))
                c.execute("INSERT INTO dreamcatcher.DCHDLinks VALUES (%s,%s,%s)", (link, member_name.lower(), post_number))
                c.execute("UPDATE dreamcatcher.DCUrl SET url = %s WHERE member = %s", (post_url, "latest"))
                c.execute("UPDATE dreamcatcher.DCUrl SET url = %s WHERE member = %s", (post_url, member_name.lower()))
                DBconn.commit()
            except Exception as e:
                log.console(e)
                pass


async def send_new_post(channel_id, channel, member_name, status_message, post_url):
    try:
        await channel.send(f">>> **New {member_name} Post\n<{post_url}>\nStatus Message: {status_message}**")
    except AttributeError:
        try:
            c.execute("DELETE from dreamcatcher.dreamcatcher WHERE serverid = %s", (channel_id,))
            DBconn.commit()
        except Exception as e:
            log.console(e)
    except Exception as e:
        await channel.send(f">>> **New {member_name} Post\n<{post_url}>**")


async def open_bat_file(bat_list):
    for bat_name in bat_list:
        # open bat file
        check_bat = await asyncio.create_subprocess_exec("Videos\\{}".format(bat_name),
                                                         stderr=asyncio.subprocess.PIPE)
        await check_bat.wait()


async def get_image_list(image_url, post_url, image_links):
    """Downloads Thumbnail Photos//This was before embeds were being used and was very inefficient."""
    photo_name_list = []
    new_count = -1
    final_image_list = []
    for image in image_url:
        new_count += 1
        new_image_url = image.img["src"]
        file_name = new_image_url[82:]
        async with session.get(new_image_url) as resp:
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
    return get_none_if_list_is_empty(photo_name_list), get_none_if_list_is_empty(final_image_list)


async def download_dc_photos(image_url):
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
