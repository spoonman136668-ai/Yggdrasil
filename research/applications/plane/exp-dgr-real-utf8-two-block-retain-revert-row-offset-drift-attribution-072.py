"""Read-only attribution of global modulo-ten gate offset drift."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-ROW-OFFSET-DRIFT-ATTRIBUTION-072"
P044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
P043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
P029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRESSURE = Path("research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py")
SEALED = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-SELECTED-INCREMENT-ROW-ATTRIBUTION-071-38784902260/result.json")
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
IDENTITIES = (
    (P044, "cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"),
    (P043, "5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"),
    (P029, "e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"),
    (PRESSURE, "0144922b4191abb451e821f5b4ab14885e1de11272c5d625c3963d1cffdbfeb9"),
    (SEALED, "abbead4be2f58facf7a0ae452a5c59b953076885bfd1867a1ae02c430c9ca1ef"),
    (NORTH_STAR, "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def norm(value):
    return str(value).replace("\\", "/")


def schedule(orders):
    return [(oi, si, name) for oi, order in enumerate(orders)
            for si in range(1, 4) for name in order[:si]]


def run():
    if any(digest(path) != expected for path, expected in IDENTITIES):
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    if sealed.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-SELECTED-INCREMENT-ROW-ATTRIBUTION-071":
        raise RuntimeError("SEALED_EXPERIMENT_MISMATCH")
    p044, p043 = load(P044, "p044_offset_072"), load(P043, "p043_offset_072")
    p043.ORDERS, p043.DEMAND_FILES = p044.ORDERS, p044.DEMAND_FILES
    orders = tuple(tuple(order) for order in p044.ORDERS)
    scheduled = schedule(orders)
    rows, current, call_count = [], None, 0

    def close_row():
        nonlocal current
        if current is not None:
            current["end"] = call_count
            rows.append(current)
            current = None

    def trace(frame, event, _arg):
        nonlocal current, call_count
        filename = norm(frame.f_code.co_filename)
        if event == "call" and frame.f_code.co_name == "gated_counts" and filename.endswith(norm(P043)):
            call_count += 1
        elif event == "line" and filename.endswith(norm(P029)) and frame.f_lineno == 302:
            close_row()
            try:
                key = (orders.index(tuple(frame.f_locals.get("order", ()))),
                       len(tuple(frame.f_locals.get("seen", ()))), frame.f_locals.get("name"))
            except ValueError:
                key = None
            current = {"key": key, "start": call_count, "increment": None}
        elif event == "line" and filename.endswith(norm(P029)) and frame.f_lineno == 439 and current is not None:
            current["increment"] = frame.f_locals.get("selected_increment")
        elif event == "return" and filename.endswith(norm(P029)) and frame.f_code.co_name == "run":
            close_row()
        return trace

    old_trace = sys.gettrace()
    sys.settrace(trace)
    try:
        gated, calls, _blocks = p043.gated_run()
    finally:
        sys.settrace(old_trace)
    old = gated["metrics"]
    control_names = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
                     "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
                     "valid_stage_count", "valid_seen_domain_evaluation_count", "matched_assignment_failure_count",
                     "capacity_growth_event_count", "retained_record_integrity_mismatch_count", "state_partition_mismatch_count")
    metrics = {name: old[name] for name in control_names}
    scheduled_set = set(scheduled)
    known = [row for row in rows if row["key"] in scheduled_set]
    counts = Counter(row["key"] for row in known)
    by_key = {row["key"]: row for row in known}
    sizes = {key: row["end"] - row["start"] for key, row in by_key.items()}
    offsets = {key: row["start"] % 10 for key, row in by_key.items()}
    aligned = {key for key, offset in offsets.items() if offset == 0}
    drifted = set(by_key) - aligned
    zero = {key for key, row in by_key.items() if row["increment"] == 0}
    positive = {key for key, row in by_key.items()
                if isinstance(row["increment"], (int, float)) and row["increment"] > 0}
    sealed_zero = {(1, 1, "AA"), (1, 2, "AA")}
    indices = {key: index for index, key in enumerate(scheduled)}
    pack = lambda values: sum(value << (4 * index) for index, value in enumerate(values))
    metrics.update({
        "observed_call_count": float(call_count), "observed_row_count": float(len(rows)),
        "unique_row_count": float(len(by_key)), "ten_call_row_count": float(sum(size == 10 for size in sizes.values())),
        "eight_call_row_count": float(sum(size == 8 for size in sizes.values())),
        "other_call_cardinality_row_count": float(sum(size not in (8, 10) for size in sizes.values())),
        "aligned_row_start_count": float(len(aligned)), "drifted_row_start_count": float(len(drifted)),
        "logical_hook_aligned_row_count": float(len(aligned)), "logical_hook_misaligned_row_count": float(len(drifted)),
        "unknown_row_count": float(len(rows) - len(known)),
        "duplicate_row_count": float(sum(count - 1 for count in counts.values() if count > 1)),
        "missing_row_count": float(len(scheduled_set - set(by_key))),
        "call_accounting_mismatch_count": float(call_count != len(calls) or sum(sizes.values()) != call_count),
        "sealed071_sign_reproduction_mismatch_count": float(zero != sealed_zero or positive != scheduled_set - sealed_zero),
        "order0_row_start_offset_mask": float(pack([offsets.get(key, 15) for key in scheduled if key[0] == 0])),
        "order1_row_start_offset_mask": float(pack([offsets.get(key, 15) for key in scheduled if key[0] == 1])),
        "aligned_row_mask": float(sum(1 << indices[key] for key in aligned)),
        "drifted_row_mask": float(sum(1 << indices[key] for key in drifted)),
    })
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("NONFINITE_METRIC")
    return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
