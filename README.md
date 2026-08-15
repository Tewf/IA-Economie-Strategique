# AI & Strategic Pricing: GAEL research internship

[![CI](https://github.com/Tewf/IA-Economie-Strategique/actions/workflows/ci.yml/badge.svg)](https://github.com/Tewf/IA-Economie-Strategique/actions/workflows/ci.yml)
[![Live pages](https://img.shields.io/badge/pages-tewf.github.io%2FIA--Economie--Strategique-1f6feb)](https://tewf.github.io/IA-Economie-Strategique/)

> [Lire en français](README.fr.md)

> [!TIP]
> **Readable as a site:
> [tewf.github.io/IA-Economie-Strategique](https://tewf.github.io/IA-Economie-Strategique/)**
> The findings and figures on one page, with the report and slides opening in
> the browser rather than downloading.

In repeated price competition, human players tend to converge on tacitly
collusive prices rather than on the competitive equilibrium. Whether algorithms
sustain that behaviour, break it, or intensify it is an open question in
industrial economics, and one with direct consequences for competition policy.

A research internship at **GAEL** (Grenoble Applied Economics Laboratory,
UGA / INRAE) spent on that question: surveying where the literature stands,
modelling the imitation mechanism that might underpin cooperation, and building
agents to watch it happen.

**The internship did not settle the question**, and its report is a study rather
than a finding. What it did produce is below, with the numbers it actually
reached.

| | |
|---|---|
| **Intern** | L2 MIASHS, Université Grenoble Alpes |
| **Supervisors** | Alexis Garapin (UGA) and Olivier Bonroy (INRAE) |
| **Laboratory** | GAEL, Grenoble Applied Economics Laboratory |
| **Dates** | 23 January to 14 April 2025 |

## The internship, as delivered

Everything submitted in May 2025 sits in [`original/`](original/), byte for
byte. Nothing in there has been edited, including what is wrong with it, which
[that folder records](original/README.md) rather than quietly repairing.

| | |
|---|---|
| [`RapportDeStageFinal.pdf`](original/RapportDeStageFinal.pdf) | The report, nine pages. Start here |
| [`Presentation.pdf`](original/Presentation.pdf) | The defence slides, 23 pages |
| [`Litterature/`](original/Litterature/) | The state of the art, as summaries written from the papers rather than the papers themselves |
| [`Neurones_Mirroirs/`](original/Neurones_Mirroirs/) | Mirror neurons as a mechanism for imitative cooperation, write-up and simulation |

## What came after, in my own time

The internship ended in April 2025. Two folders continue the report rather than
starting something else, and both play the report's own games: the Prisoner's
Dilemma iterated and sequential, the Ultimatum game from Özkes et al. (2024),
and the Dictator game from the defence slides.

| | |
|---|---|
| <img src="mirror_neurons/results/standings.png" width="320" alt="The imitating agent finishes eighth of eight"> | **[`mirror_neurons/`](mirror_neurons/), run and reported.** Observing an action multiplies its weight and renormalises, and the report expects Tit-for-Tat to fall out of that without being programmed. Given seven opponents from the literature, **it does not: over matches of 10 to 100 turns the agent finishes eighth of eight, behind a coin flip.** What the update implements is frequency matching, whose state is a pair of counts and so cannot depend on the last round at all. It passes the coin flip only in matches of several hundred turns, by freezing into a constant player rather than by reciprocating. |
| | **[`llm/`](llm/), scaffolding.** Homo silicus, which the report cites in its conclusion without ever running. Five open-weight models, locally and offline, on the same games. Nothing has been run yet. |

**On the question at the top of this page**, the mirror-neuron mechanism
sustains tacit cooperation and neither breaks nor intensifies it. Two imitators
are a feedback loop with two absorbing states and nothing in between: over 700
runs they locked onto mutual defection or mutual cooperation according to where
they started, and not once onto anything else. Imitation is a ratchet on the
initial condition rather than a route to collusion, which is what separates it
from the Q-learners of Calvano et al. (2020) that do find collusion, and read
payoffs to do it. [The full reading](mirror_neurons/#what-it-adds-up-to),
including what would change it.

The two folders are siblings on purpose. Both players expose the same two calls,
so one harness can seat either, and the interesting comparison is between a
mechanism that can only imitate and one that can also talk and explain itself.
Cheap talk and explainability are two of the eight terms the report defines, and
they are the two the Hebbian agent has no way to reach.

An equilibrium analysis used to sit here too. It went with the Prolog course
project whose game it is about, in
[University-Coursework](https://github.com/Tewf/University-Coursework/tree/main/Bachelor/SecondSemestreLanguage/Prolog/StrategyTournament).
That game does not appear in the internship report.

## Credits

Published papers are referenced rather than redistributed. See
[NOTICE](original/NOTICE), which is the one submitted with the internship and is
kept unedited, so it still lists the Prolog course project that has since moved
out of this repository.

One gap worth naming: Ng (2023), *When communicative AIs are cooperative
actors*, is summarised in `original/Litterature/Summary/` and analysed in the
report, but does not appear in that folder's bibliography. The bibliography lists
nine papers; this is a tenth.
