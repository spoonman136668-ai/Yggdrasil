"""Frozen synthetic CCE03 research evaluator; not native Yggdrasil first-use.

No two-step learning, no hidden parent labels, no post-hoc tuning.
"""
import argparse
import json
import random
import time
from pathlib import Path
from cce03 import Ecology, TRAIN, BITS, ACTIONS

SEEDS = (13, 29, 53, 97, 181)
EVAL = 384
MODES = ("cce", "full", "one", "pooled")


def transition(x: int, action: int, positive: bool) -> int:
    if not positive:
        return x
    def bit(i):
        return (x >> i) & 1
    result = x
    if action == 0:
        if bit(2) ^ bit(3):
            result ^= 1 << 0
        if bit(1) & bit(5):
            result ^= 1 << 4
    elif action == 1:
        if bit(0) & bit(4):
            result ^= 1 << 1
        result ^= 1 << 3
    elif action == 2:
        if bit(1) ^ bit(5):
            result ^= 1 << 2
        if bit(3):
            result ^= 1 << 5
    return result


def one_world(seed: int, positive: bool) -> dict:
    rng = random.Random(seed)
    learner = Ecology()
    training_start = time.perf_counter()
    for _ in range(TRAIN):
        state, action = rng.randrange(64), rng.randrange(ACTIONS)
        next_state = transition(state, action, positive)
        learner.observe(state, action, next_state)
    learner.freeze()
    trained_seconds = time.perf_counter() - training_start
    cold = Ecology.restore(learner.snapshot())
    cold_equal = (learner.snapshot() == cold.snapshot()
                  and learner.chosen_parents() == cold.chosen_parents()
                  and all(learner.predict_step(x, a, mode=mode)
                          == cold.predict_step(x, a, mode=mode)
                          for x in range(64) for a in range(ACTIONS)
                          for mode in MODES))
    val_rng = random.Random(seed + 300000)
    exact_counts = {mode: 0 for mode in MODES}
    bit_errors = {mode: 0 for mode in MODES}
    for _ in range(EVAL):
        x = val_rng.randrange(64)
        first = val_rng.randrange(ACTIONS)
        second = val_rng.randrange(ACTIONS)
        truth = transition(transition(x, first, positive), second, positive)
        for mode in MODES:
            predicted = learner.predict_two(x, first, second, mode=mode)
            exact_counts[mode] += int(predicted == truth)
            bit_errors[mode] += (predicted ^ truth).bit_count()
    chosen = learner.chosen_parents()
    return {
        "seed": seed, "world": "positive" if positive else "null",
        "train_events": TRAIN, "eval_events": EVAL,
        "two_step_exact": {mode: exact_counts[mode] / EVAL for mode in MODES},
        "two_step_bit_error": {mode: bit_errors[mode] / (BITS * EVAL) for mode in MODES},
        "nonempty_selected_parent_slots": sum(bool(parents) for parents in chosen.values()),
        "selected_parents": chosen,
        "checkpoint_bytes": len(learner.snapshot()),
        "total_hypotheses": BITS * ACTIONS * 16,
        "cold_equal": cold_equal,
        "train_wall_seconds_diagnostic": trained_seconds,
    }


def benchmark() -> dict:
    positive = [one_world(s, True) for s in SEEDS]
    null = [one_world(s, False) for s in SEEDS]
    averages = {mode: sum(row["two_step_exact"][mode] for row in positive) / len(SEEDS)
                for mode in MODES}
    strongest = max(averages[mode] for mode in MODES if mode != "cce")
    margin = averages["cce"] - strongest
    cold_count = sum(row["cold_equal"] for row in positive)
    null_all_empty = sum(row["nonempty_selected_parent_slots"] == 0 for row in null)
    supported = (averages["cce"] >= 0.80 and margin >= 0.10
                 and cold_count == 5 and null_all_empty == 5)
    partial = any(averages["cce"] > averages[mode] for mode in MODES if mode != "cce")
    return {
        "schema": "yggdrasil.y2.cce03.dev-result.v1",
        "classification": "DEVELOPMENT_SIGNAL" if supported else "MIXED" if partial else "NEGATIVE",
        "scientific_gain_verified": False,
        "native_yggdrasil_qualification": False,
        "seeds": list(SEEDS), "train_events": TRAIN, "eval_events": EVAL,
        "average_positive_two_step_exact": averages,
        "strongest_matched_control_exact": strongest,
        "margin_vs_strongest": margin,
        "cold_equal_seeds": cold_count, "null_all_empty_seeds": null_all_empty,
        "positive": positive, "null": null,
        "limits": ["Fixed bit-slot identities supplied as observations; no entity discovery",
                   "Synthetic sparse deterministic environment only",
                   "No raw perception, long-term interference, native Yggdrasil or AGI evidence",
                   "Hypothesis-selection memory and compute exceed pooled control",
                   "No independent scientific reproduction"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(benchmark(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
