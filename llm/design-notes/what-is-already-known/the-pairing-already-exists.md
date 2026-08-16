# Is the pairing itself already done? Layered answer, one layer unresolved

Part of [what the field already knows](README.md).

The repository's framing is that the two folders are one comparison. Asked
directly on 2026-08-16 whether that comparison exists already:

- **Seating LLMs and non-LLM agents in one tournament: yes, and it should not be
  claimed as new.** A search summary describes rule-based canonical IPD
  heuristics, three adaptive reinforcement learners and 12 LLM strategies in a
  single evolutionary environment. **Not verified in the paper itself**: two
  abstracts were fetched and neither gave the agent composition, so this is a
  secondary source and is recorded as such. **Resolve it before the write-up
  claims the pairing is novel.**
- **This particular Hebbian mirror-neuron agent: not found.** Imitation dynamics
  in the Prisoner's Dilemma is an established literature (spatial imitation,
  aspiration learning, replicator dynamics), but this construction, a Hebbian
  weight update over observed actions from the internship's mirror-neuron
  framing, does not appear as a studied model.

**And the honest reading of that second point is not "novel".** The agent is
bespoke, written by an L2 intern in 2025 and not a canonical baseline. That it
is unstudied is weak evidence that nobody wanted to study it, which is exactly
the confusion step 4 of the method warns against: *nobody has done this* is not
the same as *this is worth doing*.

What survives that objection is narrow and should be stated narrowly. The value
is not "imitation versus language models" in general. It is that **this
repository's own report proposed this mechanism and claimed Tit-for-Tat emerges
from it**, and both halves test that claim on shared opponents with one measure.
It is a study of an internship's hypothesis, not a contribution to the
comparative literature on agent architectures.

## What was checked in code and left alone

`axelrod.interaction_utils` computes cooperation rates, per-turn scores and
state-to-action distributions, which overlaps the arithmetic in
[`../../measurements.py`](../../measurements.py). The overlap is a few lines of
division and was left as it is, but the library is now used for something
better: it recomputes the reciprocity index a different way, and
[`../../../mirror_neurons/preflight_checks.py`](../../../mirror_neurons/preflight_checks.py)
asserts the two agree to 1e-12 across six strategies. Independent arithmetic on
the one number both folders share is worth more than saving four lines.
