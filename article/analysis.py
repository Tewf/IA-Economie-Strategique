"""What both language versions of the paper compute, in one place.

The paper exists in English and in French. The prose differs and the arithmetic
must not, so the loading, the lookups and the table formatting live here and each
`.qmd` imports them. A number that moves, moves in both papers at once, and a
diff between the two documents shows translation rather than divergence.

Reads only the committed CSVs. No plotting and no dataframe library, so the
render needs nothing beyond `requirements.txt` and the standard library.
"""

import csv
import pathlib

ROOT = (pathlib.Path.cwd().parent if pathlib.Path.cwd().name == "article"
        else pathlib.Path.cwd())
LLM = ROOT / "llm" / "results"
HEBBIAN = ROOT / "mirror_neurons" / "results"


def table(folder, name):
    with open(folder / name, newline="\n") as handle:
        return list(csv.DictReader(handle))


def rows(data, **where):
    return [row for row in data if all(row[k] == v for k, v in where.items())]


def one(data, column, **where):
    found = rows(data, **where)
    assert len(found) == 1, f"{len(found)} rows matched {where}"
    return float(found[0][column])


def pct(value, places=2):
    return f"{value:.{places}f}"


def fr(value, places=2):
    """A French decimal comma, for the translated tables."""
    return pct(value, places).replace(".", ",")


def md(header, body):
    """A markdown table, printed rather than templated, so the numbers cannot
    drift from the CSVs they came from.

    The leading blank line is not cosmetic: a table that starts on the line after
    a printed paragraph is absorbed into that paragraph and renders as a row of
    pipes, which is what happened to the imitator's table.
    """
    out = ["", "| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in body]
    print("\n".join(out))


cooperation = table(LLM, "cooperation_rates.csv")
lock_in = table(LLM, "self_play_lock_in.csv")
settling = table(LLM, "settling.csv")
opening_round = table(LLM, "opening_round.csv")
messages = table(LLM, "message_content.csv")
reasons = table(LLM, "reason_matches_action.csv")
parse = table(LLM, "parse_health.csv")
bots = table(LLM, "vs_bots.csv")
standings = table(HEBBIAN, "standings.csv")
hebbian_lock = table(HEBBIAN, "self_play_lock_in.csv")
joined = table(ROOT, "comparison.csv")

MODELS = sorted({row["model"] for row in cooperation})
READABLE = [m for m in MODELS if int(one(parse, "matches_lost", model=m)) == 0]
UNREADABLE = [m for m in MODELS if m not in READABLE]
PLAYED = sum(int(row["matches_played"]) for row in parse)
LOST = sum(int(row["matches_lost"]) for row in parse)

OPENINGS = ["neutral", "mutual_cooperation", "mutual_defection"]
CONDITIONS = ["without_cheap_talk", "with_cheap_talk"]
CELLS = [(opening, condition) for opening in OPENINGS for condition in CONDITIONS]
SHARED_OPPONENTS = ["Tit For Tat", "Grudger", "Win-Stay Lose-Shift", "Defector",
                    "Alternator"]


def captured_freed_unmoved_never():
    """The four ways a model meets an imposed defective opening."""
    captured, freed, unmoved, never = [], [], [], []
    for model in READABLE:
        silent = one(cooperation, "cooperation_rate", model=model,
                     opening="mutual_defection", condition="without_cheap_talk")
        talk = one(cooperation, "cooperation_rate", model=model,
                   opening="mutual_defection", condition="with_cheap_talk")
        if silent == 0:
            captured.append(model)
            (freed if talk > 0.5 else unmoved).append(model)
        else:
            never.append(model)
    return captured, freed, unmoved, never
