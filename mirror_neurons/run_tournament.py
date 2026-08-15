"""Write the measurements into `results/`, once the preflight checks pass.

Argument-free, so one command reproduces the whole folder:

    python run_tournament.py

Every float is written to six decimals so that two runs produce byte-identical
files and CI can ask git whether a result moved. What each number means is in
`measurements.py`; why they are trustworthy is in `preflight_checks.py`.
"""

import csv
import pathlib

import measurements
import preflight_checks

RESULTS = pathlib.Path(__file__).parent / "results"
DECIMALS = 6

TABLES = [
    ("standings.csv",
     ["rank", "player", "median_score", "cooperation_rating", "wins"],
     measurements.standings),
    ("head_to_head.csv",
     ["opponent", "agent_score_per_turn", "opponent_score_per_turn",
      "agent_cooperation", "opponent_cooperation", "reciprocity_index",
      "agreement_rate"],
     measurements.head_to_head),
    ("reciprocity.csv",
     ["player", "prober", "reciprocity_index", "agreement_rate"],
     measurements.reciprocity_table),
    ("learning_rate_sweep.csv",
     ["learning_rate", "reciprocity_index", "agreement_rate",
      "cooperation_rate", "score_per_turn"],
     measurements.learning_rate_sweep),
    ("reciprocity_decay.csv",
     ["player", "from_turn", "to_turn", "reciprocity_index"],
     measurements.reciprocity_decay),
]


def formatted(value):
    """Fixed decimals for anything measured, so a rerun writes the same bytes.

    Ranks and turn numbers are counts rather than measurements and are left
    as they are, since `1` reads better in a CSV than `1.000000`.
    """
    if isinstance(value, int) or isinstance(value, str):
        return value
    return f"{value:.{DECIMALS}f}"


def write_csv(name, header, rows):
    """One tidy CSV, with a fixed line terminator so CI can diff it."""
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / name, "w", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows([formatted(value) for value in row] for row in rows)


def main():
    preflight_checks.run_all()
    for name, header, measure in TABLES:
        write_csv(name, header, measure())
    print(f"wrote {len(TABLES)} CSVs to {RESULTS}")


if __name__ == "__main__":
    main()
