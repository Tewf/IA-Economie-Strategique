# The update in closed form

The recursion looks stateful and is not. Observing an action multiplies its
weight by `1 + eta` and renormalises, and renormalising scales both weights by
the same total, so it cancels in their ratio. In terms of the odds
`r = w_C / w_D`, observing a cooperation is exactly `r <- r * (1 + eta)` and
observing a defection divides by the same factor. Taking logs, the log-odds move
by a constant step per observation, so after `n_C` cooperations and `n_D`
defections seen **in any order**:

```
w_i  proportional to  w_i(0) * (1 + eta) ** n_i
```

The derivation and both checks are in the last cells of
[`../mirror_neurons_rerun.ipynb`](../mirror_neurons_rerun.ipynb): the closed form
matches the recursion to **1.1e-16** over 200 observations, and reshuffling the
same observations lands on identical weights to the same precision.

Three consequences, none of them visible from the recursion:

1. **The agent's entire state is a pair of counts.** The order it saw them in
   cannot affect what it does next. Tit-for-Tat is a function of the last round
   alone, so this rule has no way to represent it, whatever its parameters.
2. **The trajectory is logistic by construction**, not by observation. The
   figure in the notebook draws a curve the algebra already fixes, which is what
   [`what-the-rerun-corrected.md`](what-the-rerun-corrected.md) is about.
3. **`eta = sqrt(2) - 1` finally means something.** It makes `1 + eta` equal
   `sqrt(2)`, so the odds double every two net observations. That is the only
   reading found under which the constant is a choice rather than an arbitrary
   number, and it is still not the empirical grounding the report claims.

Naming it: weights exponential in a count, normalised, is a **Boltzmann
distribution over observation counts** at inverse temperature `log(1 + eta)`.
That is the multiplicative-weights family of **Cesa-Bianchi, Gentile and Lugosi
(2017)**, which is reference 4 of
[`../../original/Litterature/`](../../original/Litterature/) and is never cited
in the report that needed it.

It also generalises to any number of actions unchanged, which is why the obstacle
to the other games is not the size of the action set but what the agent has to
observe. That is [`what-the-agent-cannot-do.md`](what-the-agent-cannot-do.md).
