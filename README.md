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

The internship ended in April 2025. The mirror-neuron simulation could not be
run from top to bottom, so it is redone beside `original/` rather than over it.

| | |
|---|---|
| <img src="mirror_neurons/update_shape.png" width="300" alt="The weight update is logistic"> | **[Imitation as a weight update](mirror_neurons/)**. Observing an action multiplies its weight and renormalises, and Tit-for-Tat falls out without being programmed. Six figures, rerun and seeded. |

It does not overturn what the internship concluded. What changed is that the
claims the code does not support are named, and the figures carry the labels
they were computing and throwing away.

An equilibrium analysis used to sit here too. It went with the Prolog course
project whose game it is about, in
[University-Coursework](https://github.com/Tewf/University-Coursework/tree/main/Bachelor/SecondSemestreLanguage/Prolog/StrategyTournament).
That game does not appear in the internship report.

## What is being built now

Two folders, both continuing the report rather than starting something else.
**Scaffolding at this stage: no experiment has been run and no result is
committed.**

| | |
|---|---|
| [`mirror_neurons/`](mirror_neurons/) | The agent given opponents that react. It currently plays three fixed policies, one of them a coin flip, which the folder already records as the reason resembling a human is never tested. [Axelrod](https://github.com/Axelrod-Python/Axelrod) supplies Tit-for-Tat, Grudger, Pavlov and the rest from the literature, and the claim being tested is the report's own: that Tit-for-Tat emerges from imitation without being programmed |
| [`llm/`](llm/) | Homo silicus. The report cites Horton, Filippas and Manning (2023) and names the method in its conclusion without running it. Five open-weight models, run locally and offline, playing the games the report's own frame defines |

The two are siblings on purpose. Both players expose the same two calls, so one
harness can seat either, and the interesting comparison is between a mechanism
that can only imitate and one that can also talk and explain itself. Cheap talk
and explainability are two of the eight terms the report defines, and they are
the two the Hebbian agent has no way to reach.

The games are the report's: the Prisoner's Dilemma in its iterated and
sequential forms, the Ultimatum game from Özkes et al. (2024), and the Dictator
game from the defence slides. Nothing outside what the internship actually
studied has been added.

## Credits

Published papers are referenced rather than redistributed. See
[NOTICE](original/NOTICE), which is the one submitted with the internship and is
kept unedited, so it still lists the Prolog course project that has since moved
out of this repository.

One gap worth naming: Ng (2023), *When communicative AIs are cooperative
actors*, is summarised in `original/Litterature/Summary/` and analysed in the
report, but does not appear in that folder's bibliography. The bibliography lists
nine papers; this is a tenth.
