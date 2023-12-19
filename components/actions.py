from typing import Union


class Treasury(object):
    coins = 0

    def __init__(self, coins: int) -> None:
        self.coins


class CourtDeck(object):
    def __init__(self, cards) -> None:
        self.cards = cards

class CharacterCard(object):
    pass

class DukeCharacterCard(CharacterCard):
    pass

class AssassinCharacterCard(CharacterCard):
    pass

class CaptainCharacterCard(CharacterCard):
    pass

class AmbassadorCharacterCard(CharacterCard):
    pass

class ContessaCharacterCard(CharacterCard):
    pass


class Action(object):
    required_influence: Union[type[CharacterCard], None]

    def resolve(self):
        pass


class IncomeAction(Action):
    required_influence = None


class ForeignAidAction(Action):
    required_influence = None


class CoupAction(Action):
    required_influence = None

class TaxAction(Action):
    required_influence = DukeCharacterCard


class AssassinateAction(Action):
    required_influence = AssassinCharacterCard


class StealAction(Action):
    required_influence = CaptainCharacterCard


class ExchangeAction(Action):
    required_influence = AmbassadorCharacterCard


class Player(object):
    def __init__(self, coins: int, cards: list[CharacterCard]):
        self.coins = coins
        self.cards = cards

    def request_challenge(self):
        from random import random
        return random() < .10 # 10% probability

class ActionChallenge(object):
    class Status:
        Undetermined = 0
        NoShow = 1
        Show = 2

    def __init__(self, challening_player_index: int) -> None:
        self.challening_player_index = challening_player_index
        self.status = ActionChallenge.Status.Undetermined

class ActionChallengeSkipped(ActionChallenge):
    challening_player_index = -1
    status = -1
    def __init__(self, **kwargs) -> None:
        pass

class GameState(object):
    current_player_index: int
    players: list[Player]
    current_action: Union[Action, None]
    challenge: Union[ActionChallenge, None]

    def __init__(self, current_player_index: int, players: list[Player], current_action: Union[Action, None], challenge: Union[ActionChallenge, None]):
        self.current_player_index = current_player_index
        self.players = players
        self.current_action = current_action
        self.challenge = challenge

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
                return False

        self.current_action.resolve()
        self.end_turn()
        return True

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
            self.challenge = ActionChallengeSkipped()
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
        return {}