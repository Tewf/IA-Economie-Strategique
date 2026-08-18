"""Read a prompt file and render the system prompt a model is actually given.

The prompt files are prose so they can be reviewed, diffed and quoted as prose.
Three things have to happen to one before it reaches a model, and all three are
here so that none is done by hand and forgotten.

Everything above the `---` rule in a prompt file is a note to the reader about
why the scenario is worded as it is. Only what follows it is sent.

**A message call and an action call need different instructions.** The scenario
is shared, but the block telling a model to answer `ACTION: ... REASON: ...` is
for the round where it acts. Sending that block on the cheap-talk turn made
models answer it: the first run produced messages that were literal action
declarations, which is not cheap talk but announcing your move before a
simultaneous choice. The two blocks are marked in the file and selected here.
"""

import pathlib
import re

PROMPTS = pathlib.Path(__file__).parent / "prompts"
NOTE_SEPARATOR = "\n---\n"
BLOCKS = {"action": "answer-format", "message": "message-format"}
PAYOFF_BLOCK = re.compile(r"<!-- payoffs:start -->\n(.*?)<!-- payoffs:end -->\n",
                          re.DOTALL)


def _marked(name):
    return re.compile(rf"<!-- {name}:start -->\n(.*?)<!-- {name}:end -->\n?",
                      re.DOTALL)


def load(game):
    """The scenario text for one game, without the note to the reader."""
    text = (PROMPTS / f"{game}.md").read_text()
    if NOTE_SEPARATOR not in text:
        raise ValueError(f"{game}.md has no --- rule separating note from prompt")
    return text.split(NOTE_SEPARATOR, 1)[1].strip()


def render(game, repetition=0, asking_for="action"):
    """The scenario, plus the instruction for the call being made.

    `asking_for` is "action" on a round where the model chooses, and "message"
    on a cheap-talk turn. Getting this wrong does not fail, it quietly changes
    the experiment, which is why `preflight_checks.py` asserts the two differ.

    The payoff lines are counterbalanced by repetition. A list has a first item,
    and a model reading one is not indifferent to which item that is: Fish,
    Gonczarowski and Shorrer (2024) moved prices with changes no larger. Odd
    repetitions get the reversed order.
    """
    if asking_for not in BLOCKS:
        raise ValueError(f"asking_for must be one of {sorted(BLOCKS)}")
    text = load(game)
    for purpose, marker in BLOCKS.items():
        pattern = _marked(marker)
        if not pattern.search(text):
            raise ValueError(f"{game}.md has no {marker} block")
        # Keep the block this call needs, drop the one it does not.
        text = (pattern.sub(lambda m: m.group(1), text, count=1)
                if purpose == asking_for else pattern.sub("", text, count=1))
    match = PAYOFF_BLOCK.search(text)
    if match is not None:
        lines = [line for line in match.group(1).splitlines() if line.strip()]
        ordered = lines if repetition % 2 == 0 else list(reversed(lines))
        text = PAYOFF_BLOCK.sub("\n".join(ordered) + "\n", text, count=1)
    return text.strip()


def roles(game):
    """The scenario split by role, for the one-shot games.

    `render` is built for the iterated game, where one scenario is sent twice
    with different answer-format blocks. The Ultimatum game is the other shape:
    two roles that are given *different scenarios* and asked for different
    things, separated in the file by a rule and headed `## Proposer` and
    `## Responder`. The Dictator game has one role and no heading, so it comes
    back under the empty key and callers do not special-case it.
    """
    sections = load(game).split(NOTE_SEPARATOR)
    found = {}
    for section in sections:
        text = section.strip()
        if not text:
            continue
        heading = re.match(r"##\s+(.+)", text)
        name = heading.group(1).strip().lower() if heading else ""
        found[name] = (text[heading.end():].strip() if heading else text)
    return found


def render_one_shot(game, role=""):
    """The scenario one role of a one-shot game is given, and nothing else."""
    available = roles(game)
    if role not in available:
        raise ValueError(
            f"{game}.md has roles {sorted(available)}, not {role!r}")
    return available[role]


def payoff_orderings(game):
    """Both orderings, for a check that they differ and say the same thing."""
    return render(game, 0), render(game, 1)
