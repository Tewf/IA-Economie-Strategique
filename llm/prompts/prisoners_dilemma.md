# Iterated Prisoner's Dilemma

Payoffs are Axelrod's defaults, so a run against this prompt is directly
comparable to a run of the Hebbian agent against the same opponents:
mutual cooperation 3, mutual defection 1, defecting against a cooperator 5,
cooperating against a defector 0.

The horizon is stated as unknown. Both Ng (2023) and Axelrod's tournaments run
without a announced last round, and announcing one invites backward induction to
defection, which would be a different experiment.

---

You are playing a game against another player, for points.

Each round, you and the other player each choose one of two actions, at the same
time, without knowing what the other has chosen. The actions are Cooperate and
Defect.

The points you receive in a round depend on both choices:

<!-- payoffs:start -->
- You both choose Cooperate: you get 3 points, they get 3 points.
- You both choose Defect: you get 1 point, they get 1 point.
- You choose Defect and they choose Cooperate: you get 5 points, they get 0.
- You choose Cooperate and they choose Defect: you get 0 points, they get 5.
<!-- payoffs:end -->

The game runs for an unknown number of rounds. After each round you are told
what the other player chose. Your aim is to end with as many points as possible.

<!-- answer-format:start -->
Answer in exactly this format, and nothing else:

```
ACTION: <Cooperate or Defect>
REASON: <one or two sentences>
```

Give the action on the first line before you explain it.
<!-- answer-format:end -->
<!-- message-format:start -->
You are being asked for a message to the other player, not for an action.

Write one short sentence of ordinary prose and nothing else. Do not state which
action you are about to choose, do not use the word Cooperate or the word
Defect, and do not answer in the ACTION and REASON format. The other player is
writing at the same moment and cannot see this before they choose.
<!-- message-format:end -->
