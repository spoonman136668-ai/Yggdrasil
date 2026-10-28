"""Matched repeated-regime online adaptation and retention audit.

Both policies receive the same action-owned public transitions and the same
number of observations. Compare predictions BEFORE and AFTER each batch, so
delayed adaptation and forgetting cannot be hidden by final-only scoring.
CPU timings are per-run process time; structural bytes are recursive Python
object footprints (not RSS or energy). The native policy here is specifically
its public-transition adapter, not the full local-cell architecture.
"""
import json
import sys
from time import process_time_ns
from conventional_online_baseline import TabularOnlineBaseline
from online_public_learning import PublicOnlineTransitions
from two_hop_evidence_audit import build, SECOND

KEYS = tuple((frame, action) for frame, action, _, _ in SECOND)
REGIMES = (
    ("A_initial", (b"R3-positive", b"F4-negative")),
    ("B_switch", (b"X5-shift", b"Y6-shift")),
    ("C_unfamiliar", (b"N7-novel", b"P8-novel")),
    ("A_return", (b"R3-positive", b"F4-negative")),
    ("C_return", (b"N7-novel", b"P8-novel")),
    ("B_return", (b"X5-shift", b"Y6-shift")),
)

def deep_bytes(obj, seen=None):
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen:
        return 0
    seen.add(oid)
    result = sys.getsizeof(obj)
    if isinstance(obj, dict):
        return result + sum(deep_bytes(k, seen) + deep_bytes(v, seen)
                            for k, v in obj.items())
    if isinstance(obj, (list, tuple, set, frozenset)):
        return result + sum(deep_bytes(x, seen) for x in obj)
    return result

def score(predictions, expected):
    return {
        "correct": sum(a == b for a, b in zip(predictions, expected)),
        "wrong": sum(a is not None and a != b
                     for a, b in zip(predictions, expected)),
        "abstentions": sum(a is None for a in predictions),
    }

def measure(repetitions=2):
    frozen = build().active_links
    native = PublicOnlineTransitions(frozen, capacity=128)
    tabular = TabularOnlineBaseline(capacity=128, min_support=2)
    history = []
    total_native_ns = 0
    total_tabular_ns = 0
    for regime, expected in REGIMES:
        before = {
            "native": score([native.links.get(key) for key in KEYS], expected),
            "tabular": score([tabular.predict(key) for key in KEYS], expected),
        }
        # Calibration samples are produced by a fixed public-action fixture.
        # Neither policy is informed of regime identity or future consequences.
        samples = [(key, value) for _ in range(repetitions)
                   for key, value in zip(KEYS, expected)]
        start = process_time_ns()
        for key, value in samples:
            native.observe(key, value)
        native_ns = process_time_ns() - start
        start = process_time_ns()
        for key, value in samples:
            tabular.observe(key, value)
        tabular_ns = process_time_ns() - start
        total_native_ns += native_ns
        total_tabular_ns += tabular_ns
        history.append({
            "regime": regime,
            "actions": len(samples),
            "before": before,
            "after": {
                "native": score([native.links.get(key) for key in KEYS], expected),
                "tabular": score([tabular.predict(key) for key in KEYS], expected),
            },
            "native_cpu_ns": native_ns,
            "tabular_cpu_ns": tabular_ns,
            "native_bytes": deep_bytes((native.links, native.observations)),
            "tabular_bytes": deep_bytes(tabular.counts),
        })
    return {
        "stages": history,
        "total_actions": sum(s["actions"] for s in history),
        "native_examples": native.examples(),
        "tabular_examples": tabular.examples,
        "native_revisions": native.changes,
        "native_records": len(native.links),
        "tabular_records": tabular.records(),
        "native_cpu_ns": total_native_ns,
        "tabular_cpu_ns": total_tabular_ns,
        "native_bytes": deep_bytes((native.links, native.observations)),
        "tabular_bytes": deep_bytes(tabular.counts),
        "frozen_source_unchanged": frozen[KEYS[0]] == b"X5-shift",
    }

def run():
    return {
        "matched_two_sample": measure(2),
        "single_sample_negative": measure(1),
        "scope": "Six public successor regimes; matched calibration, retention and online-model adaptation",
        "limitations": "Known reachable public states, per-process microtimings not hardware qualification; no standalone task-control comparison.",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
