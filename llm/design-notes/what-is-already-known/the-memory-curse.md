# The field calls it path dependence, and one paper half-answers it

Part of [what the field already knows](README.md).

Named properly, the question is not "lock-in" but **path dependence and
sensitivity to initial conditions in repeated LLM interaction**. Under this
folder's own vocabulary the search returned nothing; under the field's name the
literature has plenty, and one paper does something close to a cell of this grid.

[The Memory Curse](https://arxiv.org/abs/2605.08060) tests 7 models across 4
games over 500 rounds and finds that **expanding accessible history degrades
cooperation in 18 of 28 model-game settings**. Its *memory sanitization* arm
holds prompt length constant and replaces the real history with **synthetic
cooperative records**, which restores cooperation substantially.

## Read from the abstract that looked like a duplicate. Read from the paper it is not

| | Memory sanitization | This grid's opening |
|---|---|---|
| Game | **Trust Game** | Prisoner's Dilemma |
| History | 80 rounds, of which **78 are overwritten** | **one** fabricated round, then 30 real ones |
| What it asks | is the curse caused by content or by length | does the regime a pair starts in capture it |
| Direction | **repairs** a collapse that already happened | **sets** a starting point and lets real play accumulate |

Theirs is a diagnostic: hold the window fixed, swap the content, see whether the
number moves. This one is an initial condition: seed one round and let the pair
write the rest. A bulk overwrite that erases the record of a collapse says
nothing about whether a pair is captured by where it began.

So the cooperative injection has a close relative in the literature and must
cite it, not that it is done. What is not done at all:

- **The defective opening as the symmetric treatment.** Sanitization injects a
  good history to repair a collapse. Nobody found here injects a bad one to see
  whether a pair that could have cooperated is captured by it.
- **Opening crossed with cheap talk.** Whether a channel lets a pair leave a
  regime it was handed is a different question from whether a channel raises
  cooperation from neutral, and the second does not imply the first.
- **A non-linguistic floor.** Sensitivity to initial conditions is described in
  this literature as *understudied*, and measured across random seeds rather
  than against a mechanism that provably cannot escape.

**The baseline to report against is therefore the sanitization result**: a
synthetic cooperative history restores cooperation. If this grid reproduces that
and finds no matching capture from a synthetic defective history, the asymmetry
is the finding. If both capture, it is a ratchet in a talking agent and it lines
up with the imitator.

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
game iterated, and the reason is what the explainability half measures.

**And read from the paper rather than the abstract, the warning is weaker than
it first looked, for one specific reason.** The deliberation penalty is measured
per model in the game that hurts it most, and *the Prisoner's Dilemma is not
that game for anybody*. Mistral-7B, the one model on both panels, takes its
worst hit in Public Goods at -49.7pp; Llama-3.3-70B takes -93.1pp in the Trust
Game. The paper says plainly that capable models "often maintain 100%
cooperation in structurally simpler games (like the Prisoner's Dilemma...)
regardless of whether CoT is utilized", and calls that a ceiling effect that
dilutes the finding.

The Prisoner's Dilemma is where the curse is weakest. This grid runs 30 rounds
against their 80-round condition, and the curve they report peaks at HL <= 5 and
decays after, so 30 is on the falling part but nowhere near their far end.

What that buys is a prediction rather than an excuse: cooperation here should be
high. If a number does come back low, the regime is the first thing to check and
not the last.
