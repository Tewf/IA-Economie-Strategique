# Two places the model does not reach

Both are decisions, not bugs. Writing them down is cheaper than discovering
later that a result depended on one of them being taken silently.

## 1. The action set is binary, and two of the games are not

The update rule holds one weight per action and multiplies the observed one by
`1 + η`. With two actions that is the logistic map on a single number. The
iterated Prisoner's Dilemma has exactly those two actions, so the agent ports to
it with no change at all.

Ultimatum and Dictator do not. Their action is an offer, a number in 0..100.
Three ways to extend the model, and they do not measure the same thing:

| Extension | What it would mean | What it costs |
|---|---|---|
| Discretise the offer space into bins and keep one weight per bin | Closest to the existing rule, and the logistic update survives unchanged | The bin width becomes a free parameter that nothing in the literature fixes, and imitation across bins is undefined: observing an offer of 47 says nothing about the weight on 46 |
| Replace the weights with a distribution over offers, updated toward the observed offer | Imitation becomes "move toward what you saw", which is what mirror neurons are supposed to do | It is no longer the original rule. Any result is about a new model, and the report's claims would not transfer |
| Keep the binary action as accept or reject, and hold the offer fixed | The rule is untouched, and the responder side of the Ultimatum game is genuinely binary | It only models the responder. The proposer, which is where Özkes et al. measure the interesting effect, is not covered, and the Dictator game has no responder at all |

The third is the honest minimum and answers the smallest question. The first is
the natural reading of "the same model, in a bigger game". The second is the
most faithful to the biology and the least faithful to the internship.

This is not resolved here. Resolving it is a modelling choice about what the
next result is supposed to mean.

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
