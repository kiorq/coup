
from components.actions import Treasury, Action
from components.cards import CharacterCard, CourtDeck


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
        return random() < .40 # 40% probability

    def is_bluffing(self, action: Action):
        return action.required_influence not in self.cards

    def loose_influence(self):
        self.revealed_cards.append(self.cards.pop())

    def swap_cards(self, court_deck: CourtDeck, action: Action):
        if action.required_influence:
            card_index = self.cards.index(action.required_influence)
            court_deck.add(self.cards[card_index])
            del self.cards[card_index]
            court_deck.shuffle()
            self.take_cards(court_deck, amount=1)
