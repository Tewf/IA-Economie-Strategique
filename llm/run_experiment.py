"""Play the grid and append each finished match to the raw log.

    python llm/run_experiment.py --plan            # the grid and its cost, no GPU
    python llm/run_experiment.py --stages          # what each model has left
    python llm/run_experiment.py --model gemma3:4b # play one stage, then stop
    python llm/run_experiment.py                   # the lot, hours of GPU

**Run it one stage at a time.** A stage is one model, thirty to sixty minutes,
and the grid loops model-outermost so stopping between them costs nothing. Three
hours unattended is what cooked the machine.

**Resumable by construction.** Each match is keyed, the key is written with the
match, and a key already in the log is skipped. A crash at hour three costs the
match in flight and nothing else, which matters because the last run of anything
like this took the machine down.

Whether the machine can take another match is [`machine_gate.py`](machine_gate.py),
and who holds the card while it does is [`run_ownership.py`](run_ownership.py).
Nothing here derives a result. The log is raw and stays raw: `measurements.py`
turns it into tables, so a mistake in the analysis costs a rerun of a few
seconds of arithmetic instead of a night on the card.
"""

import json
import pathlib
import sys
import time

import grid_config
import prompt_loader
from bot_opponent import BotOpponent
from iterated_game import play_match
from machine_gate import (OutOfHeadroom, check_can_start, check_headroom,
                          cool_down, instant_package_c, package_temperature_c,
                          throttle_count)
from ollama_player import OllamaPlayer, UnparseableReply
from panel_config import BASE_SEED, PANEL
from run_ownership import owning_the_run, read_owner

RESULTS = pathlib.Path(__file__).parent / "results"
LOG = RESULTS / "matches.jsonl"
PROMPTS_USED = RESULTS / "prompts_used.json"
GAME_NAME = "prisoners_dilemma"

# The pair is handed one finished round before it starts, which is the closest
# thing a language model has to the Hebbian agent's starting weight: a regime it
# inherits rather than chooses. "neutral" hands it nothing.
OPENINGS = {
    "neutral": None,
    "mutual_cooperation": ("Cooperate", "Cooperate"),
    "mutual_defection": ("Defect", "Defect"),
}


def build_grid():
    """Every match to play, as plain dicts. No player is constructed here."""
    specs = []
    for model in PANEL:
        for condition in grid_config.CONDITIONS:
            for opening in OPENINGS:
                for repetition in range(grid_config.REPETITIONS):
                    specs.append({"cell": "self_play", "model": model,
                                  "opponent": model, "condition": condition,
                                  "opening": opening, "repetition": repetition})
        for strategy in grid_config.BOT_OPPONENTS:
            for repetition in range(grid_config.REPETITIONS):
                specs.append({"cell": "vs_bot", "model": model,
                              "opponent": strategy.name,
                              "condition": "without_cheap_talk",
                              "opening": "neutral", "repetition": repetition})
    return specs


def key_of(spec):
    return "|".join(str(spec[field]) for field in
                    ("cell", "model", "opponent", "condition", "opening",
                     "repetition"))


def already_done(log=LOG):
    """Keys in the log. Tolerates a truncated last line from a killed run."""
    if not log.exists():
        return set()
    done = set()
    for line in log.read_text().splitlines():
        try:
            done.add(json.loads(line)["key"])
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def write_prompts_used(path=PROMPTS_USED):
    """Pin the four system prompts a run was played on, once, beside the log.

    In this method the prompt is the experiment, so it has to be in the record
    and not only in the source that rendered it. Four texts cover the grid: an
    action turn and a message turn, each in both payoff orderings, which is what
    `grid_config.REPETITIONS` counterbalances. A match names its own by
    `repetition` parity, so nothing has to be repeated per match.

    This is deliberately the opposite of what the log used to do. It stored the
    per-round user message, which is `OllamaPlayer._round_prompt` applied to
    rounds the record already holds, 60 times a match and growing with the
    match; prompt echoes were 94% of the log and the system prompt was absent.
    """
    path.parent.mkdir(exist_ok=True)
    rendered = {
        f"{asking_for}|{'even' if parity == 0 else 'odd'}_repetition":
            prompt_loader.render(GAME_NAME, parity, asking_for)
        for asking_for in ("action", "message") for parity in (0, 1)}
    path.write_text(json.dumps({"game": GAME_NAME, "prompts": rendered},
                               indent=2) + "\n")
    return rendered


def apply_opening(player, opening):
    """Hand a player one finished round it did not play."""
    if OPENINGS[opening] is None:
        return
    mine, theirs = OPENINGS[opening]
    player.own_history.append(mine)
    player.history.append(theirs)


