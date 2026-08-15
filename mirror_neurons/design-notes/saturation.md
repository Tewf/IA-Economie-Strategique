# What happens when the agent stops learning

The closed form says the weight is `w_i(0) * (1 + eta) ** n_i`, so the log-odds
between cooperating and defecting move by a constant step per observation. What
the agent sees is not balanced, so those steps accumulate into a random walk,
and a random walk is unbounded. Past roughly plus or minus 13 in log-odds the
probability is within a rounding error of 0 or 1 and the agent has become a
constant player. Nothing pulls it back.

Two measured consequences follow, and they look like opposite results until the
mechanism is named.

## It loses the reciprocity it starts with

Windowed over a 2000 turn match against a prober, the agent's reciprocity index
runs 0.135, 0.108, 0.017, 0.042 and then exactly 0.000 for every window from
turn 800 on. Tit-for-Tat holds 1.000 throughout.

Exactly zero is the signature of saturation rather than of noise: a constant
player has the same cooperation probability whatever the opponent just did, so
the difference between the two conditions is not small, it is identically zero.

Raising the learning rate does not buy the reciprocity back. It brings the
saturation forward as fast as it strengthens the response to any single
observation, which is why [the sweep](../results/learning_rate_sweep.png) peaks
around 0.13 near `eta = 0.5` and falls again by `eta = 1.0`.

## And its ranking improves because of it

Which constant it freezes into is not arbitrary. In the last twenty turns of a
500 turn match:

| Opponent | Agent's closing play |
|---|---|
| Tit For Tat, Cooperator, Win-Stay Lose-Shift | always cooperate |
| Defector, Grudger, Random | always defect |
| Alternator | still moving, at 0.75 |

Frequency matching converges on whatever the opponent plays most, so it ends up
cooperating with cooperators and defecting against defectors. Alternator is the
exception because alternating holds the two counts level, so the walk never
drifts and the agent never freezes.

That is a serviceable policy, and it is worth more than a coin flip against a
field of reciprocators, which is why the agent passes Random somewhere between
100 and 200 turns a match and reaches sixth by 500. **It is not the agent
learning to reciprocate. It is the agent ceasing to respond at all, and landing
on a constant that happens to suit the opponent.** It also takes hundreds of
rounds to arrive, and the horizons the report reads about, and that
[`../../original/Litterature/`](../../original/Litterature/) reviews, are far
shorter than that.
