"""An Axelrod strategy seated as a player this harness can drive.

The bot cell is the one that pays for itself twice. It costs the least per match,
and it puts the models on the same opponents the Hebbian agent faced, so
`../mirror_neurons/results/head_to_head.csv` and this folder's `vs_bots.csv` are
two rows of one table rather than two unrelated stories.

Axelrod strategies speak `Action.C` and `Action.D`, read their opponent off a
player object, and expect their history to be updated with both plays at once
through `update_history`, which is what `Match.simultaneous_play` does. This
adapts that to the two calls the rest of the harness uses and changes nothing
about the strategy itself. A bare `axelrod.Player` stands in for the model,
because strategies read more of an opponent than its history list: Pavlov wants
the last round both ways, and others read cooperation counts.
"""

import axelrod as axl

FROM_AXELROD = {axl.Action.C: "Cooperate", axl.Action.D: "Defect"}
TO_AXELROD = {"Cooperate": axl.Action.C, "Defect": axl.Action.D}


class BotOpponent:
    """One Axelrod strategy, with the same two calls as every other player."""

    can_talk = False

    def __init__(self, strategy, seed=0):
        self.name = strategy.name
        self.strategy = strategy()
        self.strategy.set_seed(seed)
        self.stand_in = axl.Player()
        self.history = []
        self.own_history = []
        self.transcript = []
        self._pending = None

    def select_action(self):
        """Chosen from the opponent's history so far, before this round's move."""
        action = FROM_AXELROD[self.strategy.strategy(self.stand_in)]
        self._pending = action
        self.own_history.append(action)
        return action

    def observe_and_learn(self, opponent_action):
        """Both plays are known now, which is when Axelrod expects the update."""
        self.history.append(opponent_action)
        mine = TO_AXELROD[self._pending]
        theirs = TO_AXELROD[opponent_action]
        self.strategy.update_history(mine, theirs)
        self.stand_in.update_history(theirs, mine)
        self._pending = None