def make_players(spec):
    """The two players for one spec. The only place a model is constructed."""
    system = prompt_loader.render(GAME_NAME, spec["repetition"], "action")
    message_system = prompt_loader.render(GAME_NAME, spec["repetition"], "message")
    seed_of = (lambda seat: grid_config.player_seed(
        BASE_SEED, spec["condition"], spec["model"], spec["repetition"], seat))
    player_a = OllamaPlayer(spec["model"], system, seed=seed_of("a"),
                            message_prompt=message_system)
    if spec["cell"] == "vs_bot":
        strategy = next(s for s in grid_config.BOT_OPPONENTS
                        if s.name == spec["opponent"])
        player_b = BotOpponent(strategy, seed=seed_of("b"))
    else:
        player_b = OllamaPlayer(spec["model"], system, seed=seed_of("b"),
                                message_prompt=message_system)
    for player in (player_a, player_b):
        apply_opening(player, spec["opening"])
    return player_a, player_b


def play_one(spec, make=make_players):
    """One match, as the record that gets appended. `make` is injectable so the
    whole runner can be exercised with stub players and no GPU.

    A model that answers with prose where an action was asked loses the match,
    and that is a result about the model rather than an error to hide. **How
    far it got before that is what makes the result readable**: failing in
    round 1 of every match is "cannot hold the format at all", and failing in
    round 20 is "loses the format as the context grows", which are different
    findings and the second is the one this folder's own literature note says
    to watch for. phi3:mini produced the first such reply on 2026-08-17, a
    cheap-talk message written on an action turn, and the record as it stood
    could not tell the two apart.
    """
    started = time.monotonic()
    player_a, player_b = make(spec)
    common = {**spec, "key": key_of(spec)}
    try:
        record = play_match(player_a, player_b, rounds=grid_config.ROUNDS,
                            game=grid_config.GAME,
                            cheap_talk=spec["condition"] == "with_cheap_talk")
    except UnparseableReply as failure:
        # **Keep the reply that lost the match, not only the fact that one did.**
        # A lost match used to record how far it got and nothing else, so when
        # qwen3 lost two matches to an empty answer on 2026-08-18 there was no
        # way to see whether the reasoning had run long, the answer had been
        # truncated, or the prompt had grown past the window. The transcript is
        # the evidence and it was being discarded at exactly the moment it
        # mattered. Only the tail is kept: the whole thing is what made prompt
        # echoes 94% of an earlier log.
        seats = {}
        for name, player in (("a", player_a), ("b", player_b)):
            tail = getattr(player, "transcript", [])[-2:]
            if tail:
                seats[f"{name}_last_replies"] = tail
        record = {"failed": str(failure),
                  "rounds_completed": min(len(player_a.own_history),
                                          len(player_b.own_history)),
                  **seats}
    return {**common,
            "seconds": round(time.monotonic() - started, 2),
            # Sampled the instant the match ends, which is the closest cheap
            # proxy for its peak. Recorded so "the grid reaches 93 C on its own"
            # stays a measurement rather than becoming folklore.
            "package_c_at_end": instant_package_c(),
            **record}


def stages(log=LOG):
    """Each model, and how many of its matches are still to play.

    One model is one stage. `build_grid` loops model-outermost, so stopping
    between them costs nothing and a stage is the natural unit of exposure:
    thirty to sixty minutes rather than three hours.
    """
    done = already_done(log)
    remaining = {}
    for spec in build_grid():
        if key_of(spec) not in done:
            remaining[spec["model"]] = remaining.get(spec["model"], 0) + 1
    return remaining


def run_stage(model, log=LOG):
    """Play one model's matches and stop, holding the run against a second launch."""
    remaining = stages(log)
    if model not in remaining:
        raise SystemExit(f"nothing left for {model!r}. Stages: {list(remaining)}")
    check_can_start()
    before = throttle_count()
    with owning_the_run(model):
        print(f"stage {model}: {remaining[model]} matches to play, "
              f"package {package_temperature_c()} C, throttles so far {before}")
        run([spec for spec in build_grid() if spec["model"] == model], log=log)
    after = throttle_count()
    if before is not None and after is not None:
        print(f"stage {model} done. Package throttled {after - before} times "
              f"during it ({before} to {after}), now {package_temperature_c()} C.")


def _close_any_partial_line(log):
    """End the log on a newline before appending to it.

    A process killed mid-write leaves a line with no newline. Appending the next
    record straight onto it would splice two matches into one unreadable line
    and lose the good one too, so the broken half is terminated first and left
    in place: `already_done` skips it, and it is evidence a run was interrupted.
    """
    if log.exists() and log.stat().st_size and not log.read_bytes().endswith(b"\n"):
        with open(log, "a") as handle:
            handle.write("\n")


