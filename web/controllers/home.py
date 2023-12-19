from flask import Blueprint, render_template, request
from web.services import automate_next_move, game_current_state, game_perform_action, game_start_new, get_color_by_name_func

page = Blueprint("main_page", __name__, "templates")


@page.route("/", methods=["GET", "POST"])
def home():
    # state = game_start_new()
    state = game_current_state()
    if request.method == "POST":
        data = request.form
        # perform action
        action_name = data.get("action")
        if action_name:
            state = game_perform_action(
                action_name=action_name,
                targeted_player_index=None
            )

        # automate next move (for other players)
        automate_move = data.get("automate_move")
        if automate_move:
            state = automate_next_move()

    return render_template(
        "home.html",
        game_state=state,
        get_color_by_name_func=get_color_by_name_func
    )