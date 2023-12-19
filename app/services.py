
from app.db import persist_storage, retrieve_storage
from components.actions import ActionChallenge, Treasury, get_action_by_name
from components.cards import CourtDeck, cards_from_names
from components.game import GameState
from components.player import Player

def load_game_state(data) -> GameState:
    """
        setups game state from data (e.g: database) or
        just creates a fresh game state
    """
    current_player_index = data.get("current_players_index") or 0
    treasury = Treasury(coins=data.get("treasury") or 50)
    court_deck = CourtDeck(cards=cards_from_names(data.get("court_deck") or []))

    # players
    players_from_db = data.get("players")
    if not players_from_db:
        court_deck.shuffle()
        players = []
        for _ in range(0, 4):
            player = Player(coins=0, cards=[])
            player.take_coins(treasury, amount=2)
            player.take_cards(court_deck, amount=2)
            players.append(player)
    else:
        players = [Player(
            coins=player["coins"],
            cards=cards_from_names(player["cards"]),
        ) for player in players_from_db]

    # challenge
    challenge_from_db = data.get("challenge")
    challenge = None
    if challenge_from_db:
        challenge = ActionChallenge(
            challening_player_index=challenge_from_db["challening_player_index"],
            status=challenge_from_db["status"],
        )

    # current action
    current_action_from_db = data.get("current_action")
    current_action = None
    if current_action_from_db:
        current_action = get_action_by_name(current_action_from_db["action"], targeted_player_index=current_action_from_db["targeted_player_index"])

    return GameState(
        current_player_index=current_player_index,
        players=players,
        current_action=current_action,
        challenge=challenge,
        treasury=treasury,
        court_deck=court_deck,
        turn_ended=data.get("turn_ended") or False
    )

def load_game_state_from_store() -> GameState:
    """
        loads game staste from storage
    """
    return load_game_state(retrieve_storage())


def load_game_state_clean() -> GameState:
    """
        creates a fresh game state
    """
    return load_game_state({})


def store_game_state(gs: GameState):
    """
        st0res game state in storage
    """
    state = gs.get_state()
    persist_storage(state)
    return state
