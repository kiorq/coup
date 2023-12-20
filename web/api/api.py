from flask import Blueprint, jsonify
from web.services import game_current_state

page = Blueprint("api_page", __name__, "templates")


@page.route("/api/current_state", methods=["GET", "POST"])
def game_state():
    state = game_current_state()
    return jsonify(state)