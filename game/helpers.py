from __future__ import annotations
from random import choice, random
from typing import Callable, Union
from game.errors import GameError, EligiblePlayerNotFound
from game import actions
from game import cards
from game import player

# Mapping of action names to action classes
AVAILABLE_ACTIONS: dict[str, type[actions.Action]] = {
    "income": actions.IncomeAction,
    "foreign_aid": actions.ForeignAidAction,
    "coup": actions.CoupAction,
    "tax": actions.TaxAction,
    "assassinate": actions.AssassinateAction,
    "steal": actions.StealAction,
    # "exchange": ExchangeAction
}

AVAILABLE_CARDS: dict[str, type[cards.CharacterCard]] = {
    "duke": cards.DukeCharacterCard,
    "assassin": cards.AssassinCharacterCard,
    "captain": cards.CaptainCharacterCard,
    "ambassador": cards.AmbassadorCharacterCard,
    "contessa": cards.ContessaCharacterCard
}


def probability(perc: float):
    return random() < perc


def possible_next_actions(player: player.Player, players: list[player.Player]) -> list[actions.Action]:
    """
        determine next possible actions a player can take, this determines
        if the user has the coins or eligible targets for the actions
    """
    possible_actions = []

    def player_is_not_exiled(p):
        return not p.is_exiled and p is not player

    def add_to_possible_actions(actionCls: type[actions.Action], is_player_eligible_func: Union[Callable[[player.Player], bool], None]):
        """ adds action to possible actions, if possible (e.g: there are eligible target users) """
        try:
            targeted_player_index = None
            if is_player_eligible_func:
                targeted_player_index = choose_eligible_player_index(is_player_eligible_func, players)

            possible_actions.append(actionCls(targeted_player_index))
        except EligiblePlayerNotFound:
            # can run action if they are no eligible players to perform the action on
            pass

    if player.coins >= 10:
        # 10 ore more coins, the player has to launch a cope
        targeted_player_index = choose_eligible_player_index(player_is_not_exiled, players)
        return [actions.CoupAction(targeted_player_index)]

    # income
    add_to_possible_actions(actions.IncomeAction, None)

    # foreign aid
    add_to_possible_actions(actions.ForeignAidAction, None)

    # coup
    if player.coins >= 7:
        add_to_possible_actions(actions.CoupAction, None)

    # tax
    add_to_possible_actions(actions.TaxAction, None)

    # assassinate
    if player.coins >= 3:
        add_to_possible_actions(actions.AssassinateAction, player_is_not_exiled)

    # steal
    add_to_possible_actions(actions.StealAction, lambda p: not p.is_exiled and p.coins > 0 and p is not player)

    return possible_actions


def choose_eligible_player_index(is_player_eligible_func: Callable[[player.Player], bool], players: list[player.Player]) -> int:
    """ chooses random player index that meets condition """
    eligible_player_indexes = [i for i, player in enumerate(players) if is_player_eligible_func(player)]
    if not eligible_player_indexes:
        raise EligiblePlayerNotFound("No players meet criteria")
    return choice(eligible_player_indexes)


def get_action_by_name(action_name: str, **kwargs) -> actions.Action:
    """Retrieve an action class by name."""
    if action_name not in AVAILABLE_ACTIONS.keys():
        raise GameError("Action %s does not exist" % action_name)
    return AVAILABLE_ACTIONS[action_name](**kwargs)


def cards_from_names(names: list[str]):
    return [AVAILABLE_CARDS[name]() for name in names if name in AVAILABLE_CARDS.keys()]


def default_card_list():
    """ creates the default list of card, 3 cards for each character """
    return cards_from_names(list(AVAILABLE_CARDS.keys()) * 3)
