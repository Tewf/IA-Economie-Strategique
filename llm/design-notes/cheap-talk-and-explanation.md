# Cheap talk and explainability

The internship's conceptual frame defines eight terms. Two of them are things
only a talking player can do, and they are the reason this folder is a
continuation of the mirror-neuron work rather than a separate subject.

## Cheap talk (§2.1.5)

Non-binding messages between players, before or during the game, which can
sustain cooperation by signalling intent or setting expectations. Ng (2023) is
built on it: a repeated Prisoner's Dilemma with normative communication between
rounds, four partner conditions, and the report's own summary records that
communication stabilised cooperation over the long run.

The Hebbian agent cannot participate in this at all. It observes an action and
updates a weight. There is no channel for a message and nothing in the model
that a message could act on.

A language model has the channel for free. Running the iterated Prisoner's
Dilemma with and without a message exchange between rounds is the smallest
experiment that tests something the internship read about and could not build.

## Explainability (§2.1.6)

The report defines it as the quality of the justification a player gives, and
records that Özkes et al. found the level of explanation an algorithm gave did
not shift its partner's minimum acceptable offer.

This is why `ollama_player.py` keeps every reply whole rather than parsing the
action and discarding the rest. The reasoning is the object of study. Three
things it makes measurable:

- **Whether the stated reason predicts the next action.** A model that says it
  is retaliating and then does not is doing something worth reporting.
- **Whether the reason survives the action being forced.** Ask for the reason
  before the action and after it, and see if they agree.
- **Whether models that reason alike play alike.** The panel is five different
  families, so this is a real comparison rather than five samples of one.

## The honest caveat

A reason a model gives is text it produced, not an account of a computation it
performed. Treating it as introspection is the mistake to avoid, and it is a
sharper version of the mistake the internship's write-up already made once when
it said the agent *"se rapproche du comportement humain"* with no human data in
the simulation.

What the text can support is a claim about consistency: whether what a model says
and what it does line up. That is measurable, and it does not require the text to
be true.
