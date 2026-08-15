# Two places the model does not reach

Both are decisions, not bugs. Writing them down is cheaper than discovering
later that a result depended on one of them being taken silently.

## 1. The agent needs something to watch, and one of the games gives it nothing

This note used to say the obstacle was that the action set is binary. That was
wrong, and the closed form in the notebook is what shows it: the rule is
multiplicative weights, `w_i` proportional to `w_i(0) * (1 + eta) ** n_i`, and
it is already written per action. Ten actions work exactly as two do. Nothing
about the update cares how many there are.

The real axis is **what the agent has to observe**, because `n_i` is a count of
observed actions and nothing else feeds it. Sorted that way the games separate
cleanly:

| Game | What the agent observes | Verdict |
|---|---|---|
| Prisoner's Dilemma, iterated | an action every round | native |
| Prisoner's Dilemma, sequential | the first mover's action | native, and it is the model's own sequential timing |
| Ultimatum, as proposer | accept or reject | works, but yields one observation per game |
| Ultimatum, as responder | an offer, a number carrying no metric | needs a kernel across neighbouring offers |
| Dictator | nothing at all | mute |

**The Dictator game is the sharp case.** The recipient never acts, so there is
nothing to imitate: every `n_i` stays at zero and the agent plays its starting
weights forever, whatever the dictator does and however long the game runs. It
is not that the model does the wrong thing there. It has no input.

Two of the rows still need a modelling choice, and it is a choice about meaning
rather than about code:

| For an offer, you could | What it would mean | What it costs |
|---|---|---|
| Bin the offer space and keep one weight per bin | Closest to the existing rule, which survives unchanged | Imitation across bins is undefined: seeing an offer of 47 says nothing about the weight on 46, and the bin width is a free parameter nothing in the literature fixes |
| Replace the weights with a distribution updated toward the observed offer | Imitation becomes "move toward what you saw", which is what mirror neurons are for | It is no longer the original rule, so no result would transfer to the report's claims |
| Keep the action binary as accept or reject | The rule is untouched, and the responder side genuinely is binary | Covers only the responder. Özkes et al. measure the interesting effect on the proposer |

The third is the honest minimum. The first is the natural reading of "the same
model, in a bigger game". The second is the most faithful to the biology and the
least faithful to the internship.

**Why this matters for the folder next door.** `../../llm/` has the opposite
profile: a language model in the Dictator game has everything it needs, because
the situation is describable in words even when no one has acted yet. The one
game where the imitator is mute is the one where the other approach is
unhampered. That complementarity is the argument for both folders existing, and
it is only visible once the axis is observation rather than arity.

## 2. The two timing conventions do not both fit a simultaneous-move engine

The rerun has both, and they are not equivalent:

- `play_static_game`: the agent acts, then observes and learns. Its move cannot
  depend on the opponent's move in the same round.
- `play_sequential_game`: the agent observes and learns, then acts. Its move
  depends on what the opponent just did, in the same round.

Axelrod's engine is simultaneous-move, so it is the static convention. In it,
the agent reads the opponent's previous action, which is the same information
`play_sequential_game` uses, just shifted by one round. The wrapper therefore
implements the static convention, and this is a real restriction rather than a
detail: Bauer et al.'s protocol is the sequential one, where the second mover
genuinely sees the first mover's choice before choosing.

Testing the sequential convention properly needs a sequential game, not a
simultaneous engine with a relabelled index. That is the second reason the
Prisoner's Dilemma work starts with the iterated form.
