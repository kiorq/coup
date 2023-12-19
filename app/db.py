from tinydb import TinyDB, Query, where


KEY = 1

def persist_storage(state: dict):
    state.update({"key": KEY})
    with TinyDB('./db.json') as db:
        db.upsert(state, where('key') == KEY)

def retrieve_storage():
    with TinyDB('./db.json') as db:
        return db.get(where('key') == KEY)