"""Development-only, agent-free paired-view latent prediction (not accepted science).

The source encoder and predictor are learned by gradient descent from observed
paired views; a fixed noncollapsed target encoder supplies stop-gradient targets.
No hidden simulator state, text tokens, cloud model, F139 owner or first-use data
enters training. This intentionally simple linear learner is a falsifiable pilot.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, sin

LATENT = 2
INPUT = 3
TARGET = 2
MAX_PAIRS = 4096
MAX_EPOCHS = 200


@dataclass(frozen=True)
class Pair:
    observation: tuple[float, float, float]
    other_view: tuple[float, float]


def development_pairs(start: int, count: int) -> tuple[Pair, ...]:
    """Different observable projections of a source-only synthetic causal world.

    The learner receives only Pair. Hidden state below builds test fixtures,
    not features or labels supplied to learner. This is never sealed first use.
    """
    if type(start) is not int or type(count) is not int or start < 0 or not 2 <= count <= MAX_PAIRS:
        raise ValueError("YGG_JEPA_COHORT_INVALID")
    rows = []
    for i in range(start, start + count):
        x, y = sin(i * .137), cos(i * .097)
        action = 1.0 if i % 2 else -1.0
        next_x = .72 * x + .26 * action
        next_y = .63 * y - .18 * action
        sensor = (x + .23 * y, y - .11 * x, action)
        event = (next_x + .37 * next_y, next_y - .21 * next_x)
        rows.append(Pair(sensor, event))
    return tuple(rows)


def _valid(pairs: tuple[Pair, ...]) -> None:
    if (type(pairs) is not tuple or not 2 <= len(pairs) <= MAX_PAIRS
            or any(type(p) is not Pair or len(p.observation) != INPUT
                   or len(p.other_view) != TARGET
                   or not all(type(v) is float and isfinite(v) and abs(v) <= 10
                              for v in p.observation + p.other_view)
                   for p in pairs)):
        raise ValueError("YGG_JEPA_INPUT_INVALID")
    # Fixed target teacher cannot collapse during training, but reject already
    # collapsed positive pairs instead of reporting a meaningless low loss.
    for k in range(TARGET):
        avg = sum(p.other_view[k] for p in pairs) / len(pairs)
        variance = sum((p.other_view[k] - avg) ** 2 for p in pairs) / len(pairs)
        if variance < .01:
            raise ValueError("YGG_JEPA_COLLAPSED_TARGET")


class PairedViewJEPA:
    """Two-stage trainable linear student with frozen identity target encoder."""

    def __init__(self) -> None:
        self.encoder = [[.5, .05, .02], [-.05, .5, -.02]]
        self.predictor = [[.8, .02], [-.02, .8]]

    def predict(self, observation: tuple[float, float, float]) -> tuple[float, float]:
        if (type(observation) is not tuple or len(observation) != INPUT
                or not all(type(x) is float and isfinite(x) and abs(x) <= 10 for x in observation)):
            raise ValueError("YGG_JEPA_OBSERVATION_INVALID")
        z = [sum(self.encoder[j][k] * observation[k] for k in range(INPUT)) for j in range(LATENT)]
        return tuple(sum(self.predictor[i][j] * z[j] for j in range(LATENT)) for i in range(TARGET))

    def mse(self, pairs: tuple[Pair, ...]) -> float:
        _valid(pairs)
        return sum(sum((v - target)**2 for v, target in zip(self.predict(p.observation), p.other_view))
                   for p in pairs) / (len(pairs) * TARGET)

    def fit(self, pairs: tuple[Pair, ...], *, epochs: int = 100, lr: float = .025) -> None:
        _valid(pairs)
        if type(epochs) is not int or not 1 <= epochs <= MAX_EPOCHS or type(lr) is not float or not 0 < lr <= .1:
            raise ValueError("YGG_JEPA_BUDGET_INVALID")
        # Batch gradients; target branch is never differentiated or updated.
        for _ in range(epochs):
            grad_e = [[0.0] * INPUT for _ in range(LATENT)]
            grad_p = [[0.0] * LATENT for _ in range(TARGET)]
            for p in pairs:
                x, target = p.observation, p.other_view
                z = [sum(self.encoder[j][k] * x[k] for k in range(INPUT)) for j in range(LATENT)]
                output = [sum(self.predictor[i][j] * z[j] for j in range(LATENT)) for i in range(TARGET)]
                errors = [output[i] - target[i] for i in range(TARGET)]
                for i in range(TARGET):
                    for j in range(LATENT):
                        grad_p[i][j] += errors[i] * z[j]
                for j in range(LATENT):
                    backprop = sum(errors[i] * self.predictor[i][j] for i in range(TARGET))
                    for k in range(INPUT):
                        grad_e[j][k] += backprop * x[k]
            scale = lr / len(pairs)
            for i in range(TARGET):
                for j in range(LATENT):
                    self.predictor[i][j] -= scale * max(-100., min(100., grad_p[i][j]))
            for j in range(LATENT):
                for k in range(INPUT):
                    self.encoder[j][k] -= scale * max(-100., min(100., grad_e[j][k]))
            if not all(isfinite(v) for row in self.encoder + self.predictor for v in row):
                raise ValueError("YGG_JEPA_NUMERIC_DIVERGENCE")


def mispaired(pairs: tuple[Pair, ...]) -> tuple[Pair, ...]:
    """Deterministic bad-view control: target comes from a different world."""
    _valid(pairs)
    # Cycle by half of the cohort to break same-world correspondence.
    shift = len(pairs) // 2
    return tuple(Pair(p.observation, pairs[(i + shift) % len(pairs)].other_view)
                 for i, p in enumerate(pairs))


class DirectLinearControl:
    """Fully trained conventional predictor, same paired data and SGD steps.

    Comparison is mandatory for a future science claim. This control has fewer
    parameters than the two-stage student and is not handicapped by poor views.
    """
    def __init__(self) -> None:
        self.weights = [[.5, .05, .02], [-.05, .5, -.02]]

    def predict(self, observation: tuple[float, float, float]) -> tuple[float, float]:
        if type(observation) is not tuple or len(observation) != INPUT or not all(
                type(x) is float and isfinite(x) and abs(x) <= 10 for x in observation):
            raise ValueError("YGG_JEPA_CONTROL_OBSERVATION_INVALID")
        return tuple(sum(self.weights[i][k] * observation[k] for k in range(INPUT))
                     for i in range(TARGET))

    def mse(self, pairs: tuple[Pair, ...]) -> float:
        _valid(pairs)
        return sum(sum((v - target)**2 for v, target in zip(self.predict(p.observation), p.other_view))
                   for p in pairs) / (len(pairs) * TARGET)

    def fit(self, pairs: tuple[Pair, ...], *, epochs: int = 100, lr: float = .025) -> None:
        _valid(pairs)
        if type(epochs) is not int or not 1 <= epochs <= MAX_EPOCHS or type(lr) is not float or not 0 < lr <= .1:
            raise ValueError("YGG_JEPA_CONTROL_BUDGET_INVALID")
        for _ in range(epochs):
            gradients = [[0.0] * INPUT for _ in range(TARGET)]
            for p in pairs:
                out = self.predict(p.observation)
                for i in range(TARGET):
                    error = out[i] - p.other_view[i]
                    for k in range(INPUT):
                        gradients[i][k] += error * p.observation[k]
            for i in range(TARGET):
                for k in range(INPUT):
                    self.weights[i][k] -= lr / len(pairs) * max(-100., min(100., gradients[i][k]))
