"""Sealed source for EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001."""
import argparse
import json
import math

EXPERIMENT = "EXP-DGR2-RESOURCE-PRESSURE-GRANULARITY-CONSOLIDATION-001"
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



def specialized_cell_count(phenotype):
    return sum(1 for cell in phenotype["cells"] if cell["role"] == "specialized")


def no_merge_logical_bytes(phenotype):
    return specialized_cell_count(phenotype) * 5


def developmental_merge(phenotype):
    cells = [
        {
            "index": cell["index"],
            "role": cell["role"],
            "key": cell["key"],
            "successor": cell["successor"],
            "home": cell["home"],
        }
        for cell in phenotype["cells"]
    ]
    merge_count = 0
    merge_radius_violation_count = 0
    invalid_merge_rows = 0

    for receiver_index in range(CELL_COUNT):
        receiver = cells[receiver_index]
        if receiver["role"] != "specialized":
            continue

        receiver_key = receiver["key"]
        candidates = []
        for donor_index in range(CELL_COUNT):
            if donor_index == receiver_index:
                continue
            donor = cells[donor_index]
            if donor["role"] != "specialized":
                continue
            distance = ring_distance(receiver_index, donor_index)
            if distance > LOCAL_RADIUS:
                continue
            if receiver_key[2:] != donor["key"][2:]:
                continue
            candidates.append((distance, donor_index))

        if not candidates:
            continue
        candidates.sort()
        distance, donor_index = candidates[0]
        donor = cells[donor_index]
        if distance > LOCAL_RADIUS:
            merge_radius_violation_count += 1
            continue

        variants = [
            (tuple(receiver["key"][:2]), receiver["successor"]),
            (tuple(donor["key"][:2]), donor["successor"]),
        ]
        variants.sort()
        receiver["role"] = "merged"
        receiver["shared_suffix"] = tuple(receiver_key[2:])
        receiver["variants"] = variants
        receiver["key"] = None
        receiver["successor"] = None

        donor["role"] = "generic"
        donor["key"] = None
        donor["successor"] = None
        donor["home"] = None
        merge_count += 1

    active_structures = sum(
        1 for cell in cells if cell["role"] in ("specialized", "merged")
    )
    logical_bytes = 0
    for cell in cells:
        if cell["role"] == "specialized":
            logical_bytes += 5
        elif cell["role"] == "merged":
            if len(cell["variants"]) != 2 or len(cell["shared_suffix"]) != 2:
                invalid_merge_rows += 1
                continue
            logical_bytes += 2 + 3 * len(cell["variants"])

    return {
        "cells": cells,
        "merge_count": merge_count,
        "active_structures": active_structures,
        "logical_bytes": logical_bytes,
        "merge_radius_violation_count": merge_radius_violation_count,
        "capacity_growth_event_count": 0,
        "invalid_merge_rows": invalid_merge_rows,
    }


def predict_merged(merged, key):
    home = home_cell(key)
    matches = []
    for index in local_cells(home):
        cell = merged["cells"][index]
        if cell["role"] == "specialized" and cell["key"] == key:
            matches.append((ring_distance(home, index), index, cell["successor"]))
        elif cell["role"] == "merged":
            if tuple(key[2:]) != tuple(cell["shared_suffix"]):
                continue
            prefix_key = tuple(key[:2])
            for variant_prefix, variant_successor in cell["variants"]:
                if tuple(variant_prefix) == prefix_key:
                    matches.append((ring_distance(home, index), index, variant_successor))
    if not matches:
        return 0
    matches.sort()
    return matches[0][2]


def evaluate_merged(merged, seed):
    stream, target_positions = corpus(seed, EVAL_RECORDS, control=False, evaluation=True)
    correct = 0
    total = 0
    for pos in target_positions:
        key = tuple(stream[pos - 4:pos])
        target = stream[pos]
        correct += int(predict_merged(merged, key) == target)
        total += 1
    return correct / total


def static_chunk_accuracy(seed):
    mapping = {motif(motif_id): successor(motif_id) for motif_id in range(8)}
    stream, target_positions = corpus(seed, EVAL_RECORDS, control=False, evaluation=True)
    correct = 0
    total = 0
    for pos in target_positions:
        key = tuple(stream[pos - 4:pos])
        target = stream[pos]
        correct += int(mapping.get(key, 0) == target)
        total += 1
    return correct / total


def merged_pair_signature(merged):
    signature = set()
    for cell in merged["cells"]:
        if cell["role"] != "merged":
            continue
        ids = []
        suffix = tuple(cell["shared_suffix"])
        for prefix_key, _ in cell["variants"]:
            key = tuple(prefix_key) + suffix
            motif_id = true_motif_id(key)
            if motif_id is None:
                ids = []
                break
            ids.append(motif_id)
        if len(ids) == 2:
            signature.add(tuple(sorted(ids)))
    return signature


