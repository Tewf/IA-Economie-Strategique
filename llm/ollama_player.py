"""A player backed by a local model, with the same two calls as the Hebbian one.

`HebbianMirrorNeuronAgent` exposes `observe_and_learn` and `select_action`, so
this exposes them too and a harness can seat either kind of player without
knowing which it has. What differs is what the two calls mean: the Hebbian agent
updates a weight, this one appends a round to a transcript and asks a model.

Every reply is kept whole in `self.transcript`, not just the action parsed out
of it. The reasoning a model gives is the object of study here, not a by-product
of getting the action, so discarding it would throw away the experiment.
"""

import json
import urllib.request

from panel_config import MAX_TOKENS, OLLAMA_HOST, REQUEST_TIMEOUT_SECONDS, SEED, TEMPERATURE


class OllamaPlayer:
    """One model, one game, one running transcript."""

    def __init__(self, model, system_prompt, actions=("Cooperate", "Defect"),
                 temperature=TEMPERATURE, seed=SEED):
        self.model = model
        self.system_prompt = system_prompt
        self.actions = list(actions)
        self.temperature = temperature
        self.seed = seed
        self.history = []      # what the opponent has played, oldest first
        self.transcript = []   # every reply in full, for the cheap-talk study

    def observe_and_learn(self, opponent_action):
        """No weight to update. The round becomes context for the next call."""
        self.history.append(opponent_action)

    def select_action(self):
        reply = self._ask(self._round_prompt())
        self.transcript.append(reply)
        return self._parse_action(reply)

    def _round_prompt(self):
        if not self.history:
            return "This is the first round. Which action do you choose?"
        played = ", ".join(self.history)
        return (f"So far the other player has chosen, in order: {played}.\n"
                f"Round {len(self.history) + 1}. Which action do you choose?")

    def _ask(self, user_message):
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": self.system_prompt},
                         {"role": "user", "content": user_message}],
            "stream": False,
            "options": {"temperature": self.temperature, "seed": self.seed,
                        "num_predict": MAX_TOKENS},
        }).encode()
        request = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)["message"]["content"]

    def _parse_action(self, reply):
        """First action named in the reply wins.

        Raises rather than defaulting. A model that answered nothing usable is a
        result about that model, and silently scoring it as a defection would
        report the parser's opinion as the model's.
        """
        positions = [(reply.upper().find(a.upper()), a) for a in self.actions]
        found = sorted((p, a) for p, a in positions if p >= 0)
        if not found:
            raise ValueError(f"{self.model} named no action in: {reply!r}")
        return found[0][1]
