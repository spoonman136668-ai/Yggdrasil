"""Independent exact finite-hypothesis Bayesian symbolic control for H02.

Consumes ONLY fixed public (probe, noisy observed reward) tuples. Assumes full
published four-family grammar and the true observation noise p=1/8.
NEVER import evaluator, hidden truth, protected world generator, or native weights.
"""
from __future__ import annotations

from collections import defaultdict

GRAMMAR = tuple((family, mask) for family in range(4) for mask in range(1, 64))
assert len(GRAMMAR) == 252


def causal_answer(family: int, mask: int, probe: int) -> int:
    if (type(family) is not int or family not in range(4) or
        type(mask) is not int or not 1 <= mask <= 63 or
        type(probe) is not int or not 1 <= probe < 64):
        raise ValueError("H02_INVALID_CANDIDATE")
    n = (mask & probe).bit_count()
    if family == 0:
        return n & 1
    if family == 1:
        return int(n >= 2)
    if family == 2:
        return (n & 1) ^ int((probe & 3) == 3)
    return int(n == 1)


def validate_source(rows):
    if type(rows) not in (tuple, list) or len(rows) != 12:
        raise ValueError("H02_BAD_SOURCE_COUNT")
    actions = []
    for row in rows:
        if type(row) is not tuple or len(row) != 2:
            raise ValueError("H02_BAD_ROW")
        p, y = row
        if (type(p) is not int or not 1 <= p < 64 or
            type(y) is not int or y not in (0, 1)):
            raise ValueError("H02_BAD_RECORD")
        actions.append(p)
    if len(set(actions)) != 12:
        raise ValueError("H02_DUPLICATE_PROBE")
    return tuple(rows)


class ExactBayes:
    def __init__(self, source):
        self.source = validate_source(source)
        self.weighted = []
        for family, mask in GRAMMAR:
            mismatches = sum(causal_answer(family, mask, p) != y for p, y in source)
            # (7/8) for match and (1/8) for mismatch; integer proportional weights.
            self.weighted.append((family, mask, 7 ** (12 - mismatches)))
        self.partition = sum(w for _, _, w in self.weighted)
        assert self.partition > 0

    def posterior_probability_one(self, probe: int) -> float:
        num = sum(w for f, m, w in self.weighted if causal_answer(f, m, probe))
        return num / self.partition

    def predict(self, probe: int) -> int:
        return int(self.posterior_probability_one(probe) > 0.5)


def prior_predict(probe: int) -> int:
    return int(sum(causal_answer(f, m, probe) for f, m in GRAMMAR) > len(GRAMMAR) / 2)


def version_space_aliases(source_probes, heldout_probes):
    """Index observational fingerprints over *all* allowed hidden laws."""
    by_sig = defaultdict(list)
    for program in GRAMMAR:
        by_sig[tuple(causal_answer(*program, p) for p in source_probes)].append(program)
    return {sig: tuple(progs) for sig, progs in by_sig.items()}


def is_query_identifiable(source_probes, heldout_probes, evaluator_clean_source, evaluator_clean_heldout):
    aliases = version_space_aliases(source_probes, heldout_probes)
    matched = aliases.get(tuple(evaluator_clean_source), ())
    if not matched:
        return False, 0
    return (all(tuple(causal_answer(*pr, p) for p in heldout_probes)
                == tuple(evaluator_clean_heldout) for pr in matched), len(matched))
