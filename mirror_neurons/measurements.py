"""The five tables the write-up quotes, as numbers rather than as text.

Nothing here formats or writes anything. A measurement that returned strings
would have to decide how many decimals a result deserves, which is a question
about the CSV rather than about the agent, and it would make the numbers
awkward to reuse from a notebook. `run_tournament.py` owns the formatting.
"""

import axelrod as axl

from axelrod_player import MirrorNeuronPlayer
from reciprocity import agreement_rate, reciprocity_index
from tournament_config import (DEFAULT_LEARNING_RATE, GAME, LEARNING_RATES,
                               OPPONENTS, REPETITIONS, SEED, TURNS)

# Reciprocity is a conditional probability, so it needs an opponent that plays
# both actions. Random is the only prober in the opponent set that does, and 400
# turns keeps the rarer condition from resting on a handful of rounds.
PROBER = axl.Random
PROBE_TURNS = 400

# Reciprocity against a plain Cooperator is undefined, since the condition
# "after the opponent defected" never occurs. The old measure returns 1.0 there
# for reciprocators and non-reciprocators alike, which is the demonstration that
# it measures convergence, so both probers are reported.
PROBERS = [PROBER, axl.Cooperator]

# Long enough for the last round's share of the evidence to shrink by an order
# of magnitude, in windows wide enough for each condition to clear the support
# floor in `reciprocity.py` comfortably.
DECAY_TURNS = 2000
DECAY_WINDOW = 200


def played(match):
    """One match's two histories, as separate lists."""
    return (list(side) for side in zip(*match.result))


def cooperation_rate(history):
    return sum(action == axl.Action.C for action in history) / len(history)


def measure_against(player, prober, turns=PROBE_TURNS, seed=SEED):
    """Both measures for one player facing one prober, from a single match."""
    match = axl.Match((player, prober()), turns=turns, game=GAME, seed=seed)
    match.play()
    mine, theirs = played(match)
    return reciprocity_index(mine, theirs), agreement_rate(mine, theirs)


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
             row.Median_score, row.Cooperation_rating, row.Wins)
            for row in results.summarise()]


def head_to_head():
    """The agent against each opponent on its own, which the ranking hides."""
    rows = []
    for index, strategy in enumerate(OPPONENTS):
        match = axl.Match((MirrorNeuronPlayer(), strategy()), turns=TURNS,
                          game=GAME, seed=SEED + index)
        match.play()
        mine, theirs = played(match)
        agent_score, opponent_score = match.final_score_per_turn()
        rows.append((strategy.name, agent_score, opponent_score,
                     cooperation_rate(mine), cooperation_rate(theirs),
                     reciprocity_index(mine, theirs),
                     agreement_rate(mine, theirs)))
    return rows


def reciprocity_table():
    """Every player under both measures, against both probers."""
    players = [MirrorNeuronPlayer] + list(OPPONENTS)
    return [(strategy.name, prober.name, *measure_against(strategy(), prober))
            for prober in PROBERS for strategy in players]


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
        mine, _ = played(match)
        rows.append((eta, index, naive, cooperation_rate(mine),
                     match.final_score_per_turn()[0]))
    return rows


"""Match lengths to sweep. 20 is the horizon most of the report's own reading
sits at, and 500 is long enough for the agent to have frozen against almost
every opponent."""
MATCH_LENGTHS = [5, 10, 20, 50, 100, 200, 500]


def match_length_sweep():
    """Whether finishing last survives changing how long a match is.

    It does not, and the reversal is the point. The agent saturates into a
    constant player, and a constant is worth more than a coin flip against a
    field full of reciprocators, so its ranking improves with length for a
    reason that has nothing to do with reciprocating.
    """
    rows = []
    for turns in MATCH_LENGTHS:
        players = [MirrorNeuronPlayer()] + [s() for s in OPPONENTS]
        plain_name = {str(player): player.name for player in players}
        results = axl.Tournament(players, game=GAME, turns=turns,
                                 repetitions=REPETITIONS, seed=SEED
                                 ).play(progress_bar=False)
        ranked = {plain_name.get(row.Name, row.Name): (row.Rank + 1,
                                                       row.Median_score)
                  for row in results.summarise()}
        agent_rank, agent_score = ranked["Mirror Neuron"]
        random_rank, random_score = ranked["Random"]
        rows.append((turns, agent_rank, agent_score, random_rank, random_score))
    return rows


def reciprocity_decay():
    """Where the little reciprocity the agent has actually comes from.

    The closed form says the round just played reaches the next action through
    the single count it increments. Its share of the evidence is one part in n,
    and it falls as the match runs. Tit-for-Tat's dependence on the last round
    is 1 whatever n is, which is the difference these windows measure.
    """
    rows = []
    for name, player in (("Mirror Neuron", MirrorNeuronPlayer()),
                         ("Tit For Tat", axl.TitForTat())):
        match = axl.Match((player, PROBER()), turns=DECAY_TURNS, game=GAME,
                          seed=SEED)
        match.play()
        mine, theirs = played(match)
        for start in range(0, DECAY_TURNS, DECAY_WINDOW):
            window = slice(start, start + DECAY_WINDOW)
            rows.append((name, start, start + DECAY_WINDOW,
                         reciprocity_index(mine[window], theirs[window])))
    return rows
