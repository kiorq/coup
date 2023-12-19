
from typing import Union

from components.actions import Action, ActionBlock, ActionChallenge, Treasury
from components.cards import CourtDeck
from components.errors import GameError
from components.player import Player


class GameState(object):
    current_player_index: int
    players: list[Player]
    current_action: Union[Action, None]
    challenge: Union[ActionChallenge, None]
    block: Union[ActionBlock, None]
    treasury: Treasury
    court_deck: CourtDeck
    turn_ended: bool

    def __init__(
        self,
        current_player_index: int,
        players: list[Player],
        current_action: Union[Action, None],
        challenge: Union[ActionChallenge, None],
        block: Union[ActionBlock, None],
        treasury: Treasury,
        court_deck: CourtDeck,
        turn_ended: bool,
    ) -> None:
        self.current_player_index = current_player_index
        self.players = players
        self.current_action = current_action
        if self.current_action:
            self.current_action.game_state = self
        self.challenge = challenge
        self.block = block
        self.treasury = treasury
        self.court_deck = court_deck
        self.turn_ended = turn_ended

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def get_active_players(self):
        return [player for player in self.players if not player.is_exiled]

    def get_active_player_indexes(self):
        return [player_index for player_index, player in enumerate(self.players) if not player.is_exiled]

    def get_winning_player(self):
        active_players = self.get_active_players()
        if len(active_players) == 1:
            return self.players.index(active_players[0]) # absolutely horrible
        return None

    def perform_action(self, action: Action):
        # attempt to pay penalty first before setting current acction
        try:
            action.game_state = self
            action.pay_penalty() # pay penalty for action right away
        except Treasury.TreasuryError:
            raise
        # set current action and reset vars
        self.block = None
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
            raise GameError("Not action to complete")

        # end turn
        if self.turn_ended:
            self.end_turn()
            return

        # challenges

        if self.current_action.required_influence:
            # this action can be challenged
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

        if self.current_action.is_blockably_by:
            # this action can be blocked
            if self.request_block():
                return

        if self.block:
            if self.block.is_undetermined or self.block.status == ActionBlock.Status.Challenge:
                # cannot do anything until block (or its challenge) has been resolved
                return

            if self.block.status == ActionBlock.Status.Show:
                # blocking player proved they have influence
                self.turn_ended = True
                return

            if self.block.status == ActionBlock.Status.NoChallenge:
                # does not want to challenge block
                self.turn_ended = True
                return

            # now we need to check if someone want to challenge the block

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
        """
            allows a current player to respond to a challenge
            on their current action
        """
        if not self.challenge:
            raise GameError("No challenge to respond to")

        if not self.current_action:
            raise GameError("No action being performed")

        if not self.current_action.required_influence:
            raise GameError("This action should not have been challenged")

        if self.current_player.is_bluffing(self.current_action.required_influence) \
            or status == ActionChallenge.Status.NoShow:
            self.challenge.status = ActionChallenge.Status.NoShow
            self.current_player.loose_influence()
            # TODO: cost returned to player?

        elif status == ActionChallenge.Status.Show:
            challenging_player = self.players[self.challenge.challening_player_index]
            self.challenge.status = ActionChallenge.Status.Show
            self.current_player.swap_cards(self.court_deck, self.current_action.required_influence)
            challenging_player.loose_influence()
            return
        else:
            raise GameError("Invalid response to challenge")

    def request_block(self):
        """
            asks each player if they want to block action
        """
        if not self.block:
            for player_index, player in enumerate(self.players):
                if player_index == self.current_player_index:
                    # current player cannot challenge themself
                    continue

                if player.is_exiled:
                    # user is can no longer play
                    continue

                if player.request_block():
                    self.block = ActionBlock(
                        blocking_player_index=player_index,
                    )
                    return True

            self.block = ActionBlock(-1, -1)

    def respond_to_block(self, challenging_player_index: int, status: int):
        """
            alows any player to respond block and can challenging it
            once a block is challenged, the challenged response by the blocking player is automated
        """
        if not self.block:
            raise GameError("No block to respond to")

        if not self.current_action:
            raise GameError("No action being performed")

        if status == ActionBlock.Status.NoChallenge:
            self.block.status = ActionBlock.Status.NoChallenge
            # nothing happens, turn will end when we self.try_to_complete_action

        elif status == ActionBlock.Status.Challenge:
            blocking_player = self.players[self.block.blocking_player_index]
            blocking_player_card = blocking_player.has_cards(self.current_action.is_blockably_by)
            blocking_player_is_bluffing = not bool(blocking_player_card)
            blocking_player_will_show = blocking_player.request_will_show()

            # blocking player is bluffing or does not want to show
            if blocking_player_is_bluffing or not blocking_player_will_show:
                self.block.status = ActionBlock.Status.NoShow
                blocking_player.loose_influence()
            else:
                self.block.status = ActionBlock.Status.Show
                self.players[challenging_player_index].loose_influence()
                blocking_player.swap_cards(self.court_deck, blocking_player_card)
                pass
            return
        else:
            raise GameError("Invalid response to challenge")
