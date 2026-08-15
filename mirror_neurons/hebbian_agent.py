"""The mirror-neuron agent, unchanged from the original internship notebook.

Lifted out of `mirror_neurons_rerun.ipynb` so that the notebook and the Axelrod
wrapper play the same object rather than two copies of it. The class body is
byte-for-byte what the original defined. Nothing about the model is corrected
here; what the rerun corrects is recorded in this folder's README.
"""

import numpy as np


class HebbianMirrorNeuronAgent:
    """Unchanged from the original. Observing an action strengthens it."""

    def __init__(self, learning_rate=2 ** 0.5 - 1, cooperation_rate=0.8):
        self.actions = ["Cooperate", "Defect"]
        self.weights = {"Cooperate": cooperation_rate, "Defect": 1 - cooperation_rate}
        self.learning_rate = learning_rate

    def observe_and_learn(self, human_action):
        self.weights[human_action] += self.learning_rate * self.weights[human_action]
        total = self.weights["Cooperate"] + self.weights["Defect"]
        self.weights["Cooperate"] /= total
        self.weights["Defect"] /= total

    def select_action(self):
        return np.random.choice(
            self.actions, p=[self.weights["Cooperate"], self.weights["Defect"]])
