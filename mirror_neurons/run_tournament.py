"""Run the tournament and write every number the write-up quotes.

Argument-free, so one command reproduces the whole of `results/`:

    python run_tournament.py

It is self-checking. Before it writes anything it measures players whose
reciprocity is known by construction, and stops if the measure disagrees with
them. A number that survives that is worth putting in a README; one that does
not would otherwise be quoted for months. CI runs this and then asks git
whether any CSV moved, which is the check the committed figures never had.

Every float is written to six decimals so two runs give byte-identical files.
"""

import csv
import pathlib

import axelrod as axl

from axelrod_player import MirrorNeuronPlayer
from reciprocity import agreement_rate, reciprocity_index
from tournament_config import (DEFAULT_LEARNING_RATE, GAME, LEARNING_RATES,
                               OPPONENTS, REPETITIONS, SEED, TURNS)

RESULTS = pathlib.Path(__file__).parent / "results"

# Reciprocity is a conditional probability, so it needs an opponent that plays
# both actions. Random is the only prober in the opponent set that does, and 400
# turns keeps the rarer condition from resting on a handful of rounds.
PROBER = axl.Random
PROBE_TURNS = 400

# Reciprocity against a plain Cooperator is undefined, since the condition
# "after the opponent defected" never occurs. The naive measure returns 1.0 there
# for reciprocators and non-reciprocators alike, which is the demonstration that
# it measures convergence, so both probers are reported.
PROBERS = [PROBER, axl.Cooperator]

# Long enough for the last round's share of the evidence to shrink by an order
# of magnitude, in windows wide enough for each condition to clear
# MINIMUM_SUPPORT comfortably.
DECAY_TURNS = 2000
DECAY_WINDOW = 200


def write_csv(name, header, rows):
    """One tidy CSV, with a fixed line terminator so CI can diff it."""
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / name, "w", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def formatted(value):
    """Six decimals, so a rerun on another machine produces the same bytes."""
    return f"{value:.6f}"


def measure_against(player, prober, turns=PROBE_TURNS, seed=SEED):
    """Both measures for one player facing one prober, from a single match."""
    match = axl.Match((player, prober()), turns=turns, game=GAME, seed=seed)
    match.play()
    mine, theirs = match.result and zip(*match.result)
    return (reciprocity_index(list(mine), list(theirs)),
            agreement_rate(list(mine), list(theirs)))


def check_the_measure_before_using_it():
    """Stop unless players with known reciprocity measure as themselves.

    Tit-for-Tat is reciprocity 1.0 by definition. A constant player and a coin
    flip are 0.0, because none of them reads what the opponent just did. If any
    of these is wrong the measure is wrong, and nothing below it means anything.
    """
    expected = {axl.TitForTat: 1.0, axl.Cooperator: 0.0, axl.Defector: 0.0}
    for strategy, target in expected.items():
        measured, _ = measure_against(strategy(), PROBER)
        assert abs(measured - target) < 1e-9, (
            f"{strategy.name} measured {measured}, expected {target}")
    coin_flip, _ = measure_against(axl.Random(), PROBER)
    assert abs(coin_flip) < 0.1, f"Random measured {coin_flip}, expected near 0"


