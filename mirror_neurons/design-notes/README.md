# Design notes

Two decisions that have to be made before the mirror-neuron agent can be tested
against anything, written down here rather than settled silently in code.

| | |
|---|---|
| [`opponents-and-games.md`](opponents-and-games.md) | Which games and which opponents, and where each one comes from in the internship's own literature |
| [`what-the-agent-cannot-do.md`](what-the-agent-cannot-do.md) | The two places the model does not reach, and the choices that would extend it |

The short version: the iterated Prisoner's Dilemma needs no modelling decision
at all and is ready to run. The Ultimatum and Dictator games need one, because
the agent's action set is binary and theirs is not.
