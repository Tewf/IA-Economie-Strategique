"""The panel of local models, and the budget they have to fit in.

Config, not code. Nothing here calls anything. The numbers are what
`GET /api/tags` reported on this machine, so they are disk size rather than
resident size, and resident is larger.

The card is an RTX 4060 Mobile with 8 GB. Every model below fits alone and no
two fit together, so any run over the panel is sequential by model. Ollama
unloads on its own after an idle period, but a run that switches models in a
tight loop will thrash, so switch in the outer loop.
"""

OLLAMA_HOST = "http://127.0.0.1:11434"

# name -> what it is, and the gigabytes it takes on disk.
PANEL = {
    "qwen3:8b": ("8.2B, the largest that fits", 5.23),
    "qwen2.5:7b-instruct": ("7.6B, instruction tuned", 4.68),
    "mistral:7b": ("7.2B, a different family", 4.37),
    "gemma3:4b": ("4.3B, Google's small one", 3.34),
    "phi3:mini": ("3.8B, the smallest useful one", 2.18),
}

# Deterministic by default. Horton's method is about what a model does by
# disposition, and a sampled reply measures the sampler as much as the model.
# Vary this deliberately, per experiment, and record that you did.
TEMPERATURE = 0.0
SEED = 0

# Long enough for an action plus a sentence of reasoning, short enough that a
# model that starts writing an essay is cut off rather than left running.
MAX_TOKENS = 300

# Ollama holds the request open while it loads the model from disk, and the
# first call to a cold model on this machine is far slower than the rest.
REQUEST_TIMEOUT_SECONDS = 300
