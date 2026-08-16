# What the field already knows, and what this folder can therefore claim

Searched 2026-08-16, before committing four more hours of machine time, and it
changed the framing rather than the design. Recorded because the alternative is
writing up an established result as a discovery.

## The design turns out to match the field's protocol

That is reassuring rather than disappointing: it means these numbers can be read
against other people's.

- **One-sentence free-form messages, exchanged before each decision, with the
  players told the messages are non-binding.** That is the protocol in
  [Communication Enables Cooperation in LLM Agents](https://arxiv.org/html/2510.05748v3),
  and it is what `iterated_game.py` does, arrived at independently from Ng
  (2023) via the internship's own reading.
- **Small open-weight models in a short repeated Prisoner's Dilemma.**
  [Communication Enhances LLMs' Stability in Strategic Thinking](https://arxiv.org/abs/2602.06081)
  runs 7-9B models over ten rounds. This panel is 3.8-8.2B over thirty.

## Two claims this folder must therefore not make

**That cheap talk raises cooperation in language models.** It is established.
The effect is reported as large, up to a Stag Hunt going from 0% to 96.7%
cooperation with minimal communication. Measuring it again on five local models
is a replication, and should be written as one.

**That prompt wording moves the outcome.** Also established, and the reason
[`../prompts/README.md`](../prompts/README.md) already cites Fish, Gonczarowski
and Shorrer. The 30-out-of-30 defection under the broken cheap-talk prompt
against 90-90 cooperation under the fixed one is a vivid instance of a known
phenomenon, not a new one. It is worth reporting as evidence that the fix
mattered, not as a finding about language models.

## What is left, and it is the part worth running

The internship's question is not "do talking agents cooperate". It is whether
algorithms **sustain** tacit cooperation, **break** it, or **intensify** it, and
the Hebbian half already answered it for imitation: two imitators keep whatever
regime they are dropped into, 700 runs out of 700, and cannot leave it.

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
  [`../../reciprocity.py`](../../reciprocity.py) are shared with
  `../../mirror_neurons/`, so the two are one table rather than two studies.
- **A mechanism with no channel at all as the baseline.** Most of this work
  compares communication against no communication within language models. Here
  the floor is an agent that cannot represent a message even in principle.

## What was checked and left alone

`axelrod.interaction_utils` computes cooperation rates, per-turn scores and
state-to-action distributions, which overlaps the arithmetic in
[`measurements.py`](../measurements.py). The overlap is a few lines of division
and was left as it is, but the library is now used for something better: it
recomputes the reciprocity index a different way, and
[`../../mirror_neurons/preflight_checks.py`](../../mirror_neurons/preflight_checks.py)
asserts the two agree to 1e-12 across six strategies. Independent arithmetic on
the one number both folders share is worth more than saving four lines.