def pairset_jaccard(left, right):
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def run():
    assert CELL_COUNT == 16
    assert LOCAL_RADIUS == 2
    assert len(SEEDS) == 6

    metrics = {
        "valid_seed_count": 0.0,
        "minimum_developmental_merge_heldout_accuracy": 1.0,
        "minimum_no_merge_heldout_accuracy": 1.0,
        "minimum_static_chunk_heldout_accuracy": 1.0,
        "maximum_developmental_accuracy_loss_vs_no_merge": 0.0,
        "maximum_developmental_accuracy_gap_vs_static": 0.0,
        "maximum_developmental_active_structure_count": 0.0,
        "minimum_developmental_merge_count": 8.0,
        "maximum_developmental_active_structure_ratio_vs_no_merge": 0.0,
        "maximum_developmental_logical_motif_bytes": 0.0,
        "maximum_developmental_resident_bytes_ratio_vs_no_merge": 0.0,
        "maximum_developmental_over_static_resident_bytes_ratio": 0.0,
        "minimum_pairwise_merge_structure_jaccard": 1.0,
        "maximum_final_physical_cell_count": 16.0,
        "minimum_final_physical_cell_count": 16.0,
        "merge_radius_violation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "invalid_merge_rows": 0.0,
    }
    signatures = []

    for seed in SEEDS:
        train_stream, _ = corpus(seed, TRAIN_RECORDS, control=False, evaluation=False)
        phenotype = develop(train_stream)
        true_ids = specialized_true_motif_ids(phenotype)
        if len(true_ids) != 8:
            metrics["invalid_merge_rows"] += 1.0

        no_merge_accuracy = evaluate(phenotype, seed, ablated=False)
        no_merge_active = specialized_cell_count(phenotype)
        no_merge_bytes = no_merge_logical_bytes(phenotype)

        merged = developmental_merge(phenotype)
        developmental_accuracy = evaluate_merged(merged, seed)
        static_accuracy = static_chunk_accuracy(seed)
        static_bytes = 32.0

        active_ratio = merged["active_structures"] / no_merge_active
        resident_ratio = merged["logical_bytes"] / no_merge_bytes
        over_static_ratio = merged["logical_bytes"] / static_bytes

        metrics["minimum_developmental_merge_heldout_accuracy"] = min(
            metrics["minimum_developmental_merge_heldout_accuracy"],
            developmental_accuracy,
        )
        metrics["minimum_no_merge_heldout_accuracy"] = min(
            metrics["minimum_no_merge_heldout_accuracy"],
            no_merge_accuracy,
        )
        metrics["minimum_static_chunk_heldout_accuracy"] = min(
            metrics["minimum_static_chunk_heldout_accuracy"],
            static_accuracy,
        )
        metrics["maximum_developmental_accuracy_loss_vs_no_merge"] = max(
            metrics["maximum_developmental_accuracy_loss_vs_no_merge"],
            no_merge_accuracy - developmental_accuracy,
        )
        metrics["maximum_developmental_accuracy_gap_vs_static"] = max(
            metrics["maximum_developmental_accuracy_gap_vs_static"],
            abs(static_accuracy - developmental_accuracy),
        )
        metrics["maximum_developmental_active_structure_count"] = max(
            metrics["maximum_developmental_active_structure_count"],
            float(merged["active_structures"]),
        )
        metrics["minimum_developmental_merge_count"] = min(
            metrics["minimum_developmental_merge_count"],
            float(merged["merge_count"]),
        )
        metrics["maximum_developmental_active_structure_ratio_vs_no_merge"] = max(
            metrics["maximum_developmental_active_structure_ratio_vs_no_merge"],
            active_ratio,
        )
        metrics["maximum_developmental_logical_motif_bytes"] = max(
            metrics["maximum_developmental_logical_motif_bytes"],
            float(merged["logical_bytes"]),
        )
        metrics["maximum_developmental_resident_bytes_ratio_vs_no_merge"] = max(
            metrics["maximum_developmental_resident_bytes_ratio_vs_no_merge"],
            resident_ratio,
        )
        metrics["maximum_developmental_over_static_resident_bytes_ratio"] = max(
            metrics["maximum_developmental_over_static_resident_bytes_ratio"],
            over_static_ratio,
        )
        metrics["maximum_final_physical_cell_count"] = max(
            metrics["maximum_final_physical_cell_count"],
            float(len(merged["cells"])),
        )
        metrics["minimum_final_physical_cell_count"] = min(
            metrics["minimum_final_physical_cell_count"],
            float(len(merged["cells"])),
        )
        metrics["merge_radius_violation_count"] += float(
            merged["merge_radius_violation_count"]
        )
        metrics["capacity_growth_event_count"] += float(
            merged["capacity_growth_event_count"]
        )
        metrics["invalid_merge_rows"] += float(merged["invalid_merge_rows"])
        signatures.append(merged_pair_signature(merged))
        metrics["valid_seed_count"] += 1.0

    for left_index in range(len(signatures)):
        for right_index in range(left_index + 1, len(signatures)):
            metrics["minimum_pairwise_merge_structure_jaccard"] = min(
                metrics["minimum_pairwise_merge_structure_jaccard"],
                pairset_jaccard(signatures[left_index], signatures[right_index]),
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
