from flask import Blueprint, render_template
from web.services import game_current_state

page = Blueprint("main_page", __name__, "templates")

@page.route("/", methods=["GET", "POST"])
def home():
    state = game_current_state()
    return render_template("home.html", game_state=state)