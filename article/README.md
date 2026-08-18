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
quarto render paper.qmd --to html
quarto render paper.qmd --to pdf     # needs a LaTeX install; tinytex is enough
```

Quarto runs the document's Python chunks in the active environment, so the
environment needs nothing beyond what [`../requirements.txt`](../requirements.txt)
already pins: the chunks use `csv` and `pathlib` from the standard library, and
no plotting or dataframe library at all.

**`paper.html` and `paper.pdf` are build products that CI does not rebuild.**
They are committed because GitHub Pages serves this repository directly and a
reader should not have to install Quarto to read the paper. The consequence is
the one drift risk in the repository: **re-render after anything changes a table
in `*/results/`**, or the published paper will quote numbers the CSVs no longer
hold.

## It is in English only

The two READMEs and the site are bilingual; this is not. The design notes, the
prompts and the literature are English, the prompts especially because
translating one would change the experiment the models were run on. A French
version would be a translation of finished prose rather than a second original,
and it has not been written. That is a gap, and it is named here rather than
left to be noticed.

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
