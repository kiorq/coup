from random import shuffle


class CharacterCard(object):
    character: str

    def __eq__(self, __value: 'CharacterCard') -> bool:
        return __value.character == self.character


class DukeCharacterCard(CharacterCard):
    character = "duke"


class AssassinCharacterCard(CharacterCard):
    character = "assassin"


class CaptainCharacterCard(CharacterCard):
    character = "captain"


class AmbassadorCharacterCard(CharacterCard):
    character = "ambassador"


class ContessaCharacterCard(CharacterCard):
    character = "contessa"


class CourtDeck(object):
    def __init__(self, cards: list[CharacterCard]) -> None:
        self.cards = cards

    def shuffle(self):
        shuffle(self.cards)

    def add(self, card: CharacterCard):
        self.cards.append(card)

    def __len__(self):
        return len(self.cards)

