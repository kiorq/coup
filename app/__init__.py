
from app.services import load_game_state_clean, load_game_state_from_store, store_game_state
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

    action = None # TODO: get from request
    game_state.perform_action(action)
    game_state.try_to_complete_action()

    # store and return state
    state = store_game_state(game_state)
    return jsonify(state)


@app.route("/respond_to_challenge", methods=["POST"])
def respond_to_challenge():
    game_state = load_game_state_from_store()

    challenge_response = 1 # TODO: get from request
    if game_state.respond_to_challenge(challenge_response):
        game_state.try_to_complete_action()
    # store and return state
    state = game_state.get_state()
    state = store_game_state(game_state)
    return jsonify(state)

