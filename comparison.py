"""Put the imitator and the language models in one table.

    python comparison.py        # writes comparison.csv

This file exists because the repository keeps claiming the two halves are one
comparison and never actually printed the table. [`reciprocity.py`](reciprocity.py)
sits at the root so both halves are scored by one definition, and
[`llm/grid_config.py`](llm/grid_config.py) picks its bots from the set the
Hebbian agent faced, so the join is available and was simply never made.

It sits at the root for the same reason the measure does: it belongs to neither
folder. It reads both `results/` directories and derives nothing new, so like
every other table here CI can re-run it and ask git whether anything moved.

**Score per turn is the comparable column and cooperation is not, quite.** The
Hebbian tournament runs 100 turns and this grid runs 30, and a strategy that
needs to be provoked before it retaliates spends a different share of a short
match being provoked. The scores are per turn and so survive the difference; a
cooperation rate over 30 rounds against one over 100 is close enough to read and
not close enough to subtract.
"""

import csv
import pathlib

ROOT = pathlib.Path(__file__).parent
HEBBIAN = ROOT / "mirror_neurons" / "results" / "head_to_head.csv"
MODELS = ROOT / "llm" / "results" / "vs_bots.csv"
OUT = ROOT / "comparison.csv"
IMITATOR = "Mirror Neuron"
DECIMALS = 6


def read(path):
    if not path.exists():
        return []
    with open(path, newline="\n") as handle:
        return list(csv.DictReader(handle))


def joined(hebbian=None, models=None):
    """One row per player and shared opponent, imitator first."""
    hebbian = read(HEBBIAN) if hebbian is None else hebbian
    models = read(MODELS) if models is None else models
    shared = sorted({row["bot"] for row in models}
                    & {row["opponent"] for row in hebbian})
    rows = []
    for opponent in shared:
        here = next(row for row in hebbian if row["opponent"] == opponent)
        rows.append((IMITATOR, opponent, 100,
                     float(here["agent_score_per_turn"]),
                     float(here["opponent_score_per_turn"]),
                     float(here["agent_cooperation"])))
    for row in sorted(models, key=lambda row: (row["model"], row["bot"])):
        if row["bot"] not in shared:
            continue
        rows.append((row["model"], row["bot"], 30,
                     float(row["model_score_per_turn"]),
                     float(row["bot_score_per_turn"]),
                     float(row["model_cooperation"])))
    return rows


def main():
    rows = joined()
    if not rows:
        print("one half has no results yet, nothing to join")
        return
    with open(OUT, "w", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["player", "opponent", "rounds", "player_score_per_turn",
                         "opponent_score_per_turn", "player_cooperation"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2]]
                            + [f"{value:.{DECIMALS}f}" for value in row[3:]])
    players = len({row[0] for row in rows})
    print(f"joined {players} players on {len(rows) // players} shared opponents "
          f"-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
