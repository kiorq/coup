from typing import Union
from tinydb import TinyDB, where


KEY = 1 # fixed key (only one game at a time)


def store_game_data(state: dict):
    state.update({"key": KEY})
    with TinyDB('./db.json') as db:
        db.upsert(state, where('key') == KEY)


def retrieve_game_data() -> Union[dict, None]:
    with TinyDB('./db.json') as db:
        return db.get(where('key') == KEY)