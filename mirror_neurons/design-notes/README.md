# Design notes

The decisions behind the tournament, written down here rather than settled
silently in code, and the detail the folder README links out to rather than
carrying.

| | |
|---|---|
| [`how-the-tournament-runs.md`](how-the-tournament-runs.md) | The round robin itself: how many players, how long, how often, what the payoffs are and what the ranking is over |
| [`the-closed-form.md`](the-closed-form.md) | The algebra the whole result rests on, and the three consequences the recursion hides |
| [`opponents-and-games.md`](opponents-and-games.md) | Which games and which opponents, and where each comes from in the internship's own literature |
| [`what-the-agent-cannot-do.md`](what-the-agent-cannot-do.md) | The two places the model does not reach, sorted by what the agent has to observe |
| [`measuring-reciprocity.md`](measuring-reciprocity.md) | Why the first measure was retired, and the two ways its replacement can still mislead |
| [`saturation.md`](saturation.md) | Why the agent stops responding, and why that makes its ranking climb with match length |
| [`what-the-rerun-corrected.md`](what-the-rerun-corrected.md) | What was wrong with the original simulation, and the claims it does not support |

The short version: the iterated Prisoner's Dilemma needs no modelling decision
at all and is what ran. Ultimatum needs one, because an offer is a number with
no metric on it and imitation across neighbouring offers is undefined. The
Dictator game needs none, because the agent is mute there: nobody acts for it to
observe, so its weights never move at all.
