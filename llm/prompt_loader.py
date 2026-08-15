"""Read a prompt file and render the system prompt a model is actually given.

The prompt files are prose so they can be reviewed, diffed and quoted as prose.
Two things have to happen to one before it reaches a model, and both are here so
that neither is done by hand and forgotten.

Everything above the `---` rule in a prompt file is a note to the reader about
why the scenario is worded as it is. Only what follows it is sent.
"""

import pathlib
import re

PROMPTS = pathlib.Path(__file__).parent / "prompts"
NOTE_SEPARATOR = "\n---\n"
PAYOFF_BLOCK = re.compile(r"<!-- payoffs:start -->\n(.*?)<!-- payoffs:end -->\n",
                          re.DOTALL)


def load(game):
    """The scenario text for one game, without the note to the reader."""
    text = (PROMPTS / f"{game}.md").read_text()
    if NOTE_SEPARATOR not in text:
        raise ValueError(f"{game}.md has no --- rule separating note from prompt")
    return text.split(NOTE_SEPARATOR, 1)[1].strip()


def render(game, repetition=0):
    """The scenario with its payoff lines counterbalanced by repetition.

    A list has a first item, and a model reading one is not indifferent to which
    item that is: Fish, Gonczarowski and Shorrer (2024) moved prices with changes
    no larger than this. Presenting mutual cooperation first in half the
    repetitions and last in the other half means the ordering cannot be mistaken
    for a result. Odd repetitions get the reversed order.
    """
    text = load(game)
    match = PAYOFF_BLOCK.search(text)
    if match is None:
        return text
    lines = [line for line in match.group(1).splitlines() if line.strip()]
    ordered = lines if repetition % 2 == 0 else list(reversed(lines))
    return PAYOFF_BLOCK.sub("\n".join(ordered) + "\n", text, count=1)


def payoff_orderings(game):
    """Both orderings, for a check that they differ and say the same thing."""
    return render(game, 0), render(game, 1)
