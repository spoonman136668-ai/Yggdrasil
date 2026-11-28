"""Native R7 local-cell plasticity versus conventional recency on public changes.

For each observed public two-hop consequence, predict whether the outcome
equals its PREVIOUSLY LEARNED archive prediction. The underlying native
eight-cell colony receives four binary public features and delayed completed
feedback; the tabular control observes the same completed outcome. No hidden
regime label, no novelty oracle, no original DoorKey evidence. Public context
routing and binary target reduce this to a diagnostic, NOT full successor
prediction or autonomous navigation.
"""
import json
from time import process_time_ns
from native_cells_r7 import Colony
from sliding_tabular_control import SlidingTabularControl
from multi_regime_online_comparison import REGIMES, KEYS, deep_bytes
from two_hop_evidence_audit import build

def public_features(key):
    frame, action = key
    if not isinstance(frame, bytes) or not frame or type(action) is not int:
        raise ValueError("INVALID_PUBLIC_KEY")
    return (bool(frame[0] & 1), bool(frame[-1] & 1),
            bool(action & 1), bool(len(frame) & 1))

def public_context(key):
    # Declared observable partition, not discovered causal identity.
    frame, _ = key
    return "A" if frame.startswith(b"M") else "B"

def measure(repeats=2):
    archive = dict(build().archived_links)
    colony = Colony()
    control = SlidingTabularControl(capacity=128)
    stages = []
    native_ns = 0
    control_ns = 0
    for name, successors in REGIMES:
        truths = [value == archive[key] for key, value in zip(KEYS, successors)]
        pre_native = [colony.predict(public_context(key), public_features(key))
                      for key in KEYS]
        pre_control = [control.predict(key) for key in KEYS]
        for _ in range(repeats):
            for key, expected_match in zip(KEYS, truths):
                started = process_time_ns()
                colony.learn_completed_public_feedback(
                    public_context(key), public_features(key),
                    expected_match, delay_steps=2)
                native_ns += process_time_ns() - started
                started = process_time_ns()
                control.observe(key, b"1" if expected_match else b"0")
                control_ns += process_time_ns() - started
        post_native = [colony.predict(public_context(key), public_features(key))
                       for key in KEYS]
        post_control = [control.predict(key) for key in KEYS]
        def scored(predictions):
            return {
                "correct": sum(p is not None and p == t for p, t in zip(predictions, truths)),
                "wrong": sum(p is not None and p != t for p, t in zip(predictions, truths)),
                "abstain": sum(p is None for p in predictions),
            }
        stages.append({
            "name": name,
            "actions": len(KEYS) * repeats,
            "pre_native": scored(pre_native),
            "pre_control": scored(
                [None if p is None else p == b"1" for p in pre_control]),
            "native": scored(post_native),
            "control": scored(
                [None if p is None else p == b"1" for p in post_control]),
        })
    state = colony.checkpoint()
    restarted = Colony.restore(state)
    return {
        "stages": stages,
        "actions": sum(row["actions"] for row in stages),
        "colony_feedback_updates": colony.feedback_updates,
        "colony_neighbor_messages": colony.neighbor_messages,
        "control_examples": control.examples,
        "cold_restore_equal": all(
            restarted.predict(public_context(key), public_features(key)) ==
            colony.predict(public_context(key), public_features(key))
            for key in KEYS),
        "native_cpu_ns": native_ns,
        "control_cpu_ns": control_ns,
        "native_checkpoint_bytes": len(state),
        "control_bytes": deep_bytes(control.table),
        "archive_unchanged": archive == build().archived_links,
    }

def run():
    return {
        "two_observation": measure(2),
        "single_observation": measure(1),
        "scope": "Actual R7 native local cells, binary public-change feedback, matched conventional recency",
        "limitations": "Fixed public sensory mapping and binary outcome; this does not prove learned successor identity, cognitive transfer or zero-shot regime recognition",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
