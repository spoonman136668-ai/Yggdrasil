"""Sealed source for EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001."""
import argparse
import json
import math

EXPERIMENT = "EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001"
SEEDS = (130003, 131009, 132017, 133027, 134033, 135043)
CELL_COUNT = 16
LOCAL_RADIUS = 2
TRAIN_RECORDS = 4096
EVAL_RECORDS = 2048
MASK64 = (1 << 64) - 1


def splitmix64(seed, counter):
    x = (seed + 0x9E3779B97F4A7C15 * (counter + 1)) & MASK64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK64
    return x ^ (x >> 31)


def motif(motif_id):
    return (
        128 + motif_id,
        64 + ((7 * motif_id) % 32),
        170,
        85,
    )


def successor(motif_id):
    return 16 + 13 * motif_id


def home_cell(key):
    b0, b1, b2, b3 = key
    return (3 * b0 + 5 * b1 + 7 * b2 + 11 * b3) % CELL_COUNT


def filler_byte(seed, record, filler_index, evaluation):
    offset = 1_000_000 if evaluation else 0
    value = splitmix64(seed ^ 0xA5A5A5A5A5A5A5A5, offset + record * 3 + filler_index)
    return 192 + (value % 64)


def corpus(seed, records, control=False, evaluation=False):
    stream = []
    target_positions = []
    seed_offset = seed % 8
    for record in range(records):
        motif_id = (5 * record + seed_offset) % 8
        key = motif(motif_id)
        stream.extend(key)
        target_positions.append(len(stream))
        if control:
            block_phase = (record // 8) % 7
            control_id = (motif_id + 1 + block_phase) % 8
            stream.append(successor(control_id))
        else:
            stream.append(successor(motif_id))
        for filler_index in range(3):
            stream.append(filler_byte(seed, record, filler_index, evaluation))
    return stream, target_positions


def ring_distance(a, b):
    delta = abs(a - b)
    return min(delta, CELL_COUNT - delta)


def local_cells(home):
    candidates = []
    for index in range(CELL_COUNT):
        distance = ring_distance(home, index)
        if distance <= LOCAL_RADIUS:
            candidates.append((distance, index))
    return [index for _, index in sorted(candidates)]


def best_successor(stats):
    best_byte = None
    best_count = -1
    for byte_value, count in stats["successors"].items():
        if count > best_count or (count == best_count and (best_byte is None or byte_value < best_byte)):
            best_byte = byte_value
            best_count = count
    return best_byte, best_count


def develop(stream):
    cells = [
        {
            "index": index,
            "role": "generic",
            "key": None,
            "successor": None,
            "home": None,
        }
        for index in range(CELL_COUNT)
    ]
    candidate_tables = [dict() for _ in range(CELL_COUNT)]
    assigned_keys = set()
    local_assignment_radius_violation_count = 0
    capacity_growth_event_count = 0
    invalid_candidate_rows = 0
    counter_overflow_rows = 0

    for start in range(0, len(stream) - 4):
        key = tuple(stream[start:start + 4])
        next_byte = stream[start + 4]
        if len(key) != 4 or any((value < 0 or value > 255) for value in key) or not (0 <= next_byte <= 255):
            invalid_candidate_rows += 1
            continue

        home = home_cell(key)
        table = candidate_tables[home]
        stats = table.get(key)
        if stats is None:
            stats = {"total": 0, "successors": {}}
            table[key] = stats
        stats["total"] += 1
        stats["successors"][next_byte] = stats["successors"].get(next_byte, 0) + 1

        if key in assigned_keys or stats["total"] < 64:
            continue
        learned_successor, best_count = best_successor(stats)
        consistency = best_count / stats["total"]
        if consistency < 0.90:
            continue

        target_cell = None
        for index in local_cells(home):
            if cells[index]["role"] == "generic":
                target_cell = index
                break
        if target_cell is None:
            continue
        if ring_distance(home, target_cell) > LOCAL_RADIUS:
            local_assignment_radius_violation_count += 1
            continue

        cells[target_cell]["role"] = "specialized"
        cells[target_cell]["key"] = key
        cells[target_cell]["successor"] = learned_successor
        cells[target_cell]["home"] = home
        assigned_keys.add(key)

    return {
        "cells": cells,
        "candidate_tables": candidate_tables,
        "local_assignment_radius_violation_count": local_assignment_radius_violation_count,
        "capacity_growth_event_count": capacity_growth_event_count,
        "invalid_candidate_rows": invalid_candidate_rows,
        "counter_overflow_rows": counter_overflow_rows,
    }


def true_motif_id(key):
    for motif_id in range(8):
        if key == motif(motif_id):
            return motif_id
    return None


def specialized_true_motif_ids(phenotype):
    result = set()
    for cell in phenotype["cells"]:
        if cell["role"] != "specialized":
            continue
        motif_id = true_motif_id(cell["key"])
        if motif_id is not None:
            result.add(motif_id)
    return result


def false_specialization_count(phenotype):
    count = 0
    for cell in phenotype["cells"]:
        if cell["role"] != "specialized":
            continue
        if true_motif_id(cell["key"]) is None:
            count += 1
    return count


def predict(phenotype, key, ablated=False):
    if ablated:
        return 0
    home = home_cell(key)
    matches = []
    for index in local_cells(home):
        cell = phenotype["cells"][index]
        if cell["role"] == "specialized" and cell["key"] == key:
            matches.append((ring_distance(home, index), index, cell["successor"]))
    if not matches:
        return 0
    matches.sort()
    return matches[0][2]


def evaluate(phenotype, seed, ablated=False):
    stream, target_positions = corpus(seed, EVAL_RECORDS, control=False, evaluation=True)
    correct = 0
    total = 0
    for pos in target_positions:
        key = tuple(stream[pos - 4:pos])
        target = stream[pos]
        prediction = predict(phenotype, key, ablated=ablated)
        correct += int(prediction == target)
        total += 1
    return correct / total


def jaccard(left, right):
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def run():
    assert CELL_COUNT == 16
    assert LOCAL_RADIUS == 2
    assert len(SEEDS) == 6

    true_specialized_sets = []
    metrics = {
        "valid_seed_count": 0.0,
        "minimum_true_arm_specialized_true_motif_count": 8.0,
        "minimum_true_arm_true_motif_recall": 1.0,
        "maximum_true_arm_false_specialization_count": 0.0,
        "minimum_true_arm_heldout_successor_accuracy": 1.0,
        "minimum_true_arm_ablation_accuracy_drop": 1.0,
        "maximum_control_specialized_true_motif_count": 0.0,
        "maximum_control_heldout_successor_accuracy": 0.0,
        "minimum_pairwise_true_arm_specialized_motif_jaccard": 1.0,
        "maximum_final_cell_count": 16.0,
        "minimum_final_cell_count": 16.0,
        "local_assignment_radius_violation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "invalid_candidate_rows": 0.0,
        "counter_overflow_rows": 0.0,
    }

    for seed in SEEDS:
        true_train, _ = corpus(seed, TRAIN_RECORDS, control=False, evaluation=False)
        control_train, _ = corpus(seed, TRAIN_RECORDS, control=True, evaluation=False)
        assert len(true_train) == 32768
        assert len(control_train) == 32768

        true_phenotype = develop(true_train)
        control_phenotype = develop(control_train)

        true_ids = specialized_true_motif_ids(true_phenotype)
        control_ids = specialized_true_motif_ids(control_phenotype)
        true_specialized_sets.append(true_ids)

        true_accuracy = evaluate(true_phenotype, seed, ablated=False)
        ablated_accuracy = evaluate(true_phenotype, seed, ablated=True)
        control_accuracy = evaluate(control_phenotype, seed, ablated=False)
        ablation_drop = true_accuracy - ablated_accuracy

        metrics["minimum_true_arm_specialized_true_motif_count"] = min(
            metrics["minimum_true_arm_specialized_true_motif_count"],
            float(len(true_ids)),
        )
        metrics["minimum_true_arm_true_motif_recall"] = min(
            metrics["minimum_true_arm_true_motif_recall"],
            len(true_ids) / 8.0,
        )
        metrics["maximum_true_arm_false_specialization_count"] = max(
            metrics["maximum_true_arm_false_specialization_count"],
            float(false_specialization_count(true_phenotype)),
        )
        metrics["minimum_true_arm_heldout_successor_accuracy"] = min(
            metrics["minimum_true_arm_heldout_successor_accuracy"],
            true_accuracy,
        )
        metrics["minimum_true_arm_ablation_accuracy_drop"] = min(
            metrics["minimum_true_arm_ablation_accuracy_drop"],
            ablation_drop,
        )
        metrics["maximum_control_specialized_true_motif_count"] = max(
            metrics["maximum_control_specialized_true_motif_count"],
            float(len(control_ids)),
        )
        metrics["maximum_control_heldout_successor_accuracy"] = max(
            metrics["maximum_control_heldout_successor_accuracy"],
            control_accuracy,
        )
        metrics["maximum_final_cell_count"] = max(
            metrics["maximum_final_cell_count"],
            float(len(true_phenotype["cells"])),
            float(len(control_phenotype["cells"])),
        )
        metrics["minimum_final_cell_count"] = min(
            metrics["minimum_final_cell_count"],
            float(len(true_phenotype["cells"])),
            float(len(control_phenotype["cells"])),
        )
        for phenotype in (true_phenotype, control_phenotype):
            metrics["local_assignment_radius_violation_count"] += float(
                phenotype["local_assignment_radius_violation_count"]
            )
            metrics["capacity_growth_event_count"] += float(
                phenotype["capacity_growth_event_count"]
            )
            metrics["invalid_candidate_rows"] += float(
                phenotype["invalid_candidate_rows"]
            )
            metrics["counter_overflow_rows"] += float(
                phenotype["counter_overflow_rows"]
            )

        metrics["valid_seed_count"] += 1.0

    for left_index in range(len(true_specialized_sets)):
        for right_index in range(left_index + 1, len(true_specialized_sets)):
            metrics["minimum_pairwise_true_arm_specialized_motif_jaccard"] = min(
                metrics["minimum_pairwise_true_arm_specialized_motif_jaccard"],
                jaccard(true_specialized_sets[left_index], true_specialized_sets[right_index]),
            )

    assert all(math.isfinite(value) for value in metrics.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
