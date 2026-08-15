"""Refuse to publish numbers until the things they rest on are shown to work.

Both checks here failed at some point during this folder's history, and both
failed quietly. A measure that scores a constant cooperator as a perfect
reciprocator still produces a full CSV, and an agent that arrives at its second
match already trained by its first still produces a plausible ranking. Neither
announces itself, so the run asserts them instead.
"""

import axelrod as axl

from axelrod_player import MirrorNeuronPlayer
from measurements import PROBER, measure_against
from tournament_config import GAME, SEED

# Reciprocity by construction: Tit-for-Tat replays the last round, and none of
# the constant players reads it at all.
KNOWN_RECIPROCITY = {axl.TitForTat: 1.0, axl.Cooperator: 0.0, axl.Defector: 0.0}

# A coin flip is only near zero, never exactly, since it is estimated from a
# finite match.
COIN_FLIP_TOLERANCE = 0.1


def the_measure_scores_known_players_correctly():
    """Stop unless players with known reciprocity measure as themselves.

    If any of these is wrong the measure is wrong, and nothing computed with it
    means anything.
    """
    for strategy, target in KNOWN_RECIPROCITY.items():
        measured, _ = measure_against(strategy(), PROBER)
        assert abs(measured - target) < 1e-9, (
            f"{strategy.name} measured {measured}, expected {target}")
    coin_flip, _ = measure_against(axl.Random(), PROBER)
    assert abs(coin_flip) < COIN_FLIP_TOLERANCE, (
        f"Random measured {coin_flip}, expected near 0")


def the_agent_is_fresh_in_every_match():
    """Stop unless Axelrod hands each match an untrained agent.

    The weight is the agent's whole memory, so a player carried between matches
    would arrive already trained by the previous opponent and every score after
    the first would be measuring the wrong thing. Axelrod resets players through
    `init_kwargs`, which this wrapper has to populate correctly to inherit.
    """
    player = MirrorNeuronPlayer()
    starting_weight = player.agent.weights["Cooperate"]
    axl.Match((player, axl.Defector()), turns=50, game=GAME, seed=SEED).play()
    assert player.agent.weights["Cooperate"] < starting_weight, (
        "the agent did not learn, so this check proves nothing")
    player.reset()
    assert player.agent.weights["Cooperate"] == starting_weight, (
        "the agent kept its weights across a reset, so tournament scores after "
        "the first match are measuring a pre-trained agent")


def run_all():
    the_measure_scores_known_players_correctly()
    the_agent_is_fresh_in_every_match()
