"""Matched recency-adaptation against a conventional sliding-window control.

Each model receives identical observed consequences after public actions.
Predictions are evaluated before and after every two-observation batch.
A one-observation gate exposes the abstention-versus-forgetting tradeoff.
"""
import json
from time import process_time_ns
from multi_regime_online_comparison import KEYS, REGIMES, score, deep_bytes
from two_hop_evidence_audit import build
from recency_transition_candidate import RecencyTransitionCandidate
from sliding_tabular_control import SlidingTabularControl

def measure(repeats=2):
    archive = dict(build().active_links)
    native = RecencyTransitionCandidate(archive, capacity=128)
    control = SlidingTabularControl(capacity=128)
    rows = []
    total_native_cpu = 0
    total_control_cpu = 0
    for name, successor in REGIMES:
        before = {
            "native": score([native.predict(key) for key in KEYS], successor),
            "control": score([control.predict(key) for key in KEYS], successor),
        }
        samples = [(key, value) for _ in range(repeats)
                   for key, value in zip(KEYS, successor)]
        begin = process_time_ns()
        for key, value in samples:
            native.observe(key, value)
        native_ns = process_time_ns() - begin
        begin = process_time_ns()
        for key, value in samples:
            control.observe(key, value)
        control_ns = process_time_ns() - begin
        total_native_cpu += native_ns
        total_control_cpu += control_ns
        rows.append({
            "regime": name,
            "actions": len(samples),
            "before": before,
            "after": {
                "native": score([native.predict(key) for key in KEYS], successor),
                "control": score([control.predict(key) for key in KEYS], successor),
            },
            "native_cpu_ns": native_ns,
            "control_cpu_ns": control_ns,
        })
    return {
        "stages": rows,
        "actions": sum(row["actions"] for row in rows),
        "native_examples": native.examples,
        "control_examples": control.examples,
        "native_revisions": native.revisions,
        "native_records": native.records(),
        "control_records": control.records(),
        "native_cpu_ns": total_native_cpu,
        "control_cpu_ns": total_control_cpu,
        "native_bytes": deep_bytes((native.archive, native.recent, native._previous)),
        "control_bytes": deep_bytes(control.table),
        "archive_unchanged": native.archive == archive,
    }

def run():
    return {
        "two_sample": measure(2),
        "single_sample": measure(1),
        "scope": "Six public transition regimes; equal action counts and equivalent two-step recency policies",
        "limitation": "Current observations are known public calibration states. Return after two new observations means reacquisition, not zero-shot episodic recall; microtimings are not retail hardware qualification.",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
