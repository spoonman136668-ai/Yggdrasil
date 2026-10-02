"""Sealed source for EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-004."""
import argparse
import json
import math

EXPERIMENT = "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-004"
SEEDS = (150001, 151007, 152017, 153019, 154021, 155027)
STRUCTURE_COUNT = 16
COLD_REDEVELOPMENT_OPS = 32768


def motif(i):
    return (128+i, 64+((7*i) % 32), 170, 85)


def motif_successor(i):
    return 16 + 13*i


def compound(c):
    return tuple(motif(c) + motif(c+4))


def reference_target(a, b):
    return 224 + ((a % 2) << 1) + (b % 2)


def canonical_state():
    cells = []
    for i in range(8):
        cells.append({
            "index": i,
            "type": 1,
            "key": motif(i),
            "successor": motif_successor(i),
            "active": True,
        })
    for c in range(4):
        cells.append({
            "index": 8+c,
            "type": 2,
            "key": compound(c),
            "active": True,
        })
    for c in range(4):
        cells.append({
            "index": 12+c,
            "type": 3,
            "high": c % 2,
            "low": c % 2,
            "active": True,
        })
    assert len(cells) == STRUCTURE_COUNT
    return cells


def copy_state(cells):
    result = []
    for cell in cells:
        clone = dict(cell)
        if "key" in clone:
            clone["key"] = tuple(clone["key"])
        result.append(clone)
    return result


def cell_signature(cell):
    if cell["type"] == 1:
        return (cell["index"], 1, cell["active"], tuple(cell["key"]), cell["successor"])
    if cell["type"] == 2:
        return (cell["index"], 2, cell["active"], tuple(cell["key"]))
    return (cell["index"], 3, cell["active"], cell["high"], cell["low"])


def state_signature_set(cells):
    return {cell_signature(cell) for cell in cells}


