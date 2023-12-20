from typing import Union
from game.actions import AVAILABLE_ACTIONS, Action, ActionBlock, ActionChallenge, Treasury, get_action_by_name
from game.cards import CourtDeck, cards_from_names
from game.player import Player, PlayerWithAutomation
from game.game import GameState



def ui_status_text(game_state: GameState) -> str:
    player_num = game_state.current_player_index + 1

    # check if we have a winner
    winning_player_index = game_state.get_winning_player()
    if winning_player_index is not None:
        return f"Player {winning_player_index + 1}'s WINS 🎉"

    if game_state.current_player_index == 0 and not game_state.current_action:
        return "Your Turn. Choose an action!"

    if not game_state.current_action:
        return f"Player {player_num}'s turn"
    
    if game_state.turn_ended:
        return f"Player {player_num} turn has ended"

    if not game_state.challenge and not game_state.block:
        return f"Player {player_num} Move: {game_state.current_action.action}!".title()

    if game_state.block:
        blocking_player_num = game_state.block.blocking_player_index + 1
        if game_state.block.is_undetermined:
            return f"Player {blocking_player_num} blocked Player {player_num} 🚫"
        if game_state.block.status == ActionBlock.Status.Show:
            return f"Player {blocking_player_num} revealed card 🚫"
        if game_state.block.status == ActionBlock.Status.NoShow:
            return f"Player {blocking_player_num} is bluffing 😂"
        elif game_state.block.status == ActionBlock.Status.NoChallenge:
            return f"Block was not challenged"

    if game_state.challenge:
        challening_player_num = game_state.challenge.challening_player_index + 1
        if game_state.challenge.is_undetermined:
            return f"Player {challening_player_num} challenged Player {player_num} 🤨"
        if game_state.challenge.status == ActionChallenge.Status.Show:
            return f"Player {player_num} revealed card 😮‍💨"
        if game_state.challenge.status == ActionChallenge.Status.NoShow:
            return f"Player {player_num} is bluffing 😫"

    return "-"

def ui_available_actions(game_state: GameState) -> list[dict]:
    actions = []
    if game_state.current_player_index == 0:
        current_player = game_state.current_player

        for action in AVAILABLE_ACTIONS.values():
            will_be_bluffing = current_player.is_bluffing(action.required_influence) \
                if action.required_influence else False
            actions.append({
                "action": action.action,
                "will_be_bluffing": will_be_bluffing
            })

    return actions


def ui_should_automate(game_state: GameState) -> bool:
    if game_state.current_player_index == 0 and game_state.turn_ended:
        return True
    return game_state.current_player_index != 0


def game_ui_state_json(game_state: GameState) -> dict:
    """ convers GameState to a json """
    return {
        "status_text": ui_status_text(game_state),
        "available_actions": ui_available_actions(game_state),
        "can_automate": ui_should_automate(game_state)
    }

