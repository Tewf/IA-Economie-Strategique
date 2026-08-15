"""A player that answers from a script, so the harness can be tested with no model.

Every model call costs GPU time, and the GPU is the one resource on this machine
that a mistake takes down with it. Everything about the loop that is not the
model itself, the talk order, the scoring, the record, the resumability, is
logic and can be checked for free. This is what checks it.

It also records what it knew at the moment it was asked, which is how
`preflight_checks.py` proves the cheap-talk exchange really is simultaneous
rather than merely written to look that way.
"""

import itertools


class StubPlayer:
    """Plays a fixed script and remembers what it had heard when asked."""

    can_talk = True

    def __init__(self, name, script, message="ok"):
        self.name = name
        self.script = itertools.cycle(script)
        self.message = message
        self.history = []
        self.own_history = []
        self.heard = []
        self.said = []
        self.transcript = []
        self.parse_fallbacks = 0
        # For each round, how many messages this player had heard when it wrote.
        self.heard_when_speaking = []

    def say(self):
        self.heard_when_speaking.append(len(self.heard))
        message = f"{self.message} {len(self.said) + 1}"
        self.said.append(message)
        return message

    def hear(self, message):
        self.heard.append(message)

    def select_action(self):
        action = next(self.script)
        self.own_history.append(action)
        # Shaped like a real reply, ACTION line and all, so the checks exercise
        # the parsing and the reason-against-action measure rather than skipping
        # them for want of a REASON line.
        self.transcript.append({
            "content": f"ACTION: {action}\nREASON: I choose to {action} here.",
            "thinking": "",
            "prompt": f"round {len(self.own_history)}"})
        return action

    def observe_and_learn(self, opponent_action):
        self.history.append(opponent_action)
