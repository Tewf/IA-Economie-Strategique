# AI & Strategic Pricing — GAEL research internship

> [Lire en français](README.fr.md)

Does artificial intelligence make firms *more* or *less* likely to collude?

This repository holds the work from a research internship at **GAEL**
(Grenoble Applied Economics Laboratory, UGA / INRAE), studying whether
artificial agents sustain cooperative behaviour in repeated price-competition
games — the setting where tacit collusion emerges among humans.

| | |
|---|---|
| **Intern** | Mohamed Hamlil, L2 MIASHS, Université Grenoble Alpes |
| **Supervisors** | Alexis Garapin (UGA) and Olivier Bonroy (INRAE) |
| **Laboratory** | GAEL — Grenoble Applied Economics Laboratory |
| **Period** | 23 January – 14 April 2025 |

## The question

In repeated price competition, human players often converge on tacitly
collusive prices rather than the competitive equilibrium. If pricing is
delegated to algorithms, does that tendency survive, disappear, or intensify?
The internship approached this from three directions: the experimental
economics literature, a theoretical model of imitation, and a working agent.

## Contents

| Path | What it is |
|---|---|
| [`RapportDeStageFinal.pdf`](RapportDeStageFinal.pdf) | **The internship report** — start here |
| [`Presentation.pdf`](Presentation.pdf) | Slides from the defence |
| [`Litterature/`](Litterature/) | Annotated bibliography, plus my reading notes in `Summary/` on four of the papers |
| [`Neurones_Mirroirs/`](Neurones_Mirroirs/) | Mirror neurons as a mechanism for imitative and cooperative behaviour — write-up and a Jupyter implementation |
| [`Projet_Prolog/`](Projet_Prolog/) | A Prolog agent for a repeated competitive game, pitted against other students' agents in a tournament, plus a study of which strategic equilibrium behaviour converges to |

The Prolog agent was a semester project run in parallel; it is kept here because
it is the applied counterpart to the internship's theoretical question — what
strategy an artificial agent actually settles on when it is trying to maximise
its own payoff against others doing the same.

## Credits

Published papers cited in [`Litterature/`](Litterature/README.md) are referenced
rather than redistributed, and the Prolog project brief belongs to its course.
See [NOTICE](NOTICE).
