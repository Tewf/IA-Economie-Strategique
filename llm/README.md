# LLMs as players

> [Lire en français](README.fr.md)

> **The harness is ready and the experiment has not been run.** Every model call
> needs the GPU, so nothing here has touched one: what is checked is everything
> that is logic rather than model, and that is checked on every push.

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
[`design-notes/what-is-already-known.md`](design-notes/what-is-already-known.md).

## What runs, and what it costs

```sh
export PYTHONPATH=.
python llm/preflight_checks.py            # offline, needs nothing, ~2 seconds
python llm/run_experiment.py --plan       # the grid, without playing it
python llm/preflight_checks.py --online   # smoke test, 5 models, needs Ollama
python llm/run_experiment.py              # the grid. Hours. Resumable
python llm/run_analysis.py && python llm/plot_results.py   # offline
```

275 matches of 30 rounds: 150 self-play across three openings and both
conditions, and 125 against the five Axelrod strategies the Hebbian agent also
faced. 17,250 model calls. The smoke test is what turns that into an honest
estimate of hours, because it measures the per-model rate on this card rather
than assuming one.

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
| [`preflight_checks.py`](preflight_checks.py) | Twelve offline checks and the online smoke test. Refuses to start until the harness is shown to work |
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
