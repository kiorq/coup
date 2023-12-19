from typing import Union
from random import choice
import typing
from components.cards import AmbassadorCharacterCard, AssassinCharacterCard, CaptainCharacterCard, CharacterCard, ContessaCharacterCard, CourtDeck, DukeCharacterCard
from components.errors import GameError



class Treasury(object):
    coins = 0

    class TreasuryError(GameError):
        pass

    def __init__(self, coins: int) -> None:
        self.coins = coins


class Action(object):
    required_influence: Union[CharacterCard, None]
    action: str
    targeted_player_index: Union[int, None]
    is_blockably_by: list[CharacterCard]

    if typing.TYPE_CHECKING:
        from components.game import GameState
        game_state: GameState # set by GameState when added

    def __init__(self, targeted_player_index: Union[int, None]) -> None:
        self.targeted_player_index = targeted_player_index

    def get_targeted_player(self):
        if self.targeted_player_index:
            targeted_player = self.game_state.players[self.targeted_player_index]
            if targeted_player.is_exiled:
                raise GameError("Cannot target exiled player")
            return targeted_player

        return None

    def resolve(self):
        """ will perform action """
        pass

    def pay_penalty(self):
        """ penalty paid to perfrom action, regardless if bluffing or not """
        pass


class IncomeAction(Action):
    """ Take 1 coin from the Treasury. """
    required_influence = None
    action = "income"
    is_blockably_by = []

    def resolve(self):
        self.game_state.current_player.take_coins(
            treasury=self.game_state.treasury,
            amount=1
        )



class ForeignAidAction(Action):
    """ Take 2 coins from the Treasury. """
    required_influence = None
    action = "foreign_aid"
    is_blockably_by = [DukeCharacterCard()]

    def resolve(self):
        self.game_state.current_player.take_coins(
            treasury=self.game_state.treasury,
            amount=2
        )


class CoupAction(Action):
    required_influence = None
    action = "coup"
    is_blockably_by = []

    def pay_penalty(self):
        if self.game_state.current_player.coins >= 7:
            self.game_state.current_player.pay_coins(
                treasury=self.game_state.treasury,
                amount=7
            )
        else:
            raise GameError("Player does not have enough coins")




    def resolve(self):
        targeted_player = self.get_targeted_player()
        if not targeted_player:
            raise GameError("Requires a targeted player")
        # targeted player looses influence
        targeted_player.loose_influence()

class TaxAction(Action):
    """ Take 3 coins from the Treasury. """
    required_influence = DukeCharacterCard()
    action = "tax"
    is_blockably_by = [CaptainCharacterCard()]

    def resolve(self):
        self.game_state.current_player.take_coins(
            treasury=self.game_state.treasury,
            amount=3
        )


class AssassinateAction(Action):
    """ Pays 3 coins to treasury and makes targeted player loose influence """
    required_influence = AssassinCharacterCard()
    action = "assassinate"
    is_blockably_by = [ContessaCharacterCard()]

    def pay_penalty(self):
        self.game_state.current_player.pay_coins(
            treasury=self.game_state.treasury,
            amount=3
        )

    def resolve(self):
        targeted_player = self.get_targeted_player()
        if not targeted_player:
            raise GameError("Requires a targeted player")
        # targeted player looses influence
        targeted_player.loose_influence()


class StealAction(Action):
    required_influence = CaptainCharacterCard()
    action = "steal"
    is_blockably_by = [
        CaptainCharacterCard(),
        AmbassadorCharacterCard()
    ]

    def resolve(self):
        targeted_player = self.get_targeted_player()
        if not targeted_player:
            raise GameError("Requires a targeted player")
        # steal 1 coin from targeted player
        if targeted_player.coins == 1:
            targeted_player.coins -= 1
            self.game_state.current_player.coins += 1
        elif targeted_player.coins > 1:
            targeted_player.coins -= 2
            self.game_state.current_player.coins += 2
        else:
            raise GameError("Targeted player does not have any coins")



# class ExchangeAction(Action):
#     required_influence = AmbassadorCharacterCard()
#     action = "exchange"


# Mapping of action names to action classes
AVAILABLE_ACTIONS = {
    "income": IncomeAction,
    "foreign_aid": ForeignAidAction,
    "coup": CoupAction,
    "tax": TaxAction,
    "assassinate": AssassinateAction,
    "steal": StealAction,
    # "exchange": ExchangeAction
}

def get_action_by_name(action_name: str, **kwargs) -> Action:
    """Retrieve an action class by name."""
    if action_name not in AVAILABLE_ACTIONS.keys():
        raise GameError("Action %s does not exist" % action_name)
    return AVAILABLE_ACTIONS[action_name](**kwargs)

def get_random_action(**kwargs) -> Action:
    """Retrieve an random action."""
    return choice(list(AVAILABLE_ACTIONS.values()))(**kwargs)

class ActionChallenge(object):

    challening_player_index: int
    status: int

    class Status:
        Undetermined = 0
        NoShow = 1
        Show = 2

    def __init__(self, challening_player_index: int, status = Status.Undetermined) -> None:
        self.challening_player_index = challening_player_index
        self.status = status

    @property
    def is_undetermined(self):
        return self.status == ActionChallenge.Status.Undetermined


class ActionBlock(object):
    blocking_player_index: int
    status: int

    class Status:
        Undetermined = 0
        Challenge = 1
        NoChallenge = 2
        NoShow = 3
        Show = 4

    def __init__(self, blocking_player_index: int, status = Status.Undetermined) -> None:
        self.blocking_player_index = blocking_player_index
        self.status = status

    @property
    def is_undetermined(self):
        return self.status == ActionChallenge.Status.Undetermined