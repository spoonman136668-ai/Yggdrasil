"""Sealed source for EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001."""
import argparse
import hashlib
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001"
CELL_COUNT = 16
LOCAL_RADIUS = 2
MIN_OCCURRENCE = 12
MIN_CONSISTENCY = 0.60

TRAIN_FILES = (
    ("research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc"),
    ("research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb"),
    ("research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785"),
    ("research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb"),
)
EVAL_FILES = (
    ("research/architecture/functional-regeneration.ice", "21e01507a9d93e4bfb92b2f79109c2cd94bf8216"),
    ("research/architecture/ancestor-inheritance.ice", "0603b3ed2cb8e67f95f8596883594d3deb37aa8f"),
)


def git_blob_sha(data):
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_checked(path, expected_sha):
    data = Path(path).read_bytes()
    return data, git_blob_sha(data) == expected_sha


def ring_distance(a, b):
    delta = abs(a - b)
    return min(delta, CELL_COUNT - delta)


def local_cells(home):
    rows = []
    for index in range(CELL_COUNT):
        distance = ring_distance(home, index)
        if distance <= LOCAL_RADIUS:
            rows.append((distance, index))
    rows.sort()
    return [index for _, index in rows]


def home_cell(key):
    b0, b1, b2, b3 = key
    return (3 * b0 + 5 * b1 + 7 * b2 + 11 * b3) % CELL_COUNT


def baseline_train(files):
    counts = [[0] * 256 for _ in range(256)]
    for data in files:
        for i in range(1, len(data)):
            counts[data[i - 1]][data[i]] += 1
    return counts


def baseline_predict(counts, previous):
    row = counts[previous]
    best = 0
    best_count = row[0]
    for value in range(1, 256):
        count = row[value]
        if count > best_count:
            best = value
            best_count = count
    return best


def candidate_stats(files):
    stats = {}
    overflow = 0
    invalid = 0
    for data in files:
        if len(data) < 5:
            continue
        for start in range(0, len(data) - 4):
            key = tuple(data[start:start + 4])
            target = data[start + 4]
            if len(key) != 4:
                invalid += 1
                continue
            row = stats.get(key)
            if row is None:
                row = {"total": 0, "successors": [0] * 256}
                stats[key] = row
            row["total"] += 1
            row["successors"][target] += 1
    return stats, overflow, invalid


def best_successor(row):
    best = 0
    best_count = row["successors"][0]
    for value in range(1, 256):
        count = row["successors"][value]
        if count > best_count:
            best = value
            best_count = count
    return best, best_count


def develop(stats):
    candidates = []
    for key, row in stats.items():
        if row["total"] < MIN_OCCURRENCE:
            continue
        best, best_count = best_successor(row)
        consistency = best_count / row["total"]
        if consistency < MIN_CONSISTENCY:
            continue
        candidates.append({
            "key": key,
            "total": row["total"],
            "best": best,
            "best_count": best_count,
            "consistency": consistency,
        })
    candidates.sort(key=lambda r: (
        -r["best_count"],
        -r["consistency"],
        -r["total"],
        r["key"],
    ))

    cells = [
        {"index": i, "role": "generic", "key": None, "best": None, "home": None}
        for i in range(CELL_COUNT)
    ]
    assigned = set()
    radius_violations = 0
    for row in candidates:
        if row["key"] in assigned:
            continue
        home = home_cell(row["key"])
        receiver = None
        for index in local_cells(home):
            if cells[index]["role"] == "generic":
                receiver = index
                break
        if receiver is None:
            continue
        if ring_distance(home, receiver) > LOCAL_RADIUS:
            radius_violations += 1
            continue
        cells[receiver] = {
            "index": receiver,
            "role": "specialized",
            "key": row["key"],
            "best": row["best"],
            "home": home,
        }
        assigned.add(row["key"])
        if len(assigned) == CELL_COUNT:
            break
    return cells, radius_violations


def specialized_map(cells):
    return {
        cell["key"]: cell["best"]
        for cell in cells
        if cell["role"] == "specialized"
    }


