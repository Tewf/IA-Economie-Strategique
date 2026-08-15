"""What the tournament runs against, and with what settings.

Config, not code. Nothing here runs anything. Why each opponent is in the set is
argued in `design-notes/opponents-and-games.md`; this file only names them.
"""

import axelrod as axl

# Every one of these is in Axelrod, from the literature, and none is written
# here. Cooperator, Defector and Random are the rerun's own three fixed
# policies, kept so the new results can be read against the committed figures.
OPPONENTS = [
    axl.TitForTat,          # the behaviour the model predicts should emerge
    axl.Cooperator,         # the rerun's always_cooperate
    axl.Defector,           # the rerun's always_defect
    axl.Random,             # the rerun's coin flip
    axl.Grudger,            # grim trigger, named in the report at 2.1.2(c)
    axl.WinStayLoseShift,   # Pavlov: reacts to payoff, which this agent cannot
    axl.Alternator,         # a pattern no imitator can track
]

# Axelrod's default Prisoner's Dilemma payoffs: R=3, P=1, T=5, S=0.
# The prompt in ../llm/prompts/prisoners_dilemma.md states the same four
# numbers, so a language model and this agent play the same game.
GAME = axl.Game()

# 100 rounds is what the rerun's `simulate` uses, so the weight trajectories are
# directly comparable. The agent is stochastic, so one match is one sample.
TURNS = 100
REPETITIONS = 20

# Axelrod seeds its own per-match generator from this, which is why the wrapper
# draws through `self._random` rather than through the global numpy state.
SEED = 0

# The rerun's own sweep, unchanged, plus the default the write-up uses.
# 2**0.5 - 1 is about 0.4142 and is not traceable to any measurement; the
# folder README records that.
LEARNING_RATES = [0.01, 0.1, 0.5, 1.0]
DEFAULT_LEARNING_RATE = 2 ** 0.5 - 1
