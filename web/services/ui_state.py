"""
    responsibile for providing data that makes it easier for the ui to know what to do
"""

from game.actions import ActionBlock, ActionChallenge
from game.helpers import possible_next_actions
from game.game_state import GameState
from web.services.game_state import load_game_state_from_store


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
        if not game_state.current_action.action_resolved:
            return f"Play {player_num}: {game_state.current_action.action} Successful 🎉".title()
        return f"Player {player_num}'s turn ended"

    if not game_state.challenge and not game_state.block:
        against_text = ""
        if game_state.current_action.targeted_player_index is not None:
            against_text = f" against Player {game_state.current_action.targeted_player_index + 1}"
        return f"Player {player_num}: {game_state.current_action.action}{against_text}!".title()

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

        possible_actions = possible_next_actions(current_player, game_state.players)
        for action in possible_actions:
            will_be_bluffing = current_player.is_bluffing(action.required_influence) \
                if action.required_influence else False
            actions.append({
                "action": action.action,
                "will_be_bluffing": will_be_bluffing,
                "target_player_index": action.targeted_player_index
            })

    return actions


def ui_can_automate(game_state: GameState) -> bool:
    if game_state.current_player_index == 0 and game_state.turn_ended:
        return True
    return game_state.current_player_index != 0


def ui_can_challenge(game_state: GameState) -> bool:
    return game_state.current_player_index != 0 \
        and not game_state.current_player.is_exiled \
            and not game_state.challenge

def ui_can_block(game_state: GameState) -> bool:
    return game_state.current_player_index != 0 \
        and not game_state.current_player.is_exiled \
            and not game_state.block

def ui_wait_for_player(game_state: GameState) -> bool:
    """
        this will be true when it's a player's turn and they haven't performed an action yet
        the ui will use this to automate the wait using js
    """
    return game_state.current_player_index != 0 \
        and not game_state.current_action \
        and not game_state.turn_ended


def ui_is_player_1_exiled(game_state: GameState):
    return game_state.players[0].is_exiled

def game_ui_state_json(game_state: GameState) -> dict:
    """ convers GameState to a json """
    return {
        "current_player_num": game_state.current_player_index + 1,
        "status_text": ui_status_text(game_state),
        "available_actions": ui_available_actions(game_state),
        "can_automate": ui_can_automate(game_state),
        "turn_ended": game_state.turn_ended,
        "can_challenge": ui_can_challenge(game_state),
        "can_block": ui_can_block(game_state),
        "wait_for_player": ui_wait_for_player(game_state),
        "is_player_1_exiled": ui_is_player_1_exiled(game_state)
    }


def ui_current_state() -> dict:
    """
        retrieves ui state
    """
    game_state = load_game_state_from_store()
    return game_ui_state_json(game_state)


def get_color_by_name_func(name: str):
    CARD_COLOR_CLASS_MAP: dict[str, str] = {
        "duke": "bg-purple-500",
        "assassin": "bg-black !text-white",
        "captain": "bg-blue-500",
        "ambassador": "bg-green-500",
        "contessa": "bg-red-500"
    }
    return CARD_COLOR_CLASS_MAP.get(name)