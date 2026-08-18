# The question this grid was built for, and what it returned

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

## Answered, 2026-08-17

Handed a regime they did not choose, three of the four readable models cannot
leave it: 0.00 cooperation across all thirty rounds, four matches out of four.
The ratchet the imitation half found survives being given language.

A non-binding message frees exactly one of those three, leaves two where they
were, and lowers cooperation in the fourth model, which was never captured. So
**the channel is neither necessary nor sufficient**, and the narrow question
above has a per-model answer rather than a general one.

The mechanism is in [`the-memory-curse.md`](the-memory-curse.md): an injected
history outranks a message arriving at the same moment, and which of the two
wins is the model. The full write-up is [`../../../article/paper.qmd`](../../../article/paper.qmd).

**What is genuinely left**, and none of it is in this grid: the Ultimatum and
Dictator loops, whose shared home with `mirror_neurons/` is still a structural
decision; the reasoning contrast, now in
[`../../run_contrasts.py`](../../run_contrasts.py); and a coded content analysis
of the messages, which are currently read by a substring test and by hand.
