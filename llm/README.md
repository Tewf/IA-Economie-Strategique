# LLMs as players

> Scaffolding. Nothing here has been run as an experiment, and no result is
> committed. What exists is the player, the panel, the scenario text and the
> reasons for each.

The internship read Horton, Filippas and Manning (2023) and named homo silicus in
its conclusion. It never ran it. This folder is that method, on models small
enough to run on this machine, playing the games the report's own frame defines.

It is a sibling of [`../mirror_neurons/`](../mirror_neurons/) on purpose.
`OllamaPlayer` exposes `observe_and_learn` and `select_action`, the same two
calls as `HebbianMirrorNeuronAgent`, so one harness can seat either. The
difference is what the calls mean: one updates a weight, the other appends to a
transcript and asks a model.

## Files

| | |
|---|---|
| [`ollama_player.py`](ollama_player.py) | The player. Talks to Ollama over HTTP, keeps every reply whole |
| [`models.py`](models.py) | The five local models, their sizes, and the sampling settings |
| [`prompts/`](prompts/) | One scenario per game. In this method the prompt is the experiment |
| [`design-notes/`](design-notes/) | What the method can and cannot show, and why cheap talk and explainability are the point |

## Running it

Ollama has to be up. Nothing leaves the machine and nothing costs anything.

```sh
curl -s 127.0.0.1:11434/api/tags     # the panel in models.py should all be here
python -c "import ollama_player"     # stdlib only, no install needed
```

The card is 8 GB and every model in the panel fits alone while no two fit
together, so a run over the panel is sequential by model. Do not start one while
a lecture is recording or while Cycles or ComfyUI is using the GPU.

## What is deliberately missing

The Ultimatum and Dictator harnesses. Their prompts are written, because the
scenario text is the part worth arguing about, but the game loops are not,
because those two games are needed by `../mirror_neurons/` as well and a shared
home for them is a structural decision rather than a file to dash off. See
[`../mirror_neurons/design-notes/what-the-agent-cannot-do.md`](../mirror_neurons/design-notes/what-the-agent-cannot-do.md).

## Credits

Horton, Filippas and Manning (2023) is the internship's own reference 5, summarised
in `../original/Litterature/Summary/`. Fish, Gonczarowski and Shorrer (2024) and
Calvano et al. (2020) are later reading, not internship work. Full citations are
in [`design-notes/homo-silicus.md`](design-notes/homo-silicus.md).
