
from components.actions import GameState
from flask import Flask, request, jsonify

app = Flask(__name__)

def load_game_state_from_db():
    return GameState(
        current_player_index=0,
        players=[],
        current_action=None,
        challenge=None
    )

@app.route("/", methods=["GET", "POST"])
def home():
    return {}

@app.route("/perform_action", methods=["GET", "POST"])
def perform_action():
    game_state = load_game_state_from_db()
    action = None # TODO: get from request
    game_state.perform_action(action)
    game_state.try_to_complete_action()
    return jsonify(game_state.get_state())


@app.route("/respond_to_challenge", methods=["GET", "POST"])
def respond_to_challenge():
    game_state = load_game_state_from_db()
    challenge_response = 1 # TODO: get from request
    if game_state.respond_to_challenge(challenge_response):
        game_state.try_to_complete_action()
    return jsonify(game_state.get_state())

