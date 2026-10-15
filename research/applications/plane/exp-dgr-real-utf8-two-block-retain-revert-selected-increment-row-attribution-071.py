"""Frozen selected_increment row attribution for experiment 070's bypassed rows."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-SELECTED-INCREMENT-ROW-ATTRIBUTION-071"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
PRIOR044_SHA256 = "cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"
PRIOR043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
PRIOR043_SHA256 = "5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRIOR029_SHA256 = "e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"
ERROR_GUIDED = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
ERROR_GUIDED_SHA256 = "5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"
SEALED070 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-MODEL-FRACTION-ROW-ATTRIBUTION-070-38784134132/result.json")
SEALED070_SHA256 = "54c45ab449bbf3f7cf2e7423cfac85310ba9bc390f6d11b8850a936b0d9a1fb6"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"
FROZEN_GUARD_LINE = 439


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized(path):
    return str(path).replace("\\", "/")


def schedule(orders):
    return [(oi, si, name) for oi, order in enumerate(orders)
            for si in range(1, len(order) + 1) for name in order[:si]]


def row_mask(rows, selected, order_index):
    return sum(1 << bit for bit, row in enumerate(r for r in rows if r[0] == order_index)
               if row in selected)


def metric_name(row):
    oi, si, name = row
    return f"order{oi}_stage{si}_{name.lower()}_selected_increment"


def run():
    identities = ((NORTH_STAR, NORTH_STAR_SHA256), (PRIOR044, PRIOR044_SHA256),
                  (PRIOR043, PRIOR043_SHA256), (PRIOR029, PRIOR029_SHA256),
                  (ERROR_GUIDED, ERROR_GUIDED_SHA256), (SEALED070, SEALED070_SHA256))
    if any(sha256(path) != expected for path, expected in identities):
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed070 = json.loads(SEALED070.read_text(encoding="utf-8"))
    if sealed070.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-MODEL-FRACTION-ROW-ATTRIBUTION-070":
        raise RuntimeError("SEALED_070_EXPERIMENT_MISMATCH")
    prior044 = load(PRIOR044, "prior044_selected_increment_rows_071")
    prior043 = load(PRIOR043, "prior043_selected_increment_rows_071")
    prior043.ORDERS, prior043.DEMAND_FILES = prior044.ORDERS, prior044.DEMAND_FILES
    orders = tuple(tuple(order) for order in prior044.ORDERS)
    scheduled = schedule(orders)
    observations = []

    def trace(frame, event, _arg):
        if (event == "line" and frame.f_lineno == FROZEN_GUARD_LINE
                and normalized(frame.f_code.co_filename).endswith(normalized(PRIOR029))):
            try:
                key = (orders.index(tuple(frame.f_locals.get("order", ()))),
                       len(tuple(frame.f_locals.get("seen", ()))), frame.f_locals.get("name"))
            except ValueError:
                key = None
            observations.append((key, frame.f_locals.get("selected_increment")))
        return trace

    previous_trace = sys.gettrace()
    sys.settrace(trace)
    try:
        gated, _calls, _blocks = prior043.gated_run()
    finally:
        sys.settrace(previous_trace)
    old = gated["metrics"]
    control_keys = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
                    "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
                    "valid_stage_count", "valid_seen_domain_evaluation_count", "matched_assignment_failure_count",
                    "capacity_growth_event_count", "retained_record_integrity_mismatch_count",
                    "state_partition_mismatch_count")
    metrics = {key: old[key] for key in control_keys}
    scheduled_set = set(scheduled)
    known = [(key, value) for key, value in observations if key in scheduled_set]
    counts = Counter(key for key, _value in known)
    values = {key: value for key, value in known}
    unknown = sum(key not in scheduled_set for key, _value in observations)
    duplicate = sum(count - 1 for count in counts.values() if count > 1)
    positive = {key for key, value in known if isinstance(value, (int, float)) and value > 0}
    zero = {key for key, value in known if isinstance(value, (int, float)) and value == 0}
    negative = {key for key, value in known if isinstance(value, (int, float)) and value < 0}
    sm = sealed070["metrics"]
    metrics.update({
        "observed_increment_row_count": float(len(observations)),
        "unique_increment_row_count": float(len(values)),
        "positive_increment_row_count": float(len(positive)),
        "zero_increment_row_count": float(len(zero)),
        "negative_increment_row_count": float(len(negative)),
        "duplicate_increment_row_count": float(duplicate),
        "unknown_increment_row_count": float(unknown),
        "missing_increment_row_count": float(len(scheduled_set - set(values))),
        "order0_positive_row_mask": float(row_mask(scheduled, positive, 0)),
        "order1_positive_row_mask": float(row_mask(scheduled, positive, 1)),
        "order0_zero_row_mask": float(row_mask(scheduled, zero, 0)),
        "order1_zero_row_mask": float(row_mask(scheduled, zero, 1)),
        "order0_negative_row_mask": float(row_mask(scheduled, negative, 0)),
        "order1_negative_row_mask": float(row_mask(scheduled, negative, 1)),
        "sign_accounting_mismatch_count": float(
            len(scheduled) != 12 or len(scheduled_set) != len(scheduled)
            or len(known) + unknown != len(observations)
            or len(positive | zero | negative) != len(values)
            or bool(positive & zero or positive & negative or zero & negative)),
        "sealed070_membership_reproduction_mismatch_count": float(
            row_mask(scheduled, positive, 0) != sm["order0_invoked_row_mask"]
            or row_mask(scheduled, positive, 1) != sm["order1_invoked_row_mask"]
            or row_mask(scheduled, zero | negative, 0) != sm["order0_uninvoked_row_mask"]
            or row_mask(scheduled, zero | negative, 1) != sm["order1_uninvoked_row_mask"]),
    })
    for row in scheduled:
        metrics[metric_name(row)] = values.get(row, float("nan"))
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
