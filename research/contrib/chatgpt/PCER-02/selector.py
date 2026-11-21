"""PCER-02: FIT-only outcome-stratified read-only replay selector.

No native learner training, protected-world action, checkpoint mutation or
held-out scoring. Every returned ID references immutable original evidence.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

FIT = 50
CAP = 10
TRACE = 96
SCALE = 1_000_000
MAX_ALLOCATIONS = 10_000_000
PREFIX = "PCER-01|24011|"


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def digest(raw):
    return sha256(raw).hexdigest()


def validate_fit(rows):
    if type(rows) is not list or len(rows) != FIT:
        raise ValueError("PCER02_FIT_LENGTH")
    ids = set()
    for i, row in enumerate(rows):
        if type(row) is not dict or set(row) != {
                "id", "phase", "origin", "views", "row", "prediction"}:
            raise ValueError("PCER02_ROW_SHAPE")
        ident = row["id"]
        if (type(ident) is not str or len(ident) != 64 or
                any(ch not in "0123456789abcdef" for ch in ident) or ident in ids):
            raise ValueError("PCER02_IDENTITY")
        ids.add(ident)
        if type(row["phase"]) is not int or row["phase"] != i // 32:
            raise ValueError("PCER02_PHASE")
        views = row["views"]
        if (type(views) is not list or len(views) != 2 or
                any(type(view) is not list or len(view) != 2 for view in views)):
            raise ValueError("PCER02_VIEWS")
        if type(views[0][0]) is not int or views[0][0] not in (0, 1):
            raise ValueError("PCER02_CONTEXT")
        if views[1][0] != views[0][0]:
            raise ValueError("PCER02_PAIRED_CONTEXT")
        outcome = row["row"]
        if type(outcome) is not dict or set(outcome) != {
                "s1", "x1", "s2", "x2", "y"}:
            raise ValueError("PCER02_OUTCOME_SHAPE")
        if any(type(outcome[k]) is not int or outcome[k] not in (0, 1)
               for k in ("s1", "x1", "s2", "x2", "y")):
            raise ValueError("PCER02_BIT")
        if views[0][0] != outcome["s1"]:
            raise ValueError("PCER02_MISMATCH")
        pred = row["prediction"]
        if (type(pred) is not dict or type(pred.get("native")) is not int or
                not 0 <= pred["native"] <= SCALE):
            raise ValueError("PCER02_PREQUENTIAL")
    return True


def cell(row):
    return row["views"][0][0], row["row"]["x1"]


def outcome(row):
    return row["row"]["s2"]


def residual(row):
    return (row["prediction"]["native"] - SCALE * outcome(row)) ** 2


def estimate(rows):
    counts = defaultdict(lambda: [0, 0])
    for row in rows:
        counts[cell(row)][0] += outcome(row)
        counts[cell(row)][1] += 1
    return {k: (positive + 1) / (count + 2)
            for k, (positive, count) in counts.items()}


def pick_uniform(rows):
    return {r["id"] for r in sorted(
        rows, key=lambda r: (digest((PREFIX + r["id"]).encode("ascii")),
                             r["id"]))[:CAP]}


def pick_error(rows):
    return {r["id"] for r in sorted(
        rows, key=lambda r: (-residual(r), r["id"]))[:CAP]}


def pick_pcer01(rows):
    selected = {r["id"] for r in sorted(
        rows, key=lambda r: (-residual(r), r["id"]))[:7]}
    frequencies = Counter(cell(r) for r in rows)
    by_id = {r["id"]: r for r in rows}
    for _ in range(2):
        current = {cell(by_id[ident]) for ident in selected}
        candidates = [r for r in rows if r["id"] not in selected]
        chosen = min(candidates, key=lambda r: (
            cell(r) in current, frequencies[cell(r)], r["id"]))
        selected.add(chosen["id"])
    remaining = [r for r in rows if r["id"] not in selected]
    selected.add(min(remaining, key=lambda r: (
        digest((PREFIX + r["id"]).encode("ascii")), r["id"]))["id"])
    return selected


def select(rows):
    """Find the frozen exact-capacity allocation using FIT outcomes only."""
    validate_fit(rows)
    groups = defaultdict(lambda: {0: [], 1: []})
    for row in rows:
        groups[cell(row)][outcome(row)].append(row)
    cells = sorted(groups)
    if len(cells) != 4:
        raise ValueError("PCER02_FOUR_PUBLIC_CELLS_REQUIRED")
    full = estimate(rows)
    options = []
    for key in cells:
        by_outcome = groups[key]
        for target in (0, 1):
            by_outcome[target].sort(key=lambda r: (-residual(r), r["id"]))
        row_count = sum(len(v) for v in by_outcome.values())
        choices = []
        for positives in range(min(len(by_outcome[1]), CAP) + 1):
            for negatives in range(min(len(by_outcome[0]), CAP - positives) + 1):
                n = positives + negatives
                if not 1 <= n <= CAP:
                    continue
                witnesses = by_outcome[1][:positives] + by_outcome[0][:negatives]
                gap = abs((positives + 1) / (n + 2) - full[key])
                choices.append((n, gap, row_count * gap * gap,
                                sum(residual(w) for w in witnesses),
                                tuple(w["id"] for w in witnesses)))
        options.append(choices)
    best_key = None
    best_ids = None
    explored = 0

    def enumerate_choices(depth, remaining, selected, max_gap, weighted, surprise):
        nonlocal best_key, best_ids, explored
        if depth == len(cells):
            if remaining:
                return
            explored += 1
            if explored > MAX_ALLOCATIONS:
                raise ValueError("PCER02_ALLOCATIONS_OVER_BUDGET")
            ids = tuple(sorted(selected))
            key = (max_gap, weighted, -surprise, ids)
            if best_key is None or key < best_key:
                best_key, best_ids = key, set(ids)
            return
        for n, gap, weighted_gap, residual_sum, identifiers in options[depth]:
            if n > remaining - (len(cells) - depth - 1):
                continue
            enumerate_choices(depth + 1, remaining - n,
                              selected + identifiers, max(max_gap, gap),
                              weighted + weighted_gap, surprise + residual_sum)

    enumerate_choices(0, CAP, (), 0.0, 0.0, 0)
    if best_ids is None or len(best_ids) != CAP:
        raise ValueError("PCER02_ALLOCATION_UNAVAILABLE")
    chosen = [r for r in rows if r["id"] in best_ids]
    if len(chosen) != CAP or set(cell(r) for r in chosen) != set(cells):
        raise ValueError("PCER02_SELECTION_ID_OR_COVERAGE")
    chosen_model = estimate(chosen)
    gap = {str(k): abs(chosen_model[k] - full[k]) for k in cells}
    return {
        "selected": [r["id"] for r in chosen],
        "selected_count": CAP,
        "full_count": FIT,
        "active_reference_reduction": 0.8,
        "full_fit_posterior": {str(k): full[k] for k in cells},
        "selected_fit_posterior": {str(k): chosen_model[k] for k in cells},
        "fit_absolute_gaps": gap,
        "fit_max_gap": max(gap.values()),
        "fit_engineering_gate_met": max(gap.values()) <= 0.1 + 1e-12,
        "allocation_candidates_evaluated": explored,
        "controls": {
            "uniform10": sorted(pick_uniform(rows)),
            "pureerror10": sorted(pick_error(rows)),
            "frozen_pcer01_10": sorted(pick_pcer01(rows)),
            "full50": [r["id"] for r in rows],
            "exact_sufficient_statistics": {
                str(k): [sum(outcome(r) for r in rows if cell(r) == k),
                         sum(cell(r) == k for r in rows)] for k in cells},
        },
        "scientific_native_gain": "UNVERIFIED",
        "held_scoring": "NOT_RUN",
        "native_checkpoint_modified": False,
    }


def cold_verify(fit, manifest):
    if select(fit) != manifest:
        raise ValueError("PCER02_COLD_INDEX_DIVERGENCE")
    return True


def run(source, prereg, index):
    if Path(index).exists():
        raise ValueError("PCER02_OUTPUT_EXISTS")
    protocol_raw = Path(prereg).read_bytes()
    protocol = json.loads(protocol_raw)
    if protocol.get("experiment_id") != "PCER-02":
        raise ValueError("PCER02_PROTOCOL")
    raw = Path(source).read_bytes()
    actual = digest(raw)
    if actual != protocol["source"]["sha256"]:
        raise ValueError("PCER02_SOURCE_SHA")
    data = json.loads(raw)
    if type(data) is not list or len(data) != TRACE:
        raise ValueError("PCER02_SOURCE_LENGTH")
    # Only FIT values pass to the selector; excluded 50:96 never do.
    fit = data[:FIT]
    result = select(fit)
    cold_verify(fit, result)
    if digest(Path(source).read_bytes()) != actual:
        raise ValueError("PCER02_ORIGINAL_MODIFIED")
    receipt = {
        "schema": "yggdrasil.pcer02.fit-only-readonly.v1",
        "experiment_id": "PCER-02", "source_sha256": actual,
        "prereg_sha256": digest(protocol_raw), "frozen_parent": protocol["exact_parent_sha"],
        "fit_result": result,
        "classification": "FIT_ENGINEERING_FEASIBILITY" if result["fit_engineering_gate_met"]
                          else "FIT_ENGINEERING_NO_GO",
        "fresh_science": "NOT_RUN", "deployment": "NONE",
        "original_source_evidence_mutated": False,
    }
    Path(index).write_bytes(canonical(receipt))
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--prereg", type=Path, required=True)
    p.add_argument("--index", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.source, a.prereg, a.index), indent=2, sort_keys=True))
