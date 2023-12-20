from random import choice
from typing import Union
from game import actions
from game import cards
from game.errors import GameError
from game.ai_helpers import possible_next_actions, probability


class Player(object):
    """
        Represents the state and actions of a player in the game.

        Attributes:
        - coins (int): The number of coins held by the player.
        - cards (list[CharacterCard]): List of character cards held by the player.
        - revealed_cards (list[CharacterCard]): List of revealed character cards, indicating lost influence.
    """
    coins: int
    cards: list['cards.CharacterCard']
    revealed_cards: list['cards.CharacterCard']

    def __init__(self, coins: int, cards: list['cards.CharacterCard'], revealed_cards: list['cards.CharacterCard'] = []):
        self.coins = coins
        self.cards = cards
        self.revealed_cards = revealed_cards

    @property
    def is_exiled(self):
        return len(self.cards) == 0

    def take_coins(self, treasury: actions.Treasury, amount: int):
        """ takes coins from treasury """
        if treasury.coins < amount:
            raise actions.Treasury.TreasuryError("Treasure has no more coins")

        treasury.coins -=amount
        self.coins +=amount

    def pay_coins(self, treasury: actions.Treasury, amount: int):
        if self.coins < amount:
            raise actions.Treasury.TreasuryError("Player does not have enough coins")

        treasury.coins +=amount
        self.coins -=amount

    def take_cards(self, court_deck: 'cards.CourtDeck', amount: int):
        """ takes coins from treasury """
        if len(court_deck.cards) < amount:
            raise GameError("Court deck has no more cards")

        self.cards += court_deck.cards[:amount]
        court_deck.cards[:] = court_deck.cards[amount:]

    def next_move(self, players: list['Player']) -> actions.Action:
        # default, this will be handled by the ui
        return actions.Action(None)

    def request_challenge(self, action: actions.Action):
        # default, this will be handled by the ui
        return False

    def request_block(self, action: actions.Action):
        # default, this will be handled by the ui
        return False

    def request_will_show(self, action: actions.Action):
        # default, this will be handled by the ui
        return False

    def request_will_challenge_block(self, action: actions.Action):
        # default, this will be handled by the ui
        return False

    def has_cards(self, cards: list['cards.CharacterCard']):
        for card in cards:
            if card in self.cards:
                return card
        return None

    def is_bluffing(self, card: 'cards.CharacterCard'):
        """ check player could be bluffing (does not have card) """
        return not bool(self.has_cards([card]))

    def loose_influence(self):
        self.revealed_cards.append(self.cards.pop())

    def swap_cards(self, court_deck: 'cards.CourtDeck', card: Union['cards.CharacterCard', None]):
        # if action.required_influence:
        if card:
            card_index = self.cards.index(card)
            court_deck.add(self.cards[card_index])
            del self.cards[card_index]
            court_deck.shuffle()
            self.take_cards(court_deck, amount=1)


class PlayerWithAutomation(Player):

    def next_move(self, players: list['Player']) -> actions.Action:
        """ chooses next move based """
        possible_actions = possible_next_actions(self, players)
        return choice(possible_actions)

    def request_challenge(self, action: actions.Action):
        """ ask player if they want to challenge """
        return probability(.5) # could be changed as part of a game mode (easy, normal, hard)

    def request_block(self, action: actions.Action):
        """ ask player if they want to block """
        return probability(.5) # could be changed as part of a game mode (easy, normal, hard)

    def request_will_show(self, action: actions.Action):
        """ ask the player will show their influence """
        return probability(.5) # could be changed as part of a game mode (easy, normal, hard)

    def request_will_challenge_block(self, action: actions.Action):
        """ ask the player will challenge block """
        return probability(.5) # could be changed as part of a game mode (easy, normal, hard)

