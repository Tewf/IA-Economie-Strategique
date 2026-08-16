"""What matches get played, and how a player's seed is derived.

Config, not code. The panel itself is in `panel_config.py`.

The grid has three cells, and the third is the one that pays for itself twice:
it puts the models and the Hebbian agent on identical opponents, so
`../mirror_neurons/results/` and `results/` hold comparable numbers instead of
two unrelated stories.
"""

import hashlib

import axelrod as axl

# 30 rounds, so a strategy has room to establish itself and then be tested, and
# short enough that the whole grid is an evening rather than a week. Axelrod's payoffs, so the numbers line up with the Hebbian tournament
# exactly. Both are stated in `prompts/prisoners_dilemma.md` too.
ROUNDS = 30
# Four, not five. The payoff order alternates on even and odd repetitions, so
# only an even count balances it: five gives a 3:2 skew and defeats half the
# point of counterbalancing at all. Repetitions are part of the match key, so
# raising this later replays nothing already done.
REPETITIONS = 4
GAME = axl.Game()

# Cheap talk is the treatment Ng (2023) is built on: non-binding messages that
# can sustain cooperation by signalling intent. Running with and without it is
# the smallest experiment testing something the internship read about and could
# not build.
CONDITIONS = ["with_cheap_talk", "without_cheap_talk"]

# The same five the Hebbian agent met, minus Cooperator and Random which say
# little about a talking player, plus Alternator which no imitator can track.
BOT_OPPONENTS = [
    axl.TitForTat,
    axl.Grudger,
    axl.Defector,
    axl.WinStayLoseShift,
    axl.Alternator,
]

# The lock-in cell. Two imitators settle on whatever they start with, 700 runs
# out of 700 (`../mirror_neurons/results/self_play_lock_in.csv`). A language
# model has no starting weight to set, so the equivalent lever is what it is
# told about the round before the first: an opening the pair inherits rather
# than chooses. The question is whether talking lets them leave it.
LOCK_IN_OPENINGS = ["mutual_cooperation", "mutual_defection"]


def player_seed(base, condition, model, repetition, seat):
    """A seed unique to one seat in one match.

    Both seats of a self-play match must differ or the two sides are the same
    player twice, which is the degeneracy `panel_config.TEMPERATURE` exists to
    avoid. Derived rather than random so a rerun of one cell reproduces it, and
    derived with blake2b rather than `hash()` because Python salts string
    hashing per process: `hash()` here would give a different seed on every run
    and quietly cost the reproducibility this function exists to provide.
    """
    key = f"{base}|{condition}|{model}|{repetition}|{seat}".encode()
    return int.from_bytes(hashlib.blake2b(key, digest_size=4).digest(), "big")
