"""Every table the write-up will quote, derived from the raw match log.

No network, no GPU, no model. This layer is pure arithmetic over
`results/matches.jsonl`, which is why CI can re-derive it on every push and fail
on any difference, exactly as it does for the Hebbian tournament. The raw log
cannot be regenerated without hours on the card; these tables can be regenerated
in a second, so the honesty guarantee lives here.

The reciprocity index is imported from the repository root rather than
reimplemented, so a model and the Hebbian agent are scored by one definition and
the comparison between the two folders cannot drift.
"""

import collections
import json
import pathlib

from axelrod.action import Action

from panel_config import CONTEXT_TOKENS
from reciprocity import reciprocity_index

LOG = pathlib.Path(__file__).parent / "results" / "matches.jsonl"

# A pair counts as settled if the last third of the match is one regime
# throughout. The Hebbian side used the last 20 of 200 turns; 30 rounds is
# shorter, so a third is the same idea at this scale.
SETTLED_TAIL = 10
TO_ACTION = {"Cooperate": Action.C, "Defect": Action.D}


def read(log=LOG):
    """Every complete match in the log. Failed and truncated ones are skipped."""
    if not log.exists():
        return []
    matches = []
    for line in log.read_text().splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "rounds" in record:
            matches.append(record)
    return matches


def failures(log=LOG):
    """Matches lost to a reply that named no action, which is a result."""
    if not log.exists():
        return []
    lost = []
    for line in log.read_text().splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "failed" in record:
            lost.append(record)
    return lost


def _actions(match, seat):
    return [step[f"{seat}_action"] for step in match["rounds"]]


def _cooperation(actions):
    return sum(action == "Cooperate" for action in actions) / len(actions)


def _mean(values):
    return sum(values) / len(values) if values else float("nan")


