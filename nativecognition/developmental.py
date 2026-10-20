"""NCI-01 Yggdrasil local developmental-cell learning seam.

The genome is a shared, trainable THREE-weight local update rule. Phenotype
consists of bounded per-cell state and activity. No transformer, global
attention, external model or saved phenotype is used for development/regrowth.
This is an unaccepted source-only primitive, not a claim of regeneration.
"""
from __future__ import annotations

import json
import math


class Colony:
    CELLS = 8
    WEIGHTS = 3

    def __init__(self, learning_rate: float = 0.05) -> None:
        if not self._valid(learning_rate) or not 0 <= learning_rate <= 0.2:
            raise ValueError("invalid learning rate")
        self.learning_rate = float(learning_rate)
        self.genome = [0.3, 0.2, 0.1]  # self, local-neighbor, local-signal
        self.state = [0.0] * self.CELLS
        self.alive = [True] * self.CELLS
        self.steps = 0

    @staticmethod
    def _valid(v: object) -> bool:
        return isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)

    def _input(self, stimuli: list[float]) -> list[float]:
        if len(stimuli) != self.CELLS or any(
            not self._valid(x) or abs(x) > 1 for x in stimuli
        ):
            raise ValueError("invalid bounded local stimuli")
        return [float(x) for x in stimuli]

    def _features(self, index: int, stimulus: float) -> tuple[float, float, float]:
        left, right = (index - 1) % self.CELLS, (index + 1) % self.CELLS
        local = [(self.state[j] if self.alive[j] else 0.0) for j in (left, right)]
        return self.state[index], (local[0] + local[1]) / 2.0, stimulus

    def step(self, stimuli: list[float], targets: list[float] | None = None) -> tuple[float, ...]:
        """Synchronous local phenotype update; optional training-only outcome signal.

        Targets train the common developmental rule via source-local prediction
        errors and never become phenotype state or future evaluation queries.
        """
        signals = self._input(stimuli)
        outcomes = self._input(targets) if targets is not None else None
        if self.steps >= 1_000_000:
            raise ValueError("development step limit reached")
        if any(not self._valid(w) or abs(w) > 3 for w in self.genome):
            raise ValueError("genome outside hard bounds")
        states: list[float] = list(self.state)
        gradient = [0.0] * self.WEIGHTS
        count = 0
        for i in range(self.CELLS):
            if not self.alive[i]:
                states[i] = 0.0
                continue
            features = self._features(i, signals[i])
            out = math.tanh(sum(w * x for w, x in zip(self.genome, features)))
            states[i] = out
            if outcomes is not None:
                residual = outcomes[i] - out
                for k in range(self.WEIGHTS):
                    gradient[k] += residual * (1 - out * out) * features[k]
                count += 1
        # The genome is trained from local prediction errors; each output was
        # computed with the OLD shared genome and OLD neighboring states.
        if count and self.learning_rate:
            for k in range(self.WEIGHTS):
                self.genome[k] = max(-3.0, min(3.0, self.genome[k] +
                        self.learning_rate * gradient[k] / count))
        self.state = states
        self.steps += 1
        return tuple(states)

    def lesion(self, index: int) -> None:
        self._check_index(index)
        self.alive[index] = False
        self.state[index] = 0.0

    def regrow(self, index: int, local_signal: float) -> float:
        """Instantiate a missing cell from current neighbor state + genome only.

        No saved pre-lesion phenotype or full previous checkpoint is consulted.
        This operation alone does NOT demonstrate recovered task capability.
        """
        self._check_index(index)
        if self.alive[index]:
            raise ValueError("cell is not missing")
        if not self._valid(local_signal) or abs(local_signal) > 1:
            raise ValueError("invalid local regrowth stimulus")
        left, right = (index - 1) % self.CELLS, (index + 1) % self.CELLS
        if not (self.alive[left] or self.alive[right]):
            raise ValueError("no surviving local neighbor")
        features = self._features(index, float(local_signal))
        regenerated = math.tanh(sum(w * x for w, x in zip(self.genome, features)))
        self.state[index] = regenerated
        self.alive[index] = True
        return regenerated

    def genome_checkpoint(self) -> bytes:
        """Persistent genome only; phenotype is deliberately excluded."""
        if any(not self._valid(w) or abs(w) > 3 for w in self.genome):
            raise ValueError("invalid genome")
        return json.dumps({"version": 1, "weights": self.genome},
                          sort_keys=True, separators=(",", ":")).encode("ascii")

    @classmethod
    def from_genome(cls, data: bytes, learning_rate: float = 0.0) -> "Colony":
        if len(data) > 512:
            raise ValueError("oversized genome checkpoint")
        obj = json.loads(data.decode("ascii"))
        if (not isinstance(obj, dict) or set(obj) != {"version", "weights"}
                or obj["version"] != 1 or not isinstance(obj["weights"], list)
                or len(obj["weights"]) != cls.WEIGHTS or any(
                  not cls._valid(x) or abs(x) > 3 for x in obj["weights"])):
            raise ValueError("invalid genome schema")
        colony = cls(learning_rate)
        colony.genome = list(obj["weights"])
        return colony

    @classmethod
    def _check_index(cls, index: int) -> None:
        if type(index) is not int or index < 0 or index >= cls.CELLS:
            raise ValueError("invalid cell identity")
