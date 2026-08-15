"""Play the grid and append each finished match to the raw log.

    python llm/run_experiment.py          # needs Ollama, hours of GPU
    python llm/run_experiment.py --plan   # prints the grid and stops, no GPU

**Resumable by construction.** Each match is keyed, the key is written with the
match, and a key already in the log is skipped. A crash at hour three costs the
match in flight and nothing else, which matters because the last run of anything
like this took the machine down.

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
from ollama_player import OllamaPlayer, UnparseableReply
from panel_config import BASE_SEED, PANEL

LOG = pathlib.Path(__file__).parent / "results" / "matches.jsonl"
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
    system = prompt_loader.render(GAME_NAME, spec["repetition"])
    seed_of = (lambda seat: grid_config.player_seed(
        BASE_SEED, spec["condition"], spec["model"], spec["repetition"], seat))
    player_a = OllamaPlayer(spec["model"], system, seed=seed_of("a"))
    if spec["cell"] == "vs_bot":
        strategy = next(s for s in grid_config.BOT_OPPONENTS
                        if s.name == spec["opponent"])
        player_b = BotOpponent(strategy, seed=seed_of("b"))
    else:
        player_b = OllamaPlayer(spec["model"], system, seed=seed_of("b"))
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


def run(specs=None, make=make_players, log=LOG):
    """Play everything not already in the log, appending as each finishes."""
    specs = build_grid() if specs is None else specs
    done = already_done(log)
    todo = [spec for spec in specs if key_of(spec) not in done]
    print(f"{len(specs)} matches in the grid, {len(done)} already done, "
          f"{len(todo)} to play")
    log.parent.mkdir(exist_ok=True)
    _close_any_partial_line(log)
    for index, spec in enumerate(todo, start=1):
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


def describe():
    """The grid, without playing it or loading a model."""
    specs = build_grid()
    talking = sum(s["condition"] == "with_cheap_talk" for s in specs)
    calls = sum(grid_config.ROUNDS * (4 if s["condition"] == "with_cheap_talk"
                                      else 2 if s["cell"] == "self_play" else 1)
                for s in specs)
    print(f"{len(specs)} matches, {talking} of them with cheap talk")
    print(f"{grid_config.ROUNDS} rounds each, {calls} model calls in total")
    for cell in ("self_play", "vs_bot"):
        print(f"  {cell}: {sum(s['cell'] == cell for s in specs)}")
    print(f"already done: {len(already_done())}")


if __name__ == "__main__":
    describe() if "--plan" in sys.argv else run()
