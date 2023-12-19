
from app.services import load_game_state_clean, load_game_state_from_store, store_game_state
from components.actions import get_action_by_name
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    return {}


@app.route("/state", methods=["GET"])
def state():
    game_state = load_game_state_from_store()
    return jsonify(game_state.get_state())


@app.route("/start_new", methods=["POST"])
def start_new():
    game_state = load_game_state_clean()

    # store and return state
    state = store_game_state(game_state)
    return jsonify(state)


@app.route("/perform_action", methods=["POST"])
def perform_action():
    game_state = load_game_state_from_store()

    if game_state.current_player_index != 0:
        raise Exception("Not your turn")

    if game_state.current_action:
        raise Exception("Action already being performed, may be challenged or blocked")

    data = request.json

    action = get_action_by_name(
        data.get("action")
    )

    game_state.perform_action(action)
    game_state.try_to_complete_action()

    # store and return state
    state = store_game_state(game_state)
    return jsonify(state)


@app.route("/respond_to_challenge", methods=["POST"])
def respond_to_challenge():
    game_state = load_game_state_from_store()

    if not game_state.challenge or not game_state.challenge.is_undetermined:
        raise Exception("Not challenge to respond to")

    data = request.json

    challenge_response = data["challenge_response"]
    game_state.respond_to_challenge(challenge_response)
    game_state.try_to_complete_action()
    # store and return state
    state = game_state.get_state()
    state = store_game_state(game_state)
    return jsonify(state)