def check_the_agent_resets_between_matches():
    """Stop unless Axelrod hands each match a fresh agent.

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


def standings():
    """The full tournament, every player against every player.

    Axelrod's summary names a player by its repr, which carries the parameters
    it was built with, so the agent would land in the CSV as "Mirror Neuron:
    0.41421356237309515, 0.8". A float repr inside a data column moves whenever
    a default changes and puts a comma in a field, so the class names are put
    back here.
    """
    players = [MirrorNeuronPlayer()] + [strategy() for strategy in OPPONENTS]
    plain_name = {str(player): player.name for player in players}
    results = axl.Tournament(players, game=GAME, turns=TURNS,
                             repetitions=REPETITIONS, seed=SEED
                             ).play(progress_bar=False)
    return [(row.Rank + 1, plain_name.get(row.Name, row.Name),
             formatted(row.Median_score),
             formatted(row.Cooperation_rating), formatted(row.Wins))
            for row in results.summarise()]


def reciprocity_decay():
    """Where the little reciprocity the agent has actually comes from.

    The closed form says the weight depends on how many of each action the agent
    has seen and never on their order, so the round just played can only reach
    the next action through the single count it increments. Its share of the
    evidence is one part in n, and it falls as the match runs. Tit-for-Tat's
    dependence on the last round is 1 whatever n is, which is the difference
    these windows measure.
    """
    rows = []
    for name, player in (("Mirror Neuron", MirrorNeuronPlayer()),
                         ("Tit For Tat", axl.TitForTat())):
        match = axl.Match((player, PROBER()), turns=DECAY_TURNS, game=GAME,
                          seed=SEED)
        match.play()
        mine, theirs = (list(side) for side in zip(*match.result))
        for start in range(0, DECAY_TURNS, DECAY_WINDOW):
            window = slice(start, start + DECAY_WINDOW)
            rows.append((name, start, start + DECAY_WINDOW,
                         formatted(reciprocity_index(mine[window],
                                                     theirs[window]))))
    return rows


def head_to_head():
    """The agent against each opponent on its own, which the ranking hides."""
    rows = []
    for index, strategy in enumerate(OPPONENTS):
        match = axl.Match((MirrorNeuronPlayer(), strategy()), turns=TURNS,
                          game=GAME, seed=SEED + index)
        match.play()
        mine, theirs = (list(side) for side in zip(*match.result))
        agent_score, opponent_score = match.final_score_per_turn()
        rows.append((strategy.name, formatted(agent_score),
                     formatted(opponent_score),
                     formatted(sum(a == axl.Action.C for a in mine) / len(mine)),
                     formatted(sum(a == axl.Action.C for a in theirs) / len(theirs)),
                     formatted(reciprocity_index(mine, theirs)),
                     formatted(agreement_rate(mine, theirs))))
    return rows


def reciprocity_table():
    """Every player under both measures, against both probers."""
    players = [MirrorNeuronPlayer] + list(OPPONENTS)
    rows = []
    for prober in PROBERS:
        for strategy in players:
            index, naive = measure_against(strategy(), prober)
            rows.append((strategy.name, prober.name,
                         formatted(index), formatted(naive)))
    return rows


def learning_rate_sweep():
    """Does the agent get closer to Tit-for-Tat as the learning rate grows?

    That is the report's claim, and the closed form says no: the weight depends
    on how many of each action it has seen, never on their order, so no value of
    the learning rate can make the action depend on the previous round.
    """
    rows = []
    for eta in sorted(set(LEARNING_RATES + [DEFAULT_LEARNING_RATE])):
        index, naive = measure_against(MirrorNeuronPlayer(learning_rate=eta),
                                       PROBER)
        match = axl.Match((MirrorNeuronPlayer(learning_rate=eta), PROBER()),
                          turns=PROBE_TURNS, game=GAME, seed=SEED)
        match.play()
        mine = [pair[0] for pair in match.result]
        rows.append((formatted(eta), formatted(index), formatted(naive),
                     formatted(sum(a == axl.Action.C for a in mine) / len(mine)),
                     formatted(match.final_score_per_turn()[0])))
    return rows


def main():
    check_the_measure_before_using_it()
    check_the_agent_resets_between_matches()
    write_csv("standings.csv",
              ["rank", "player", "median_score", "cooperation_rating", "wins"],
              standings())
    write_csv("head_to_head.csv",
              ["opponent", "agent_score_per_turn", "opponent_score_per_turn",
               "agent_cooperation", "opponent_cooperation",
               "reciprocity_index", "agreement_rate"],
              head_to_head())
    write_csv("reciprocity.csv",
              ["player", "prober", "reciprocity_index", "agreement_rate"],
              reciprocity_table())
    write_csv("learning_rate_sweep.csv",
              ["learning_rate", "reciprocity_index", "agreement_rate",
               "cooperation_rate", "score_per_turn"],
              learning_rate_sweep())
    write_csv("reciprocity_decay.csv",
              ["player", "from_turn", "to_turn", "reciprocity_index"],
              reciprocity_decay())
    print(f"wrote 5 CSVs to {RESULTS}")


if __name__ == "__main__":
    main()
