# Ultimatum game

Özkes, Hanaki, Vanderelst and Willems (2024) endow the pair with 100 points, and
measure the proposer's offer and the responder's minimum acceptable offer. Their
404 UK participants found no significant difference in minimum acceptable offer
between a human and an algorithmic partner, and offered a human about 4 points
more than an algorithm. Both halves are here because the interesting comparison
is between the two roles, and a model can be put in either.

Their partner conditions (HU, MA imitating, OA optimising, NA unexplained) are
treatments to be added as variant files when that experiment is run. Neither
prompt below states what the other party is.

---

## Proposer

You have been given 100 points to divide between yourself and one other player.

You propose how to split them. The other player then sees your proposal and
either accepts or rejects it.

- If they accept, the split happens as you proposed.
- If they reject, you both receive nothing.

You make one proposal. There is no negotiation and no second attempt.

Answer in exactly this format, and nothing else:

```
OFFER: <a whole number from 0 to 100, the points the other player receives>
REASON: <one or two sentences>
```

---

## Responder

Another player has been given 100 points to divide between the two of you.

They have proposed a split. You either accept or reject it.

- If you accept, the split happens as they proposed.
- If you reject, you both receive nothing.

You decide once. There is no negotiation and no counter-offer.

Before you are told the proposal, state the smallest number of points you would
accept.

Answer in exactly this format, and nothing else:

```
MINIMUM: <a whole number from 0 to 100>
REASON: <one or two sentences>
```
