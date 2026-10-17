"""F99P pure query-blind native path-closure feasibility primitives.

This is NOT an online policy, learned model, heldout evaluator, or authority.
Only source-native record tuples are analyzed. Future observations, eventual
question, true answer and source-family labels are not accepted as inputs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREREG_BLOB = "9abcfbde16137d15248e8ce1229660a46b853dc1"
F98_METHOD_BLOB = "4a03573c31d24decd9a058c4930a8e9a6fbc1f3f"
MAX_SIGNATURES = 250_000
MEMORY_BYTES = 144


class ClosureLimitExceeded(RuntimeError):
    """Fail closed; do not silently truncate exact native memory paths."""


def git_blob_sha(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def frozen_dependencies():
    """Load immutable predecessor with exact SHA checks; no cohort access."""
    assert git_blob_sha(HERE / "prereg.json") == PREREG_BLOB, "F99_PREREG_DRIFT"
    f98_path = ROOT / "20261016-y-f98" / "microchain.py"
    assert git_blob_sha(f98_path) == F98_METHOD_BLOB, "F99_PARENT_METHOD_DRIFT"
    spec = importlib.util.spec_from_file_location("f99_exact_f98", f98_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.dependencies()


def signed_reverse(codes):
    """Reverse the path, exchanging every role with its signed inverse."""
    codes = tuple(codes)
    if not codes or any(type(v) is not int or not 0 <= v <= 7 for v in codes):
        raise ValueError("F99_INVALID_NATIVE_ROLE_CODE")
    return tuple(code ^ 1 for code in reversed(codes))


def native_arcs(memory):
    """Represent only given native packed-record endpoint paths, both ways."""
    arcs = defaultdict(set)
    for source, target, codes in memory:
        if type(source) is not int or type(target) is not int or source == target:
            raise ValueError("F99_INVALID_NATIVE_ENDPOINTS")
        codes = tuple(codes)
        inverse = signed_reverse(codes)
        arcs[source].add((target, codes))
        arcs[target].add((source, inverse))
    return {source: tuple(sorted(options)) for source, options in arcs.items()}


def closure(memory, max_hops=6, max_signatures=MAX_SIGNATURES):
    """Exact endpoint + ordered signed-role reachability within native memory.

    A stored multi-role native record has no named intermediate endpoints;
    it is atomic for joining. Only matching retained record endpoints compose.
    Path reuse is permitted and bounded by role hop count (not time/index).
    """
    if type(max_hops) is not int or not 1 <= max_hops <= 6:
        raise ValueError("F99_HOP_BOUND")
    if type(max_signatures) is not int or max_signatures < 1:
        raise ValueError("F99_RESOURCE_BOUND")
    if len(memory) > 12:
        raise ValueError("F99_NATIVE_RECORD_CAP")
    arcs = native_arcs(memory)
    signatures = set()
    frontier = deque()
    for source, options in arcs.items():
        for target, codes in options:
            if len(codes) > max_hops:
                continue
            entry = (source, codes, target)
            if entry not in signatures:
                signatures.add(entry)
                if len(signatures) > max_signatures:
                    raise ClosureLimitExceeded("F99_SOURCE_RESOURCE_INELIGIBLE")
                frontier.append(entry)
    while frontier:
        start, codes, intermediate = frontier.popleft()
        for target, extra in arcs.get(intermediate, ()):
            length = len(codes) + len(extra)
            if length > max_hops:
                continue
            entry = (start, codes + extra, target)
            if entry not in signatures:
                signatures.add(entry)
                if len(signatures) > max_signatures:
                    raise ClosureLimitExceeded("F99_SOURCE_RESOURCE_INELIGIBLE")
                frontier.append(entry)
    return frozenset(signatures)


def eligible_closure(baseline, candidate):
    """Pure task-blind necessary-condition screen; not a correctness oracle."""
    baseline_signatures = closure(baseline)
    candidate_signatures = closure(candidate)
    retained = {row for row in baseline_signatures if len(row[1]) <= 4}
    preservation = retained.issubset(candidate_signatures)
    baseline_long = {row for row in baseline_signatures if 5 <= len(row[1]) <= 6}
    candidate_long = {row for row in candidate_signatures if 5 <= len(row[1]) <= 6}
    gained = len(candidate_long - baseline_long)
    return dict(
        short_signatures_preserved=preservation,
        four_hop_signatures_lost=len(retained - candidate_signatures),
        novel_five_six_hop_signatures=gained,
        eligible=preservation and gained > 0,
    )


def audit_native_prefix(memory, event, index, pack, native):
    """Enumerate EVERY source-native action; query and future events forbidden."""
    if not 0 <= index < 72 or len(event) != 3:
        raise ValueError("F99_PREFIX_BOUND")
    f60 = native._f60_step(memory, event, pack)
    choices = native.actions(memory, event, index, pack)
    if sum(1 for opt in choices if opt[3] == f60) != 1:
        raise AssertionError("F99_NATIVE_F60_PARITY")
    native._valid_memory(f60, pack)
    for rec in f60:
        if len(pack.pack(*rec)) != 12:
            raise AssertionError("F99_NATIVE_PACKING_DRIFT")
    results = []
    for j, option in enumerate(choices):
        after = option[3]
        if after == f60:
            continue
        native._valid_memory(after, pack)
        if len(after) > 12 or sum(len(pack.pack(*rec)) for rec in after) > MEMORY_BYTES:
            raise AssertionError("F99_NATIVE_BUDGET")
        comparison = eligible_closure(f60, after)
        results.append(dict(action_index=j, **comparison))
    return f60, tuple(results)
