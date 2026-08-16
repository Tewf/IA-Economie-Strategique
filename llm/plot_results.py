"""Draw the figures from the committed CSVs, never from a fresh run.

    PYTHONPATH=. python llm/plot_results.py

Reads the same files the write-up quotes, so a figure cannot disagree with the
number printed beside it. Two of the three put a model and the Hebbian agent on
one pair of axes, which is the whole reason the two folders share a reciprocity
measure and a set of opponents.

Says so and exits cleanly when there is nothing to draw yet.
"""

import csv
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set first)

RESULTS = pathlib.Path(__file__).parent / "results"
HEBBIAN = pathlib.Path(__file__).parent.parent / "mirror_neurons" / "results"

plt.rcParams.update({"figure.figsize": (8, 4.5), "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 110})
TALK = "#1f6feb"
NO_TALK = "#c1440e"


def read(folder, name):
    path = folder / name
    if not path.exists():
        return None
    with open(path, newline="\n") as handle:
        return list(csv.DictReader(handle))


def save(figure, name):
    figure.savefig(RESULTS / name, bbox_inches="tight")
    plt.close(figure)


def plot_cooperation_by_condition(rows):
    """Does a non-binding message change how often a model cooperates?"""
    models = sorted({row["model"] for row in rows})
    figure, axes = plt.subplots()
    width = 0.38
    for offset, condition, colour in ((-width / 2, "with_cheap_talk", TALK),
                                      (width / 2, "without_cheap_talk", NO_TALK)):
        heights = [_mean([float(row["cooperation_rate"]) for row in rows
                          if row["model"] == model
                          and row["condition"] == condition]) for model in models]
        axes.bar([i + offset for i in range(len(models))], heights, width,
                 color=colour, label=condition.replace("_", " "))
    axes.set_xticks(range(len(models)), models, rotation=20, ha="right")
    axes.set_ylabel("cooperation rate")
    axes.set_ylim(0, 1)
    axes.set_title("Cheap talk against silence")
    axes.legend(frameon=False)
    save(figure, "cooperation_by_condition.png")


def plot_lock_in(rows):
    """The comparison the whole folder exists for: does talking break the ratchet?"""
    openings = ["mutual_cooperation", "neutral", "mutual_defection"]
    figure, axes = plt.subplots()
    for condition, colour in (("with_cheap_talk", TALK),
                              ("without_cheap_talk", NO_TALK)):
        kept = []
        for opening in openings:
            here = [row for row in rows if row["opening"] == opening
                    and row["condition"] == condition]
            settled = sum(int(row["settled_on_mutual_cooperation"]) for row in here)
            total = sum(int(row["matches"]) for row in here)
            kept.append(settled / total if total else float("nan"))
        axes.plot(openings, kept, marker="o", color=colour,
                  label=condition.replace("_", " "))
    axes.set_ylabel("share settling on mutual cooperation")
    axes.set_ylim(-0.05, 1.05)
    axes.set_title("Two models, by the regime they were handed")
    axes.legend(frameon=False)
    save(figure, "self_play_lock_in.png")


def plot_reciprocity_against_the_imitator(rows):
    """Every model's reciprocity, with the Hebbian agent and Tit-for-Tat marked.

    **Undefined seats are dropped rather than averaged in.** Reciprocity is
    `P(cooperate | they defected last)` subtracted from `P(cooperate | they
    cooperated last)`, so a match in which nobody ever defects has no second
    term and `measurements.reciprocity` writes `nan`. That is the honest value
    and it happens here: under cheap talk these models cooperate throughout.
    Averaging it in would make one NaN erase a model's whole bar, and a missing
    bar reads as zero reciprocity rather than as no defection to react to.
    """
    hebbian = read(HEBBIAN, "reciprocity.csv") or []
    marks = {row["player"]: float(row["reciprocity_index"])
             for row in hebbian if row["prober"] == "Random"
             and row["player"] in ("Mirror Neuron", "Tit For Tat")}
    models = sorted({row["model"] for row in rows})
    values = [_mean([value for value in
                     (float(row["reciprocity_index"]) for row in rows
                      if row["model"] == model) if value == value])
              for model in models]
    undefined = [model for model, value in zip(models, values) if value != value]
    figure, axes = plt.subplots()
    axes.barh(models, [0 if value != value else value for value in values],
              color=TALK)
    for name, value in marks.items():
        axes.axvline(value, ls="--", lw=1, c="#c1440e")
        axes.text(value, -0.6, f" {name} {value:.2f}", color="#c1440e", fontsize=8)
    axes.set_xlabel("reciprocity index" if not undefined else
                    f"reciprocity index. Undefined, so drawn at zero: "
                    f"{', '.join(undefined)}")
    axes.set_title("Models against the imitator, on one measure")
    save(figure, "reciprocity_against_the_imitator.png")


def _mean(values):
    return sum(values) / len(values) if values else float("nan")


def main():
    cooperation = read(RESULTS, "cooperation_rates.csv")
    lock_in = read(RESULTS, "self_play_lock_in.csv")
    reciprocity = read(RESULTS, "reciprocity.csv")
    if not (cooperation and lock_in and reciprocity):
        print(f"no derived tables in {RESULTS}, nothing to draw yet")
        return
    plot_cooperation_by_condition(cooperation)
    plot_lock_in(lock_in)
    plot_reciprocity_against_the_imitator(reciprocity)
    print(f"wrote 3 figures to {RESULTS}")


if __name__ == "__main__":
    main()
