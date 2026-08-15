# How the tournament runs

A round robin: eight players, the agent and
[seven opponents from the literature](opponents-and-games.md), each meeting
every other **and itself** over **100 turns**, repeated **20 times** because two
of the eight draw their moves at random, this agent and the coin flip, so a
single pass would be one sample.

Payoffs are Axelrod's standard Prisoner's Dilemma: **3 each for mutual
cooperation, 1 each for mutual defection, 5 for defecting on a cooperator and 0
for being defected on.** That is also what
[the LLM prompt](../../llm/prompts/prisoners_dilemma.md) states, so a language
model and this agent play the same game and their numbers can be read together.

A player is ranked by its **median score per turn across all its matches**, so
the ranking rewards holding up against the whole field rather than beating any
one opponent. That distinction does real work here: Defector wins the most
individual matches, seven of them, and still places third, while Tit-for-Tat
wins none and places first. The agent wins one and places last.

Every match starts the agent fresh, with its opening weights and no memory of
the previous opponent. [`../preflight_checks.py`](../preflight_checks.py)
asserts that before any result is written, because the weight is the agent's
whole memory and one carried between matches would be scored on training it got
from somebody else.

The settings and the seed are in
[`../tournament_config.py`](../tournament_config.py), which is the only place
they are written down. Match length is the one setting worth changing
deliberately rather than accepting, and
[`saturation.md`](saturation.md) is what happens when you do.