def structure_jaccard(left, right):
    a = state_signature_set(left)
    b = state_signature_set(right)
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def lesion_ids(seed):
    p = (seed // 2) % 4
    return (p, (p+1) % 4)


def serialize_retained(cells, selected_ids):
    records = []
    for c in selected_ids:
        cell = cells[8+c]
        assert cell["type"] == 2 and cell["active"]
        record = bytes([cell["index"], 2] + list(cell["key"]))
        assert len(record) == 10
        records.append(record)
    for c in selected_ids:
        cell = cells[12+c]
        assert cell["type"] == 3 and cell["active"]
        record = bytes([cell["index"], 3, cell["high"], cell["low"]])
        assert len(record) == 4
        records.append(record)
    assert sum(len(record) for record in records) == 28
    return records


def apply_lesion(cells, selected_ids):
    out = copy_state(cells)
    indices = {8+c for c in selected_ids} | {12+c for c in selected_ids}
    for index in indices:
        out[index]["active"] = False
        if out[index]["type"] == 2:
            out[index]["key"] = tuple()
        elif out[index]["type"] == 3:
            out[index]["high"] = -1
            out[index]["low"] = -1
    return out, indices


def repair(cells, records):
    out = copy_state(cells)
    operations = 0
    read_bytes = 0
    invalid = 0
    for record in records:
        read_bytes += len(record)
        if len(record) not in (4, 10):
            invalid += 1
            continue
        receiver = record[0]
        type_byte = record[1]
        if receiver >= STRUCTURE_COUNT:
            invalid += 1
            continue
        if out[receiver]["active"]:
            invalid += 1
            continue
        if type_byte == 2 and len(record) == 10 and 8 <= receiver <= 11:
            out[receiver] = {
                "index": receiver,
                "type": 2,
                "key": tuple(record[2:10]),
                "active": True,
            }
            operations += 1
        elif type_byte == 3 and len(record) == 4 and 12 <= receiver <= 15:
            if record[2] not in (0,1) or record[3] not in (0,1):
                invalid += 1
                continue
            out[receiver] = {
                "index": receiver,
                "type": 3,
                "high": record[2],
                "low": record[3],
                "active": True,
            }
            operations += 1
        else:
            invalid += 1
    return out, operations, read_bytes, invalid


def shuffled_records(records):
    compounds = [bytearray(r) for r in records if len(r) == 10]
    profiles = [bytes(r) for r in records if len(r) == 4]
    assert len(compounds) == 2 and len(profiles) == 2
    payload0 = bytes(compounds[0][2:10])
    payload1 = bytes(compounds[1][2:10])
    compounds[0][2:10] = payload1
    compounds[1][2:10] = payload0
    return [bytes(compounds[0]), bytes(compounds[1]), profiles[0], profiles[1]]


def find_compound_id(cells, raw_key):
    for index in range(8, 12):
        cell = cells[index]
        if cell["active"] and tuple(cell["key"]) == tuple(raw_key):
            return index - 8
    return None


def predict_reference(cells, a_key, b_key):
    a = find_compound_id(cells, a_key)
    b = find_compound_id(cells, b_key)
    if a is None or b is None:
        return 255
    pa = cells[12+a]
    pb = cells[12+b]
    if not pa["active"] or not pb["active"]:
        return 255
    if pa["type"] != 3 or pb["type"] != 3:
        return 255
    return 224 + (pa["high"] << 1) + pb["low"]


def predict_local(cells, key):
    for index in range(8):
        cell = cells[index]
        if cell["active"] and tuple(cell["key"]) == tuple(key):
            return cell["successor"]
    return 255


def filler(seed, record, j):
    state = (seed ^ 0x9E3779B9 ^ (record * 0x45D9F3B)) & 0xFFFFFFFF
    for k in range(j+1):
        state = (1664525 * state + 1013904223 + k) & 0xFFFFFFFF
    return 192 + ((state >> 24) & 63)


def grammar_records(seed):
    rows = []
    record = 0
    for repeat in range(128):
        for a in range(4):
            for b in range(4):
                raw = list(compound(a))
                raw.extend(filler(seed, record, j) for j in range(12))
                raw.extend(compound(b))
                raw.append(reference_target(a,b))
                raw.extend(filler(seed ^ 0xA5A5A5A5, record, j) for j in range(3))
                assert len(raw) == 32
                rows.append((a,b,bytes(raw)))
                record += 1
    assert len(rows) == 2048
    return rows


def local_accuracy(cells):
    correct = 0
    total = 0
    for repeat in range(128):
        for i in range(8):
            key = motif(i)
            correct += int(predict_local(cells, key) == motif_successor(i))
            total += 1
    return correct / total


def long_range_strata(cells, seed, selected_ids):
    affected_correct = 0
    affected_total = 0
    unaffected_correct = 0
    unaffected_total = 0
    all_correct = 0
    all_total = 0
    selected = set(selected_ids)
    for a,b,raw in grammar_records(seed):
        a_key = tuple(raw[0:8])
        b_key = tuple(raw[20:28])
        target = raw[28]
        pred = predict_reference(cells, a_key, b_key)
        ok = int(pred == target)
        all_correct += ok
        all_total += 1
        if a in selected or b in selected:
            affected_correct += ok
            affected_total += 1
        else:
            unaffected_correct += ok
            unaffected_total += 1
    return (
        all_correct / all_total,
        affected_correct / affected_total,
        unaffected_correct / unaffected_total,
    )


def unlesioned_mutations(before, after, lesioned_indices):
    count = 0
    for index in range(STRUCTURE_COUNT):
        if index in lesioned_indices:
            continue
        if cell_signature(before[index]) != cell_signature(after[index]):
            count += 1
    return count


def run():
    metrics = {
        "valid_seed_count": 0.0,
        "minimum_pre_lesion_local_accuracy": 1.0,
        "minimum_pre_lesion_long_range_accuracy": 1.0,
        "minimum_post_lesion_local_accuracy": 1.0,
        "maximum_post_lesion_affected_long_range_accuracy": 0.0,
        "minimum_post_lesion_unaffected_long_range_accuracy": 1.0,
        "minimum_post_regeneration_local_accuracy": 1.0,
        "minimum_post_regeneration_affected_long_range_accuracy": 1.0,
        "minimum_post_regeneration_unaffected_long_range_accuracy": 1.0,
        "minimum_structure_jaccard_pre_vs_regenerated": 1.0,
        "maximum_unlesioned_structure_mutation_count": 0.0,
        "maximum_repair_read_bytes": 0.0,
        "minimum_repair_read_bytes": 28.0,
        "maximum_repair_operations": 0.0,
        "maximum_repair_to_cold_operation_ratio": 0.0,
        "maximum_erased_control_affected_long_range_accuracy": 0.0,
        "maximum_shuffled_control_affected_long_range_accuracy": 0.0,
        "maximum_final_structure_count": 16.0,
        "minimum_final_structure_count": 16.0,
        "capacity_growth_event_count": 0.0,
        "invalid_repair_rows": 0.0,
    }

    for seed in SEEDS:
        base = canonical_state()
        selected = lesion_ids(seed)
        assert selected[0] != selected[1]
        assert (selected[0] % 2) != (selected[1] % 2)

        pre_local = local_accuracy(base)
        pre_all, _, _ = long_range_strata(base, seed, selected)
        metrics["minimum_pre_lesion_local_accuracy"] = min(metrics["minimum_pre_lesion_local_accuracy"], pre_local)
        metrics["minimum_pre_lesion_long_range_accuracy"] = min(metrics["minimum_pre_lesion_long_range_accuracy"], pre_all)

        retained = serialize_retained(base, selected)
        lesioned, lesioned_indices = apply_lesion(base, selected)
        post_local = local_accuracy(lesioned)
        _, post_affected, post_unaffected = long_range_strata(lesioned, seed, selected)
        metrics["minimum_post_lesion_local_accuracy"] = min(metrics["minimum_post_lesion_local_accuracy"], post_local)
        metrics["maximum_post_lesion_affected_long_range_accuracy"] = max(metrics["maximum_post_lesion_affected_long_range_accuracy"], post_affected)
        metrics["minimum_post_lesion_unaffected_long_range_accuracy"] = min(metrics["minimum_post_lesion_unaffected_long_range_accuracy"], post_unaffected)

        repaired, operations, read_bytes, invalid = repair(lesioned, retained)
        metrics["invalid_repair_rows"] += invalid
        repaired_local = local_accuracy(repaired)
        _, repaired_affected, repaired_unaffected = long_range_strata(repaired, seed, selected)
        metrics["minimum_post_regeneration_local_accuracy"] = min(metrics["minimum_post_regeneration_local_accuracy"], repaired_local)
        metrics["minimum_post_regeneration_affected_long_range_accuracy"] = min(metrics["minimum_post_regeneration_affected_long_range_accuracy"], repaired_affected)
        metrics["minimum_post_regeneration_unaffected_long_range_accuracy"] = min(metrics["minimum_post_regeneration_unaffected_long_range_accuracy"], repaired_unaffected)
        metrics["minimum_structure_jaccard_pre_vs_regenerated"] = min(metrics["minimum_structure_jaccard_pre_vs_regenerated"], structure_jaccard(base, repaired))
        metrics["maximum_unlesioned_structure_mutation_count"] = max(metrics["maximum_unlesioned_structure_mutation_count"], unlesioned_mutations(base, repaired, lesioned_indices))
        metrics["maximum_repair_read_bytes"] = max(metrics["maximum_repair_read_bytes"], float(read_bytes))
        metrics["minimum_repair_read_bytes"] = min(metrics["minimum_repair_read_bytes"], float(read_bytes))
        metrics["maximum_repair_operations"] = max(metrics["maximum_repair_operations"], float(operations))
        metrics["maximum_repair_to_cold_operation_ratio"] = max(metrics["maximum_repair_to_cold_operation_ratio"], operations / COLD_REDEVELOPMENT_OPS)

        erased, _, _, erased_invalid = repair(lesioned, [])
        metrics["invalid_repair_rows"] += erased_invalid
        _, erased_affected, _ = long_range_strata(erased, seed, selected)
        metrics["maximum_erased_control_affected_long_range_accuracy"] = max(metrics["maximum_erased_control_affected_long_range_accuracy"], erased_affected)

        shuffled = shuffled_records(retained)
        shuffled_state, _, _, shuffled_invalid = repair(lesioned, shuffled)
        metrics["invalid_repair_rows"] += shuffled_invalid
        _, shuffled_affected, _ = long_range_strata(shuffled_state, seed, selected)
        metrics["maximum_shuffled_control_affected_long_range_accuracy"] = max(metrics["maximum_shuffled_control_affected_long_range_accuracy"], shuffled_affected)

        final_count = sum(1 for cell in repaired if cell["active"])
        metrics["maximum_final_structure_count"] = max(metrics["maximum_final_structure_count"], float(final_count))
        metrics["minimum_final_structure_count"] = min(metrics["minimum_final_structure_count"], float(final_count))
        metrics["valid_seed_count"] += 1.0

    assert all(math.isfinite(v) for v in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle:
        json.dump(run(),handle,allow_nan=False,separators=(",",":"))


if __name__=="__main__":
    main()
