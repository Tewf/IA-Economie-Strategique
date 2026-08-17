"""A player backed by a local model, with the same two calls as the Hebbian one.

`HebbianMirrorNeuronAgent` exposes `observe_and_learn` and `select_action`, so
this exposes them too and a harness can seat either kind of player without
knowing which it has. What differs is what the two calls mean: the Hebbian agent
updates a weight, this one appends a round to a transcript and asks a model.

It adds two calls the Hebbian agent cannot have, `say` and `hear`, because cheap
talk is one of the two things the report defines that only a talking player can
do. A harness asks `can_talk` rather than assuming.

Every reply is kept whole in `self.transcript`, reasoning included and kept
apart from the answer. The reasoning is the object of study here, not a
by-product of getting the action, so discarding it would throw away the
experiment.
"""

import json
import time
import urllib.request

from panel_config import (CONTEXT_TOKENS, OLLAMA_HOST, PANEL,
                          REQUEST_TIMEOUT_SECONDS, TEMPERATURE)

ACTION_LINE = "ACTION:"


class UnparseableReply(ValueError):
    """The model named no action. A result about the model, not an error to hide."""


class OllamaPlayer:
    """One model, one game, one running transcript."""

    can_talk = True

    def __init__(self, model, system_prompt, actions=("Cooperate", "Defect"),
                 temperature=TEMPERATURE, seed=0, max_tokens=None, think=None,
                 message_prompt=None):
        settings = PANEL.get(model, {})
        self.model = model
        self.system_prompt = system_prompt
        # A cheap-talk turn needs its own instructions. Left to the action
        # prompt, a model obeys "answer in exactly this format" and sends an
        # ACTION line as its message, which announces the move it is about to
        # make and stops the choice being simultaneous at all.
        self.message_prompt = message_prompt or system_prompt
        self.actions = list(actions)
        self.temperature = temperature
        self.seed = seed
        self.max_tokens = max_tokens or settings.get("max_tokens", 300)
        self.context_tokens = settings.get("context_tokens", CONTEXT_TOKENS)
        self.think = settings.get("think", False) if think is None else think
        self.history = []       # what the opponent played, oldest first
        self.own_history = []   # what this player played, same order
        self.heard = []         # messages received, one per round played
        self.said = []          # messages sent
        self.transcript = []    # every reply in full, reasoning kept separate
        self.parse_fallbacks = 0

    # The two calls the Hebbian agent also has.

    def observe_and_learn(self, opponent_action):
        """No weight to update. The round becomes context for the next call."""
        self.history.append(opponent_action)

    def select_action(self):
        reply = self._ask(self._round_prompt(), self.system_prompt)
        action = self._parse_action(reply["content"])
        self.own_history.append(action)
        return action

    # The two only a talking player has.

    def say(self):
        """One non-binding message, written before either side has acted."""
        reply = self._ask(self._message_prompt(), self.message_prompt)
        message = reply["content"].strip().strip('"').strip()
        self.said.append(message)
        return message

    def hear(self, message):
        self.heard.append(message)

    # Everything below is how the two are built.

    def _rounds_so_far(self):
        """Both sides of every completed round, which is what a player remembers.

        The opponent's history alone is not enough. A player that cannot see its
        own past moves cannot know its score and cannot run any strategy that
        refers to what it did, which is most of them.
        """
        lines = []
        for index, theirs in enumerate(self.history):
            mine = self.own_history[index] if index < len(self.own_history) else "?"
            said = self.said[index] if index < len(self.said) else None
            heard = self.heard[index] if index < len(self.heard) else None
            line = f"Round {index + 1}: you chose {mine}, they chose {theirs}."
            if said is not None and heard is not None:
                line += f' Before choosing you said "{said}" and they said "{heard}".'
            lines.append(line)
        return lines

    def _round_prompt(self):
        rounds = self._rounds_so_far()
        heading = ("This is the first round." if not rounds
                   else "\n".join(rounds))
        pending = ""
        if len(self.heard) > len(self.history):
            pending = (f'\nBefore this round they said: "{self.heard[-1]}"'
                       f'\nYou said: "{self.said[-1]}"')
        return (f"{heading}{pending}\n\nRound {len(self.history) + 1}. "
                f"Which action do you choose?")

    def _message_prompt(self):
        rounds = self._rounds_so_far()
        heading = ("This is the first round." if not rounds
                   else "\n".join(rounds))
        return (f"{heading}\n\nBefore round {len(self.history) + 1} you may send "
                f"the other player one short message. They are writing theirs at "
                f"the same time, so neither of you can see the other's first. "
                f"The message is not binding. Write only the message.")

    def _ask(self, user_message, system):
        """One call, keeping the answer and any reasoning apart.

        qwen3 returns its reasoning in `message.thinking` rather than in
        `content`. Reading only `content`, which this file used to do, silently
        discarded the reasoning on the one model that produces it explicitly.

        **The user message is not kept, and that is the whole size of the log.**
        It is `_round_prompt` or `_message_prompt` applied to the rounds played
        so far, so every byte of it is already in the record and grows with the
        match: keeping it made prompt echoes 94% of a 39 MB log, of which the
        one thing not recoverable, the system prompt that is the treatment, was
        the part not stored at all. `run_experiment` writes that once per run.
        """
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user_message}],
            "stream": False,
            "think": self.think,
            "options": {"temperature": self.temperature, "seed": self.seed,
                        "num_predict": self.max_tokens,
                        "num_ctx": self.context_tokens},
        }).encode()
        request = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat", data=body,
            headers={"Content-Type": "application/json"})
        started = time.monotonic()
        with urllib.request.urlopen(request,
                                    timeout=REQUEST_TIMEOUT_SECONDS) as response:
            answer = json.load(response)
        message = answer["message"]
        # Timed per call, because the first call to a cold model also pays to
        # load it from disk. A long run pays that once per model; a rate that
        # smears it over three calls prices the grid at several times its cost.
        reply = {"content": message.get("content", ""),
                 "thinking": message.get("thinking", ""),
                 # How close this call came to the window. Recorded because a
                 # prompt over `num_ctx` is cut rather than refused, and the cut
                 # takes the system prompt first, so the only way to know the
                 # experiment was still the experiment is to hold the number.
                 "prompt_tokens": answer.get("prompt_eval_count"),
                 "seconds": round(time.monotonic() - started, 3)}
        self.transcript.append(reply)
        return reply

    def _parse_action(self, reply):
        """The action on the ACTION line, or the first one named anywhere.

        Every prompt asks for the action on its own first line, so that line is
        the answer and anything later is commentary. Reading the whole reply
        instead scores "I will not Defect, I choose Cooperate" as a defection.
        The loose reading is kept as a fallback because a model that ignores the
        format still made a choice, and each use is counted so the write-up can
        say how often the format held.
        """
        for line in reply.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith(ACTION_LINE):
                named = self._first_named(stripped[len(ACTION_LINE):])
                if named:
                    return named
        named = self._first_named(reply)
        if named:
            self.parse_fallbacks += 1
            return named
        raise UnparseableReply(f"{self.model} named no action in: {reply!r}")

    def _first_named(self, text):
        found = sorted((text.upper().find(a.upper()), a) for a in self.actions
                       if text.upper().find(a.upper()) >= 0)
        return found[0][1] if found else None
