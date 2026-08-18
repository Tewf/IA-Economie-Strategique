"""The Dictator and Ultimatum games, which are one decision rather than thirty.

    python llm/one_shot_games.py --plan
    python llm/one_shot_games.py            # the lot, minutes rather than hours

**Why these live here and not in a shared home.** The repository deferred them
because both folders were thought to need them, which would make where they live
a structural decision rather than a file to write. Reading
[`../mirror_neurons/design-notes/what-the-agent-cannot-do.md`](../mirror_neurons/design-notes/what-the-agent-cannot-do.md)
settles it: in the Dictator game the imitator is **mute**, since the recipient
never acts and so there is nothing to imitate, and as an Ultimatum responder it
would need a kernel across neighbouring offers that nothing in the literature
fixes. A language model has the opposite profile, because the situation is
describable in words even when no one has acted. The game where the imitator has
no input is exactly the game where the model is unhampered, so there is no shared
harness to design and this one belongs to `llm/` alone.

**What the pair of games measures, which neither measures alone.** The Dictator
game removes the rejection, so nothing strategic is left and what an allocator
offers is disposition. The Ultimatum proposer faces the same split with a
refusal possible. The difference between the two offers is what a model gives in
order not to be refused, and reporting either number on its own says very little.
The responder's stated minimum completes it, and is asked before any proposal is
shown so it cannot be an accommodation to one.

Design follows Özkes et al. (2024), cited in `prompts/ultimatum.md`: an endowment
of 100 points, the proposer's offer and the responder's minimum acceptable offer.
Their partner conditions are not run here.
"""

import json
import pathlib
import re
import sys
import time

import grid_config
import prompt_loader
from machine_gate import check_can_start, check_headroom, cool_down, instant_package_c
from ollama_player import ask_once
from panel_config import BASE_SEED, CONTEXT_TOKENS, PANEL
from run_ownership import owning_the_run

RESULTS = pathlib.Path(__file__).parent / "results"
LOG = RESULTS / "one_shot.jsonl"

# One decision, one short answer. The iterated game's 300 is already generous
# for "a number and one sentence", and qwen3 is given room because it reasons
# in the open like everywhere else.
MAX_TOKENS = {"qwen3:8b": 2000}
DEFAULT_MAX_TOKENS = 300

# Each is a game, the role played, and the field the answer must carry.
DECISIONS = [
    ("dictator", "", "OFFER"),
    ("ultimatum", "proposer", "OFFER"),
    ("ultimatum", "responder", "MINIMUM"),
]
ASK = ("This is your decision. Answer in exactly the format you were given, "
       "and nothing else.")


def build_plan():
    """Every decision to make, as plain dicts."""
    return [{"game": game, "role": role, "field": field, "model": model,
             "repetition": repetition}
            for model in PANEL
            for game, role, field in DECISIONS
            for repetition in range(grid_config.REPETITIONS)]


def key_of(spec):
    return "|".join(str(spec[field]) for field in
                    ("game", "role", "model", "repetition"))


def already_done(log=LOG):
    if not log.exists():
        return set()
    done = set()
    for line in log.read_text().splitlines():
        try:
            done.add(json.loads(line)["key"])
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def read_number(text, field):
    """The number on the field's line, or the first number anywhere.

    Same policy as the iterated game's action parsing: the strict read is the
    line the prompt asked for, a looser read is recorded as a fallback rather
    than silently accepted, and neither is allowed to invent a value. An offer
    outside 0 to 100 is not clipped, because a model that answers 150 has not
    understood the endowment and clipping would hide that.
    """
    strict = re.search(rf"{field}\s*:\s*(-?\d+)", text, re.IGNORECASE)
    if strict:
        return int(strict.group(1)), False
    loose = re.search(r"-?\d+", text)
    if loose:
        return int(loose.group()), True
    return None, False


def play_one(spec, ask=ask_once):
    """One decision, as the record that gets appended."""
    system = prompt_loader.render_one_shot(spec["game"], spec["role"])
    seed = grid_config.player_seed(BASE_SEED, spec["game"], spec["model"],
                                   spec["repetition"], spec["role"] or "only")
    started = time.monotonic()
    reply = ask(spec["model"], system, ASK, seed=seed,
                max_tokens=MAX_TOKENS.get(spec["model"], DEFAULT_MAX_TOKENS),
                context_tokens=CONTEXT_TOKENS,
                think=PANEL.get(spec["model"], {}).get("think", False))
    value, loose = read_number(reply.get("content", ""), spec["field"])
    return {**spec, "key": key_of(spec), "value": value, "loose_read": loose,
            "reply": reply,
            "seconds": round(time.monotonic() - started, 2),
            "package_c_at_end": instant_package_c()}


def run(specs=None, log=LOG, ask=ask_once, gate=check_headroom):
    specs = build_plan() if specs is None else specs
    done = already_done(log)
    todo = [spec for spec in specs if key_of(spec) not in done]
    print(f"{len(specs)} decisions, {len(done)} already made, {len(todo)} to make")
    log.parent.mkdir(exist_ok=True)
    for index, spec in enumerate(todo, start=1):
        if index > 1:
            cool_down()
        gate()
        record = play_one(spec, ask)
        with open(log, "a") as handle:
            handle.write(json.dumps(record) + "\n")
        shown = "unparseable" if record["value"] is None else record["value"]
        print(f"  [{index}/{len(todo)}] {record['key']} -> {shown}"
              f"{' (loose)' if record['loose_read'] else ''} "
              f"in {record['seconds']}s")


def describe():
    plan = build_plan()
    print(f"{len(plan)} decisions: {len(PANEL)} models x {len(DECISIONS)} "
          f"decisions x {grid_config.REPETITIONS} repetitions")
    for game, role, field in DECISIONS:
        print(f"  {game} {role or '(single role)'}: answers with {field}")
    print(f"One call each, against thirty for a match of the iterated game, so "
          f"this is minutes of card time rather than hours.")


if __name__ == "__main__":
    if "--plan" in sys.argv:
        describe()
    else:
        check_can_start()
        with owning_the_run("one-shot games"):
            run()
