from flask import Blueprint, render_template, request
from game.actions import ActionBlock, ActionChallenge
from game.errors import GameError
from web.services.game_state import automate_next_move, block_action, challenge_action, game_current_state, game_perform_action, game_start_new, respond_to_block, respond_to_challenge
from web.services.ui_state import get_color_by_name_func, ui_current_state

page = Blueprint("main_page", __name__, "templates")


@page.route("/", methods=["GET", "POST"])
def home():
    # state = game_start_new()
    game_state = game_current_state()
    error_message = None
    if request.method == "POST":
        data = request.form

        try:
            # reset game (start over)
            reset_req = data.get("reset")
            starting_player_index = int(data.get("starting_player_index") or 0)
            if reset_req:
                game_state = game_start_new(
                    current_players_index=starting_player_index,
                )

            # perform action
            action_name_req = data.get("action")
            if action_name_req:
                game_state = game_perform_action(
                    action_name=action_name_req,
                    targeted_player_index=None
                )

            # respond to challenge
            respond_to_challenge_req = data.get("respond_to_challenge")
            if respond_to_challenge_req:
                game_state = respond_to_challenge(
                    ActionChallenge.Status.Show \
                        if respond_to_challenge_req == "show" \
                            else ActionChallenge.Status.NoShow
                )

            # respond to block
            respond_to_block_req = data.get("respond_to_block")
            if respond_to_block_req:
                game_state = respond_to_block(
                    ActionBlock.Status.Challenge \
                        if respond_to_block_req == "challenge" \
                            else ActionBlock.Status.NoChallenge
                )

            # challenge another's player action
            challenge_action_req = data.get("challenge_action")
            if challenge_action_req:
                game_state = challenge_action()

            # block another's player action
            block_action_req = data.get("block_action")
            if block_action_req:
                game_state = block_action()

            # automate next move (for other players)
            automate_move = data.get("automate_move")
            if automate_move:
                game_state = automate_next_move()
        except GameError as e:
            error_message = str(e)

    # get updated ui state
    ui = ui_current_state()

    return render_template(
        "home.html",
        game_state=game_state,
        ui=ui,
        error_message=error_message,
        get_color_by_name_func=get_color_by_name_func
    )