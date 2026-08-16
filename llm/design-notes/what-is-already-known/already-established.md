# What is established, and the two claims that follow from it

Part of [what the field already knows](README.md).

## The design turns out to match the field's protocol

That is reassuring rather than disappointing: it means these numbers can be read
against other people's.

- **One-sentence free-form messages, exchanged before each decision, with the
  players told the messages are non-binding.** That is the protocol in
  [Communication Enables Cooperation in LLM Agents](https://arxiv.org/html/2510.05748v3),
  and it is what [`../../iterated_game.py`](../../iterated_game.py) does,
  arrived at independently from Ng (2023) via the internship's own reading.
- **Small open-weight models in a short repeated Prisoner's Dilemma.**
  [Communication Enhances LLMs' Stability in Strategic Thinking](https://arxiv.org/abs/2602.06081)
  runs 7-9B models over ten rounds. This panel is 3.8-8.2B over thirty.

## Two claims this folder must therefore not make

**That cheap talk raises cooperation in language models.** It is established.
The effect is reported as large, up to a Stag Hunt going from 0% to 96.7%
cooperation with minimal communication. Measuring it again on five local models
is a replication, and should be written as one.

**That prompt wording moves the outcome.** Also established, and the reason
[`../../prompts/README.md`](../../prompts/README.md) already cites Fish,
Gonczarowski and Shorrer. The 30-out-of-30 defection under the broken cheap-talk
prompt against 90-90 cooperation under the fixed one is a vivid instance of a
known phenomenon, not a new one. It is worth reporting as evidence that the fix
mattered, not as a finding about language models.
