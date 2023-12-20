
from random import choice
from typing import Union
from game.actions import ActionBlock, ActionChallenge
from game.game_state import GameState
from game.errors import GameError
from game.helpers import get_action_by_name
from web.models.game import store_game_data, retrieve_game_data
from web.serializer import game_state_from_json, game_state_to_json

def load_game_state_from_store() -> GameState:
    """
        loads game staste from storage
    """
    return game_state_from_json(retrieve_game_data() or {})


def load_game_state_clean(current_players_index:int =0) -> GameState:
    """
        creates a fresh game state
    """
    return game_state_from_json({
        "current_players_index": current_players_index
    })


def store_game_state(gs: GameState):
    """
        stores game state in storage
    """
    state = game_state_to_json(gs)
    store_game_data(state)
    return state


def game_current_state() -> dict:
    """
        retrieves game state
    """
    game_state = load_game_state_from_store()
    return game_state_to_json(game_state)


def game_start_new(current_players_index: int):
    """
        starts game over
    """
    game_state = load_game_state_clean(current_players_index)

    # store and return state
    return store_game_state(game_state)


def game_perform_action(action_name: str, targeted_player_index: Union[int, None]) -> dict:
    """
        performs action on game state
    """
    game_state = load_game_state_from_store()

    if game_state.current_player_index != 0:
        raise GameError("Not your turn")

    if game_state.current_action:
        raise GameError("Action already being performed, may be challenged or blocked")

    # make action
    action = get_action_by_name(
        action_name=action_name,
        targeted_player_index=targeted_player_index
    )

    game_state.perform_action(action)
    game_state.try_to_complete_action()

    # store and return state
    return store_game_state(game_state)


def automate_next_move():
    """
        automate the next move for the ai players
        this is designed to be called step by step until
        it is the human player's turn
    """
    game_state = load_game_state_from_store()

    if game_state.turn_ended:
        game_state.end_turn()
        return store_game_state(game_state)

    if game_state.current_player_index == 0 and not game_state.turn_ended:
        raise GameError("Cannot skip your turn")

    # handle selecting action
    if not game_state.current_action:
        action = game_state.current_player.next_move(game_state.players)
        game_state.perform_action(action)
        return store_game_state(game_state)

    # handle challenge
    elif game_state.challenge and game_state.challenge.is_undetermined:
        random_response = (
            ActionChallenge.Status.Show
            if game_state.current_player.request_will_show(game_state.current_action) 
            else ActionChallenge.Status.NoShow
        )
        game_state.respond_to_challenge(random_response)
        return store_game_state(game_state)

    # handle block
    elif game_state.block and game_state.block.is_undetermined:
        random_response = (
            ActionBlock.Status.Challenge
            if game_state.current_player.request_will_challenge_block(game_state.current_action) 
            else ActionBlock.Status.NoChallenge
        )
        game_state.respond_to_block(
            challenging_player_index=game_state.current_player_index, # TODO: or get a random id
            status=random_response
        )
        return store_game_state(game_state)

    game_state.try_to_complete_action()

    # store and return state
    return store_game_state(game_state)


def respond_to_challenge(challenge_response: int):
    """
        allows human player to response to challenge (show or noshow)
    """
    game_state = load_game_state_from_store()

    if not game_state.challenge or not game_state.challenge.is_undetermined:
        raise GameError("Not challenge to respond to")

    game_state.respond_to_challenge(challenge_response)
    game_state.try_to_complete_action()
    # store and return state
    return store_game_state(game_state)


def respond_to_block(block_response: int):
    """
        allows human player to respond to block (ignore or challenge)
    """
    game_state = load_game_state_from_store()

    if not game_state.block or not game_state.block.is_undetermined:
        raise GameError("No block to respond to")

    game_state.respond_to_block(
        challenging_player_index=0, # human player
        status=block_response
    )
    game_state.try_to_complete_action()
    # store and return state
    return store_game_state(game_state)


def challenge_action():
    """ challenges another player's action """
    game_state = load_game_state_from_store()

    if game_state.challenge:
        raise GameError("Action already challenged")

    # set challenge as player 1
    game_state.challenge_action(player_index=0)
    game_state.try_to_complete_action()
    # store and return state
    return store_game_state(game_state)

def block_action():
    """ block another player's action"""
    game_state = load_game_state_from_store()

    if game_state.block:
        raise GameError("Action already blocked")

    # set challenge as player 1
    game_state.block_action(player_index=0)
    game_state.try_to_complete_action()
    # store and return state
    return store_game_state(game_state)
