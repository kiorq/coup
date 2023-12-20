from __future__ import annotations
from random import choice, random
from typing import Callable, Union
from game.errors import EligiblePlayerNotFound
from game import actions
from game import player


def probability(perc: float):
    return random() < perc

def possible_next_actions(player: player.Player, players: list[player.Player]) -> list[actions.Action]:
    """ determine next actions a player can take """
    possible_actions = []

    def player_is_not_exiled(player):
        return not player.is_exiled

    def add_to_possible_actions(actionCls: type[actions.Action], is_player_eligible_func: Union[Callable[[player.Player], bool], None]):
        """ adds action to possible actions, if possible (e.g: there are elible target users) """
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
    add_to_possible_actions(actions.StealAction, lambda player: not player.is_exiled and player.coins > 0)

    return possible_actions


def choose_eligible_player_index(is_player_eligible_func: Callable[[player.Player], bool], players: list[player.Player]) -> int:
    """ chooses random player index that meets condition """
    eligible_player_indexes = [i for i, player in enumerate(players) if is_player_eligible_func(player)]
    if not eligible_player_indexes:
        raise EligiblePlayerNotFound("No players meet criteria")
    return choice(eligible_player_indexes)