"""Follow-up arms that answer one question each, kept out of the grid.

    python llm/run_contrasts.py --list
    python llm/run_contrasts.py --contrast phi3-quantisation

**These write to `results/contrasts.jsonl`, never to `results/matches.jsonl`.**
The grid is 220 matches over five declared models, and it stays 220: an arm run
afterwards to answer a confound is a follow-up, not more of the same experiment,
and folding it into the main tables would quietly change what the headline
numbers are averaging over. `measurements.py` reads only the grid; the contrast
tables are derived beside it.

**Each arm holds the seed stream of the run it is compared against.** A seed here
is derived from the model *name*, so a contrast that simply used its own name
would differ from its control in two ways at once and settle nothing. `seed_as`
pins the stream to the original, leaving exactly one thing changed.
"""

import pathlib
import sys

import grid_config
import prompt_loader
import run_experiment
from machine_gate import check_can_start, package_temperature_c, throttle_count
from ollama_player import OllamaPlayer
from panel_config import BASE_SEED
from run_ownership import owning_the_run

RESULTS = pathlib.Path(__file__).parent / "results"
LOG = RESULTS / "contrasts.jsonl"

CONTRASTS = {
    # **This arm did not measure what it was named for, and the name is kept so
    # the log stays honest.** It was written to vary quantisation alone, on the
    # belief that `phi3:mini` is the 4k build. It is not: `phi3:mini` resolves to
    # the 128k variant (`phi3.context_length` 131072), and the build pulled here
    # is 4096. The grid asks for `num_ctx` 8192, so this arm ran a 4k model at
    # twice its trained window, and its 75% loss rate says so. The same mistake
    # the panel already documents, made again: a tag is not a version, and
    # "mini" names a family rather than a context length.
    "phi3-quantisation": {
        "question": "Does a 4k build survive being asked for an 8192-token window?",
        "why": (
            "Intended as the quantisation control and mis-specified. It varies "
            "quantisation AND context length at once, so it answers neither "
            "cleanly; what it does show is that a 4096-context build asked for "
            "8192 fails 33 of 44 matches against the original's 10. Kept because "
            "the run happened and deleting an inconvenient arm is worse than "
            "labelling it. The control it was meant to be is the next entry."),
        "varies": "quantisation and context length",
        "model": "phi3:3.8b-mini-4k-instruct-q4_K_M",
        "seed_as": "phi3:mini",
        "compare_with": "phi3:mini",
        "think": False,
        "max_tokens": 300,
        "select": lambda spec: spec["model"] == "phi3:mini",
    },
    "phi3-quantisation-matched": {
        "question": "Are phi3's unparseable replies the model, or its quantisation?",
        "why": (
            "The control the arm above was meant to be. `phi3:mini` is the 128k "
            "variant at Q4_0, so the only build that isolates quantisation is the "
            "128k variant at Q4_K_M: same weights, same 131072 context, same "
            "seeds, same prompts, one thing changed. Answered 2026-08-18: 4 of "
            "44 against the original's 10 of 44, so the coarser packing is much "
            "of why phi3 could not hold an answer format. Not all of it, since 4 "
            "of 44 is still the only non-zero loss rate in the panel."),
        "varies": "quantisation only",
        "model": "phi3:3.8b-mini-128k-instruct-q4_K_M",
        "seed_as": "phi3:mini",
        "compare_with": "phi3:mini",
        "think": False,
        "max_tokens": 300,
        "select": lambda spec: spec["model"] == "phi3:mini",
    },
    "qwen3-think": {
        "question": "Does explicit reasoning change whether qwen3 leaves an imposed regime?",
        "why": (
            "qwen3:8b is the panel's hardest case: it never cooperates with any "
            "bot, defects from a neutral silent start, and a message does not move "
            "it. `panel_config.REASONING_CONTRAST_MODEL` names it for a deliberate "
            "contrast that the grid deliberately did not run, because thinking "
            "costs it 34 s a call against 1.9 s and would have added days. Liu et "
            "al. report that ablating chain-of-thought often *reduces* a "
            "cooperation collapse, so turning it on is the sharper test: it should "
            "make this worse, and if it makes it better the mechanism is not what "
            "that paper describes."),
        "model": "qwen3:8b",
        "seed_as": "qwen3:8b",
        "compare_with": "qwen3:8b",
        "think": True,
        # A reasoning model needs room for the reasoning and the answer; 300
        # truncates qwen3 mid-thought and the reply parses as nothing.
        "max_tokens": 2000,
        "select": lambda spec: (spec["model"] == "qwen3:8b"
                                and spec["cell"] == "self_play"
                                and spec["opening"] == "mutual_defection"),
    },
}


def specs_for(name):
    """The contrast's matches, tagged so a record says which arm it belongs to."""
    arm = CONTRASTS[name]
    specs = []
    for spec in run_experiment.build_grid():
        if not arm["select"](spec):
            continue
        specs.append({**spec, "model": arm["model"],
                      "opponent": (arm["model"] if spec["cell"] == "self_play"
                                   else spec["opponent"]),
                      "contrast": name})
    return specs


def make_players_for(name):
    """`make_players`, with the arm's settings and the control's seed stream."""
    arm = CONTRASTS[name]

    def make(spec):
        system = prompt_loader.render(run_experiment.GAME_NAME,
                                      spec["repetition"], "action")
        message_system = prompt_loader.render(run_experiment.GAME_NAME,
                                              spec["repetition"], "message")
        seed_of = (lambda seat: grid_config.player_seed(
            BASE_SEED, spec["condition"], arm["seed_as"], spec["repetition"], seat))
        built = []
        for seat in ("a", "b"):
            built.append(OllamaPlayer(arm["model"], system, seed=seed_of(seat),
                                      message_prompt=message_system,
                                      max_tokens=arm["max_tokens"],
                                      think=arm["think"]))
        if spec["cell"] == "vs_bot":
            strategy = next(s for s in grid_config.BOT_OPPONENTS
                            if s.name == spec["opponent"])
            built[1] = run_experiment.BotOpponent(strategy, seed=seed_of("b"))
        for player in built:
            run_experiment.apply_opening(player, spec["opening"])
        return built[0], built[1]

    return make


def run_contrast(name, log=LOG):
    arm = CONTRASTS[name]
    specs = specs_for(name)
    check_can_start()
    before = throttle_count()
    with owning_the_run(f"contrast:{name}"):
        print(f"contrast {name}: {arm['question']}")
        print(f"  {arm['model']}, seeded as {arm['seed_as']}, "
              f"{len(specs)} matches, package {package_temperature_c()} C")
        run_experiment.run(specs, make=make_players_for(name), log=log)
    after = throttle_count()
    if before is not None and after is not None:
        print(f"contrast {name} done. Package throttled {after - before} times.")


def show():
    done = run_experiment.already_done(LOG)
    for name, arm in CONTRASTS.items():
        specs = specs_for(name)
        left = [s for s in specs if run_experiment.key_of(s) not in done]
        print(f"{name}: {len(specs) - len(left)}/{len(specs)} played "
              f"against {arm['compare_with']}")
        print(f"    {arm['question']}")


if __name__ == "__main__":
    if "--contrast" in sys.argv:
        run_contrast(sys.argv[sys.argv.index("--contrast") + 1])
    else:
        show()
