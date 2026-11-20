"""Gate28 complete finite causal grammar and diagnostic-only control-coverage audit.

This is NOT a trained Bayesian baseline or a primary scientific comparison.
Uses private generator rules ONLY inside the diagnostic audit, never as
learner training, action-selection, initialization or held-out evidence.
"""
from __future__ import annotations

from itertools import combinations, permutations

import bayes
import world

DIAGNOSTIC_SEEDS = tuple(range(900001, 900013))
EXPECTED_COUNTS = (784, 1104, 1500, 1980, 2552, 3224, 280)


def signature(kind: str, parents: tuple[int, ...],
              invert: int) -> tuple[str, tuple[int, ...], int]:
    """Normalize only operator symmetries; preserve causal ordering.

    lag_xor's first parent refers to previous context, so order matters.
    compose's third parent is ANDed with XOR of its first two parents.
    """
    if kind not in world.RULE_DICTIONARY or invert not in (0, 1):
        raise ValueError("INVALID_RULE")
    if kind in ("xor", "and", "or", "nand") and len(parents) == 2:
        normalized = tuple(sorted(parents))
    elif kind == "maj3" and len(parents) == 3:
        normalized = tuple(sorted(parents))
    elif kind == "compose" and len(parents) == 3:
        normalized = (*sorted(parents[:2]), parents[2])
    elif kind == "lag_xor" and len(parents) == 2:
        normalized = tuple(parents)
    else:
        raise ValueError("INVALID_RULE_ARITY")
    if len(set(normalized)) != len(normalized):
        raise ValueError("DUPLICATED_CAUSAL_PARENT")
    return kind, normalized, invert


def universe(node: int) -> frozenset[tuple[str, tuple[int, ...], int]]:
    if type(node) is not int or not 0 <= node < 7:
        raise ValueError("INVALID_NODE")
    candidates = range(8 + node) if node < 6 else range(8, 14)
    out = set()
    for parents in combinations(candidates, 2):
        for kind in ("xor", "and", "or", "nand"):
            for inv in (0, 1):
                out.add(signature(kind, parents, inv))
    if node < 6:
        for parents in permutations(candidates, 2):
            for inv in (0, 1):
                out.add(signature("lag_xor", parents, inv))
    for parents in combinations(candidates, 3):
        for inv in (0, 1):
            out.add(signature("maj3", parents, inv))
        for last in parents:
            pair = tuple(p for p in parents if p != last)
            for inv in (0, 1):
                out.add(signature("compose", pair + (last,), inv))
    result = frozenset(out)
    if len(result) != EXPECTED_COUNTS[node]:
        raise ValueError("GRAMMAR_UNEXPECTED_CARDINALITY")
    return result


FULL_BANKS = tuple(universe(i) for i in range(7))
LEGACY_BANKS = tuple(frozenset(signature(*h) for h in bank)
                     for bank in bayes.BANKS)


def audit() -> dict:
    """Audit private truth with diagnostic seeds only; never score primary."""
    count = full = legacy = 0
    per_family: dict[str, dict[str, int]] = {}
    for seed in DIAGNOSTIC_SEEDS:
        w = world.HiddenWorld(seed, diagnostic=True)
        for layer in ("A", "B"):
            for node in range(7):
                rule = w._rules[layer][node] if node < 6 else w._outputs[layer]
                truth = signature(rule.kind, rule.parents, rule.invert)
                count += 1
                if truth in FULL_BANKS[node]:
                    full += 1
                if truth in LEGACY_BANKS[node]:
                    legacy += 1
                family = layer + "_" + rule.kind
                tally = per_family.setdefault(family, {"total": 0, "full": 0,
                                                       "legacy": 0})
                tally["total"] += 1
                tally["full"] += int(truth in FULL_BANKS[node])
                tally["legacy"] += int(truth in LEGACY_BANKS[node])
    if full != count:
        raise ValueError("FULL_GRAMMAR_DOES_NOT_COVER_GENERATOR")
    if legacy >= count:
        raise ValueError("NEGATIVE_CONTROL_NOT_DISCRIMINATING")
    return {
        "status": "G28_DIAGNOSTIC_GRAMMAR_COVERAGE_PASS",
        "scientific_control_adequacy": "FAIL_LEGACY_BAYES_UNDERCOVERS_TRUTH",
        "source": "diagnostic-private-rule-audit-only",
        "primary_seeds_consumed": False,
        "seeds": len(DIAGNOSTIC_SEEDS),
        "cases": count,
        "complete_cases": full,
        "legacy_96_cases": legacy,
        "complete_bank_sizes": list(EXPECTED_COUNTS),
        "legacy_bank_sizes": [len(v) for v in LEGACY_BANKS],
        "by_family": dict(sorted(per_family.items())),
        "scientific_gain_verified": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), sort_keys=True))
