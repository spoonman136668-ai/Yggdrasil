"""G33: bounded shared-genome NCA development candidate, NOT accepted DG-1.

Exactly one 3x3 neighborhood, fixed 16-channel cell state, no global model,
no cell creation, and no primary task/evaluator. Only deterministic toy
supervision for interface qualification; no scientific learning claim.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random


CHANNELS = 16
HIDDEN = 8
INPUTS = 2 * CHANNELS + 1
OUTPUTS = CHANNELS - 2
GENOME_PARAMETER_COUNT = INPUTS * HIDDEN + HIDDEN + HIDDEN * OUTPUTS + OUTPUTS


def _valid_number(value, limit=4.0):
    return type(value) in (int, float) and math.isfinite(value) and abs(value) <= limit


@dataclass(frozen=True)
class SharedGenome:
    first: tuple[float, ...]
    first_bias: tuple[float, ...]
    second: tuple[float, ...]
    second_bias: tuple[float, ...]

    def __post_init__(self):
        expected = (INPUTS * HIDDEN, HIDDEN, HIDDEN * OUTPUTS, OUTPUTS)
        parts = (self.first, self.first_bias, self.second, self.second_bias)
        if any(type(part) is not tuple or len(part) != n
               for part, n in zip(parts, expected)):
            raise ValueError("YGG_G33_GENOME_SHAPE")
        if any(not _valid_number(x, 10.0) for part in parts for x in part):
            raise ValueError("YGG_G33_GENOME_NONFINITE_OR_UNBOUNDED")

    @property
    def parameter_count(self):
        return sum(map(len, (self.first, self.first_bias,
                             self.second, self.second_bias)))


def seeded_genome(seed=17):
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("YGG_G33_SEED")
    rng = random.Random(seed)

    def weights(n):
        return tuple(rng.uniform(-0.10, 0.10) for _ in range(n))

    return SharedGenome(weights(INPUTS * HIDDEN), (0.0,) * HIDDEN,
                        weights(HIDDEN * OUTPUTS), (0.0,) * OUTPUTS)


@dataclass(frozen=True)
class DG1APrototype:
    """Bounded architecture candidate, not the verified native DG-1 engine.

    Cell 0 is immutable task input; cell channel 1 is an immutable alive gate;
    channels 2..15 are developmental state. The same neural rule is shared
    by all cells, using only the current cell, its Moore neighbors, and
    local sensory. No prediction, label, or reward bit is passed to step().
    """
    width: int = 4
    height: int = 4
    rate: float = 0.125

    def __post_init__(self):
        if (type(self.width) is not int or type(self.height) is not int or
                not 2 <= self.width <= 16 or not 2 <= self.height <= 16 or
                self.width * self.height > 256 or
                type(self.rate) is not float or
                not math.isfinite(self.rate) or not 0.0 < self.rate <= 0.25):
            raise ValueError("YGG_G33_BUDGET_OR_SHAPE")

    def initial_state(self):
        cell = (0.0, 1.0) + (0.0,) * OUTPUTS
        return tuple(tuple(cell for _ in range(self.width))
                     for _ in range(self.height))

    def _validate(self, state, sensory, genome):
        if not isinstance(genome, SharedGenome):
            raise ValueError("YGG_G33_NOT_SHARED_GENOME")
        if len(state) != self.height or len(sensory) != self.height:
            raise ValueError("YGG_G33_GRID")
        for row, inputs in zip(state, sensory):
            if len(row) != self.width or len(inputs) != self.width:
                raise ValueError("YGG_G33_GRID")
            if any(len(cell) != CHANNELS or
                   any(not _valid_number(x) for x in cell) or
                   not 0.0 <= cell[1] <= 1.0 for cell in row):
                raise ValueError("YGG_G33_CELL")
            if any(not _valid_number(x, 1.0) for x in inputs):
                raise ValueError("YGG_G33_SENSORY")

    def _features(self, state, sensory, y, x):
        own = state[y][x]
        near = [state[yy][xx]
                for yy in range(max(0, y - 1), min(self.height, y + 2))
                for xx in range(max(0, x - 1), min(self.width, x + 2))]
        means = tuple(sum(cell[k] for cell in near) / len(near)
                      for k in range(CHANNELS))
        return own + means + (sensory[y][x],)

    @staticmethod
    def _neural(genome, features):
        hidden = tuple(math.tanh(genome.first_bias[j] +
                       sum(genome.first[j * INPUTS + k] * features[k]
                           for k in range(INPUTS))) for j in range(HIDDEN))
        outputs = tuple(math.tanh(genome.second_bias[i] +
                        sum(genome.second[i * HIDDEN + j] * hidden[j]
                            for j in range(HIDDEN))) for i in range(OUTPUTS))
        return hidden, outputs

    def step(self, state, sensory, genome):
        self._validate(state, sensory, genome)
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                old = state[y][x]
                _, output = self._neural(
                    genome, self._features(state, sensory, y, x))
                mutable = tuple(max(-4.0, min(4.0,
                                old[k + 2] + self.rate * old[1] * output[k]))
                                for k in range(OUTPUTS))
                row.append(old[:2] + mutable)
            rows.append(tuple(row))
        return tuple(rows)

    def fit_one_cell(self, state, sensory, genome, y, x, target, learning_rate=0.5):
        """One transparent supervised DEV gradient step on mutable channel 2.

        target must be derived from a permitted DEV task, never protected
        outcomes. This is an interface/gradient test, not primary learning.
        """
        self._validate(state, sensory, genome)
        if (type(y) is not int or type(x) is not int or not 0 <= y < self.height
                or not 0 <= x < self.width or not _valid_number(target) or
                type(learning_rate) is not float or
                not math.isfinite(learning_rate) or
                not 0.0 < learning_rate <= 0.5):
            raise ValueError("YGG_G33_TRAINING_BUDGET")
        features = self._features(state, sensory, y, x)
        hidden, outputs = self._neural(genome, features)
        old = state[y][x]
        predicted = old[2] + self.rate * old[1] * outputs[0]
        error = predicted - target
        d2 = error * self.rate * old[1] * (1.0 - outputs[0] ** 2)
        first = list(genome.first)
        b1 = list(genome.first_bias)
        second = list(genome.second)
        b2 = list(genome.second_bias)
        for j in range(HIDDEN):
            d1 = d2 * genome.second[j] * (1.0 - hidden[j] ** 2)
            for k in range(INPUTS):
                first[j * INPUTS + k] -= learning_rate * d1 * features[k]
            b1[j] -= learning_rate * d1
            second[j] -= learning_rate * d2 * hidden[j]
        b2[0] -= learning_rate * d2
        return SharedGenome(tuple(first), tuple(b1), tuple(second), tuple(b2))
