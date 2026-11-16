"""NKR-10: bounded read-only *historical* relation-template mining.

This is an engineering diagnostic, not causal identification, source truth
authentication or model admission. Source triples are prior-consumed TRAIN.
No validation/test, probabilistic negative evidence or inferred fact write.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import json
import time

from yggdrasil.native_knowledge_activation import (
    PINNED_PACKED_SHA, PINNED_ROWS, PINNED_TRAIN_SHA, open_installed_session,
)

MAX_ANCHORS = 32768
MAX_EDGES = 8
MAX_JOINS = 2_097_152
MAX_TEMPLATES = 128
MAX_UNIQUE_KEYS = 65536
MIN_SUPPORT = 6
MAX_SECONDS = 180


def _row(weights, index):
    x = weights.row_at(index)
    if (not isinstance(x, (tuple, list)) or len(x) != 3 or
            any(type(n) is not int or not (0 < n <= 0xffffffff) for n in x)):
        raise ValueError("NKR10_MALFORMED_QPQ_ROW")
    return tuple(x)


def _sample_indices(count):
    if type(count) is not int or count < 1:
        raise ValueError("NKR10_EMPTY_SOURCE")
    k = min(MAX_ANCHORS, count)
    if k == 1:
        return (0,)
    return tuple(i * (count - 1) // (k - 1) for i in range(k))


def mine_bounded(weights, *, max_seconds=MAX_SECONDS):
    """Mine witnessed rule triples using only row_at and len, without writes.

    Each anchor X-P3-Z is a *direct existing fact*. A support subject counts
    only if the same source also has X-P1-Y and Y-P2-Z. At most 8 outgoing
    edges for each X and Y are inspected, in source row order. This is a
    biased bounded sample, not comprehensive 21M fact rule mining.
    """
    if type(max_seconds) not in (int, float) or not 0 < max_seconds <= MAX_SECONDS:
        raise ValueError("NKR10_WALL_BUDGET_INVALID")
    n = len(weights)
    indices = _sample_indices(n)
    start = time.monotonic()

    @lru_cache(maxsize=8192)
    def outgoing(subject):
        # Source sorted by (subject, predicate, object). Do not scan entire
        # historical graph or require a separate unpinned index.
        low, high = 0, n
        while low < high:
            mid = (low + high) // 2
            if _row(weights, mid)[0] < subject:
                low = mid + 1
            else:
                high = mid
        out = []
        while low < n and len(out) < MAX_EDGES:
            s, p, o = _row(weights, low)
            if s != subject:
                break
            out.append((p, o))
            low += 1
        return tuple(out)

    subjects = defaultdict(set)
    anchor_subjects = set()
    joins = 0
    previous = None
    for step, index in enumerate(indices):
        if step % 128 == 0 and time.monotonic() - start > max_seconds:
            raise TimeoutError("NKR10_WALL_BUDGET_EXCEEDED")
        s, p3, z = _row(weights, index)
        current = (s, p3, z)
        if previous is not None and current < previous:
            raise ValueError("NKR10_SOURCE_SORT_ORDER")
        previous = current
        anchor_subjects.add(s)
        for p1, y in outgoing(s):
            for p2, zz in outgoing(y):
                joins += 1
                if joins > MAX_JOINS:
                    raise ValueError("NKR10_JOIN_BUDGET_EXCEEDED")
                if zz != z or p3 == p1 or p3 == p2:
                    continue
                key = (p3, p1, p2)
                subjects[key].add(s)
                if len(subjects) > MAX_UNIQUE_KEYS:
                    raise MemoryError("NKR10_UNIQUE_KEY_BUDGET_EXCEEDED")
    if time.monotonic() - start > max_seconds:
        raise TimeoutError("NKR10_WALL_BUDGET_EXCEEDED")
    scored = sorted(
        ([*key, len(witnesses)] for key, witnesses in subjects.items()
         if len(witnesses) >= MIN_SUPPORT),
        key=lambda x: (-x[3], x[0], x[1], x[2]))
    return {
        "schema": "yggdrasil.nkr10.historical-rule-scan.v1",
        "classification": "HISTORICAL_TRAIN_CORRELATION_DIAGNOSTIC",
        "sampled_anchor_rows": len(indices),
        "distinct_anchor_subjects": len(anchor_subjects),
        "bounded_join_witnesses": joins,
        "distinct_candidate_templates": len(subjects),
        "templates_at_min_support": len(scored),
        "top_templates_p3_p1_p2_support": scored[:MAX_TEMPLATES],
        "min_support_unique_subjects": MIN_SUPPORT,
        "max_first_and_second_edges": MAX_EDGES,
        "max_anchors": MAX_ANCHORS,
        "source_sample_bias": "STRIDED_SORTED_ROWS_AND_FIRST_8_OUTGOING",
        "absent_edges_are_negatives": False,
        "verified_new_real_world_facts": 0,
        "identified_causal_laws": 0,
        "scientific_pass": False,
        "native_accepted": False,
        "source_mutated": False,
        "wall_seconds": time.monotonic() - start,
    }


def run_installed_image(path):
    """Explicit opt-in: reuse only previously-consumed, SHA-verified TRAIN."""
    with open_installed_session(path) as session:
        weights = session._weights
        if (len(weights) != PINNED_ROWS or
                weights.manifest["packed_sha256"] != PINNED_PACKED_SHA or
                weights.manifest["source_train_sha256"] != PINNED_TRAIN_SHA):
            raise ValueError("NKR10_HISTORICAL_SOURCE_IDENTITY_DRIFT")
        first = weights.row_at(0)
        last = weights.row_at(len(weights) - 1)
        result = mine_bounded(weights)
        if weights.row_at(0) != first or weights.row_at(len(weights) - 1) != last:
            raise AssertionError("NKR10_HISTORICAL_IMAGE_CHANGED")
        result.update({
            "historical_train_rows": PINNED_ROWS,
            "historical_image_sha256": PINNED_PACKED_SHA,
            "historical_train_sha256": PINNED_TRAIN_SHA,
            "original_scientific_first_use": False,
            "historical_train_previously_consumed": True,
        })
        return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--installed-session", required=True,
                   help="Existing read-only NKR-06 local session; never writes")
    args = p.parse_args()
    print("NKR10_HISTORICAL_RULE_SCAN=" +
          json.dumps(run_installed_image(args.installed_session),
                     sort_keys=True, separators=(",", ":")), flush=True)
