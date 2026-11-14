"""Frozen WSP88 action-consequence comparison; reserved DEV requires explicit flag."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from world import make_world
from weights import DirectWeights, GradientSoftmaxControl, LiteralLookup, WIDTH, SGD_EPOCHS

FIXTURE_SEEDS = (92001, 92002)
RESERVED_DEV_SEEDS = (13011, 13012, 13013, 13014, 13015, 13016, 13017, 13018)


def accuracy(predictions, labels) -> float:
    return sum(x == y for x, y in zip(predictions, labels)) / len(labels)


def freeze(*values) -> str:
    return hashlib.sha256(json.dumps(values, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()


def single_world(seed: int) -> dict:
    start = time.process_time_ns()
    world = make_world(seed)
    numeric = DirectWeights()
    literal = LiteralLookup()
    conventional = GradientSoftmaxControl()
    examples: list[tuple[str, int]] = []
    paid_actions = 0

    def acquire(utterances):
        nonlocal paid_actions
        for phrase in utterances:
            successes = 0
            for actuator in range(3):
                reward = world.probe(phrase, actuator)
                paid_actions += 1
                numeric.observe(phrase, actuator, reward)
                literal.observe(phrase, actuator, reward)
                if reward:
                    examples.append((phrase, actuator))
                    successes += 1
            assert successes == 1, "inconsistent world intervention consequence"

    # Stage A: paid observations only; raw strings and binary rewards.
    acquire(world.train_a)
    conventional.fit(tuple(examples))
    qa_num = tuple(numeric.predict(q) for q in world.eval_a)
    qa_sgd = tuple(conventional.predict(q) for q in world.eval_a)
    qa_lit = tuple(literal.predict(q) for q in world.eval_a)
    snap_a = numeric.snapshot()
    assert tuple(DirectWeights.restore(snap_a).predict(q) for q in world.eval_a) == qa_num

    # Stage B: nine new utterances with 27 paid trials. No old example replay
    # in direct numeric learner; the ordinary trained baseline is refitted on
    # exactly the same historical observations, and its extra compute measured.
    acquire(world.train_b)
    conventional.fit(tuple(examples))
    qb_num = tuple(numeric.predict(q) for q in world.eval_b)
    qb_sgd = tuple(conventional.predict(q) for q in world.eval_b)
    qold_num = tuple(numeric.predict(q) for q in world.eval_a)
    qold_sgd = tuple(conventional.predict(q) for q in world.eval_a)
    unknown = tuple(numeric.predict(q) for q in world.unknown)
    snap_b = numeric.snapshot()
    restored = DirectWeights.restore(snap_b)
    cold_equal = (
        tuple(restored.predict(q) for q in world.eval_b) == qb_num
        and tuple(restored.predict(q) for q in world.eval_a) == qold_num
    )
    invalid = json.loads(snap_b)
    invalid["payload"]["weights"][0][0] += 1.0
    tamper_rejected = False
    try:
        DirectWeights.restore(json.dumps(invalid))
    except ValueError:
        tamper_rejected = True

    # Keep action-feedback class counts but break association with raw phrases.
    shuffled = DirectWeights()
    rng = random.Random(seed + 8420)
    labels = [action for _, action in examples[:len(world.train_a)]]
    rng.shuffle(labels)
    for (phrase, _), wrong in zip(examples[:len(world.train_a)], labels):
        for actuator in range(3):
            shuffled.observe(phrase, actuator, actuator == wrong)
    qshuffled = tuple(shuffled.predict(q) for q in world.eval_a)

    # True actuator assignments are read only after all predictions were frozen.
    prediction_sha = freeze(qa_num, qa_sgd, qa_lit, qb_num, qb_sgd,
                            qold_num, qold_sgd, unknown, qshuffled)
    truth_a = world.evaluator_truth(world.eval_a)
    truth_b = world.evaluator_truth(world.eval_b)
    train_correct = sum(conventional.predict(text) == target for text, target in examples)

    return {
        "seed": seed,
        "stageA_correct": sum(a == b for a, b in zip(qa_num, truth_a)),
        "stageA_total": len(truth_a),
        "stageB_new_correct": sum(a == b for a, b in zip(qb_num, truth_b)),
        "stageB_new_total": len(truth_b),
        "old_after_stageB_correct": sum(a == b for a, b in zip(qold_num, truth_a)),
        "old_after_stageB_total": len(truth_a),
        "trained_softmax_A_correct": sum(a == b for a, b in zip(qa_sgd, truth_a)),
        "trained_softmax_B_correct": sum(a == b for a, b in zip(qb_sgd, truth_b)),
        "trained_softmax_old_retained": sum(a == b for a, b in zip(qold_sgd, truth_a)),
        "trained_softmax_train_correct": train_correct,
        "trained_softmax_train_total": len(examples),
        "literal_A_correct": sum(a == b for a, b in zip(qa_lit, truth_a)),
        "shuffled_A_correct": sum(a == b for a, b in zip(qshuffled, truth_a)),
        "unknown_confident": sum(x is not None for x in unknown),
        "unknown_total": len(unknown),
        "paid_actions": paid_actions,
        "weight_count": WIDTH * 3,
        "softmax_epochs_per_stage": SGD_EPOCHS,
        "cold_bitwise_predictions_equal": cold_equal,
        "tamper_rejected": tamper_rejected,
        "stageA_numeric_snapshot_sha256": hashlib.sha256(snap_a.encode()).hexdigest(),
        "stageB_numeric_snapshot_sha256": hashlib.sha256(snap_b.encode()).hexdigest(),
        "all_predictions_frozen_before_oracle_sha256": prediction_sha,
        "whole_process_cpu_ns": time.process_time_ns() - start,
    }


def classify(rows: list[dict], *, dev: bool) -> dict:
    trial_checks = []
    for r in rows:
        stageA = r["stageA_correct"] / r["stageA_total"]
        stageB = r["stageB_new_correct"] / r["stageB_new_total"]
        retain = r["old_after_stageB_correct"] / r["old_after_stageB_total"]
        sgdA = r["trained_softmax_A_correct"] / r["stageA_total"]
        sgdB = r["trained_softmax_B_correct"] / r["stageB_new_total"]
        checks = {
            "heldout_old_90pct": stageA >= 0.90,
            "fewshot_new_alias_75pct": stageB >= 0.75,
            "old_retention_95pct": retain >= 0.95,
            "literal_gain_30pp": stageA - r["literal_A_correct"] / r["stageA_total"] >= 0.30,
            "shuffled_no_shortcut_45pct": r["shuffled_A_correct"] / r["stageA_total"] <= 0.45,
            "unknown_95pct_abstain": r["unknown_confident"] / r["unknown_total"] <= 0.05,
            "within_10pp_converged_SGD": max(sgdA - stageA, sgdB - stageB) <= 0.10,
            "fully_trained_SGD_control": r["trained_softmax_train_correct"] == r["trained_softmax_train_total"],
            "cold_snapshot": r["cold_bitwise_predictions_equal"],
            "tamper_detected": r["tamper_rejected"],
            "paid_351_interventions": r["paid_actions"] == 351,
            "whole_CPU_timed": r["whole_process_cpu_ns"] > 0
        }
        trial_checks.append({"seed": r["seed"], "checks": checks, "passed": all(checks.values())})
    passed = len(rows) == (8 if dev else 2) and all(x["passed"] for x in trial_checks)
    return {
        "schema": "wsp88.raw-utterance-grounding-result.v1",
        "cohort": "RESERVED_DEV_FIRST_USE" if dev else "PUBLIC_DEVELOPMENT_FIXTURE",
        "classification": (
            ("DEV_GROUNDING_FEASIBLE" if passed else "DEV_GROUNDING_NEGATIVE")
            if dev else ("FIXTURE_FEASIBLE" if passed else "FIXTURE_NEGATIVE")
        ),
        "worlds_passed": sum(x["passed"] for x in trial_checks),
        "worlds_total": len(rows),
        "checks": trial_checks,
        "stageA_correct": sum(r["stageA_correct"] for r in rows),
        "stageA_total": sum(r["stageA_total"] for r in rows),
        "stageB_correct": sum(r["stageB_new_correct"] for r in rows),
        "stageB_total": sum(r["stageB_new_total"] for r in rows),
        "retained_correct": sum(r["old_after_stageB_correct"] for r in rows),
        "retained_total": sum(r["old_after_stageB_total"] for r in rows),
        "symbolic_knowledge_equivalence_not_claimed": True,
        "scientific_acceptance": "UNVERIFIED",
        "general_intelligence_or_language_mastery": False,
        "deployment": "NONE",
        "trials": rows
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--public-fixtures-only", action="store_true")
    mode.add_argument("--reserved-dev-first-use", action="store_true")
    args = ap.parse_args()
    seeds = FIXTURE_SEEDS if args.public_fixtures_only else RESERVED_DEV_SEEDS
    result = classify([single_world(seed) for seed in seeds], dev=args.reserved_dev_first_use)
    print("WSP88_RESULT=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
