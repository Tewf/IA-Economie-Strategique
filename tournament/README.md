# The tournament

![Sixteen agents, log scale](leaderboard.png)

Two of the agents in [`../original/Projet_Prolog/Code.pl`](../original/Projet_Prolog/)
were entered in Tournoi n° 1, April 2025, L2 MIASHS UGA, against thirteen other
students' agents. The standings are page 1 of the tournament log, which is a
636-page 9 MB PDF, so they are surfaced here.

```sh
python plot_leaderboard.py
```

## Where they placed

| | agent | cumulative score |
|---|---|---|
| 1 | best_duo | 2.02 × 10⁶² |
| 2 | naenae | 2.58 × 10⁵⁷ |
| 3 | youxi | 4.14 × 10⁵⁴ |
| 4 | lesStrateges | 8.88 × 10³² |
| 5 | lesCowBoys | 8.88 × 10³² |
| 6 | syntax_terror | 6.34 × 10²⁹ |
| **7** | **stage_test** | **6,163,877** |
| **8** | **nash_equilibrium** | **1,490,429** |
| 9 to 16 | kAuCarre down to dfy | 177,854 to 5,226 |

Two things are true at once and both matter. `stage_test` beat
`nash_equilibrium`, which is the same ordering the equilibrium analysis predicts.
And both were beaten by six agents, the top three by more than fifty orders of
magnitude.

That is consistent rather than contradictory. A tournament scores **cumulative
points**, and `stage_test` is built to win a head-to-head margin, which it does
by giving up absolute payoff. The [equilibrium analysis](../equilibrium/) shows
the trade directly: against a Nash opponent it earns 3.5552 where simply playing
Nash earns 3.8889. Winning the match and scoring the most points are different
objectives, and this agent optimises the first.

## The agents that competed

The two entrants are the short ones. Both are stateless: they sample from a
fixed distribution and ignore the history entirely.

| agent | what it plays |
|---|---|
| `stage_test` | `[0.03, 0.444, 0.203, 0.323, 0.0]` |
| `nash_equilibrium` | `[0, 0, 4/9, 2/9, 1/3]` |

`khawa_khawa`, the adaptive agent in the same file, is the substantial one: it
estimates the opponent's recent frequencies, models each action as normal via a
central-limit argument, and best-responds against the payoff matrix. **It does
not appear anywhere in the 636-page log.** Searching every page returns 1,825
matches for `stage_test`, 1,833 for `nash_equilibrium` and **zero** for
`khawa_khawa`. It was built alongside the entrants rather than entered, or it
competed under a name the log does not carry.

## The part worth noticing

Both entrants' constants come straight out of
[`Equilibrium_Analysis.ipynb`](../original/Projet_Prolog/), and they match to the
rounding:

| notebook | shipped in `Code.pl` |
|---|---|
| `Fraction(27, 896)` = 0.0301 | `0.03` |
| `Fraction(440, 991)` = 0.4440 | `0.444` |
| `Fraction(101, 497)` = 0.2032 | `0.203` |
| `Fraction(292, 905)` = 0.3227 | `0.323` |
| NashPy's `[0, 0, 4/9, 2/9, 1/3]` | `[0, 0, 0.444, 0.222, 0.333]` |

The analysis and the submitted agent are the same object. That is the strongest
evidence in the repository that the work is joined up end to end, and no README
mentioned it.

## The game

Both players pick an integer from 1 to 5 at the same time. If the picks differ
by exactly one, whoever picked the **smaller** number takes the sum and the other
takes nothing. Otherwise each scores the number they picked. Repeated, highest
cumulative score wins. Undercutting by one is rewarded, so every number invites
being undercut, which is what makes 5 both the greediest pick and the most
exposed.
