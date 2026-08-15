# The equilibrium, recomputed

![The match, and what it cost](equilibrium_comparison.png)

Corrects the analysis in
[`../original/Projet_Prolog/Convergence des stratégies dans un jeu répété/`](../original/Projet_Prolog/).
The original is preserved untouched and nothing here edits it.

```sh
pip install -r requirements.txt
jupyter execute equilibrium_recomputed.ipynb
```

## The conclusion still stands

`stage_test` does outscore the Nash equilibrium when the two play each other.
Recomputed independently here, it reproduces the original exactly:

| | payoff in that match |
|---|---|
| `stage_test` | **3.5552** |
| Nash | 3.1521 |

That is not a surprise once stated properly. Nash is a **safety** concept: it
guarantees a floor against any opponent. It is not a maximising one. A strategy
aimed at a known opponent should beat it head to head, and give ground
elsewhere, which is exactly the pattern in the original's own comparison table.

## What the original got wrong was the derivation

It minimised the sum of squared payoff gradients, commented *"zero at a
stationary (Nash) point"*. On a simplex that is the wrong condition. Player 1's
payoff is linear in their own strategy, so the gradient is constant, and it is
never zero unless every action pays zero. **Minimising its norm searches for the
strategies that pay least.**

The right condition is that the payoff vector is flat across the actions
actually played, with nothing unplayed paying more. Equivalently the regret
`max_i (A y)_i − x'A y` is zero for both players.

Two things follow, both visible in the original's own committed output:

- It printed `Stationarity residual: 80.89` directly under a success tick. It
  checked only that the optimiser converged, never that the objective reached
  zero, which was its own stated criterion.
- On Battle of the Sexes it returned a point that is **none** of the three
  equilibria and pays both players 0.48, against 2.0, 1.0 and 0.667 for the real
  ones. It got the Prisoner's Dilemma right, but only because mutual defection
  is also the lowest-paying cell there, which is what its objective was seeking.

The notebook checks against both textbook games before touching the 5x5, which
is the step that would have caught this.

## One distinction worth drawing

Outscoring an opponent is not the same as maximising your own payoff. Against a
Nash opponent, playing Nash earns **3.8889**, while `stage_test` earns **3.5552**.
It wins the match by costing the opponent more than it costs itself.

That is a reasonable thing to want in a head-to-head and the wrong thing to want
in a tournament scored on cumulative points, which is consistent with where
these agents placed: 7th and 8th of 16, with the winners orders of magnitude
ahead.

## The stated definition, implemented

The write-up defines the target as maximising your own payoff given that the
opponent maximises theirs. That is not Nash, where both optimise at once; it is
the Stackelberg family, where one side moves first and the other best-responds.

It needs no optimiser. The follower's best response to a fixed leader strategy
is a pure action, so enumerate which action it is and solve one linear program
per case. Here the leader's best play turns out to be the Nash strategy itself,
earning **5.0000** instead of 3.8889.

The gain comes entirely from the follower being indifferent between actions 3, 4
and 5 at that point, and this assumes the tie breaks in the leader's favour,
which is the optimistic convention. Under the pessimistic one the leader takes
the worst of the three, so 5.0 is an upper bound rather than a guarantee.
