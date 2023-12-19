
from typing import Union

from components.actions import Action, ActionChallenge, Treasury
from components.cards import CourtDeck
from components.player import Player


class GameState(object):
    current_player_index: int
    players: list[Player]
    current_action: Union[Action, None]
    challenge: Union[ActionChallenge, None]
    treasury: Treasury
    court_deck: CourtDeck

    def __init__(self, current_player_index: int, players: list[Player], current_action: Union[Action, None], challenge: Union[ActionChallenge, None], treasury: Treasury, court_deck: CourtDeck):
        self.current_player_index = current_player_index
        self.players = players
        self.current_action = current_action
        self.challenge = challenge
        self.treasury = treasury
        self.court_deck = court_deck

    def perform_action(self, action: Action):
        self.current_action = action

    def end_turn(self):
        """
            resets game state for next turn
        """
        self.current_action = None
        if self.current_player_index + 1 == len(self.players):
            self.current_player_index = 0
        else:
            self.current_player_index += 1

    def try_to_complete_action(self):
        """
            this will try and continue the action until it's resolved or the player's turn has ended
            returns with action is resolved or turn has ended
        """
        if not self.current_action:
            raise Exception("Not action to complete")

        if self.current_action.required_influence:
            if self.request_challenge():
                return

        self.current_action.resolve()
        self.end_turn()
        return

    def request_challenge(self):
        """
            asks each player if they want to challenge action
        """
        if not self.challenge:
            for player_index, player in enumerate(self.players):
                if player_index == self.current_player_index:
                    # current player cannot challenge themself
                    continue

                if player.request_challenge():
                    self.challenge = ActionChallenge(
                        challening_player_index=player_index,
                    )
                    return True
            # no one wanted to challenge
            self.challenge = ActionChallenge(-1, -1)
        return False

    def respond_to_challenge(self, status: int):
        if not self.challenge:
            raise Exception("No challenge to respond to")

        if status == ActionChallenge.Status.Show:
            self.challenge.status = ActionChallenge.Status.Show
            # ActionChallenge.challening_player_index loses influence
            # self.current_player_index swaps related card
            return True
            # we still need to run try_to_complete (another user could block)
        elif status == ActionChallenge.Status.NoShow:
            self.challenge.status = ActionChallenge.Status.NoShow
            # self.current_player_index looses influence
            # cost returned to player
            self.end_turn()
            return False
        else:
            raise Exception("Invalid response to challenge")

    def get_state(self):
        """ a state that front end will use to determine what to do next """
        def playerJson(player_index, player: Player):
            return {
                "player_index": player_index,
                "coins": player.coins,
                "cards": [card.character for card in player.cards]
            }
        def actionJson(action: Union[Action, None]):
            if not action:
                return None
            return action.action
        def challengeJson(challenge: Union[ActionChallenge, None]):
            if not challenge:
                return {}
            return {
                "challening_player_index": challenge.challening_player_index,
                "status": challenge.status,
            }
        def courtDeckJson(court_deck: CourtDeck):
            return [card.character for card in court_deck.cards]

        return {
            "current_players_index": self.current_player_index,
            "players": [playerJson(player_index, player) for player_index, player in enumerate(self.players)],
            "current_action": actionJson(self.current_action),
            "challenge": challengeJson(self.challenge),
            "treasury": self.treasury.coins,
            "court_deck": courtDeckJson(self.court_deck),
        }