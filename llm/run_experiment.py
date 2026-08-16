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

Nothing here derives a result. The log is raw and stays raw: `measurements.py`
turns it into tables, so a mistake in the analysis costs a rerun of a few
seconds of arithmetic instead of a night on the card.
"""

import contextlib
import datetime
import json
import os
import pathlib
import sys
import time

import grid_config
import prompt_loader
from bot_opponent import BotOpponent
from iterated_game import play_match
from ollama_player import OllamaPlayer, UnparseableReply
from panel_config import BASE_SEED, PANEL

LOG = pathlib.Path(__file__).parent / "results" / "matches.jsonl"
OWNER = pathlib.Path(__file__).parent / "results" / ".running"
GAME_NAME = "prisoners_dilemma"

# Floors below which the run stops rather than pressing on. Chosen from what
# the machine looked like when it died: swap at zero and RAM exhausted.
MINIMUM_MEMORY_GIB = 1.5
MINIMUM_SWAP_GIB = 1.0
# The machine idles near 52 C. One pinned core from any other session puts
# it at 79-87 C, so anything above this means the grid does not fit beside
# whatever else is running.
MAXIMUM_TEMPERATURE_C = 70

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


class OutOfHeadroom(RuntimeError):
    """Stopped before the machine ran out, not after."""


def headroom():
    """Available RAM and free swap, in GiB, as the kernel reports them."""
    fields = {}
    for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
        name, _, value = line.partition(":")
        fields[name] = int(value.split()[0]) / (1024 ** 2)
    return fields["MemAvailable"], fields["SwapFree"]


def package_temperature_c():
    """Hottest CPU package the kernel reports, or None if no sensor says.

    Read from `coretemp` rather than a thermal zone, because the zones on this
    board include the battery and the wifi card and the numbers are not
    comparable.
    """
    hottest = None
    for chip in pathlib.Path("/sys/class/hwmon").iterdir():
        try:
            if (chip / "name").read_text().strip() != "coretemp":
                continue
            for label in chip.glob("temp*_label"):
                if not label.read_text().startswith("Package"):
                    continue
                reading = int((chip / label.name.replace("_label", "_input")
                               ).read_text())
                hottest = max(hottest or 0, reading // 1000)
        except OSError:
            continue
    return hottest


def throttle_count():
    """Times the package has been throttled since boot, or None."""
    counter = pathlib.Path("/sys/devices/system/cpu/cpu0/thermal_throttle/"
                           "package_throttle_count")
    return int(counter.read_text()) if counter.exists() else None


def check_headroom():
    """Refuse to start another match if the machine is running out of anything.

    Memory, because that is what took the machine down on 2026-08-15: swap hit
    zero, the OOM killer fired, and the GPU fell off the bus behind it while the
    card still reported 7.6 GiB free. Watching VRAM would not have caught it.

    Temperature, because this chassis has none to spare. It idles at 52 C and
    one pinned core from any other session holds it at 79-87 C, so a package
    above the ceiling means something else is running and the grid does not fit
    beside it. Checked every match and not only at the start, so a stage that
    heats up under a neighbour stops instead of running on throttled and
    reporting timings that mean nothing.

    Stopping is cheap because the run is resumable: every finished match is
    already in the log, so an abort costs the match in flight.
    """
    memory, swap = headroom()
    if memory < MINIMUM_MEMORY_GIB or swap < MINIMUM_SWAP_GIB:
        raise OutOfHeadroom(
            f"stopping with {memory:.1f} GiB RAM and {swap:.1f} GiB swap free, "
            f"below the {MINIMUM_MEMORY_GIB}/{MINIMUM_SWAP_GIB} GiB floor. "
            f"Finished matches are in the log; rerun to resume.")
    temperature = package_temperature_c()
    if temperature is not None and temperature > MAXIMUM_TEMPERATURE_C:
        raise OutOfHeadroom(
            f"stopping at {temperature} C package, above the "
            f"{MAXIMUM_TEMPERATURE_C} C ceiling. Something else is running: "
            f"this machine idles near 52 C. Finished matches are in the log.")


class AlreadyRunning(RuntimeError):
    """Another stage owns the card. Two at once is how the log got raced."""


def _owner_is_alive(owner):
    try:
        os.kill(int(owner["pid"]), 0)
    except (OSError, ValueError, KeyError):
        return False
    return True


def read_owner(marker=OWNER):
    """Who is running a stage right now, or None."""
    if not marker.exists():
        return None
    try:
        owner = json.loads(marker.read_text())
    except json.JSONDecodeError:
        return None
    return owner if _owner_is_alive(owner) else None


@contextlib.contextmanager
def owning_the_run(stage, marker=OWNER):
    """Claim the run, and say on disk and on screen who holds it.

    On 2026-08-16 the grid was launched three times and killed twice inside
    seventeen minutes, by a session and by that session's own subagent, neither
    able to see the other. Two separate failures, and this addresses both.

    It refuses a second launch while one is live, which is the overlap that
    produced the race. And it names the owner where anyone reaching for a
    `pkill` will look, because the agent that killed this was right that
    something hot needed stopping and wrong that it could decide alone.
    """
    live = read_owner(marker)
    if live is not None:
        raise AlreadyRunning(
            f"stage {live.get('stage')} is already running as PID {live['pid']}, "
            f"started {live.get('started')} by {live.get('owner')}. "
            f"Wait for it, or ask its owner to stop it. Do not kill it blind.")
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(json.dumps({
        "pid": os.getpid(), "stage": stage,
        "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "owner": os.environ.get("CLAUDE_SESSION_ID", "unknown session"),
        "note": "ask the owner before killing this; it holds the GPU for ~an hour",
    }, indent=2) + "\n")
    print(f"owner: PID {os.getpid()} holds stage {stage}. "
          f"{marker} names it; ask before killing.")
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)


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
    whole runner can be exercised with stub players and no GPU."""
    started = time.monotonic()
    player_a, player_b = make(spec)
    record = play_match(player_a, player_b, rounds=grid_config.ROUNDS,
                        game=grid_config.GAME,
                        cheap_talk=spec["condition"] == "with_cheap_talk")
    return {**spec, "key": key_of(spec), "seconds": round(time.monotonic() - started, 2),
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
    before = throttle_count()
    with owning_the_run(model):
        print(f"stage {model}: {remaining[model]} matches to play, "
              f"package {package_temperature_c()} C, throttles so far {before}")
        run([spec for spec in build_grid() if spec["model"] == model], log=log)
    after = throttle_count()
    if before is not None and after is not None:
        print(f"stage {model} done. Package throttled {after - before} times "
              f"during it ({before} to {after}), now {package_temperature_c()} C.")


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
        gate()
        # A model that answers with prose where an action was asked loses its
        # match, and that is a result about the model. Recording it and carrying
        # on is the difference between a reported failure rate and a run that
        # dies at hour three on its first bad reply.
        try:
            record = play_one(spec, make)
            outcome = f"{record['a_total']}-{record['b_total']}"
        except UnparseableReply as failure:
            record = {**spec, "key": key_of(spec), "failed": str(failure)}
            outcome = "UNPARSEABLE"
        with open(log, "a") as handle:
            handle.write(json.dumps(record) + "\n")
        print(f"  [{index}/{len(todo)}] {record['key']} {outcome}"
              f"{' in ' + str(record['seconds']) + 's' if 'seconds' in record else ''}")


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
    # No rate has been measured on this card yet, so the spread is the honest
    # answer until `preflight_checks.py --online` replaces it with one.
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
        check_headroom()
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
        run_stage(sys.argv[sys.argv.index("--model") + 1])
    else:
        run()
