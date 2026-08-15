# The prompts

One file per game. Each is the system prompt a model is given before it plays,
and it is the experiment design: change the wording and you have run a different
experiment, which is exactly what Fish, Gonczarowski and Shorrer found when
innocuous phrasing changes moved prices.

They are prose files rather than string literals in Python so that they can be
reviewed as prose, diffed as prose, and quoted in a write-up without being
transcribed.

## Rules they all follow

- **Give an endowment, information and a payoff. Do not give a theory.** Horton's
  method is to put a model in the position of a subject, not to ask it what a
  subject would do. Nothing here mentions Nash, cooperation, reciprocity,
  fairness or tit-for-tat, because naming the phenomenon is a way of causing it.
- **Never say the other player is a machine, or a person.** Ng (2023) varies
  exactly that and finds it moves behaviour, so it is a treatment, not a
  background detail. The neutral wording is the baseline; a variant that states
  the partner's nature belongs in its own file when that experiment is run.
- **Ask for the action first, then the reason.** The action has to be parseable
  by `ollama_player.py` whether or not the reasoning is coherent.
- **Say the horizon honestly.** A repeated game with a known last round is a
  different game from one without, by backward induction, and the model may well
  perform that induction.

## Files

| | |
|---|---|
| [`prisoners_dilemma.md`](prisoners_dilemma.md) | The iterated form. Ng (2023), Bauer et al. (2023) |
| [`ultimatum.md`](ultimatum.md) | Proposer and responder. Özkes et al. (2024) |
| [`dictator.md`](dictator.md) | Allocation with no responder. Horton's replications |

The Ultimatum and Dictator harnesses are not written yet. The prompts are, because
the scenario text is the part worth arguing about and it is not blocked on the
code.
