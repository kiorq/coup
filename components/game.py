
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
    turn_ended: bool

    def __init__(self, current_player_index: int, players: list[Player], current_action: Union[Action, None], challenge: Union[ActionChallenge, None], treasury: Treasury, court_deck: CourtDeck, turn_ended: bool):
        self.current_player_index = current_player_index
        self.players = players
        self.current_action = current_action
        self.challenge = challenge
        self.treasury = treasury
        self.court_deck = court_deck
        self.turn_ended = turn_ended

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def get_winning_player(self):
        active_players = [player for player in self.players if not player.is_exiled]
        if len(active_players) == 1:
            return self.players.index(active_players[0]) # absolutely horrible
        return None

    def perform_action(self, action: Action):
        self.challenge = None
        self.current_action = action

    def end_turn(self):
        """
            resets game state for next turn
        """
        self.turn_ended = False
        self.current_action = None
        self.challenge = None
        if self.current_player_index + 1 == len(self.players):
            self.current_player_index = 0
        else:
            self.current_player_index += 1

        if self.players[self.current_player_index].is_exiled:
            # this user cannot play
            self.end_turn()

    def try_to_complete_action(self):
        """
            this will try and continue the action until it's resolved or the player's turn has ended
            returns with action is resolved or turn has ended
        """
        if not self.current_action:
            raise Exception("Not action to complete")

        # end turn
        if self.turn_ended:
            self.end_turn()
            return

        # challenges

        if self.current_action.required_influence:
            if self.request_challenge():
                return

        if self.challenge:
            if self.challenge.is_undetermined:
                # cannot do anything until challenge is resolved
                return

            if self.challenge.status == ActionChallenge.Status.NoShow:
                # player did not show influencing character card
                # end turn
                self.turn_ended = True
                return

        # blocks

        self.current_action.resolve()
        self.turn_ended = True
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

                if player.is_exiled:
                    # user is can no longer play
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

        if not self.current_action:
            raise Exception("No action being performed")

        if self.current_player.is_bluffing(self.current_action) or status == ActionChallenge.Status.NoShow:
            self.challenge.status = ActionChallenge.Status.NoShow
            self.current_player.loose_influence()
            # TODO: cost returned to player

        elif status == ActionChallenge.Status.Show:
            challenging_player = self.players[self.challenge.challening_player_index]
            self.challenge.status = ActionChallenge.Status.Show
            self.current_player.swap_cards(self.court_deck, self.current_action)
            challenging_player.loose_influence()
            return
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
            "turn_ended": self.turn_ended,
            "winning_player_index": self.get_winning_player()
        }