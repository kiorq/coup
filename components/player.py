from random import random
from typing import Union
from components.actions import Treasury, Action
from components.cards import CharacterCard, CourtDeck
from components.errors import GameError


class Player(object):
    coins: int
    cards: list[CharacterCard]
    revealed_cards: list[CharacterCard]

    def __init__(self, coins: int, cards: list[CharacterCard], revealed_cards: list[CharacterCard] = []):
        self.coins = coins
        self.cards = cards
        self.revealed_cards = revealed_cards

    @property
    def is_exiled(self):
        return len(self.cards) == 0

    def take_coins(self, treasury: Treasury, amount: int):
        """ takes coins from treasury """
        if treasury.coins < amount:
            raise Treasury.TreasuryError("Treasure has no more coins")

        treasury.coins -=amount
        self.coins +=amount

    def pay_coins(self, treasury: Treasury, amount: int):
        if self.coins < amount:
            raise Treasury.TreasuryError("Player does not have enough coins")

        treasury.coins +=amount
        self.coins -=amount

    def take_cards(self, court_deck: CourtDeck, amount: int):
        """ takes coins from treasury """
        if len(court_deck.cards) < amount:
            raise GameError("Court deck has no more cards")

        self.cards += court_deck.cards[:amount]
        court_deck.cards[:] = court_deck.cards[amount:]

    def request_challenge(self):
        return random() < .40 # 40% probability

    def request_block(self):
        return True
        return random() < .20 # 20% probability

    def request_will_show(self):
        """ will the player show card """
        return True
        return random() < .50 # 50% probability

    def has_cards(self, cards: list[CharacterCard]):
        for card in cards:
            if card in self.cards:
                return card
        return None

    def is_bluffing(self, card: CharacterCard):
        """ check player could be bluffing (does not have card) """
        return not bool(self.has_cards([card]))

    def loose_influence(self):
        self.revealed_cards.append(self.cards.pop())

    def swap_cards(self, court_deck: CourtDeck, card: Union[CharacterCard, None]):
        # if action.required_influence:
        if card:
            card_index = self.cards.index(card)
            court_deck.add(self.cards[card_index])
            del self.cards[card_index]
            court_deck.shuffle()
            self.take_cards(court_deck, amount=1)
