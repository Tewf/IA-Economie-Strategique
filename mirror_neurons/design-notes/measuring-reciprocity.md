# Measuring reciprocity, after the first measure turned out to measure nothing

The claim under test is the report's: that Tit-for-Tat emerges from imitation
without being programmed. Testing it needs a number that separates
*reciprocating* from merely *agreeing*, and the measure this folder started with
does not.

## What was wrong with the first one

It scored the share of rounds in which a player replayed the opponent's previous
action, and it was called `tit_for_tat_likeness`, which is a claim rather than a
description. Against a plain Cooperator it returns:

| Player | Score |
|---|---:|
| Tit For Tat | 1.000 |
| Cooperator | 1.000 |
| Grudger | 1.000 |
| Win-Stay Lose-Shift | 1.000 |
| Mirror Neuron | 0.997 |

Everything that ends up cooperating scores the same, whether it is reciprocating
or simply agreeing. It measures convergence. It is kept in
[`../reciprocity.py`](../reciprocity.py) as `agreement_rate`, named for what it
computes, and reported beside the real measure so the gap is visible rather than
asserted.

## What replaced it

```
reciprocity = P(cooperate | opponent cooperated last) - P(cooperate | defected last)
```

1.0 is Tit-for-Tat, 0.0 is any player whose action ignores what the opponent just
did, and negative is a player that punishes cooperation.

Three consequences of that definition, each of which changed a number:

**It needs an opponent that plays both actions.** Against a Cooperator the second
condition never occurs and the index is undefined, which is reported as `nan`
rather than as a zero. Zero would read as "never reciprocates" and would turn an
unmeasurable pairing into a measured one. The measurement in
[`../run_tournament.py`](../run_tournament.py) is therefore taken against Random,
over 400 turns.

**A rare condition is not a measured one.** Grudger cooperates until the first
defection and never again, so in a hundred rounds "the round after the opponent
cooperated" happens exactly once. The agent happened to cooperate in it, and the
index came out **0.949**, a near-perfect reciprocator built from one observation.
Conditions with fewer than ten supporting rounds now return `nan`.

**It is memory-one, so it under-reports triggers.** Grudger is genuinely
reciprocal and scores 0.000 against a prober, because its trigger depends on the
whole history rather than on the last round. That is the right measure for the
claim under test, which is about Tit-for-Tat specifically, and it is the wrong
measure for reciprocity in general. The write-up says so rather than presenting
this as a general reciprocity score.

## Why the runner refuses to write without checking

Players whose reciprocity is known by construction are measured first, and
`run_tournament.py` stops before writing anything if they come out wrong:
Tit-for-Tat must score 1.0, a constant cooperator and a constant defector must
score 0.0, and a coin flip must land near 0. A measure that fails those is not
worth the CSVs it would fill, and a number that fails them silently would be
quoted for months.

The same run also checks that Axelrod hands each match a fresh agent. The weight
is the agent's whole memory, so a player carried between matches would arrive
pre-trained by the previous opponent and every score after the first would
describe something else entirely.
