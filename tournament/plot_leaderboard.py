"""The April 2025 tournament standings, as a chart.

Scores are transcribed from page 1 of
../original/Projet_Prolog/Convergence des stratégies dans un jeu répété/data2.pdf,
which is the tournament log as produced by the course harness.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STANDINGS = [
    ("best_duo",       201948395872482084950540887069436735146155115216970443725750792),
    ("naenae",         2584939414228211483973152162718652107287198305130004896256),
    ("youxi",          4135903062765138374357044094175114381943761302861102102),
    ("lesStrateges",   888178419700125232339271902533575),
    ("lesCowBoys",     888178419700125232338905334984421),
    ("syntax_terror",  633825300704410511107059080170),
    ("stage_test",     6163877),
    ("nash_equilibrium", 1490429),
    ("kAuCarre",       177854),
    ("deficit",        25551),
    ("ctrlAltDefeat",  17658),
    ("fao",            11289),
    ("un_pain_pita",   9566),
    ("ghost",          9350),
    ("fave_ok",        8290),
    ("dfy",            5226),
]

MINE = {"stage_test", "nash_equilibrium"}

names = [n for n, _ in STANDINGS][::-1]
scores = [float(s) for _, s in STANDINGS][::-1]   # exact ints overflow C long
colours = ["#2ca02c" if n in MINE else "#c0c4c8" for n in names]

fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(names, scores, color=colours)
ax.set_xscale("log")
ax.set_xlabel("cumulative score, log scale")
ax.set_title("Tournoi n° 1, April 2025, L2 MIASHS UGA: 16 agents")
for i, (name, score) in enumerate(zip(names, scores)):
    if name in MINE:
        ax.text(score * 1.6, i, f"{int(score):,}", va="center", fontsize=9, color="#1a7431")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("leaderboard.png", dpi=110, bbox_inches="tight")

rank = {n: i + 1 for i, (n, _) in enumerate(STANDINGS)}
print(f"stage_test:       {rank['stage_test']}th of {len(STANDINGS)}, {dict(STANDINGS)['stage_test']:,}")
print(f"nash_equilibrium: {rank['nash_equilibrium']}th of {len(STANDINGS)}, {dict(STANDINGS)['nash_equilibrium']:,}")
print(f"winner is {STANDINGS[0][0]} at {STANDINGS[0][1]:.3e}, "
      f"{STANDINGS[0][1] / dict(STANDINGS)['stage_test']:.1e} times more")
print("wrote leaderboard.png")
