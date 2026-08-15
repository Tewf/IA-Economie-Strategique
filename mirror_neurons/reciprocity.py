"""How reciprocity is measured, and why the obvious measure does not work.

The claim under test is the report's own: that Tit-for-Tat emerges from
imitation without being programmed. Testing it needs a number that separates
*reciprocating* from merely *agreeing*, and the measure this folder started with
does not. It scored the share of rounds in which a player replayed the
opponent's previous action, which a constant cooperator satisfies perfectly
against a cooperative opponent while reciprocating nothing. That measure is kept
below as `agreement_rate`, named for what it computes rather than for what it
was once thought to compute, and it is reported beside the real one so the
difference is visible rather than asserted.

Both take two equal-length histories of Axelrod `Action` values and read only
the last round, so both are memory-one measures. That is right for the claim
under test, which is about Tit-for-Tat, and it under-reports trigger strategies:
Grudger is genuinely reciprocal and scores near zero here because its trigger
depends on the whole history. The write-up says so rather than presenting this
as a general reciprocity score.
"""

from axelrod.action import Action

UNDEFINED = float("nan")

# Both halves of the index are conditional probabilities, and one of them can
# rest on almost nothing. Against Grudger, which cooperates until the first
# defection and never again, "the round after the opponent cooperated" happens
# exactly once in a hundred: the agent happened to cooperate in it, and the
# index came out 0.949, a near-perfect reciprocator built from one observation.
# Below this many rounds the condition is not estimated, it is guessed.
MINIMUM_SUPPORT = 10


def _cooperation_rate_after(player_history, opponent_history, previous):
    """How often the player cooperated in the round after `previous` was played.

    Returns NaN when the opponent played `previous` fewer than
    `MINIMUM_SUPPORT` times, because the conditional probability is then not
    measurable from this match. Returning zero there would read as "never
    cooperates" and quietly turn an unmeasurable pairing into a measured one,
    which is how a cooperative opponent ends up scoring as a non-reciprocator.
    """
    followed = [mine for mine, theirs
                in zip(player_history[1:], opponent_history[:-1])
                if theirs == previous]
    if len(followed) < MINIMUM_SUPPORT:
        return UNDEFINED
    return sum(action == Action.C for action in followed) / len(followed)


def reciprocity_index(player_history, opponent_history):
    """P(cooperate | opponent cooperated last) minus P(cooperate | defected last).

    1.0 is Tit-for-Tat, 0.0 is any player whose action ignores what the opponent
    just did, whether it always cooperates, always defects or flips a coin.
    Negative is a player that punishes cooperation.

    NaN when the opponent never varied, which is why the measurement in
    `run_tournament.py` is taken against a probing opponent rather than against
    the whole tournament.
    """
    if len(player_history) < 2:
        return UNDEFINED
    after_cooperation = _cooperation_rate_after(
        player_history, opponent_history, Action.C)
    after_defection = _cooperation_rate_after(
        player_history, opponent_history, Action.D)
    return after_cooperation - after_defection


def agreement_rate(player_history, opponent_history):
    """Share of rounds where the player replayed the opponent's previous action.

    The measure this folder started with, under its former name
    `tit_for_tat_likeness`. It is reported only as a labelled comparator: it
    scores 1.0 for Tit-for-Tat, and also 1.0 for a constant cooperator facing a
    cooperative opponent, so it measures convergence rather than reciprocity.
    The first round is excluded, having no previous action to match.
    """
    if len(player_history) < 2:
        return UNDEFINED
    matched = sum(mine == theirs for mine, theirs
                  in zip(player_history[1:], opponent_history[:-1]))
    return matched / (len(player_history) - 1)
