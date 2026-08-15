"""Write the derived tables into `results/`, from the raw log alone.

    PYTHONPATH=. python llm/run_analysis.py

Needs no GPU and no network, so CI runs it on every push and asks git whether
any table moved. Until a real run exists there is nothing to derive and it says
so and exits cleanly, which is correct: the check starts guarding the moment
there is something to guard.

Floats are written to six decimals for the same reason as the Hebbian side, so
two runs produce byte-identical files.
"""

import csv
import pathlib

import measurements

RESULTS = pathlib.Path(__file__).parent / "results"
DECIMALS = 6

TABLES = [
    ("cooperation_rates.csv",
     ["model", "condition", "opening", "matches", "cooperation_rate"],
     lambda played, lost: measurements.cooperation_rates(played)),
    ("vs_bots.csv",
     ["model", "bot", "matches", "model_score_per_turn", "bot_score_per_turn",
      "model_cooperation", "reciprocity_index"],
     lambda played, lost: measurements.vs_bots(played)),
    ("reciprocity.csv",
     ["model", "condition", "seats_measured", "reciprocity_index"],
     lambda played, lost: measurements.reciprocity(played)),
    ("self_play_lock_in.csv",
     ["model", "opening", "condition", "matches",
      "settled_on_mutual_cooperation", "settled_on_mutual_defection",
      "unsettled", "mean_score_per_turn"],
     lambda played, lost: measurements.self_play_lock_in(played)),
    ("reason_matches_action.csv",
     ["model", "rounds_naming_an_action", "rounds_agreeing", "agreement_rate"],
     lambda played, lost: measurements.reason_matches_action(played)),
    ("parse_health.csv",
     ["model", "matches_played", "matches_lost", "loose_reads"],
     lambda played, lost: measurements.parse_health(played, lost)),
]


def formatted(value):
    """Counts stay counts; anything measured gets fixed decimals."""
    if isinstance(value, (int, str)):
        return value
    return f"{value:.{DECIMALS}f}"


def write_csv(name, header, rows, results=RESULTS):
    results.mkdir(parents=True, exist_ok=True)
    with open(results / name, "w", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows([formatted(value) for value in row] for row in rows)


def main(log=measurements.LOG, results=RESULTS):
    played = measurements.read(log)
    lost = measurements.failures(log)
    if not played and not lost:
        print(f"no matches in {log}, nothing to derive yet")
        return
    for name, header, derive in TABLES:
        write_csv(name, header, derive(played, lost), results)
    print(f"derived {len(TABLES)} tables from {len(played)} matches "
          f"({len(lost)} lost to unparseable replies)")


if __name__ == "__main__":
    main()
