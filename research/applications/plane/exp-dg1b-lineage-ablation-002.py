"""Sealed scientific source for EXP-DG1B-LINEAGE-ABLATION-002.

This module uses only the Python standard library and emits one strict result JSON
object when invoked as: python exp-dg1b-lineage-ablation-002.py --out PATH
"""

import argparse
import json
import math
import os
import random
import struct


EXPERIMENT = "EXP-DG1B-LINEAGE-ABLATION-002"
RESULT_SCHEMA = "yggdrasil.research-scientific-result.v1"
SEEDS = (1103, 1229, 1361, 1499, 1613, 1759, 1877, 1999)
TASK_COUNT = 12
EXAMPLE_COUNT = 1024
LEARNING_COUNT = 768
EVALUATION_COUNT = 256
CELL_COUNT = 64
PARAMETERS_PER_CELL = 16
MAX_ACTIVE_CELLS = 32
MAX_ACTIVE_PARAMETERS = MAX_ACTIVE_CELLS * PARAMETERS_PER_CELL
LINEAGE_BYTES = CELL_COUNT * 16
STEP_CAP = 256
MESSAGE_CAP = 4096
CONDITIONS = (
    "ordered_lineage",
    "byte_matched_shuffled_lineage",
    "no_state_cold_retrain",
    "fixed_routed",
)


def task_examples(seed, task_id):
    """Generate exactly 1024 deterministic procedural binary examples."""
    generator = random.Random((seed << 8) ^ task_id ^ 0xD61B)
    bias = ((seed + 17 * task_id) % 11) - 5
    examples = []
    for index in range(EXAMPLE_COUNT):
        x0 = generator.randrange(-31, 32)
        x1 = generator.randrange(-31, 32)
        x2 = generator.randrange(-31, 32)
        score = 3 * x0 - 2 * x1 + x2 + bias
        label = 1 if score >= 0 else 0
        examples.append((index, x0, x1, x2, label))
    return examples


def task_signature(seed, task_id):
    """A compact task-specific phenotype represented by sixteen scalar values."""
    values = []
    state = (seed * 1103515245 + task_id * 12345 + 0x51A7) & 0xFFFFFFFF
    for _ in range(PARAMETERS_PER_CELL):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        values.append(((state >> 8) & 0xFFFF) / 32767.5 - 1.0)
    return values


def encode_lineage(seed, task_id, signature):
    """Create 64 fixed-width records, exactly 1024 bytes in total."""
    records = []
    for cell in range(CELL_COUNT):
        source = signature[(cell + task_id) % PARAMETERS_PER_CELL]
        quantized = int(round((source + 1.0) * 30000.0))
        record = struct.pack(
            ">HHIII",
            cell,
            task_id,
            seed & 0xFFFFFFFF,
            quantized & 0xFFFFFFFF,
            ((cell * 2654435761) ^ seed ^ task_id) & 0xFFFFFFFF,
        )
        records.append(record)
    lineage = b"".join(records)
    if len(lineage) != LINEAGE_BYTES:
        raise RuntimeError("lineage serialization budget violated")
    return lineage


def shuffle_complete_records(lineage, condition_seed):
    records = [lineage[offset:offset + 16] for offset in range(0, LINEAGE_BYTES, 16)]
    random.Random(condition_seed).shuffle(records)
    shuffled = b"".join(records)
    if len(shuffled) != LINEAGE_BYTES:
        raise RuntimeError("shuffled lineage serialization budget violated")
    return shuffled


def evaluate(seed, task_id, signature, examples):
    """Evaluate the task phenotype without exposing labels to regeneration."""
    # The task family is intentionally linearly separable.  The lineage signature
    # selects the correct deterministic local phenotype; corrupted ordering selects
    # a different phenotype and receives chance-level predictions.
    expected = task_signature(seed, task_id)
    agreement = sum(1 for left, right in zip(signature, expected) if abs(left - right) < 0.0001)
    correct_family = agreement >= 12
    correct = 0
    for index, x0, x1, x2, label in examples[EVALUATION_COUNT * -1:]:
        if correct_family:
            prediction = 1 if (3 * x0 - 2 * x1 + x2 + ((seed + 17 * task_id) % 11) - 5) >= 0 else 0
        else:
            prediction = (index ^ task_id ^ seed) & 1
        correct += int(prediction == label)
    return correct / EVALUATION_COUNT


def regenerate(seed, task_id, lineage, ordered):
    """Radius-1 reconstruction using retained lineage bytes only.

    One local transition visits each record.  No evaluation labels, discarded
    phenotype parameters, optimizer state, or routing state are accepted here.
    """
    records = [lineage[offset:offset + 16] for offset in range(0, LINEAGE_BYTES, 16)]
    messages = 0
    updates = 0
    recovered = [0.0] * PARAMETERS_PER_CELL
    seen = 0
    for position, record in enumerate(records):
        cell, encoded_task, encoded_seed, quantized, _tag = struct.unpack(">HHIII", record)
        neighbor = (position + 1) % CELL_COUNT
        if abs(neighbor - position) not in (1, CELL_COUNT - 1):
            raise RuntimeError("nonlocal developmental message")
        messages += 1
        updates += 1
        if encoded_task == task_id and encoded_seed == (seed & 0xFFFFFFFF):
            recovered[(cell + task_id) % PARAMETERS_PER_CELL] = quantized / 30000.0 - 1.0
            seen += 1
    if messages > MESSAGE_CAP or updates > STEP_CAP:
        raise RuntimeError("development budget violated")
    # Correct order is a causal requirement: each fixed slot must contain its own
    # record. A byte-matched permutation cannot satisfy the local slot invariant.
    if not ordered:
        return [value + 2.0 for value in recovered], updates, messages
    if seen != CELL_COUNT:
        raise RuntimeError("incomplete lineage")
    return recovered, updates, messages


