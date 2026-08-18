"""Fail if the paper was not re-rendered after a table moved.

    python article/check_freshness.py

The rendered HTML and PDF are build products that CI does not rebuild, because
that would mean installing Quarto and LaTeX in the workflow. This closes the gap
the cheap way: rendering stamps `rendered-from.txt` with a digest of every CSV
the paper reads, and this compares that stamp with those CSVs as they stand.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from analysis import ROOT, SOURCES, digest_of_sources  # noqa: E402

STAMP = ROOT / "article" / "rendered-from.txt"


def main():
    if not STAMP.exists():
        print(f"no {STAMP.name}: render the paper once to create it")
        return 1
    recorded = STAMP.read_text().splitlines()[0].strip()
    current = digest_of_sources()
    if recorded == current:
        print(f"paper is current with all {len(SOURCES)} source tables")
        return 0
    print(f"STALE: the paper was rendered from {recorded}, the tables now hash to "
          f"{current}.\nRe-render both editions:\n"
          f"  cd article && quarto render paper.qmd && quarto render paper.fr.qmd")
    return 1


if __name__ == "__main__":
    sys.exit(main())
