# LLMs as players

> [Lire en français](README.fr.md)

> **The grid has been run: 220 matches, five models, 2026-08-17.** The numbers are
> in [What it found](#what-it-found) and the tables in [`results/`](results/).
> Every claim below the raw log is re-derived from it on every push.

The internship read Horton, Filippas and Manning (2023) and named homo silicus in
its conclusion. It never ran it. This folder is that method, on models small
enough to run on this machine, playing the games the report's own frame defines.

It is a sibling of [`../mirror_neurons/`](../mirror_neurons/) on purpose.
`OllamaPlayer` exposes `observe_and_learn` and `select_action`, the same two
calls as `HebbianMirrorNeuronAgent`, so one harness can seat either. Both score
reciprocity with [`../reciprocity.py`](../reciprocity.py), which sits at the root
so that one definition serves both and the comparison cannot drift.

## The question it is set up to answer

Two imitators keep whatever regime they are dropped into, 700 runs out of 700
([`../mirror_neurons/results/self_play_lock_in.csv`](../mirror_neurons/results/self_play_lock_in.csv)).
They have no channel for a message and nothing a message could act on.

A language model has the channel for free. So: **hand two models a regime they
did not choose, and see whether a non-binding message lets them leave it.** Each
pair starts from a mutually cooperative round, a mutually defecting one, or
nothing at all, with cheap talk and without.

**Half of that is a replication, and is written up as one.** Injecting a
synthetic cooperative history is the *memory sanitization* arm of
[The Memory Curse](https://arxiv.org/abs/2605.08060), which found it restores
cooperation, and cheap talk raising cooperation in language models is
established besides. What is not found done is the defective mirror of that
injection, crossed with the channel, against a mechanism that provably cannot
escape. The claims this folder may and may not make, and the baseline to report
against, are in
[`design-notes/what-is-already-known/`](design-notes/what-is-already-known/).

## What it found

220 matches played 2026-08-17, 210 readable and 10 lost, all of them phi3:mini.
Self-play cooperation rate over 30 rounds, 4 matches per cell:

| model | neutral, silent | neutral, talk | cooperative, silent | cooperative, talk | **imposed defection, silent** | **imposed defection, talk** |
|---|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 1.00 | 1.00 | 1.00 | 1.00 | **0.00** | **1.00** |
| mistral:7b | 1.00 | 1.00 | 1.00 | 1.00 | **0.99** | **0.74** |
| gemma3:4b | 0.89 | 1.00 | 0.76 | 1.00 | **0.00** | **0.00** |
| qwen3:8b | **0.00** | 1.00 | 1.00 | 1.00 | **0.00** | **0.00** |
| phi3:mini | 0.58 | 1.00 | 0.57 | 0.95 | 0.54 | 0.91 |

**Three of the four readable models are captured completely by a regime they did
not choose.** Handed a mutually defecting opening with no channel, qwen2.5,
gemma3 and qwen3 defect in all 30 rounds, 4 matches out of 4, cooperation rate
exactly zero. That is the imitator's ratchet reproduced in a language model.

**A non-binding message breaks the capture in exactly one of the three.** qwen2.5
goes from 0.00 to 1.00, 4 out of 4. gemma3 and qwen3 do not move at all. And
mistral is never captured in the first place: it climbs out of the defective
opening while silent, 0.99, and the message *lowers* that to 0.74.

So the answer to the question above is that two talking agents can leave an
imposed regime, but **the channel is neither necessary nor sufficient**. mistral
leaves without one, and gemma3 and qwen3 stay with one. Which models can is a
fact about the models, reported as the design notes require: variation across
models, stated as variation across models, not as a property of language models.

**Silence is not one treatment either.** qwen3:8b defects for all 30 rounds from
a *neutral* start when silent, 4 out of 4, where every other model cooperates. For
that model cheap talk is not what escapes a defective regime, it is what stops one
forming. gemma3 is unstable the same way, 2 of its 4 silent matches from a
cooperative opening decaying into mutual defection. Where cheap talk is not
fighting an imposed opening it is a perfect stabiliser: 1.00 everywhere.

### Against the Axelrod strategies

Score per turn, model first, same five opponents and same reciprocity index as
[`../mirror_neurons/`](../mirror_neurons/) so the two halves are one table:

| model | Tit For Tat | Grudger | Win-Stay Lose-Shift | Defector | Alternator |
|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 3.00 - 3.00 | 3.00 - 3.00 | 3.00 - 3.00 | 0.95 - 1.20 | 2.20 - 2.37 |
| mistral:7b | 3.00 - 3.00 | 3.00 - 3.00 | 3.00 - 3.00 | **0.41 - 3.37** | 1.50 - 4.00 |
| gemma3:4b | 2.80 - 2.76 | 2.80 - 2.76 | 3.00 - 2.71 | 0.97 - 1.13 | 1.50 - 4.00 |
| qwen3:8b | **1.13 - 0.97** | 1.13 - 0.97 | **3.00 - 0.50** | 1.00 - 1.00 | **3.00 - 0.50** |
| phi3:mini | 2.43 - 2.38 | 0.73 - 3.35 | 2.07 - 2.65 | 0.42 - 3.33 | 1.98 - 2.73 |

The same two dispositions the self-play cells found. qwen2.5 and mistral hold
mutual 3.00 against every reciprocator; qwen3 cooperates with nothing at all
(0.00 against all five), which pays 3.00 to 0.50 against the two exploitable
strategies and costs it 1.13 against the retaliators the cooperators farm at
3.00. Recognising a pure defector splits the panel again: qwen2.5 and gemma3 stop
feeding Defector (0.05 and 0.03 cooperation), while **mistral cooperates with it
59% of the time, handing it 3.37 per turn while earning 0.41**. That is the
worst cell in the grid.

### Does the stated reason match the move

The prompt asks for a reason. Of the rounds whose reasoning named an action, how
often the move agreed: qwen3 0.997 (1667 rounds), gemma3 0.939 (1583), qwen2.5
0.938 (1044), phi3 0.735 (573), **mistral 0.666 (500)**. mistral contradicts its
own stated reasoning in 33% of the rounds where it states one, which with its 938
loose parses is the caveat on every mistral number above.

Read beside [what the messages say](results/README.md), qwen3 is the instructive
case: it has the highest agreement between its stated reason and its move, and
its *messages* are decoupled from both. Saying what you will do and doing it does
not mean the signal you send carries any of it.

### Two caveats that are part of the result

- **phi3:mini is reported as unreadable, not as a result.** 10 of 44 matches lost
  at a mean of 16.2 rounds in, no silent condition ever settling, and a longest
  prompt of 8023 tokens against the 8192 requested, which leaves **169 tokens of
  headroom** where mistral had 5540 and qwen3 6211. It came within 169 tokens of
  re-triggering the truncation that invalidated an earlier run.
- **The panel is five models of 4B to 8B on an 8 GB card.** Where these results
  differ from Horton et al. or Bauer et al., model scale is a live explanation and
  cannot be ruled out from inside this repository.

The payoff-order effect the first stage showed against Alternator does not
generalise across the panel. gemma3 and mistral are fully exploited in both
orders, and qwen3 fully exploits it in both. It stays reported as what it was:
evidence that counterbalancing the payoff order was worth doing, an instance of
Fish, Gonczarowski and Shorrer (2024), and not a finding about language models.

## What runs, and what it costs

```sh
export PYTHONPATH=.
python llm/preflight_checks.py            # offline, needs nothing, ~2 seconds
python llm/run_experiment.py --plan       # the grid, without playing it
python llm/preflight_checks.py --online   # smoke test, 5 models, needs Ollama
python llm/run_experiment.py              # the grid. Hours. Resumable
python llm/run_analysis.py && python llm/plot_results.py   # offline
```

220 matches of 30 rounds: 120 self-play across three openings and both
conditions, and 100 against the five Axelrod strategies the Hebbian agent also
faced. 13,800 model calls. The smoke test is what turns that into an honest
estimate of hours, because it measures the per-model rate on this card rather
than assuming one, and on 2026-08-17 it priced the grid at **3.3 h**. The grid
then took **4.81 h of match time** summed from the log, plus cooldown between
matches and between stages. The estimate was low per model and the ordering was
wrong about which model is cheap: phi3:mini was the most expensive of the five,
1.67 h for its 44 matches against qwen3:8b's 0.89 h, because its prompts run
long and ten of its matches burned rounds before failing to parse.

**Do not start the grid while anything else wants the GPU.** One model fits at a
time and switching in a tight loop is what took this machine down on 2026-08-15.

## Why the raw log and the tables are separate

`results/matches.jsonl` is one line per finished match, every reply whole,
reasoning kept apart from the answer. It costs hours on the card and is never
regenerated. Every CSV beside it is derived from that file by
[`measurements.py`](measurements.py), which is pure arithmetic, so CI re-derives
them on every push and fails on any difference. The Hebbian folder gets that
guarantee by rerunning the tournament; this one cannot, so it gets it by keeping
the expensive half raw and the checkable half cheap.

The same split makes the run resumable: each match is keyed and a key already in
the log is skipped, so a crash costs the match in flight and nothing more.

**[`results/README.md`](results/README.md) is the data dictionary**: every field
of the raw log, every column of the seven tables, and the run conditions that have
to be reported with a number for it to mean anything: the model digests and
quantisation levels, the seeds, the hardware, and the confound in phi3:mini's
build.

## The files

| | |
|---|---|
| [`ollama_player.py`](ollama_player.py) | The player. Talks to Ollama, keeps every reply whole, and reads the `ACTION:` line rather than guessing from the prose |
| [`bot_opponent.py`](bot_opponent.py) | An Axelrod strategy seated as a player, so models and the imitator meet the same opponents |
| [`iterated_game.py`](iterated_game.py) | The match loop. Cheap talk is simultaneous: both write blind, then both hear, then both act |
| [`stub_player.py`](stub_player.py) | A scripted player, so all of the above can be tested with the card cold |
| [`panel_config.py`](panel_config.py) · [`grid_config.py`](grid_config.py) | The five models and how they are sampled; what matches get played |
| [`prompt_loader.py`](prompt_loader.py) | Renders a prompt, counterbalancing the payoff order across repetitions |
| [`run_experiment.py`](run_experiment.py) · [`run_analysis.py`](run_analysis.py) · [`plot_results.py`](plot_results.py) | Play the grid; derive the tables; draw the figures |
| [`machine_gate.py`](machine_gate.py) · [`run_ownership.py`](run_ownership.py) | Whether this laptop can take another match, and who holds the card while it does. Both are incident reports as much as code |
| [`preflight_checks.py`](preflight_checks.py) | Nineteen offline checks and the online smoke test. Refuses to start until the harness is shown to work |
| [`prompts/`](prompts/) | One scenario per game. In this method the prompt is the experiment |
| [`design-notes/`](design-notes/) | What the method can and cannot show, and why cheap talk and explainability are the point |

## What is deliberately missing

The Ultimatum and Dictator harnesses. Their prompts are written, because the
scenario text is the part worth arguing about, but the game loops are not,
because those two games are needed by [`../mirror_neurons/`](../mirror_neurons/)
as well and a shared home for them is a structural decision rather than a file
to dash off. See
[`../mirror_neurons/design-notes/what-the-agent-cannot-do.md`](../mirror_neurons/design-notes/what-the-agent-cannot-do.md),
where the Dictator game is the case that separates the two folders: the imitator
is mute there, and a model is not.

Design notes and prompts stay in English. Translating a prompt would change the
experiment the models are run on.

## Credits

Horton, Filippas and Manning (2023) is the internship's own reference 5, summarised
in `../original/Litterature/Summary/`. Fish, Gonczarowski and Shorrer (2024) and
Calvano et al. (2020) are later reading, not internship work. Full citations are
in [`design-notes/homo-silicus.md`](design-notes/homo-silicus.md).
