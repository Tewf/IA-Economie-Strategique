"""Draw the figures from the committed CSVs, never from a fresh run.

Reading the same files the README quotes means a figure cannot disagree with the
number printed beside it. Run it after `run_tournament.py`:

    python plot_results.py

Writes three PNGs into `results/`, next to the CSVs they came from.
"""

import csv
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set first)

RESULTS = pathlib.Path(__file__).parent / "results"
AGENT = "Mirror Neuron"

plt.rcParams.update({"figure.figsize": (8, 4.5), "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 110})


def read(name):
    """One CSV as a list of dicts, exactly as committed."""
    with open(RESULTS / name, newline="\n") as handle:
        return list(csv.DictReader(handle))


def save(figure, name):
    figure.savefig(RESULTS / name, bbox_inches="tight")
    plt.close(figure)


def plot_decay():
    """The headline result: the agent's reciprocity is a transient."""
    rows = read("reciprocity_decay.csv")
    figure, axes = plt.subplots()
    for player, colour in ((AGENT, "#c1440e"), ("Tit For Tat", "#1f6feb")):
        windows = [row for row in rows if row["player"] == player]
        midpoints = [(int(row["from_turn"]) + int(row["to_turn"])) / 2
                     for row in windows]
        axes.plot(midpoints, [float(row["reciprocity_index"]) for row in windows],
                  marker="o", color=colour, label=player)
    axes.set_xlabel("turn")
    axes.set_ylabel("reciprocity index in a 200 turn window")
    axes.set_ylim(-0.1, 1.1)
    axes.set_title("Reciprocity that fades, against reciprocity that does not")
    axes.legend(frameon=False)
    save(figure, "reciprocity_decay.png")


def plot_learning_rate_sweep():
    """The report's claim was that a larger learning rate approaches Tit-for-Tat."""
    rows = read("learning_rate_sweep.csv")
    rates = [float(row["learning_rate"]) for row in rows]
    figure, axes = plt.subplots()
    axes.plot(rates, [float(row["reciprocity_index"]) for row in rows],
              marker="o", color="#c1440e", label="the agent")
    axes.axhline(1.0, ls="--", lw=1, c="#1f6feb",
                 label="Tit-for-Tat, at every learning rate")
    axes.set_xscale("log")
    axes.set_xlabel("learning rate")
    axes.set_ylabel("reciprocity index")
    axes.set_ylim(-0.1, 1.1)
    axes.set_title("Raising the learning rate does not buy reciprocity")
    axes.legend(frameon=False)
    save(figure, "learning_rate_sweep.png")


def plot_match_length():
    """Where "behind a coin flip" stops being true, and why that is not progress."""
    rows = read("match_length_sweep.csv")
    turns = [int(row["turns"]) for row in rows]
    figure, axes = plt.subplots()
    axes.plot(turns, [float(row["agent_median_score"]) for row in rows],
              marker="o", color="#c1440e", label="Mirror Neuron")
    axes.plot(turns, [float(row["random_median_score"]) for row in rows],
              marker="o", color="#6e7781", label="Random")
    axes.set_xscale("log")
    axes.set_xlabel("turns per match")
    axes.set_ylabel("median score per turn")
    axes.set_title("The imitator overtakes the coin flip only by freezing")
    axes.legend(frameon=False)
    save(figure, "match_length_sweep.png")


def plot_standings():
    """Eighth of eight, which is the finding rather than the failure."""
    rows = list(reversed(read("standings.csv")))
    names = [row["player"] for row in rows]
    figure, axes = plt.subplots()
    axes.barh(names, [float(row["median_score"]) for row in rows],
              color=["#c1440e" if name == AGENT else "#c9d1d9" for name in names])
    axes.set_xlabel("median score per turn")
    axes.set_title("At 100 turns a match, the imitator finishes last")
    save(figure, "standings.png")


if __name__ == "__main__":
    plot_decay()
    plot_match_length()
    plot_learning_rate_sweep()
    plot_standings()
    print(f"wrote 4 figures to {RESULTS}")
