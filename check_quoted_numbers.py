"""Fail if a number written into prose no longer matches the table it came from.

    python check_quoted_numbers.py

Every derived table is re-derived by CI and compared byte for byte, and the
article reads its figures from those tables at render time, so neither can drift.
The READMEs and the site cannot: their numbers are typed by hand, and a sentence
quoting 0.630 sits happily beside a CSV that now says 0.666. That happened once
already, on 2026-08-18, and the fix was noticing rather than a check.

**A stale sentence beside a fresh number is worse than two stale ones**, because
the live figure lends the dead one its credibility. This is the missing half of
the guarantee: each claim below names a file, the exact string that must appear
in it, and how to compute that string from the committed CSVs. Move a table and
the string stops matching, and the build says which sentence to rewrite.

Adding a claim is cheap and worth it for any number a reader would quote back.
"""

import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
LLM = ROOT / "llm" / "results"


def table(name, folder=LLM):
    with open(folder / name, newline="\n") as handle:
        return list(csv.DictReader(handle))


def cell(rows, column, **where):
    found = [r for r in rows if all(r[k] == v for k, v in where.items())]
    assert len(found) == 1, f"{len(found)} rows matched {where} in {column}"
    return float(found[0][column])


def claims():
    """(file, expected string, what it is) for every hand-typed figure."""
    reasons = table("reason_matches_action.csv")
    cooperation = table("cooperation_rates.csv")
    parse = table("parse_health.csv")
    messages = table("message_content.csv")
    one_shot = table("one_shot_offers.csv")
    out = []

    # The reason-and-action line, in both languages. This is the one that rotted.
    for model, blank in (("qwen3:8b", "qwen3"), ("gemma3:4b", "gemma3"),
                         ("qwen2.5:7b-instruct", "qwen2.5"),
                         ("phi3:mini", "phi3"), ("mistral:7b", "mistral")):
        rate = cell(reasons, "agreement_rate", model=model)
        naming = int(cell(reasons, "rounds_naming_an_action", model=model))
        out.append(("llm/README.md", f"{blank} {rate:.3f} ({naming} rounds)"
                    if model == "qwen3:8b" else f"{blank} {rate:.3f} ({naming})",
                    f"{model} reason/action agreement"))
        # French writes the decimal with a comma and leaves the model's own dot
        # alone, so only the rate is converted. Replacing the first "." in the
        # whole string mangles "qwen2.5" instead.
        decimal = f"{rate:.3f}".replace(".", ",")
        out.append(("llm/README.fr.md",
                    f"{blank} {decimal} ({naming} tours)" if model == "qwen3:8b"
                    else f"{blank} {decimal} ({naming})",
                    f"{model} reason/action agreement, French"))

    # The headline cell, quoted in the site and both root READMEs as 0.00/1.00.
    freed = cell(cooperation, "cooperation_rate", model="qwen2.5:7b-instruct",
                 opening="mutual_defection", condition="with_cheap_talk")
    out.append(("llm/README.md", f"| **{freed:.2f}** |",
                "qwen2.5 freed by a message"))

    # phi3's losses, quoted in four places.
    lost = int(cell(parse, "matches_lost", model="phi3:mini"))
    played = int(cell(parse, "matches_played", model="phi3:mini"))
    out.append(("llm/README.md", f"{lost} of {lost + played} matches lost",
                "phi3 losses"))

    # The message length that carries the mechanism claim.
    chars = cell(messages, "mean_characters", model="gemma3:4b",
                 opening="mutual_defection")
    out.append(("index.html", f"averaging {chars:.0f}", "gemma3 message length"))

    # What qwen3 pays not to be refused, which the README quotes as the premium
    # over the Dictator game rather than as the raw offer.
    premium = cell(one_shot, "paid_to_avoid_refusal", model="qwen3:8b")
    out.append(("llm/README.md", f"qwen3 pays {premium:.0f} points of 100",
                "qwen3's premium to avoid refusal"))
    return out


def flattened(text):
    """Prose as one line, without emphasis, so a claim survives rewrapping.

    A figure that is correct but sits across a line break, or inside `**bold**`,
    is not stale and must not fail the build: this check exists to catch numbers
    that moved, not paragraphs that were reflowed.
    """
    return " ".join(text.replace("*", "").split())


def main():
    stale = []
    for path, expected, what in claims():
        text = flattened((ROOT / path).read_text())
        if flattened(expected) not in text:
            stale.append((path, expected, what))
    for path, expected, what in stale:
        print(f"STALE  {path}: expected to find {expected!r} ({what})")
    if stale:
        print(f"\n{len(stale)} quoted figures no longer match their table. "
              f"Rewrite the sentence, or fix the claim in {pathlib.Path(__file__).name}.")
        return 1
    print(f"all {len(claims())} quoted figures match their tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
