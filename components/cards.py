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
    def __init__(self, cards: list[CharacterCard] = []) -> None:
        self.cards = cards or self.default_list()

    def default_list(self):
        """ creates the default list of card, 3 cards for each character """
        return cards_from_names(list(AVAILABLE_CARDS.keys()) * 3)

    def shuffle(self):
        shuffle(self.cards)

    def add(self, card: CharacterCard):
        self.cards.append(card)


AVAILABLE_CARDS: dict[str, type[CharacterCard]] = {
    "duke": DukeCharacterCard,
    "assassin": AssassinCharacterCard,
    "captain": CaptainCharacterCard,
    "ambassador": AmbassadorCharacterCard,
    "contessa": ContessaCharacterCard
}

def cards_from_names(names: list[str]):
    return [AVAILABLE_CARDS[name]() for name in names if name in AVAILABLE_CARDS.keys()]