def evaluate_file(data, baseline, learned):
    if len(data) < 5:
        return {
            "transferred": 0,
            "coverage": 0.0,
            "gain": 0.0,
            "event_reduction": 0.0,
        }
    transferred = set()
    covered = 0
    learned_correct = 0
    baseline_correct = 0
    for i in range(4, len(data)):
        key = tuple(data[i - 4:i])
        if key not in learned:
            continue
        transferred.add(key)
        covered += 1
        target = data[i]
        if learned[key] == target:
            learned_correct += 1
        if baseline_predict(baseline, data[i - 1]) == target:
            baseline_correct += 1
    denom = max(1, len(data) - 4)
    coverage = covered / denom
    gain = 0.0
    if covered:
        gain = (learned_correct - baseline_correct) / covered

    events = 0
    i = 0
    while i < len(data):
        if i + 4 <= len(data) and tuple(data[i:i + 4]) in learned:
            events += 1
            i += 4
        else:
            events += 1
            i += 1
    event_reduction = (len(data) - events) / len(data) if data else 0.0
    return {
        "transferred": len(transferred),
        "coverage": coverage,
        "gain": gain,
        "event_reduction": event_reduction,
    }


def run():
    metrics = {
        "training_file_identity_mismatch_count": 0.0,
        "evaluation_file_identity_mismatch_count": 0.0,
        "train_eval_blob_overlap_count": 0.0,
        "differentiated_cell_count": 0.0,
        "maximum_differentiated_cell_count": 0.0,
        "minimum_transferred_motif_count_per_eval_file": 16.0,
        "minimum_eval_covered_position_fraction": 1.0,
        "minimum_eval_covered_accuracy_gain": 1.0,
        "minimum_effective_event_reduction_fraction": 1.0,
        "maximum_final_cell_count": 16.0,
        "minimum_final_cell_count": 16.0,
        "local_assignment_radius_violation_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "invalid_byte_rows": 0.0,
        "counter_overflow_rows": 0.0,
    }

    train = []
    evals = []
    train_shas = set()
    for path, expected in TRAIN_FILES:
        data, ok = load_checked(path, expected)
        if not ok:
            metrics["training_file_identity_mismatch_count"] += 1.0
        train.append(data)
        train_shas.add(expected)
    for path, expected in EVAL_FILES:
        data, ok = load_checked(path, expected)
        if not ok:
            metrics["evaluation_file_identity_mismatch_count"] += 1.0
        if expected in train_shas:
            metrics["train_eval_blob_overlap_count"] += 1.0
        evals.append(data)

    baseline = baseline_train(train)
    stats, overflow, invalid = candidate_stats(train)
    metrics["counter_overflow_rows"] += float(overflow)
    metrics["invalid_byte_rows"] += float(invalid)
    cells, radius_violations = develop(stats)
    learned = specialized_map(cells)

    metrics["differentiated_cell_count"] = float(len(learned))
    metrics["maximum_differentiated_cell_count"] = float(len(learned))
    metrics["local_assignment_radius_violation_count"] = float(radius_violations)
    metrics["maximum_final_cell_count"] = float(len(cells))
    metrics["minimum_final_cell_count"] = float(len(cells))

    for data in evals:
        row = evaluate_file(data, baseline, learned)
        metrics["minimum_transferred_motif_count_per_eval_file"] = min(
            metrics["minimum_transferred_motif_count_per_eval_file"],
            float(row["transferred"]),
        )
        metrics["minimum_eval_covered_position_fraction"] = min(
            metrics["minimum_eval_covered_position_fraction"],
            row["coverage"],
        )
        metrics["minimum_eval_covered_accuracy_gain"] = min(
            metrics["minimum_eval_covered_accuracy_gain"],
            row["gain"],
        )
        metrics["minimum_effective_event_reduction_fraction"] = min(
            metrics["minimum_effective_event_reduction_fraction"],
            row["event_reduction"],
        )

    if not learned:
        metrics["minimum_transferred_motif_count_per_eval_file"] = 0.0
        metrics["minimum_eval_covered_position_fraction"] = 0.0
        metrics["minimum_eval_covered_accuracy_gain"] = 0.0
        metrics["minimum_effective_event_reduction_fraction"] = 0.0

    assert all(math.isfinite(v) for v in metrics.values())
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
