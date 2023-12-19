from flask import Flask, jsonify
from game.errors import GameError

from web.controllers import home


app = Flask(__name__)

app.register_blueprint(home.page)


# @app.route("/state", methods=["GET"])
# def state():
#     game_state = load_game_state_from_store()
#     return jsonify(game_state_to_json(game_state))


# @app.route("/start_new", methods=["POST"])
# def start_new():
#     game_state = load_game_state_clean()

#     # store and return state
#     state = store_game_state(game_state)
#     return jsonify(state)


# @app.route("/perform_action", methods=["POST"])
# def perform_action():
#     game_state = load_game_state_from_store()

#     if game_state.current_player_index != 0:
#         raise GameError("Not your turn")

#     if game_state.current_action:
#         raise GameError("Action already being performed, may be challenged or blocked")

#     data = request.json

#     action = get_action_by_name(
#         data.get("action"),
#         targeted_player_index=data.get("targeted_player_index", None)
#     )

#     game_state.perform_action(action)
#     game_state.try_to_complete_action()

#     # store and return state
#     state = store_game_state(game_state)
#     return jsonify(state)


# @app.route("/next", methods=["POST"])
# def next():
#     """
#         radomly chooses what other players do
#     """
#     game_state = load_game_state_from_store()

#     if game_state.turn_ended:
#         game_state.end_turn()
#         state = store_game_state(game_state)
#         return jsonify(state)

#     if game_state.current_player_index == 0 and not game_state.turn_ended:
#         raise GameError("Cannot skip your turn")

#     # handle selecting action
#     if not game_state.current_action:
#         targeted_player_index = choice(game_state.get_active_player_indexes())
#         action = get_random_action(
#             targeted_player_index=targeted_player_index
#         )
#         game_state.perform_action(action)

#     # handle challenge
#     elif game_state.challenge and game_state.challenge.is_undetermined:
#         random_response = choice([
#             ActionChallenge.Status.NoShow,
#             ActionChallenge.Status.Show,
#         ])
#         game_state.respond_to_challenge(random_response)

#     # handle block
#     elif game_state.block and game_state.block.is_undetermined:
#         random_response = choice([
#             ActionBlock.Status.NoChallenge,
#             ActionBlock.Status.Challenge,
#         ])
#         game_state.respond_to_block(
#             challenging_player_index=game_state.current_player_index, # TODO: or get a random id
#             status=random_response
#         )

#     game_state.try_to_complete_action()

#     # store and return state
#     state = store_game_state(game_state)
#     return jsonify(state)


# @app.route("/respond_to_challenge", methods=["POST"])
# def respond_to_challenge():
#     game_state = load_game_state_from_store()

#     if not game_state.challenge or not game_state.challenge.is_undetermined:
#         raise GameError("Not challenge to respond to")

#     data = request.json

#     challenge_response = data["challenge_response"]
#     game_state.respond_to_challenge(challenge_response)
#     game_state.try_to_complete_action()
#     # store and return state
#     state = store_game_state(game_state)
#     return jsonify(state)


# @app.route("/respond_to_block", methods=["POST"])
# def respond_to_block():
#     game_state = load_game_state_from_store()

#     if not game_state.block or not game_state.block.is_undetermined:
#         raise GameError("No block to respond to")

#     data = request.json

#     block_response = data["block_response"]
#     game_state.respond_to_block(
#         challenging_player_index=0,
#         status=block_response
#     )
#     game_state.try_to_complete_action()
#     # store and return state
#     state = store_game_state(game_state)
#     return jsonify(state)


@app.errorhandler(GameError)
def handle_game_error(e: GameError):
    return jsonify({"error": str(e)}), 400
