# What is left, and it is the part worth running

Part of [what the field already knows](README.md).

The internship's question is not "do talking agents cooperate". It is whether
algorithms **sustain** tacit cooperation, **break** it, or **intensify** it, and
the Hebbian half already answered it for imitation: two imitators keep whatever
regime they are dropped into, 700 runs out of 700
([`../../../mirror_neurons/results/self_play_lock_in.csv`](../../../mirror_neurons/results/self_play_lock_in.csv)),
and cannot leave it.

So the question here is narrower than the literature's and not answered by it:

**Handed a regime they did not choose, can two talking agents leave it?**

That is why the grid has `mutual_cooperation`, `mutual_defection` and `neutral`
openings rather than just running matches. A paper reporting that communication
raises cooperation from a neutral start says nothing about whether it breaks a
ratchet, and the ratchet is the thing the imitation half found.

Two further things the comparison has that the literature does not, both by
accident of continuing an internship rather than starting a study:

- **The same opponents and the same measure as a non-linguistic agent.** The
  five Axelrod strategies and the reciprocity index in
  [`../../../reciprocity.py`](../../../reciprocity.py) are shared with
  [`../../../mirror_neurons/`](../../../mirror_neurons/), so the two are one
  table rather than two studies.
- **A mechanism with no channel at all as the baseline.** Most of this work
  compares communication against no communication within language models. Here
  the floor is an agent that cannot represent a message even in principle.
