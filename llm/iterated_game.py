"""One iterated Prisoner's Dilemma match between any two players.

It never learns what kind of player it is driving. Anything exposing
`observe_and_learn` and `select_action` can be seated, which is how a model, an
Axelrod strategy and a stub all run through the same loop, and why the loop can
be tested with no GPU and no network.

**Cheap talk is simultaneous.** Both players write before either has heard the
other, then both hear, then both act. Letting one read the other's message first
would hand the second speaker an advantage that is not in Ng's design, and it is
the kind of thing that is invisible in a result and obvious in a loop, so the
order below is deliberate rather than incidental.
"""

import axelrod as axl

TO_AXELROD = {"Cooperate": axl.Action.C, "Defect": axl.Action.D}


def exchange_messages(player_a, player_b):
    """Both write blind, then both hear. Returns what each said."""
    said_a = player_a.say()
    said_b = player_b.say()
    player_a.hear(said_b)
    player_b.hear(said_a)
    return said_a, said_b


def play_round(player_a, player_b, game, cheap_talk):
    """One round: talk if the condition says so, then act, then tell each other."""
    said_a = said_b = None
    if cheap_talk:
        said_a, said_b = exchange_messages(player_a, player_b)
    action_a = player_a.select_action()
    action_b = player_b.select_action()
    player_a.observe_and_learn(action_b)
    player_b.observe_and_learn(action_a)
    score_a, score_b = game.score((TO_AXELROD[action_a], TO_AXELROD[action_b]))
    # Axelrod scores are numpy integers, which json.dumps refuses. The log is
    # the only copy of a run that costs hours, so it is written in plain types.
    return {"a_action": action_a, "b_action": action_b,
            "a_message": said_a, "b_message": said_b,
            "a_score": int(score_a), "b_score": int(score_b)}


def play_match(player_a, player_b, rounds, game, cheap_talk):
    """A whole match, as the record that gets written to the log.

    Transcripts are kept whole rather than reduced to the actions, because the
    reasoning is what the explainability half of this folder measures and it
    cannot be recovered once thrown away.
    """
    if cheap_talk and not (getattr(player_a, "can_talk", False)
                           and getattr(player_b, "can_talk", False)):
        raise ValueError("cheap talk asked of a player that cannot talk")
    played = [play_round(player_a, player_b, game, cheap_talk)
              for _ in range(rounds)]
    return {
        "rounds": played,
        "a_total": sum(step["a_score"] for step in played),
        "b_total": sum(step["b_score"] for step in played),
        "a_transcript": getattr(player_a, "transcript", []),
        "b_transcript": getattr(player_b, "transcript", []),
        "a_parse_fallbacks": getattr(player_a, "parse_fallbacks", 0),
        "b_parse_fallbacks": getattr(player_b, "parse_fallbacks", 0),
    }
