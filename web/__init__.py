from flask import Flask, jsonify
from game.errors import GameError
from web.controllers import home


app = Flask(__name__)

# pages

app.register_blueprint(home.page)

# error hanlding

@app.errorhandler(GameError)
def handle_game_error(e: GameError):
    return jsonify({"error": str(e)}), 400
