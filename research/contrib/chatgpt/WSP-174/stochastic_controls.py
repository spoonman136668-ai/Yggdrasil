"""WSP-177: source-free stochastic descendant-color scoring and conventional controls.

Original CausalMBRL chemistry MLP.forward samples from OneHotCategorical.
Only objects ABOVE the intervened object index may have learned downstream
changes; the intervention itself and lower indices are trivially predictable.
No original simulator imports or calls. Do not use this module to grant a lease.
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping
from typing import Any

from public_boundary import ACTION_COUNT, N_COLORS, N_OBJECTS, PublicEvidence, _scene

PUBLIC_POLICY_KEYS = frozenset({"current", "goal"})
SCHEMA = "yggdrasil.wsp177.public-descendant-brier.v1"
# A single categorical color has five classes; ordinary (unscaled)
# multiclass Brier = sum((p_k - indicator[k == observed_color])**2).


def validate_policy_input(values: Any, action: int) -> tuple[tuple[int, int, int], ...]:
    if type(values) is not dict or set(values) != PUBLIC_POLICY_KEYS:
        raise ValueError("WSP177_PUBLIC_POLICY_FIELDS")
    current = _scene(values["current"])
    goal = _scene(values["goal"])
    if any(a[:2] != b[:2] for a, b in zip(current, goal)):
        raise ValueError("WSP177_GOAL_POSITIONS")
    if type(action) is not int or not 0 <= action < ACTION_COUNT:
        raise ValueError("WSP177_ACTION")
    return current


def descendants(action: int) -> tuple[int, ...]:
    if type(action) is not int or not 0 <= action < ACTION_COUNT:
        raise ValueError("WSP177_ACTION")
    return tuple(range(action // N_COLORS + 1, N_OBJECTS))


def _onehot(color: int) -> tuple[float, ...]:
    return tuple(float(k == color) for k in range(N_COLORS))


def identity_forecast(policy_input: dict[str, object], action: int) -> dict[int, tuple[float, ...]]:
    """Zero-learning control: all downstream objects retain present color."""
    current = validate_policy_input(policy_input, action)
    return {i: _onehot(current[i][2]) for i in descendants(action)}


def uniform_forecast(policy_input: dict[str, object], action: int) -> dict[int, tuple[float, ...]]:
    """Zero-learning uniform color control."""
    validate_policy_input(policy_input, action)
    return {i: tuple(1.0 / N_COLORS for _ in range(N_COLORS)) for i in descendants(action)}


def descendant_brier(observed: PublicEvidence,
                     prediction: Mapping[int, tuple[float, ...]]) -> float | None:
    """Mean proper multiclass Brier across strictly downstream color variables.

    Called *after* the action; prediction MUST have been computed only from
    current+public goal and the action. Zero-descendant actions return None,
    never misleading zero-loss/passing information.
    """
    if type(observed) is not PublicEvidence:
        raise ValueError("WSP177_PUBLIC_EVIDENCE")
    expected = descendants(observed.action)
    if type(prediction) is not dict or set(prediction) != set(expected):
        raise ValueError("WSP177_FORECAST_KEYS")
    if not expected:
        return None
    totals: list[float] = []
    for i in expected:
        probs = prediction[i]
        if type(probs) not in (tuple, list) or len(probs) != N_COLORS:
            raise ValueError("WSP177_FORECAST_SHAPE")
        if any(type(p) not in (float, int) or not math.isfinite(p) or
               not (0 <= p <= 1) for p in probs):
            raise ValueError("WSP177_FORECAST_PROBABILITY")
        if not math.isclose(math.fsum(probs), 1.0, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError("WSP177_FORECAST_NORMALIZATION")
        color = observed.next[i][2]
        totals.append(math.fsum((p - float(k == color)) ** 2
                                for k, p in enumerate(probs)))
    return math.fsum(totals) / len(expected)


class ConditionalDirichlet:
    """Exactly fitted categorical count/Bayes control for a declared feature family.

    Public condition: intervention action, downstream object, and its PRE-action
    color; predicted target is POST-action downstream color. With alpha=1 for
    all 5 colors, exact posterior predictive is (count+1)/(N+5). This is
    converged for its categorical model class, NOT a claim to be the strongest
    conventional neural/graphical reference.
    """
    def __init__(self) -> None:
        self._counts: dict[tuple[int, int, int], Counter[int]] = {}
        self._frozen = False
        self.fit_records = 0
        self.fit_descendants = 0

    def fit_observed(self, observed: PublicEvidence) -> None:
        if self._frozen:
            raise ValueError("WSP177_FIT_FROZEN")
        if type(observed) is not PublicEvidence:
            raise ValueError("WSP177_PUBLIC_EVIDENCE")
        for i in descendants(observed.action):
            key = (observed.action, i, observed.current[i][2])
            self._counts.setdefault(key, Counter())[observed.next[i][2]] += 1
            self.fit_descendants += 1
        self.fit_records += 1

    def freeze(self) -> None:
        self._frozen = True

    def forecast(self, policy_input: dict[str, object],
                 action: int) -> dict[int, tuple[float, ...]]:
        if not self._frozen:
            raise ValueError("WSP177_FIT_NOT_FROZEN")
        current = validate_policy_input(policy_input, action)
        output = {}
        for i in descendants(action):
            counts = self._counts.get((action, i, current[i][2]), Counter())
            denominator = sum(counts.values()) + N_COLORS
            output[i] = tuple((counts[k] + 1) / denominator
                              for k in range(N_COLORS))
        return output

    def summary(self) -> dict[str, int | str]:
        return {"schema": SCHEMA, "fit_records": self.fit_records,
                "fit_descendants": self.fit_descendants,
                "conditional_cells": len(self._counts)}
