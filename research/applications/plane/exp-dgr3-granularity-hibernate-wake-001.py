"""Sealed source for EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001."""
import argparse
import json
import math

EXPERIMENT = "EXP-DGR3-GRANULARITY-HIBERNATE-WAKE-001"
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



def hibernate(merged):
    records = []
    for cell in sorted(merged["cells"], key=lambda row: row["index"]):
        if cell["role"] != "merged":
            continue
        variants = list(cell["variants"])
        variants.sort()
        assert len(variants) == 2
        record = [
            cell["index"],
            cell["shared_suffix"][0],
            cell["shared_suffix"][1],
            variants[0][0][0],
            variants[0][0][1],
            variants[0][1],
            variants[1][0][0],
            variants[1][0][1],
            variants[1][1],
        ]
        assert len(record) == 9
        assert all(0 <= value <= 255 for value in record)
        records.extend(record)
    return bytes(records)


def wake(retained, strict=True):
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
    invalid = 0
    operations = 0
    if len(retained) != 36:
        return {"cells": cells}, 0, 1

    used = set()
    for offset in range(0, 36, 9):
        record = list(retained[offset:offset + 9])
        receiver = record[0]
        if receiver >= CELL_COUNT:
            if strict:
                invalid += 1
            continue
        if receiver in used and strict:
            invalid += 1
            continue
        used.add(receiver)
        suffix = (record[1], record[2])
        variants = [
            ((record[3], record[4]), record[5]),
            ((record[6], record[7]), record[8]),
        ]
        variants.sort()
        cells[receiver]["role"] = "merged"
        cells[receiver]["shared_suffix"] = suffix
        cells[receiver]["variants"] = variants
        operations += 1

    return {"cells": cells}, operations, invalid


def active_motif_structure_count(phenotype):
    return sum(
        1
        for cell in phenotype["cells"]
        if cell["role"] in ("specialized", "merged")
    )


def successor_shuffled_retained(retained):
    data = bytearray(retained)
    successor_positions = []
    for offset in range(0, 36, 9):
        successor_positions.extend((offset + 5, offset + 8))
    values = [data[index] for index in successor_positions]
    rotated = values[1:] + values[:1]
    for index, value in zip(successor_positions, rotated):
        data[index] = value
    return bytes(data)


def run():
    assert CELL_COUNT == 16
    assert LOCAL_RADIUS == 2
    assert len(SEEDS) == 6

    metrics = {
        "valid_seed_count": 0.0,
        "minimum_post_wake_accuracy_across_cycles": 1.0,
        "minimum_cold_redevelopment_accuracy": 1.0,
        "maximum_wake_accuracy_gap_vs_cold": 0.0,
        "maximum_hibernated_active_structure_count": 0.0,
        "maximum_retained_wake_bytes": 0.0,
        "minimum_retained_wake_bytes": 36.0,
        "maximum_wake_operations": 0.0,
        "minimum_cold_redevelopment_operations": float("inf"),
        "maximum_wake_to_cold_operation_ratio": 0.0,
        "maximum_erased_wake_control_accuracy": 0.0,
        "maximum_successor_shuffled_wake_control_accuracy": 0.0,
        "minimum_wake_structure_jaccard_vs_prehibernate": 1.0,
        "maximum_final_physical_cell_count": 16.0,
        "minimum_final_physical_cell_count": 16.0,
        "capacity_growth_event_count": 0.0,
        "invalid_wake_rows": 0.0,
    }

    for seed in SEEDS:
        train_stream, _ = corpus(seed, TRAIN_RECORDS, control=False, evaluation=False)
        phenotype = develop(train_stream)
        merged = developmental_merge(phenotype)
        if merged["merge_count"] != 4 or merged["active_structures"] != 4:
            metrics["invalid_wake_rows"] += 1.0

        cold_accuracy = evaluate_merged(merged, seed)
        cold_operations = (len(train_stream) - 4) + merged["merge_count"]
        metrics["minimum_cold_redevelopment_accuracy"] = min(
            metrics["minimum_cold_redevelopment_accuracy"],
            cold_accuracy,
        )
        metrics["minimum_cold_redevelopment_operations"] = min(
            metrics["minimum_cold_redevelopment_operations"],
            float(cold_operations),
        )

        active = merged
        pre_signature = merged_pair_signature(active)
        first_retained = None
        for cycle in range(3):
            retained = hibernate(active)
            if first_retained is None:
                first_retained = retained
            hibernated_active = 0
            metrics["maximum_hibernated_active_structure_count"] = max(
                metrics["maximum_hibernated_active_structure_count"],
                float(hibernated_active),
            )
            metrics["maximum_retained_wake_bytes"] = max(
                metrics["maximum_retained_wake_bytes"],
                float(len(retained)),
            )
            metrics["minimum_retained_wake_bytes"] = min(
                metrics["minimum_retained_wake_bytes"],
                float(len(retained)),
            )

            woken, wake_operations, invalid = wake(retained, strict=True)
            metrics["invalid_wake_rows"] += float(invalid)
            metrics["maximum_wake_operations"] = max(
                metrics["maximum_wake_operations"],
                float(wake_operations),
            )
            ratio = wake_operations / cold_operations
            metrics["maximum_wake_to_cold_operation_ratio"] = max(
                metrics["maximum_wake_to_cold_operation_ratio"],
                ratio,
            )

            wake_accuracy = evaluate_merged(woken, seed)
            metrics["minimum_post_wake_accuracy_across_cycles"] = min(
                metrics["minimum_post_wake_accuracy_across_cycles"],
                wake_accuracy,
            )
            metrics["maximum_wake_accuracy_gap_vs_cold"] = max(
                metrics["maximum_wake_accuracy_gap_vs_cold"],
                abs(cold_accuracy - wake_accuracy),
            )
            wake_signature = merged_pair_signature(woken)
            metrics["minimum_wake_structure_jaccard_vs_prehibernate"] = min(
                metrics["minimum_wake_structure_jaccard_vs_prehibernate"],
                pairset_jaccard(pre_signature, wake_signature),
            )
            metrics["maximum_final_physical_cell_count"] = max(
                metrics["maximum_final_physical_cell_count"],
                float(len(woken["cells"])),
            )
            metrics["minimum_final_physical_cell_count"] = min(
                metrics["minimum_final_physical_cell_count"],
                float(len(woken["cells"])),
            )
            active = woken

        erased = bytes(36)
        erased_wake, _, _ = wake(erased, strict=False)
        erased_accuracy = evaluate_merged(erased_wake, seed)
        metrics["maximum_erased_wake_control_accuracy"] = max(
            metrics["maximum_erased_wake_control_accuracy"],
            erased_accuracy,
        )

        shuffled = successor_shuffled_retained(first_retained)
        shuffled_wake, _, invalid = wake(shuffled, strict=True)
        metrics["invalid_wake_rows"] += float(invalid)
        shuffled_accuracy = evaluate_merged(shuffled_wake, seed)
        metrics["maximum_successor_shuffled_wake_control_accuracy"] = max(
            metrics["maximum_successor_shuffled_wake_control_accuracy"],
            shuffled_accuracy,
        )

        metrics["valid_seed_count"] += 1.0

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
