from typing import Union

from components.cards import AmbassadorCharacterCard, AssassinCharacterCard, CaptainCharacterCard, CharacterCard, CourtDeck, DukeCharacterCard


class Treasury(object):
    coins = 0

    def __init__(self, coins: int) -> None:
        self.coins = coins


class Action(object):
    required_influence: Union[CharacterCard, None]
    action: str

    def resolve(self):
        pass


class IncomeAction(Action):
    required_influence = None
    action = "income"


class ForeignAidAction(Action):
    required_influence = None
    action = "forieng_aid"


class CoupAction(Action):
    required_influence = None
    action = "coup"

class TaxAction(Action):
    required_influence = DukeCharacterCard()
    action = "tax"


class AssassinateAction(Action):
    required_influence = AssassinCharacterCard()
    action = "assassinate"


class StealAction(Action):
    required_influence = CaptainCharacterCard()
    action = "steal"


class ExchangeAction(Action):
    required_influence = AmbassadorCharacterCard()
    action = "exchange"


# Mapping of action names to action classes
AVAILABLE_ACTIONS = {
    "income": IncomeAction,
    "foreign_aid": ForeignAidAction,
    "coup": CoupAction,
    "tax": TaxAction,
    "assassinate": AssassinateAction,
    "steal": StealAction,
    "exchange": ExchangeAction
}

def get_action_by_name(action_name: str) -> Action:
    """Retrieve an action class by name."""
    if action_name not in AVAILABLE_ACTIONS.keys():
        raise Exception("Action %s does not exist" % action_name)
    return AVAILABLE_ACTIONS[action_name]()


class ActionChallenge(object):
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
