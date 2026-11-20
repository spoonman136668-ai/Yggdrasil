"""Gate24 source-free opt-in symmetric cross-view interaction probe.

Research-only shadow calculation; NEVER alters native/JEPA source or checkpoints.
Protocol: symmetric_pair_residual_freeze.md, committed before implementation.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import exp, isfinite, log
import json

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist

RIDGE = 0.05
NEWTON_STEPS = 14
EXTRAS = (0, 0, 0)
PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))
SCHEMA = "yggdrasil.amalgam.symmetric-pair-residual-dev.v1"


def _sigmoid(x):
    return 1.0 / (1.0 + exp(-x)) if x >= 0 else exp(x) / (1.0 + exp(x))


def _public_pair(views):
    if (type(views) is not tuple or len(views) != 2
            or any(type(v) is not tuple or len(v) != 2 for v in views)
            or any(type(bit) is not int or bit not in (0, 1)
                   for v in views for bit in v)
            or views[0][0] != views[1][0]):
        raise ValueError("GATE24_PUBLIC_PAIR")
    return views[0][1], views[1][1]


def _features(views, *, interaction):
    a, b = _public_pair(views)
    basic = (1.0, float(a + b))
    return basic + (float(a * b),) if interaction else basic


def rows(law, context):
    if law not in ("xor", "or") or type(context) is not int or context not in (0, 1):
        raise ValueError("GATE24_LAW_CONTEXT")
    result = []
    for rep in range(4):
        for a, b in PAIRS:
            y = (a ^ b) if law == "xor" else (a | b)
            identifier = f"gate24/{law}/{rep}/{a}/{b}"
            result.append((identifier, ((context, a), (context, b)), y))
    return tuple(result)


def _solve_spd(hessian, gradient):
    """Deterministic fixed-order elimination: ridge makes Hessian positive definite."""
    n = len(gradient)
    a = [list(hessian[i]) + [gradient[i]] for i in range(n)]
    for i in range(n):
        pivot = a[i][i]
        if not (isfinite(pivot) and pivot > 1e-14):
            raise ValueError("GATE24_HESSIAN_PIVOT")
        for j in range(i + 1, n):
            factor = a[j][i] / pivot
            for k in range(i + 1, n + 1):
                a[j][k] -= factor * a[i][k]
            a[j][i] = 0.0
    out = [0.0] * n
    for i in range(n - 1, -1, -1):
        out[i] = (a[i][n] - sum(a[i][j] * out[j]
                               for j in range(i + 1, n))) / a[i][i]
    return out


class SymmetricPairResidual:
    """A small learnable shadow-only residual; default OFF returns old p exactly."""

    def __init__(self, *, interaction=True):
        if type(interaction) is not bool:
            raise ValueError("GATE24_INTERACTION_TYPE")
        self.interaction = interaction
        self.weights = (0.0,) * (3 if interaction else 2)
        self.fit_rows = 0
        self.row_exposures = 0

    def fit(self, witnessed_rows):
        if (type(witnessed_rows) is not tuple or len(witnessed_rows) != 16
                or any(type(row) is not tuple or len(row) != 3
                       or type(row[0]) is not str
                       or type(row[2]) is not int or row[2] not in (0, 1)
                       for row in witnessed_rows)
                or len({r[0] for r in witnessed_rows}) != 16):
            raise ValueError("GATE24_FIT_WITNESSES")
        tape = [(_features(views, interaction=self.interaction), label)
                for _, views, label in witnessed_rows]
        n = len(self.weights)
        w = [0.0] * n
        for _ in range(NEWTON_STEPS):
            g = [RIDGE * w[i] for i in range(n)]
            h = [[RIDGE if i == j else 0.0 for j in range(n)]
                 for i in range(n)]
            for x, label in tape:
                p = _sigmoid(sum(w[i] * x[i] for i in range(n)))
                v = p * (1.0 - p)
                for i in range(n):
                    g[i] += (p - label) * x[i]
                    for j in range(n):
                        h[i][j] += v * x[i] * x[j]
            step = _solve_spd(h, g)
            for i in range(n):
                w[i] -= step[i]
        if not all(isfinite(v) and abs(v) < 100 for v in w):
            raise ValueError("GATE24_NUMERIC")
        self.weights = tuple(w)
        self.fit_rows = len(tape)
        self.row_exposures = NEWTON_STEPS * len(tape)
        return self

    def probability(self, original_probability, views, *, enabled=False):
        if type(enabled) is not bool:
            raise ValueError("GATE24_ENABLED_TYPE")
        # Critical reversible boundary: no view transforms or fp arithmetic
        # affect the old specialist in the default-disabled state.
        if not enabled:
            return original_probability
        if (type(original_probability) is not float
                or not isfinite(original_probability)
                or not 0.0 <= original_probability <= 1.0):
            raise ValueError("GATE24_ORIGINAL_PROBABILITY")
        x = _features(views, interaction=self.interaction)
        p = min(1.0 - 1e-12, max(1e-12, original_probability))
        shift = sum(a * b for a, b in zip(self.weights, x))
        return _sigmoid(log(p / (1.0 - p)) + shift)


def _pair_counts(tape):
    count = defaultdict(lambda: [0, 0])
    for _, views, y in tape:
        count[_public_pair(views)][y] += 1
    return {pair: Fraction(count[pair][1] + 1, sum(count[pair]) + 2)
            for pair in PAIRS}


def _symbolic_fit(tape):
    hypotheses = {
        "xor": lambda a, b: a ^ b,
        "or": lambda a, b: a | b,
    }
    exact = [name for name, law in hypotheses.items()
             if all(law(*_public_pair(views)) == y for _, views, y in tape)]
    if len(exact) != 1:
        raise ValueError("GATE24_SYMBOLIC_NOT_IDENTIFIED")
    return hypotheses[exact[0]], exact[0]


def _score(probs, eval_rows):
    return {
        "correct": sum(int(probs[_public_pair(views)] > 0.5) == y
                       for _, views, y in eval_rows) // 4,
        "brier": sum((probs[_public_pair(views)] - y)**2
                     for _, views, y in eval_rows) / len(eval_rows),
    }


def audit_law(law):
    fit_tape = rows(law, 0)
    eval_tape = rows(law, 1)
    base = ActionLatentSpecialist("reward")
    for _, views, y in fit_tape:
        base.observe(views, EXTRAS, y)
    before_weights = json.dumps(base.as_data(), sort_keys=True, separators=(",", ":"))
    before = {
        pair: base.probability(((1, pair[0]), (1, pair[1])), *EXTRAS)
        for pair in PAIRS
    }

    full = SymmetricPairResidual(interaction=True).fit(fit_tape)
    ablated = SymmetricPairResidual(interaction=False).fit(fit_tape)
    enabled = {pair: full.probability(before[pair],
                                     ((1, pair[0]), (1, pair[1])), enabled=True)
               for pair in PAIRS}
    no_interaction = {pair: ablated.probability(
        before[pair], ((1, pair[0]), (1, pair[1])), enabled=True)
        for pair in PAIRS}
    disabled = {pair: full.probability(
        before[pair], ((1, pair[0]), (1, pair[1])))
        for pair in PAIRS}
    counts = _pair_counts(fit_tape)
    symbolic, selected = _symbolic_fit(fit_tape)
    exact = {pair: Fraction(symbolic(*pair), 1) for pair in PAIRS}
    after_weights = json.dumps(base.as_data(), sort_keys=True, separators=(",", ":"))
    return {
        "schema": SCHEMA,
        "law": law,
        "fit_rows": len(fit_tape),
        "eval_rows_untrained": len(eval_tape),
        "full_params": len(full.weights),
        "ablation_params": len(ablated.weights),
        "newton_steps": NEWTON_STEPS,
        "row_exposures_each_residual_arm": full.row_exposures,
        "weights": full.weights,
        "base_weights_unchanged": before_weights == after_weights,
        "off_mode_exact": disabled == before,
        "base": _score(before, eval_tape),
        "active": _score(enabled, eval_tape),
        "no_interaction": _score(no_interaction, eval_tape),
        "pair_count": _score(counts, eval_tape),
        "exact_symbolic": _score(exact, eval_tape),
        "symbolic_fit_selected": selected,
        "original_source_actions": 0,
        "canonical_model_updates": 0,
        "scientific_pass": False,
    }


def audit():
    xor = audit_law("xor")
    other = audit_law("or")
    # Cross-law active readout is tested against a separate law it did NOT fit:
    # a known regression risk; no beneficial cumulative retention is inferred.
    base = ActionLatentSpecialist("reward")
    for _, views, y in rows("xor", 0):
        base.observe(views, EXTRAS, y)
    adapter = SymmetricPairResidual().fit(rows("xor", 0))
    activated = {pair: adapter.probability(
        base.probability(((1, pair[0]), (1, pair[1])), *EXTRAS),
        ((1, pair[0]), (1, pair[1])), enabled=True) for pair in PAIRS}
    other["xor_adapter_on_or"] = _score(activated, rows("or", 1))
    return {"schema": SCHEMA, "xor": xor, "or_negative": other,
            "integration_authority": "NONE_SHADOW_RESEARCH_ONLY",
            "scientific_pass": False}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2, default=str))
