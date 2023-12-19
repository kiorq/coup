from typing import Union
from game.actions import AVAILABLE_ACTIONS, Action, ActionBlock, ActionChallenge, Treasury, get_action_by_name
from game.cards import CourtDeck, cards_from_names
from game.player import Player
from game.game import GameState


def player_to_json(player_index, player: Player):
    return {
        "player_index": player_index,
        "coins": player.coins,
        "cards": [card.character for card in player.cards],
        "revealed_cards": [card.character for card in player.revealed_cards],
        "is_exiled": player.is_exiled,
    }


def action_to_json(action: Union[Action, None]):
    if not action:
        return None
    return {"action": action.action, "targeted_player_index": action.targeted_player_index}


def challenge_to_json(challenge: Union[ActionChallenge, None]):
    if not challenge:
        return None

    return {
        "challenging_player_index": challenge.challening_player_index,
        "status": challenge.status,
        "is_undetermined": challenge.is_undetermined,
    }


def block_to_json(block: Union[ActionBlock, None]):
    if not block:
        return None

    return {
        "blocking_player_index": block.blocking_player_index,
        "status": block.status,
        "is_undetermined": block.is_undetermined,
    }


def court_deck_to_json(court_deck: CourtDeck):
    return [card.character for card in court_deck.cards]


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

    if not game_state.challenge and not game_state.block:
        return f"Player {player_num} Move: {game_state.current_action.action}!".title()

    if game_state.challenge:
        challening_player_num = game_state.challenge.challening_player_index + 1
        if game_state.challenge.is_undetermined:
            return f"Player {challening_player_num} challenged Player {player_num} 🤨"
        if game_state.challenge.status == ActionChallenge.Status.Show:
            return f"Player {player_num} revealed card 😮‍💨"
        if game_state.challenge.status == ActionChallenge.Status.NoShow:
            return f"Player {player_num} is bluffing 😫"

    if game_state.block:
        blocking_player_num = game_state.block.blocking_player_index + 1
        if game_state.block.is_undetermined:
            return f"Player {blocking_player_num} blocked Player {player_num} 🚫"
        if game_state.block.status == ActionBlock.Status.Show:
            return f"Player {player_num} revealed card 🚫"
        if game_state.block.status == ActionBlock.Status.NoShow:
            return f"Player {player_num} is bluffing 😂"

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

def game_state_to_json(game_state: GameState) -> dict:
    """ convers GameState to a json """
    return {
        "current_players_index": game_state.current_player_index,
        "players": [player_to_json(player_index, player) for player_index, player in enumerate(game_state.players)],
        "current_action": action_to_json(game_state.current_action),
        "challenge": challenge_to_json(game_state.challenge),
        "block": block_to_json(game_state.block),
        "treasury": game_state.treasury.coins,
        "court_deck": court_deck_to_json(game_state.court_deck),
        "turn_ended": game_state.turn_ended,
        "winning_player_index": game_state.get_winning_player(),
        "ui": {
            "status_text": ui_status_text(game_state),
            "available_actions": ui_available_actions(game_state),
            "can_automate": ui_should_automate(game_state)
        }
    }


def game_state_from_json(data: dict) -> GameState:
    """
        setups GameState from a json
        or creates a fresh GameState using default if empty
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
            revealed_cards=cards_from_names(player["revealed_cards"])
        ) for player in players_from_db]

    # challenge
    challenge_from_db = data.get("challenge")
    challenge = None
    if challenge_from_db:

        challenge = ActionChallenge(
            challening_player_index=challenge_from_db["challenging_player_index"],
            status=challenge_from_db["status"],
        )

    # block
    block_from_db = data.get("block")
    block = None
    if block_from_db:
        block = ActionBlock(
            blocking_player_index=block_from_db["blocking_player_index"],
            status=block_from_db["status"],
        )

    # current action
    current_action_from_db = data.get("current_action")
    current_action = None
    if current_action_from_db:
        current_action = get_action_by_name(
            action_name=current_action_from_db["action"],
            targeted_player_index=current_action_from_db["targeted_player_index"]
        )

    return GameState(
        current_player_index=current_player_index,
        players=players,
        current_action=current_action,
        challenge=challenge,
        block=block,
        treasury=treasury,
        court_deck=court_deck,
        turn_ended=data.get("turn_ended") or False
    )