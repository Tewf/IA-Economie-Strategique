"""The panel of local models, and how each one is sampled.

Config, not code. Nothing here calls anything. The sizes are what
`GET /api/tags` reported on this machine, so they are disk size rather than
resident size, and resident is larger.

The card is an RTX 4060 Mobile with 8 GB. Every model below fits alone and no
two fit together, so any run over the panel is sequential by model. A run that
switches models in a tight loop thrashes the card badly enough to take the
machine down, which it did on 2026-08-15, so switch in the outer loop and never
in the inner one.

What matches get played is in `grid_config.py`. This file is only the players.
"""

OLLAMA_HOST = "http://127.0.0.1:11434"

# **Set explicitly, because Ollama's default silently rewrites the experiment.**
# Ollama serves a model at `num_ctx` 4096 regardless of what the model supports,
# and a prompt over that is not refused, it is cut: `msg="truncating input
# prompt" limit=4096 prompt=4430 keep=4`. `keep=4` is the whole problem. What
# gets cut is the *oldest* part of the input, which is the system prompt, so a
# long match quietly continues without the scenario or the answer format in it
# at all, and the model's reply stops being an answer to the experiment.
#
# It bit phi3:mini on 2026-08-17, seven calls between 09:29 and 11:12. The
# visible symptom was 53 s a call against 0.78 s measured, because a truncated
# prefix invalidates the cache and re-evaluates 4096 tokens every turn; the
# invisible one was matches recorded as the model failing to hold a format it
# was no longer being shown. The two completed stages were checked against the
# same journal and had none.
#
# 8192 covers the longest prompt seen here with room for the reply, and every
# model in this panel still loads 100% on the card at that size.
CONTEXT_TOKENS = 8192

# Per model: what it is, gigabytes on disk, its token budget, and whether it is
# asked to think. A reasoning model needs room for the reasoning plus the answer,
# and 300 tokens truncates qwen3 mid-thought and yields an unparseable reply.
PANEL = {
    "qwen3:8b": {
        "description": "8.2B, the largest that fits, and the only one that "
                       "returns reasoning in a separate field",
        "gigabytes": 5.23,
        "max_tokens": 2000,
        "think": False,
    },
    "qwen2.5:7b-instruct": {
        "description": "7.6B, instruction tuned",
        "gigabytes": 4.68,
        "max_tokens": 300,
        "think": False,
    },
    "mistral:7b": {
        "description": "7.2B, a different family",
        "gigabytes": 4.37,
        "max_tokens": 300,
        "think": False,
    },
    "gemma3:4b": {
        "description": "4.3B, Google's small one",
        "gigabytes": 3.34,
        "max_tokens": 300,
        "think": False,
    },
    "phi3:mini": {
        "description": "3.8B, the smallest useful one",
        "gigabytes": 2.18,
        "max_tokens": 300,
        "think": False,
    },
}

# `think` is a treatment rather than a setting. qwen3 takes 34 s a call with it
# on against 1.9 s with it off, and flipped from Defect to Cooperate on a single
# first-round call, so the contrast is worth running deliberately and separately
# rather than leaving on through a grid it would add days to.
REASONING_CONTRAST_MODEL = "qwen3:8b"

# **Not zero, and this overrides the original reasoning here.** Horton's method
# is about what a model does by disposition, which argues for greedy decoding.
# But greedy decoding is a function of the prompt alone: in self-play both sides
# hold the same prompt, so both emit the identical message and the identical
# action, forever, and the seed cannot separate them because nothing is sampled.
# A degenerate match measures nothing at all, which is worse than sampling noise.
TEMPERATURE = 0.7

# The base a per-player seed is derived from, in `grid_config.player_seed`.
BASE_SEED = 0

# Ollama holds the request open while it loads the model from disk, and the
# first call to a cold model on this machine is far slower than the rest.
REQUEST_TIMEOUT_SECONDS = 300
