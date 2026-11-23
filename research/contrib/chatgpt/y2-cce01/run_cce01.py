"""Frozen Y2-CCE01 synthetic development benchmark, no external episodes.

Requires preexisting prereg.json committed before implementation/results.
Unit tests may run independently. Primary run must not be repeated/tuned to
turn a negative result positive. This script does not schedule any runner.
"""

import argparse
import json
import random
from pathlib import Path

from cce01 import CausalContractEcology, CountModel

SEEDS = (7, 19, 43, 83, 131)
TRAIN_EVENTS = 192
EVAL_EVENTS = 256
MIN_MARGIN = 0.005


def events(seed: int, count: int, positive: bool):
    generator = random.Random(seed)
    for _ in range(count):
        bits = (generator.randrange(2), generator.randrange(2))
        action = generator.randrange(2)
        # Ground truth used only by the sealed environment, never learner.
        outcome = (action ^ bits[0]) if positive else action
        yield bits, action, outcome


def run_world(seed: int, positive: bool) -> dict:
    learner = CausalContractEcology()
    pooled = CountModel()
    full = CountModel((0, 1))
    for bits, action, outcome in events(seed, TRAIN_EVENTS, positive):
        learner.observe(bits, action, outcome)
        pooled.observe(bits, action, outcome)
        full.observe(bits, action, outcome)

    packed = learner.snapshot()
    cold = CausalContractEcology.restore(packed)
    cold_equal = (
        learner.events == cold.events
        and learner.selected_feature == cold.selected_feature
        and learner.selection_step == cold.selection_step
        and all(
            learner.predict((x0, x1), a) == cold.predict((x0, x1), a)
            for x0 in (0, 1) for x1 in (0, 1) for a in (0, 1)
        )
    )
    scores = {"cce": 0.0, "pooled": 0.0, "full": 0.0}
    for bits, action, outcome in events(seed + 100000, EVAL_EVENTS, positive):
        scores["cce"] += (learner.predict(bits, action) - outcome) ** 2
        scores["pooled"] += (pooled.predict(bits, action) - outcome) ** 2
        scores["full"] += (full.predict(bits, action) - outcome) ** 2
    scores = {name: value / EVAL_EVENTS for name, value in scores.items()}
    return {
        "seed": seed, "world": "positive" if positive else "null",
        "scores": scores, "selected_feature": learner.selected_feature,
        "selection_step": learner.selection_step,
        "cold_equal": cold_equal, "checkpoint_bytes": len(packed),
        "hypothesis_count": 3, "training_events": TRAIN_EVENTS,
        "evaluation_events": EVAL_EVENTS,
    }


def benchmark() -> dict:
    positive = [run_world(seed, True) for seed in SEEDS]
    null = [run_world(seed, False) for seed in SEEDS]
    average_cce = sum(v["scores"]["cce"] for v in positive) / len(SEEDS)
    average_strongest = sum(
        min(v["scores"]["pooled"], v["scores"]["full"])
        for v in positive
    ) / len(SEEDS)
    margin = average_strongest - average_cce
    valid_feature = sum(v["selected_feature"] == 0 for v in positive)
    null_no_split = sum(v["selected_feature"] is None for v in null)
    cold_count = sum(v["cold_equal"] for v in positive)
    positive_seed_wins = sum(
        v["scores"]["cce"] < min(v["scores"]["pooled"], v["scores"]["full"])
        for v in positive
    )
    supported = (margin >= MIN_MARGIN and valid_feature >= 4
                 and null_no_split >= 4 and cold_count == 5)
    mixed = (margin >= MIN_MARGIN or positive_seed_wins > 0
             or valid_feature > 0) and not supported
    classification = ("DEVELOPMENT_SIGNAL" if supported
                      else "MIXED" if mixed else "NEGATIVE")
    return {
        "schema": "yggdrasil.y2.cce01.dev-result.v1",
        "classification": classification,
        "scientific_gain_verified": False,
        "native_yggdrasil_acceptance": False,
        "notes": "Synthetic, fixed two-feature world only. No AGI, novel identity, unfamiliar transfer, fully local cell authority, or independent replication claim.",
        "preregistration": "research/contrib/chatgpt/y2-cce01/prereg.json",
        "frozen": {"seeds": list(SEEDS), "train_events": TRAIN_EVENTS,
                   "eval_events": EVAL_EVENTS, "minimum_margin": MIN_MARGIN},
        "summary": {
            "avg_cce_brier": average_cce,
            "avg_per_seed_strongest_control_brier": average_strongest,
            "margin_vs_strongest": margin,
            "correct_split_seeds": valid_feature,
            "null_no_split_seeds": null_no_split,
            "cold_equal_seeds": cold_count,
            "positive_seed_wins": positive_seed_wins,
        },
        "positive": positive, "null": null,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        help="Write this one preregistered development result as JSON")
    args = parser.parse_args()
    result = benchmark()
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
