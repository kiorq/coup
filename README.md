# Coup by @kiorq

![In game screenshot](/images/in-game-screenshot.png)

## Setup

- Set up the Python environment (Python v3).
- Install requirements: pip install -r requirements.txt
- Run `flask --app web run --debug`
- Visit http://127.0.0.1:5000 to view.

## How to Play

First, you need to know [how to play coup](https://www.ultraboardgames.com/coup/game-rules.php).

### Layout

The UI's layout is organized into four invisible rows:

1. Other Players
2. Player 1
3. Status and Action Bar
4. Treasury and Court Dock

**Other Players**

The first row represents the other three players in the game (players 2-4). You can observe their coin count and facedown cards. Once revealed, their color and name will be exposed.

A player labeled "👻 Exiled" has all their cards shown.

When it's a player's turn, the label "🤖 Playing" will appear beneath them.

**Player 1**

Below the other players is your section, labeled "Player 1 (You)." You'll see the coins you have left and your two cards. These cards are always visible to you, and once revealed, their opacity will change.

**Status and Action Bar**

Below Player 1 is the status and action bar.

The status updates you on what is happening in the game, including the start of a turn, performed actions, challenges, blocks, and the end of a turn or the winner.

Under the status, buttons appear for the actions you can perform. Actions with the ✔️ emoji signify actions without bluffing, while those with the ⚠️ emoji involve bluffing.

When challenged or blocked, you'll have options to respond accordingly.

**Treasury and Court Dock**

This section displays the remaining coins in the treasury and the number of cards in the court dock.

## Design and Architecture

**Technology Stack:**

- **Backend:** Flask
- **Frontend:** HTML, Python (No JavaScript written, only tailwindcss cdn included)

**State Management:**

- The game operates as a state machine, with each move represented in the game state.
- The state is stored and retrieved in JSON format. (see `serializer.py`)

**Interaction Flow:**

1. User clicks on an action button in the Action Bar on the frontend.
2. Frontend sends a POST request to the backend.
3. Backend analyzes the request, updating the state based on the specific action.
4. Frontend reloads with the updated state, reflecting changes.

**State Observation:**

- Visit `[GET] /api/current_state` to observe the current game state in JSON format at any given time.
- The frontend dynamically adapts based on this data (`web/services/ui_state.py` helper functions make this easier).

**Randomized Player Moves:**

- Other player moves are randomized, providing an unpredictable gaming experience.
- The state machine facilitates step-by-step observation of action and challenge resolutions.

**Zero JavaScript Requirement:**

- The design emphasizes simplicity, requiring zero JavaScript.
- Python and HTML collaboratively deliver an engaging gaming experience.

**Inspiration:**

- Inspired by the classic [Pokémon Crater](https://pokemoncrater.fandom.com/wiki/Pokemon_Crater_Wiki) game.

**Directory Structure:**

- `game` directory houses core game logic.
- `web` directory implements a Model-View-Controller (MVC) Flask setup, and interaction with game logic.
