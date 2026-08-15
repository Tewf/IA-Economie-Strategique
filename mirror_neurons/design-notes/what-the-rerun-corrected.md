# What the rerun corrected, before any opponent reacted

The simulation in [`../../original/Neurones_Mirroirs/`](../../original/Neurones_Mirroirs/)
is preserved untouched. It could not be run from top to bottom, so it was redone
beside it rather than over it. This is the list, kept because a reader who opens
the original should know what was wrong with it and what was left alone.

| | |
|---|---|
| The last cell was `while(True)` around `input()` | Any run-all hung there forever. It is a scripted exchange now |
| Three of five figures had no `legend()` | They computed a per-curve `eta` label and then discarded it, rendering four indistinguishable lines |
| All nine execution counts were `null` | No record of what produced the committed figures, or in what order |
| The draws were unseeded | No run reproduced any other |
| The write-up calls the weight's growth concave | It is the logistic map, so concave only above 0.5. It looks concave in the original figures because the weight starts at 0.8, already past the inflection |

![The update is the logistic map, concave only above 0.5](../results/update_shape.png)

**The model itself is unchanged.** Everything corrected is around it. The rerun's
own figures, including the three whose legends the original computed and threw
away, are in [`../results/`](../results/) beside the tournament's.

## Two claims the simulation does not support

Recorded because the report sits next to this and a reader will read both.
Neither undermines the idea, which is a reasonable one. They are claims the code
was never asked to check.

- It says the agents *"se rapproche du comportement humain"*. There is no human
  data anywhere in the simulation. The agent plays three hardcoded fixed
  policies, one of which is a coin flip. Resemblance to a human is never tested.
- It says the parameters are *"basées sur des données empiriques"* from Ng
  (2023). They are `2**0.5 - 1` and `0.8`. Neither is traceable to that paper or
  to any measurement, though the closed form does at least give the first one a
  reading: it makes the odds double every two net observations.

A third claim, that Tit-for-Tat emerges from imitation, needed opponents that
react before it could be tested at all. That test is
[the folder README](../README.md), and the claim does not survive it.
