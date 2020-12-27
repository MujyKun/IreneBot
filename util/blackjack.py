from Utility import resources as ex
from module.keys import bot_id
from module import logger as log
import random
import discord


# noinspection PyPep8
class BlackJack:
    @staticmethod
    async def check_in_game(user_id, ctx):  # this is meant for when it is accessed by commands outside of BlackJack.
        """Check if a user is in a game."""
        check = ex.first_result(await ex.conn.fetchrow("SELECT COUNT(*) From blackjack.games WHERE player1 = $1 OR player2 = $1", user_id))
        if check:
            await ctx.send(f"> **{ctx.author}, you are already in a pending/active game. Please type {await ex.get_server_prefix_by_context(ctx)}endgame.**")
            return True

    async def add_bj_game(self, user_id, bid, ctx, mode):
        """Add the user to a blackjack game."""
        await ex.conn.execute("INSERT INTO blackjack.games (player1, bid1, channelid) VALUES ($1, $2, $3)", user_id, str(bid), ctx.channel.id)
        game_id = await self.get_game_by_player(user_id)
        if mode != "bot":
            await ctx.send(f"> **There are currently 1/2 members signed up for BlackJack. To join the game, please type {await ex.get_server_prefix_by_context(ctx)}joingame {game_id} (bid)** ")

    async def process_bj_game(self, ctx, amount, user_id):
        """pre requisites for joining a blackjack game."""
        if amount >= 0:
            if not await self.check_in_game(user_id, ctx):
                if amount > await ex.u_currency.get_balance(user_id):
                    await ctx.send(f"> **{ctx.author}, you can not bet more than your current balance.**")
                else:
                    return True
        else:
            await ctx.send(f"> **{ctx.author}, you can not bet a negative number.**")

    @staticmethod
    async def get_game_by_player(player_id):
        """Get the current game of a player."""
        return ex.first_result(await ex.conn.fetchrow("SELECT gameid FROM blackjack.games WHERE player1 = $1 OR player2 = $1", player_id))

    @staticmethod
    async def get_game(game_id):
        """Get the game from its ID"""
        return await ex.conn.fetchrow("SELECT gameid, player1, player2, bid1, bid2, channelid FROM blackjack.games WHERE gameid = $1", game_id)

    @staticmethod
    async def add_player_two(game_id, user_id, bid):
        """Add a second player to a blackjack game."""
        await ex.conn.execute("UPDATE blackjack.games SET player2 = $1, bid2 = $2 WHERE gameid = $3 ", user_id, str(bid), game_id)

    @staticmethod
    async def get_current_cards(user_id):
        """Get the current cards of a user."""
        in_hand = ex.first_result(await ex.conn.fetchrow("SELECT inhand FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if in_hand is None:
            return []
        return in_hand.split(',')

    @staticmethod
    async def check_player_standing(user_id):
        """Check if a player is standing."""
        return ex.first_result(await ex.conn.fetchrow("SELECT stand FROM blackjack.currentstatus WHERE userid = $1", user_id)) == 1

    @staticmethod
    async def set_player_stand(user_id):
        """Set a player to stand."""
        await ex.conn.execute("UPDATE blackjack.currentstatus SET stand = $1 WHERE userid = $2", 1, user_id)

    @staticmethod
    async def delete_player_status(user_id):
        """Remove a player's status from a game."""
        await ex.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", user_id)

    async def add_player_status(self, user_id):
        """Add a player's status to a game."""
        await self.delete_player_status(user_id)
        await ex.conn.execute("INSERT INTO blackjack.currentstatus (userid, stand, total) VALUES ($1, $2, $2)", user_id, 0)

    @staticmethod
    async def get_player_total(user_id):
        """Get a player's total score."""
        return ex.first_result(await ex.conn.fetchrow("SELECT total FROM blackjack.currentstatus WHERE userid = $1", user_id))

    @staticmethod
    async def get_card_value(card):
        """Get the value of a card."""
        return ex.first_result(await ex.conn.fetchrow("SELECT value FROM blackjack.cards WHERE id = $1", card))

    @staticmethod
    async def get_all_cards():
        """Get all the cards from a deck."""
        card_tuple = await ex.conn.fetch("SELECT id FROM blackjack.cards")
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

    @staticmethod
    async def get_card_name(card_id):
        """Get the name of a card."""
        return ex.first_result(await ex.conn.fetchrow("SELECT name FROM blackjack.cards WHERE id = $1", card_id))

    async def check_if_ace(self, card_id, user_id):
        """Check if the card is an ace and is not used."""
        aces = ["1", "14", "27", "40"]
        aces_used = await self.get_aces_used(user_id)
        if card_id in aces and card_id not in aces_used:
            aces_used.append(card_id)
            await self.set_aces_used(aces_used, user_id)
            return True
        return False

    @staticmethod
    async def set_aces_used(card_list, user_id):
        """Mark an ace as used."""
        separator = ','
        cards = separator.join(card_list)
        await ex.conn.execute("UPDATE blackjack.currentstatus SET acesused = $1 WHERE userid = $2", cards, user_id)

    @staticmethod
    async def get_aces_used(user_id):
        """Get the aces that were changed from 11 to 1."""
        aces_used = ex.first_result(await ex.conn.fetchrow("SELECT acesused FROM blackjack.currentstatus WHERE userid = $1", user_id))
        if aces_used is None:
            return []
        return aces_used.split(',')

    def check_if_bot(self, user_id):
        """Check if the player is a bot. (The bot would be Irene)"""
        return str(self.get_int_index(bot_id, 9)) in str(user_id)

    async def add_card(self, user_id):
        """Check status of a game, it's player, manages the bot that plays, and then adds a card."""
        end_game = False
        check = 0

        separator = ','
        current_cards = await self.get_current_cards(user_id)
        game_id = await ex.u_blackjack.get_game_by_player(user_id)
        game = await self.get_game(game_id)
        channel = await ex.client.fetch_channel(game[5])
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
            await ex.conn.execute("UPDATE blackjack.currentstatus SET inhand = $1, total = $2 WHERE userid = $3", cards, current_total, user_id)
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
        game_id = await ex.u_blackjack.get_game_by_player(user_id)
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
            elif score2 < 21 < score1:
                return 'player2'
            elif score1 < 21 < score2:
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
            await channel.send(f"> **<@{bot_id}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")
        elif self.check_if_bot(loser):
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{bot_id}> with {loser_points}.**")
        else:
            await channel.send(f"> **<@{winner}> has won ${int(win_amount):,} with {winner_points} points against <@{loser}> with {loser_points}.**")

    async def announce_tie(self, channel, player1, player2, tied_points):
        """Send a message to the channel of a tie."""
        if self.check_if_bot(player1) or self.check_if_bot(player2):
            await channel.send(f"> **<@{player1}> and <@{bot_id}> have tied with {tied_points}**")
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
            player1_current_bal = await ex.u_currency.get_balance(game[1])
            player2_current_bal = await ex.u_currency.get_balance(game[2])
            if winner == 'player1':
                await ex.u_currency.update_balance(game[1], player1_current_bal + int(game[4]))
                if not self.check_if_bot(game[2]):
                    await ex.u_currency.update_balance(game[2], player2_current_bal - int(game[4]))
                await self.announce_winner(channel, game[1], game[2], player1_score, player2_score, game[4])
            elif winner == 'player2':
                if not self.check_if_bot(game[2]):
                    await ex.u_currency.update_balance(game[2], player2_current_bal + int(game[3]))
                await ex.u_currency.update_balance(game[1], player1_current_bal - int(game[3]))
                await self.announce_winner(channel, game[2], game[1], player2_score, player1_score, game[3])
            elif winner == 'tie':
                await self.announce_tie(channel, game[1], game[2], player1_score)
            await self.delete_game(game_id)

    async def delete_game(self, game_id):
        """Delete a blackjack game."""
        game = await self.get_game(game_id)
        await ex.conn.execute("DELETE FROM blackjack.games WHERE gameid = $1", game_id)
        await ex.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[1])
        await ex.conn.execute("DELETE FROM blackjack.currentstatus WHERE userid = $1", game[2])
        log.console(f"Game {game_id} deleted.")

    async def delete_all_games(self):
        """Delete all blackjack games."""
        all_games = await ex.conn.fetch("SELECT gameid FROM blackjack.games")
        for games in all_games:
            game_id = games[0]
            await self.delete_game(game_id)

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
