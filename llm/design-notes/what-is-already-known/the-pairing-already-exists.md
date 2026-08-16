# Is the pairing itself already done? Yes, and it is published

Part of [what the field already knows](README.md).

The repository's framing is that the two folders are one comparison. Asked
directly on 2026-08-16 whether that comparison already exists, the answer came
back in three layers, and the first one was left unresolved that day because it
rested on a search summary rather than on a source. **Resolved 2026-08-17.**

## Seating language models beside canonical strategies: published, and first

[Strategic Intelligence in Large Language Models: Evidence from evolutionary
Game Theory](https://arxiv.org/abs/2507.02618) (Payne and Alloui-Cros, July
2025) runs "the first ever series of evolutionary IPD tournaments, pitting
canonical strategies (e.g., Tit-for-Tat, Grim Trigger) against agents from the
leading frontier AI companies". They vary the termination probability, the
shadow of the future, and read nearly 32,000 prose rationales.

So the structural idea is not new, it is claimed as a first by its authors, and
**this folder must not present the pairing as its contribution.**

The summary that prompted the question described "13 rule-based strategies,
three adaptive learners and 12 LLM agents in one evolutionary environment". That
composition is real but it is not the paper: it is
[HCSS-Data-Lab/Strategic-LLM-IPD](https://github.com/HCSS-Data-Lab/Strategic-LLM-IPD),
a December 2025 framework built on Payne et al., whose three adaptive agents are
Q-learning, Thompson sampling and a gradient meta-learner. Worth recording
exactly because the earlier note nearly cited a repository's description as a
finding.

**What still differs here, stated narrowly.** Their panel is frontier models
behind APIs; this one is five open-weight models on one 8 GB card. Their lever
is the shadow of the future; this one's is the history a pair inherits. They run
no cheap-talk channel. None of that makes the pairing novel, and all of it means
the numbers are not interchangeable.

## This particular Hebbian mirror-neuron agent: not found

Imitation dynamics in the Prisoner's Dilemma is an established literature
(spatial imitation, aspiration learning, replicator dynamics), but this
construction, a Hebbian weight update over observed actions from the
internship's mirror-neuron framing, does not appear as a studied model.

**And the honest reading of that is not "novel".** The agent is bespoke, written
by an L2 intern in 2025 and not a canonical baseline. That it is unstudied is
weak evidence that nobody wanted to study it, which is exactly the confusion the
method's fourth step warns against: *nobody has done this* is not the same as
*this is worth doing*.

What survives is narrow and should be stated narrowly. The value is not
"imitation versus language models" in general. It is that **this repository's
own report proposed this mechanism and claimed Tit-for-Tat emerges from it**,
and both halves test that claim on shared opponents with one measure. It is a
study of an internship's hypothesis, not a contribution to the comparative
literature on agent architectures.

## What was checked in code and left alone

`axelrod.interaction_utils` computes cooperation rates, per-turn scores and
state-to-action distributions, which overlaps the arithmetic in
[`../../measurements.py`](../../measurements.py). The overlap is a few lines of
division and was left as it is, but the library is now used for something
better: it recomputes the reciprocity index a different way, and
[`../../../mirror_neurons/preflight_checks.py`](../../../mirror_neurons/preflight_checks.py)
asserts the two agree to 1e-12 across six strategies. Independent arithmetic on
the one number both folders share is worth more than saving four lines.
