# The article

[`paper.qmd`](paper.qmd) is the write-up of both halves of this repository as one
study: the imitation mechanism, the five-model grid, and the literature each is
positioned against. It renders to [`paper.html`](paper.html) and
[`paper.pdf`](paper.pdf).

**No number in it is typed by hand.** Every figure in the text is read at render
time from the committed CSVs in [`../llm/results/`](../llm/results/) and
[`../mirror_neurons/results/`](../mirror_neurons/results/), by the same
arithmetic continuous integration re-derives on each push. A claim in a sentence
and the table under it come from one source, so they cannot disagree. The three
figures are the committed PNGs, drawn by
[`../llm/plot_results.py`](../llm/plot_results.py), not redrawn here.

## Rendering it

```sh
conda activate gael
cd article
for doc in paper.qmd paper.fr.qmd; do
    quarto render "$doc" --to html
    quarto render "$doc" --to pdf    # needs a LaTeX install; tinytex is enough
done
```

Quarto runs the document's Python chunks in the active environment, so the
environment needs nothing beyond what [`../requirements.txt`](../requirements.txt)
already pins: the chunks use `csv` and `pathlib` from the standard library, and
no plotting or dataframe library at all.

**The four rendered files are build products that CI does not rebuild**, because
that would mean installing Quarto and LaTeX in the workflow to check a document.
They are committed because GitHub Pages serves this repository directly and a
reader should not have to install Quarto to read the paper.

That would be the one drift risk in the repository, so the cheap half of the
guarantee is wired in: rendering stamps [`rendered-from.txt`](rendered-from.txt)
with a digest of every table the paper read, and
[`check_freshness.py`](check_freshness.py) compares it with those tables as they
stand. CI runs it, so a table that moves without the paper being re-rendered
turns the build red instead of publishing numbers the data no longer holds.

    python article/check_freshness.py

## Two languages, one set of numbers

[`paper.qmd`](paper.qmd) and [`paper.fr.qmd`](paper.fr.qmd) are the English and
French editions. Both import [`analysis.py`](analysis.py), which owns the loading,
the lookups and the table formatting, so the arithmetic exists once and a diff
between the two documents shows translation rather than divergence. A number that
moves, moves in both papers at once.

The prompts and the design notes stay English whatever the paper does, because
translating a prompt would change the experiment the models were run on.

## What is in it that is not elsewhere

The READMEs report what the grid found. The paper adds the parts that only make
sense at length:

- **A literature review** placing the work in five threads, and saying plainly
  which of its results are replications of established findings and which are
  not. The bibliography in [`references.bib`](references.bib) was resolved
  against the arXiv API rather than from memory, and the note at the top of that
  file says so.
- **The mechanism behind the headline result.** The cheap-talk messages are read,
  not only counted, and the two models a message does not free turn out to be the
  two whose messages never propose anything.
- **Threats to validity** stated as a section rather than as scattered caveats,
  including why significance testing on four matches per cell with near-zero
  variance would be theatre.