def run(specs=None, make=make_players, log=LOG, gate=check_headroom):
    """Play everything not already in the log, appending as each finishes.

    `gate` is what decides the machine can take another match. It defaults
    to the real check and is replaced by a no-op in the offline checks,
    which drive stub players and touch neither the card nor the CPU: a
    thermal gate there would fail the test suite whenever some other
    session happened to be busy, which is exactly backwards.
    """
    specs = build_grid() if specs is None else specs
    done = already_done(log)
    todo = [spec for spec in specs if key_of(spec) not in done]
    print(f"{len(specs)} matches in the grid, {len(done)} already done, "
          f"{len(todo)} to play")
    log.parent.mkdir(exist_ok=True)
    _close_any_partial_line(log)
    for index, spec in enumerate(todo, start=1):
        if index > 1:
            waited, settled = cool_down()
            if waited:
                print(f"    cooled {waited}s to {settled} C")
        gate()
        # Carrying on past a lost match is the difference between a reported
        # failure rate and a run that dies at hour three on its first bad
        # reply. `play_one` turns the loss into a record rather than raising.
        record = play_one(spec, make)
        outcome = (f"UNPARSEABLE after {record['rounds_completed']} rounds"
                   if "failed" in record
                   else f"{record['a_total']}-{record['b_total']}")
        with open(log, "a") as handle:
            handle.write(json.dumps(record) + "\n")
        print(f"  [{index}/{len(todo)}] {record['key']} {outcome} "
              f"in {record['seconds']}s")


def calls_in(spec):
    """Model calls one match costs. Cheap talk doubles it: a message and an action."""
    if spec["condition"] == "with_cheap_talk":
        return grid_config.ROUNDS * 4
    return grid_config.ROUNDS * (2 if spec["cell"] == "self_play" else 1)


def calls_per_model(specs=None):
    """Calls each model owes, which is what an hours estimate has to be built on.

    A total is not enough. The models do not answer at the same speed, and the
    slowest one here is several times the fastest, so a grid priced on an
    average is priced on a model that does not exist.
    """
    specs = build_grid() if specs is None else specs
    owed = {}
    for spec in specs:
        owed[spec["model"]] = owed.get(spec["model"], 0) + calls_in(spec)
    return owed


def hours_at(rates, specs=None):
    """Hours the grid would take, given seconds per call for each model."""
    owed = calls_per_model(specs)
    return sum(count * rates.get(model, 0) for model, count in owed.items()) / 3600


def describe(specs=None):
    """The grid, without playing it or loading a model."""
    specs = build_grid() if specs is None else specs
    talking = sum(s["condition"] == "with_cheap_talk" for s in specs)
    owed = calls_per_model(specs)
    print(f"{len(specs)} matches, {talking} of them with cheap talk")
    print(f"{grid_config.ROUNDS} rounds each, {sum(owed.values())} model calls")
    for cell in ("self_play", "vs_bot"):
        print(f"  {cell}: {sum(s['cell'] == cell for s in specs)}")
    print("  calls per model: " + ", ".join(f"{m} {c}" for m, c in owed.items()))
    # Measured on this card by `preflight_checks.py --online`, so the spread is
    # a bracket around a real rate rather than a guess.
    for label, rate in (("fast, 0.5 s a call", 0.5), ("1.0 s", 1.0),
                        ("slow, 2.0 s", 2.0)):
        flat = {model: rate for model in owed}
        print(f"  at {label:20} {hours_at(flat, specs):.1f} h")
    print(f"already done: {len(already_done())}")


def show_stages():
    """What is left, by stage, and whether the machine will let one start."""
    remaining = stages()
    print(f"{sum(remaining.values())} matches left, by stage:")
    for model, count in remaining.items():
        print(f"  {model:24} {count:>3}")
    live = read_owner()
    if live:
        print(f"\nrunning now: stage {live.get('stage')} as PID {live['pid']}")
    try:
        check_can_start()
        print(f"\nthe machine will allow a stage to start "
              f"({package_temperature_c()} C).")
    except OutOfHeadroom as refusal:
        print(f"\nthe machine will refuse a stage right now: {refusal}")


if __name__ == "__main__":
    if "--plan" in sys.argv:
        describe()
    elif "--stages" in sys.argv:
        show_stages()
    elif "--model" in sys.argv:
        write_prompts_used()
        run_stage(sys.argv[sys.argv.index("--model") + 1])
    else:
        write_prompts_used()
        run()
