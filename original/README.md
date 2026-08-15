# The internship as delivered

Everything in this folder is exactly what was submitted at the end of the GAEL
internship in May 2025. Nothing here has been edited, reformatted or corrected,
including the parts that are wrong. It is kept so the corrected work beside it
can be read against what it corrects.

**Do not expect any of it to run.** There are no pinned dependencies, the
notebooks were saved from out-of-order sessions, and one of them does not
terminate. The runnable versions are one level up.

| | |
|---|---|
| `RapportDeStageFinal.pdf` | The internship report, 9 pages |
| `Presentation.pdf` | The defence slides, 23 pages |
| `Litterature/` | Annotated bibliography, and four summaries written from the papers rather than the papers themselves |
| `Neurones_Mirroirs/` | Mirror neurons as a mechanism for imitative cooperation, write-up and simulation |
| `NOTICE` | What in here is not the author's own work |

One folder that was submitted alongside these is no longer here. `Projet_Prolog/`
held a Prolog course project: two agents, a tournament entry and a 636-page match
log. It was L2 coursework rather than internship work, and it was most of this
repository by weight, so it now lives with the rest of the coursework. This
repository is about what the internship itself produced.

## Known defects, recorded rather than repaired

These were found when the corrected layer was built. They are listed here
because a reader will meet them, and silently inheriting them into new prose
would be worse than naming them. None of them is fixed in this folder, by
design.

**In the report.** Two statistics are truncated mid-number, and the cause is the
LaTeX unescaped `%`: everything after it on the line becomes a comment.

- p. 4: `le modèle « welfare conditionnel » rend compte d'environ 84,5` and the
  sentence ends there. The figure is a percentage.
- p. 5: `Préférences des joueurs Après le jeu, 40` and the sentence ends there.

There is no committed LaTeX source, so these cannot be regenerated. Both numbers
survive in the defence slides, which were compiled separately.

**In the slides.** One result is reported as `ANOVA : F = ∞, p < 0.001`. An F
statistic cannot be infinite; it indicates zero within-group variance or a
degenerate computation. The accompanying `t = −0.065, p = 0.948` is fine.

**In `Neurones_Mirroirs_Code.ipynb`.**

- The final cell is an unguarded `while(True)` around `input()`. Any run-all
  hangs there forever.
- All nine execution counts are `null`, yet five cells carry committed figures.
  There is no record of what produced them or in what order.
- Three of the five figures compute a per-curve `η` label and never call
  `legend()`, `xlabel()` or `ylabel()`, so four indistinguishable curves are
  plotted with the labels discarded.
- There are no markdown cells at all.

**In `Litterature/`.**

- `Summary/READ.md` opens a fenced code block and never closes it, so everything
  after it renders as raw code.
- `Summary/WhenCommunicativeAIAreCooperativeActors.pdf` summarises Ng (2023),
  which does not appear in `Litterature/README.md` at all, despite being one of
  the three papers the report analyses in depth.
