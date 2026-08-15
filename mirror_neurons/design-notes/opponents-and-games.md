# The games, and the opponents

Everything here is named in the internship itself. The report's conceptual frame
(§2.1 of [`RapportDeStageFinal.pdf`](../../original/RapportDeStageFinal.pdf))
defines the games, and the three papers it reviews supply the protocols.

## The games

| Game | Where it comes from |
|---|---|
| Prisoner's Dilemma, iterated | §2.1.2(c). Ng (2023), repeated static with cheap talk between rounds, four partner conditions. Sandholm and Crites (1996) and Wang et al. (2018) in the supplementary reading |
| Prisoner's Dilemma, sequential | §2.1.2(b). Bauer et al. (2023), the strategy method, GPT-3.5 and GPT-4 as second mover |
| Ultimatum | §2.1.3 and §2.3.2. Özkes et al. (2024): 100 points, a minimum acceptable offer, partner types HU, MA, OA and NA |
| Dictator | The defence slides, via Horton's homo silicus replications |

The 5x5 undercutting game is not here. That was the Prolog course project, it
does not appear in the report, and it has moved to
[University-Coursework](https://github.com/Tewf/University-Coursework/tree/main/Bachelor/SecondSemestreLanguage/Prolog/StrategyTournament).

## The opponents

The rerun plays three fixed policies: always cooperate, always defect, and a
coin flip. That is the recorded gap. None of them reacts, so nothing the agent
does changes what it faces, and the folder README already says resembling a
human is never tested.

[Axelrod-Python](https://github.com/Axelrod-Python/Axelrod) 4.14.0 supplies the
rest, MIT licensed, with over 200 strategies from the literature and the
tournament engine and payoff bookkeeping to go with them. Nothing below is
written here.

| Opponent | Why it is in the set |
|---|---|
| `TitForTat` | The behaviour the whole model predicts should emerge. Playing against it is the sharpest test: an imitator facing an imitator |
| `Defector`, `Cooperator` | The rerun's own two fixed policies, so the new results can be read against the committed figures |
| `Random` | The rerun's coin flip |
| `Grudger` | §2.1.2(c) names grim trigger beside tit-for-tat as a reciprocity strategy that sustains cooperation |
| `WinStayLoseShift` | Pavlov. Reacts to payoff rather than to the opponent's action, which is exactly what this agent cannot do |
| `Alternator` | A pattern no imitator can track, since imitating the last action is always wrong against it |

`Grudger` and `WinStayLoseShift` are the two that should separate imitation from
reciprocity. A tit-for-tat that emerges from imitation is indistinguishable from
a programmed one until the opponent does something that only a payoff-reading or
memory-carrying strategy responds to.

## What to measure

Cooperation rate and score come free from Axelrod. The one that matters is not
in the library: how close the agent's play is to Tit-for-Tat, measured as the
share of rounds in which its action equals the opponent's previous action. The
report claims that as the learning rate grows the agent approaches Tit-for-Tat.
That is a measurable claim and it has never been measured.