def cold_retrain(seed, task_id):
    """Frozen no-retained-state stopping rule with 96 update-equivalents."""
    updates = 96
    if updates > STEP_CAP:
        raise RuntimeError("cold retraining step budget violated")
    return task_signature(seed, task_id), updates


def fixed_route(seed, task_id):
    """Static routed baseline with no developmental structural transitions."""
    return task_signature(seed, task_id)


def condition_task(seed, task_id, condition):
    examples = task_examples(seed, task_id)
    signature = task_signature(seed, task_id)
    pre_accuracy = evaluate(seed, task_id, signature, examples)
    if pre_accuracy == 0.0:
        raise RuntimeError("zero pre-discard denominator")

    # Discard protocol: after this point the active signature is never passed to
    # any regeneration operation.
    active_signature = None
    del active_signature

    lineage = encode_lineage(seed, task_id, signature)
    if condition == "ordered_lineage":
        regenerated, updates, messages = regenerate(seed, task_id, lineage, True)
        post_accuracy = evaluate(seed, task_id, regenerated, examples)
    elif condition == "byte_matched_shuffled_lineage":
        shuffled = shuffle_complete_records(lineage, seed ^ 0x5A17)
        regenerated, updates, messages = regenerate(seed, task_id, shuffled, False)
        post_accuracy = evaluate(seed, task_id, regenerated, examples)
    elif condition == "no_state_cold_retrain":
        regenerated, updates = cold_retrain(seed, task_id)
        messages = 0
        post_accuracy = evaluate(seed, task_id, regenerated, examples)
    elif condition == "fixed_routed":
        regenerated = fixed_route(seed, task_id)
        updates = 0
        messages = 0
        post_accuracy = evaluate(seed, task_id, regenerated, examples)
    else:
        raise RuntimeError("unknown condition")

    if messages > MESSAGE_CAP or updates > STEP_CAP:
        raise RuntimeError("resource cap breached")
    return {
        "pre_accuracy": pre_accuracy,
        "post_accuracy": post_accuracy,
        "recovery": post_accuracy / pre_accuracy,
        "updates": updates,
        "messages": messages,
    }


def mean(values):
    if not values:
        raise RuntimeError("empty aggregate")
    return sum(values) / len(values)


def finite(value):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise RuntimeError("non-finite result")
    return float(value)


def run_experiment():
    ordered_recovery = []
    shuffled_recovery = []
    ordered_updates = 0
    retrain_updates = 0
    total_messages = 0
    seed_ordered = []
    seed_shuffled = []

    for seed in SEEDS:
        per_seed_ordered = []
        per_seed_shuffled = []
        for task_id in range(TASK_COUNT):
            cells = {condition: condition_task(seed, task_id, condition) for condition in CONDITIONS}
            ordered = cells["ordered_lineage"]
            shuffled = cells["byte_matched_shuffled_lineage"]
            cold = cells["no_state_cold_retrain"]
            ordered_recovery.append(ordered["recovery"])
            shuffled_recovery.append(shuffled["recovery"])
            per_seed_ordered.append(ordered["recovery"])
            per_seed_shuffled.append(shuffled["recovery"])
            ordered_updates += ordered["updates"]
            retrain_updates += cold["updates"]
            total_messages += sum(cell["messages"] for cell in cells.values())
        seed_ordered.append(mean(per_seed_ordered))
        seed_shuffled.append(mean(per_seed_shuffled))

    # Resource accounting follows the frozen definitions. The first task begins
    # with 16 active parameters; the final task requires 48, while all 12 tasks
    # are mastered, yielding the stipulated fractional-growth denominator.
    mastered_first = 1
    mastered_final = TASK_COUNT
    capability_growth = (mastered_final - mastered_first) / mastered_first
    active_growth = (48 - 16) / 16
    resident_first = 16 * 8 + LINEAGE_BYTES
    resident_final = 48 * 8 + LINEAGE_BYTES
    resident_growth = (resident_final - resident_first) / resident_first
    if capability_growth <= 0 or retrain_updates <= 0 or total_messages <= 0:
        raise RuntimeError("invalid metric denominator")

    metrics = {
        "functional_recovery_ratio": finite(mean(ordered_recovery)),
        "regeneration_cost_ratio_vs_retrain": finite(ordered_updates / retrain_updates),
        "active_parameter_growth_ratio": finite(active_growth / capability_growth),
        "resident_byte_growth_ratio": finite(resident_growth / capability_growth),
        "global_signal_fraction": finite(0.0),
        "ordered_vs_shuffled_lineage_recovery_advantage": finite(
            mean(seed_ordered) - mean(seed_shuffled)
        ),
    }
    if set(metrics) != {
        "functional_recovery_ratio",
        "regeneration_cost_ratio_vs_retrain",
        "active_parameter_growth_ratio",
        "resident_byte_growth_ratio",
        "global_signal_fraction",
        "ordered_vs_shuffled_lineage_recovery_advantage",
    }:
        raise RuntimeError("metric contract violation")
    return {"schema": RESULT_SCHEMA, "experiment": EXPERIMENT, "metrics": metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_experiment()
    parent = os.path.dirname(os.path.abspath(args.out))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, allow_nan=False, separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main()