def cooperation_rates(matches):
    """How often each model cooperated, split by condition and by opening."""
    grouped = collections.defaultdict(list)
    for match in matches:
        if match["cell"] != "self_play":
            continue
        key = (match["model"], match["condition"], match["opening"])
        grouped[key].extend([_cooperation(_actions(match, "a")),
                             _cooperation(_actions(match, "b"))])
    return [(model, condition, opening, len(rates) // 2, _mean(rates))
            for (model, condition, opening), rates in sorted(grouped.items())]


def vs_bots(matches):
    """Each model against the opponents the Hebbian agent also faced."""
    grouped = collections.defaultdict(list)
    for match in matches:
        if match["cell"] != "vs_bot":
            continue
        grouped[(match["model"], match["opponent"])].append(match)
    rows = []
    for (model, bot), played in sorted(grouped.items()):
        rounds = len(played[0]["rounds"])
        rows.append((
            model, bot, len(played),
            _mean([match["a_total"] / rounds for match in played]),
            _mean([match["b_total"] / rounds for match in played]),
            _mean([_cooperation(_actions(match, "a")) for match in played]),
            _mean([reciprocity_index([TO_ACTION[a] for a in _actions(match, "a")],
                                     [TO_ACTION[b] for b in _actions(match, "b")])
                   for match in played])))
    return rows


def reciprocity(matches):
    """The root measure, applied to models, split by condition.

    Directly comparable to `../mirror_neurons/results/reciprocity.csv`, which is
    the whole point of importing it rather than writing a second copy.
    """
    grouped = collections.defaultdict(list)
    for match in matches:
        for seat, other in (("a", "b"), ("b", "a")):
            index = reciprocity_index(
                [TO_ACTION[x] for x in _actions(match, seat)],
                [TO_ACTION[x] for x in _actions(match, other)])
            grouped[(match["model"], match["condition"])].append(index)
    return [(model, condition, len(values),
             _mean([v for v in values if v == v]))
            for (model, condition), values in sorted(grouped.items())]


def self_play_lock_in(matches):
    """Does a talking pair keep the regime it was handed, as an imitating pair does?

    The Hebbian pair settled on whatever it started with, 700 runs out of 700.
    A model has no starting weight, so the lever is the opening round it is given
    and never chose. Cheap talk is the treatment: if anything can break a
    ratchet, a non-binding message is the candidate the report's own frame names.
    """
    grouped = collections.defaultdict(list)
    for match in matches:
        if match["cell"] != "self_play":
            continue
        grouped[(match["model"], match["opening"], match["condition"])].append(match)
    rows = []
    for (model, opening, condition), played in sorted(grouped.items()):
        settled_c = settled_d = 0
        for match in played:
            tail = match["rounds"][-SETTLED_TAIL:]
            settled_c += all(step["a_action"] == step["b_action"] == "Cooperate"
                             for step in tail)
            settled_d += all(step["a_action"] == step["b_action"] == "Defect"
                             for step in tail)
        rounds = len(played[0]["rounds"])
        rows.append((model, opening, condition, len(played), settled_c, settled_d,
                     len(played) - settled_c - settled_d,
                     _mean([match["a_total"] / rounds for match in played])))
    return rows


def _action_replies(match, seat):
    """The replies that decided a move, in round order.

    **A transcript is one entry per model call, not per round.** With a channel
    a round costs two calls, the message and then the action, so the reply that
    decided round k sits at 2k+1 and the even entries are messages. Zipping the
    whole transcript against the actions therefore compared round k's stated
    reason with round 2k+1's move, and silently dropped the second half of every
    talking match when the actions ran out. Both were wrong only where a match
    varied its action, which is why the error survived a table that looked
    plausible.
    """
    transcript = match.get(f"{seat}_transcript", [])
    if match["condition"] == "with_cheap_talk":
        return transcript[1::2]
    return transcript


def reason_matches_action(matches):
    """Does the reason a model gives name the action it actually took?

    The only honest thing the text supports, per
    `design-notes/cheap-talk-and-explanation.md`: not whether the model is
    telling the truth about a computation, which it cannot be, but whether what
    it says and what it does line up. Rounds whose reason names neither action
    are excluded rather than counted as agreement.
    """
    grouped = collections.defaultdict(lambda: [0, 0])
    for match in matches:
        for seat in ("a", "b"):
            actions = _actions(match, seat)
            for reply, action in zip(_action_replies(match, seat), actions):
                reason = reply.get("content", "").split("REASON:", 1)
                if len(reason) < 2:
                    continue
                text = reason[1].upper()
                named = [name for name in ("COOPERATE", "DEFECT") if name in text]
                if len(named) != 1:
                    continue
                counted = grouped[match["model"]]
                counted[1] += 1
                counted[0] += named[0] == action.upper()
    return [(model, total, agreed, agreed / total if total else float("nan"))
            for model, (agreed, total) in sorted(grouped.items())]


def context_headroom(matches, lost, limit=CONTEXT_TOKENS):
    """The longest prompt each model actually sent, against the window it had.

    This table exists because the failure it guards against is silent. Ollama
    serves 4096 tokens by default and cuts anything longer instead of refusing
    it, oldest tokens first, which is the system prompt: the match carries on
    with the scenario and the answer format gone, and the log looks normal. It
    happened on 2026-08-17 and cost a stage.

    A `longest_prompt` at the limit means the run was truncated and the numbers
    beside it describe a different experiment. Anything comfortably below it
    means the prompt reached the model whole.
    """
    longest = collections.defaultdict(int)
    for record in list(matches) + list(lost):
        for seat in ("a", "b"):
            for reply in record.get(f"{seat}_transcript", []):
                seen = reply.get("prompt_tokens")
                if seen:
                    longest[record["model"]] = max(longest[record["model"]], seen)
    return [(model, limit, longest[model], limit - longest[model])
            for model in sorted(longest)]


def parse_health(matches, lost):
    """How often the answer format held, how often a match was lost to it, and
    how far the model got first.

    The last column is what separates two different findings. A model that
    names no action in round 1 of every match cannot hold the format at all; a
    model that holds it for twenty rounds and then loses it is degrading as the
    context grows, which is the memory-curse shape this folder is set up to
    watch for. Reported as a mean over lost matches, and `nan` for a model that
    lost none, because zero would read as "failed immediately".
    """
    loose = collections.Counter()
    played = collections.Counter()
    for match in matches:
        played[match["model"]] += 1
        loose[match["model"]] += (match.get("a_parse_fallbacks", 0)
                                  + match.get("b_parse_fallbacks", 0))
    failed = collections.Counter(record["model"] for record in lost)
    reached = collections.defaultdict(list)
    for record in lost:
        reached[record["model"]].append(record.get("rounds_completed", 0))
    models = sorted(set(played) | set(failed))
    return [(model, played[model], failed[model], loose[model],
             _mean(reached[model])) for model in models]
