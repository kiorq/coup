from typing import Union
from random import choice
from game.errors import GameError


class Treasury(object):
    coins = 0

    class TreasuryError(GameError):
        pass

    def __init__(self, coins: int) -> None:
        self.coins = coins