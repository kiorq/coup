
from components.actions import Treasury
from components.cards import CharacterCard, CourtDeck


class Player(object):
    def __init__(self, coins: int, cards: list[CharacterCard]):
        self.coins = coins
        self.cards = cards

    def take_coins(self, treasury: Treasury, amount: int):
        """ takes coins from treasury """
        if treasury.coins < amount:
            raise Exception("Treasure has no more coins")

        treasury.coins -=amount
        self.coins +=amount

    def take_cards(self, court_deck: CourtDeck, amount: int):
        """ takes coins from treasury """
        if len(court_deck.cards) < amount:
            raise Exception("Court deck has no more cards")

        self.cards += court_deck.cards[:amount]
        court_deck.cards[:] = court_deck.cards[amount:]

    def request_challenge(self):
        from random import random
        return random() < .10 # 10% probability
