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


def _settled_from(match):
    """The first round after which the pair never changed its joint outcome.

    Round 0 means the opening decided the whole match. A late round means the
    pair moved, which is the thing `self_play_lock_in` cannot show: it reports
    that a match ended settled, never whether it was settled from the start.
    Returns the round index and the regime, or None if the tail is not one
    regime throughout.
    """
    rounds = match["rounds"]
    tail = rounds[-SETTLED_TAIL:]
    for regime in ("Cooperate", "Defect"):
        if all(step["a_action"] == step["b_action"] == regime for step in tail):
            first = len(rounds) - SETTLED_TAIL
            while first > 0:
                step = rounds[first - 1]
                if step["a_action"] != regime or step["b_action"] != regime:
                    break
                first -= 1
            return first, regime
    return None


def settling(matches):
    """How long a self-play pair took to reach the regime it ended in.

    The lock-in table answers whether the opening captured a pair. This one
    answers whether it captured it *immediately*, which is what separates "the
    first round decided everything" from "there was a window and it closed".
    """
    grouped = collections.defaultdict(list)
    for match in matches:
        if match["cell"] != "self_play":
            continue
        grouped[(match["model"], match["opening"], match["condition"])].append(match)
    rows = []
    for (model, opening, condition), played in sorted(grouped.items()):
        settled = [_settled_from(match) for match in played]
        cooperative = [at for at, regime in filter(None, settled)
                       if regime == "Cooperate"]
        defective = [at for at, regime in filter(None, settled)
                     if regime == "Defect"]
        rows.append((model, opening, condition, len(played),
                     len(cooperative), _mean(cooperative),
                     len(defective), _mean(defective),
                     sum(outcome is None for outcome in settled)))
    return rows


ONE_SHOT_LOG = pathlib.Path(__file__).parent / "results" / "one_shot.jsonl"


def read_one_shot(log=ONE_SHOT_LOG):
    """Every decision from the one-shot games. A separate log, and separate here.

    The Dictator and Ultimatum games are one decision rather than thirty rounds,
    so they share no field with `matches.jsonl` and are kept out of it. Reading
    them here rather than in a second module keeps one home for "every table the
    write-up quotes".
    """
    if not log.exists():
        return []
    decisions = []
    for line in log.read_text().splitlines():
        try:
            decisions.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return decisions


def one_shot_offers(decisions):
    """What each model gives, and what it demands, across the two games.

    The pair is the measurement, not either game alone. The Dictator game has no
    rejection, so what is offered there is disposition; the Ultimatum proposer
    faces the same split with a refusal possible, so **the difference between the
    two is what a model gives in order not to be refused**. The responder's
    stated minimum is asked before any proposal is shown, so it cannot be an
    accommodation to one, and it is the number that says whether a model would
    accept its own offer.
    """
    grouped = collections.defaultdict(list)
    for decision in decisions:
        if decision["value"] is None:
            continue
        grouped[(decision["model"], decision["game"], decision["role"])].append(
            decision["value"])
    rows = []
    for model in sorted({decision["model"] for decision in decisions}):
        given = grouped[(model, "dictator", "")]
        offered = grouped[(model, "ultimatum", "proposer")]
        demanded = grouped[(model, "ultimatum", "responder")]
        gap = (_mean(offered) - _mean(given)
               if given and offered else float("nan"))
        rows.append((model, len(given), _mean(given), len(offered),
                     _mean(offered), gap, len(demanded), _mean(demanded),
                     _mean(offered) < _mean(demanded) if offered and demanded
                     else False))
    return rows


def opening_round(matches):
    """What a pair does in the first round it actually controls.

    The crux of the whole grid, and the one round where the evidence available
    to a model is known exactly. Before round 0 a model holds the payoff matrix,
    plus a fabricated history if the cell imposes one, plus a message if the cell
    has a channel, and nothing else: no play of its own to cite. Since almost
    every match settles at round 0 (`settling`), this is where the outcome is
    decided, and separating the three sources of evidence is what tells a model
    that ignores messages apart from one that has none to read.
    """
    grouped = collections.defaultdict(list)
    for match in matches:
        if match["cell"] != "self_play":
            continue
        key = (match["model"], match["opening"], match["condition"])
        first = match["rounds"][0]
        grouped[key].extend([first["a_action"] == "Cooperate",
                             first["b_action"] == "Cooperate"])
    return [(model, opening, condition, len(seats), _mean(seats))
            for (model, opening, condition), seats in sorted(grouped.items())]


def _messages(match, seat):
    return [step[f"{seat}_message"] for step in match["rounds"]
            if step.get(f"{seat}_message")]


def message_content(matches):
    """What the non-binding messages actually say, where there is a channel.

    The grid's claim is about what a message does, and until this table the
    messages themselves were never read: only whether the *reason* attached to
    an action named that action. Three lexical facts, which is all the text can
    honestly support without a second model judging it:

    - whether a message names Cooperate or Defect at all, so a channel that goes
      unused looks different from one that proposes something and is ignored;
    - which of the two it names, so a pair talking itself into defection is not
      counted the same as a pair proposing cooperation;
    - whether both seats sent the identical string, which in self-play is the
      degenerate case the temperature was raised to avoid.
    """
    grouped = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for match in matches:
        if match["condition"] != "with_cheap_talk" or match["cell"] != "self_play":
            continue
        counted = grouped[(match["model"], match["opening"])]
        for step in match["rounds"]:
            said = [step.get("a_message") or "", step.get("b_message") or ""]
            for text in said:
                if not text:
                    continue
                counted[0] += 1
                upper = text.upper()
                counted[1] += "COOPERAT" in upper
                counted[2] += "DEFECT" in upper
                counted[3] += len(text)
            counted[4] += bool(said[0]) and said[0] == said[1]
    rows = []
    for (model, opening), (sent, naming_c, naming_d, characters,
                           identical) in sorted(grouped.items()):
        rows.append((model, opening, sent,
                     naming_c / sent if sent else float("nan"),
                     naming_d / sent if sent else float("nan"),
                     characters / sent if sent else float("nan"),
                     identical))
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
