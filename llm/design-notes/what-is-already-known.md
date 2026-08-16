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

## The field's word for the question is *path dependence*, and half of it is done

Named properly, the question is not "lock-in" but **path dependence and
sensitivity to initial conditions in repeated LLM interaction**. Under that name
the literature has plenty, and one paper does something very close to a cell of
this grid.

[The Memory Curse](https://arxiv.org/abs/2605.08060) tests 7 models across 4
games over 500 rounds and finds that **expanding accessible history degrades
cooperation in 18 of 28 model-game settings**. Its *memory sanitization* arm
holds prompt length constant and replaces the real history with **synthetic
cooperative records**, which restores cooperation substantially.

That is the `mutual_cooperation` opening, done already and by a stronger design.
What is not done, as far as this search reached:

- **The defective opening as the symmetric treatment.** Sanitization injects a
  good history to repair a collapse. Nobody found here injects a bad one to see
  whether a pair that could have cooperated is captured by it.
- **Opening crossed with cheap talk.** Whether a channel lets a pair leave a
  regime it was handed is a different question from whether a channel raises
  cooperation from neutral, and the second does not imply the first.
- **A non-linguistic floor.** Sensitivity to initial conditions is described in
  this literature as *understudied*, and measured across random seeds rather
  than against a mechanism that provably cannot escape. The Hebbian agent is
  that floor: 700 runs out of 700 keeping the regime it was dropped into.

**The baseline to report against is therefore the sanitization result**:
a synthetic cooperative history restores cooperation. If this grid reproduces
that and finds no matching capture from a synthetic defective history, the
asymmetry is the finding. If both capture, it is a ratchet in a talking agent
and it lines up with the imitator.

## Is the pairing itself already done? Layered answer, one layer unresolved

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

## Two design choices that sit in the collapse-prone regime

Worth stating before the run rather than discovering in the numbers, because
both were chosen for other reasons and both are named in that paper as things
that make cooperation worse:

- **Every round of history is in every prompt.** `_rounds_so_far` replays both
  sides of every finished round, messages included, so by round 30 the context
  is long. That is the memory-curse condition.
- **The prompt asks for a REASON.** Explicit deliberation is reported to
  *amplify* the collapse, and removing chain-of-thought often reduces it.

Neither is a reason to change the design: the history is what makes an iterated
game iterated, and the reason is what the explainability half measures. They are
reasons to expect less cooperation than a short-context, action-only setup would
give, and to say so beside any number that comes back low. Thirty rounds is also
far short of the 500 where the effect was characterised.

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
