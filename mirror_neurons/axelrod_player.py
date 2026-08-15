"""The mirror-neuron agent as an Axelrod player, so it can face real opponents.

The rerun plays three fixed policies that never react. Axelrod supplies the
opponents from the literature, the match engine and the payoff bookkeeping, so
none of that is written here.

Two things about this wrapper are decisions rather than plumbing, and both are
argued in `design-notes/what-the-agent-cannot-do.md`:

- Axelrod's engine is simultaneous-move, which is the model's *static* timing.
  The agent reads the opponent's previous action, never the current one.
- The draw is taken with Axelrod's per-match generator rather than through
  `HebbianMirrorNeuronAgent.select_action`. It is the same Bernoulli draw on the
  same weights, so behaviour is unchanged, but it makes a tournament reproducible
  from Axelrod's own seed instead of from the global numpy state. The weight
  update, which is the model, is untouched and still lives in `hebbian_agent.py`.
"""

import axelrod as axl
from axelrod.action import Action

from hebbian_agent import HebbianMirrorNeuronAgent

TO_AGENT_ACTION = {Action.C: "Cooperate", Action.D: "Defect"}


class MirrorNeuronPlayer(axl.Player):
    """Imitates whatever it last saw, with no notion of payoff.

    It never reads the score. That is the model, not an oversight: the claim
    under test is that reciprocity emerges from imitation alone.
    """

    name = "Mirror Neuron"
    classifier = {
        # The weight carries every observation, so the whole history matters.
        "memory_depth": float("inf"),
        "stochastic": True,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, learning_rate=2 ** 0.5 - 1, cooperation_rate=0.8):
        super().__init__()
        self.agent = HebbianMirrorNeuronAgent(learning_rate, cooperation_rate)

    def strategy(self, opponent):
        if opponent.history:
            self.agent.observe_and_learn(TO_AGENT_ACTION[opponent.history[-1]])
        return self._random.random_choice(self.agent.weights["Cooperate"])
