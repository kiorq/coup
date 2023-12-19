from flask import Blueprint, render_template
from web.services import game_current_state, game_start_new

page = Blueprint("main_page", __name__, "templates")

def get_color_by_name_func(name: str):
    CARD_COLOR_CLASS_MAP: dict[str, str] = {
        "duke": "bg-purple-500",
        "assassin": "bg-black-500",
        "captain": "bg-blue-500",
        "ambassador": "bg-gren-500",
        "contessa": "bg-red-500"
    }
    return CARD_COLOR_CLASS_MAP.get(name)

@page.route("/", methods=["GET", "POST"])
def home():
    # state = game_start_new()
    state = game_current_state()
    return render_template(
        "home.html",
        game_state=state,
        get_color_by_name_func=get_color_by_name_func
    )