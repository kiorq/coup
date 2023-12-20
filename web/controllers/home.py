from flask import Blueprint, render_template, request
from game.actions import ActionBlock, ActionChallenge
from game.errors import GameError
from web.services import automate_next_move, game_current_state, game_perform_action, game_start_new, get_color_by_name_func, respond_to_block, respond_to_challenge

page = Blueprint("main_page", __name__, "templates")


@page.route("/", methods=["GET", "POST"])
def home():
    # state = game_start_new()
    state = game_current_state()
    game_state = state["game_state"]
    ui = state["ui"]
    error_message = None
    if request.method == "POST":
        data = request.form

        try:
            # reset game (start over)
            reset_req = data.get("reset")
            starting_player_index = int(data.get("starting_player_index") or 0)
            if reset_req:
                state = game_start_new(
                    current_players_index=starting_player_index,
                )

            # perform action
            action_name_req = data.get("action")
            if action_name_req:
                state = game_perform_action(
                    action_name=action_name_req,
                    targeted_player_index=None
                )

            # respond to challenge
            respond_to_challenge_req = data.get("respond_to_challenge")
            if respond_to_challenge_req:
                state = respond_to_challenge(
                    ActionChallenge.Status.Show \
                        if respond_to_challenge_req == "show" \
                            else ActionChallenge.Status.NoShow
                )

            # respond to block
            respond_to_block_req = data.get("respond_to_block")
            if respond_to_block_req:
                state = respond_to_block(
                    ActionBlock.Status.Challenge \
                        if respond_to_block_req == "challenge" \
                            else ActionBlock.Status.NoChallenge
                )

            # automate next move (for other players)
            automate_move = data.get("automate_move")
            if automate_move:
                state = automate_next_move()
        except GameError as e:
            error_message = str(e)


    return render_template(
        "home.html",
        game_state=game_state,
        ui=ui,
        error_message=error_message,
        get_color_by_name_func=get_color_by_name_func
    )