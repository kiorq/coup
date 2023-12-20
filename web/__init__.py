from flask import Flask, jsonify
from game.errors import GameError
from web.controllers import home
from web.api import api


app = Flask(__name__)

# pages

app.register_blueprint(home.page)
app.register_blueprint(api.page)

# error hanlding

@app.errorhandler(GameError)
def handle_game_error(e: GameError):
    return jsonify({"error": str(e)}), 400
