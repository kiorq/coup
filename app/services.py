
from app.db import persist_storage, retrieve_storage
from components.game import GameState
from components.game_serializer import game_state_from_json, game_state_to_json

def load_game_state_from_store() -> GameState:
    """
        loads game staste from storage
    """
    return game_state_from_json(retrieve_storage())


def load_game_state_clean() -> GameState:
    """
        creates a fresh game state
    """
    return game_state_from_json({})


def store_game_state(gs: GameState):
    """
        stores game state in storage
    """
    state = game_state_to_json(gs)
    persist_storage(state)
    return state
