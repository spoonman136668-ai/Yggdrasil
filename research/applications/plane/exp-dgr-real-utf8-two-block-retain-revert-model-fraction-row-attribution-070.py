"""Frozen row attribution for experiment 069's model_fraction invocations."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-MODEL-FRACTION-ROW-ATTRIBUTION-070"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
PRIOR044_SHA256 = "cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"
PRIOR043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
PRIOR043_SHA256 = "5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRIOR029_SHA256 = "e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"
ERROR_GUIDED = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
ERROR_GUIDED_SHA256 = "5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"
SEALED069 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-AUXILIARY-CALLSITE-ATTRIBUTION-069-38783347305/result.json")
SEALED069_SHA256 = "a5f85d72526e90cef62c43453501f03e023719f4e4b50523dd5311e9a0cf35da"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"
FROZEN_CALLER_LINE = 440


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
    rows = []
    for order_index, order in enumerate(orders):
        for stage_index in range(1, len(order) + 1):
            for name in order[:stage_index]:
                rows.append((order_index, stage_index, name))
    return rows


def row_mask(rows, selected, order_index):
    order_rows = [row for row in rows if row[0] == order_index]
    return sum((1 << bit) for bit, row in enumerate(order_rows) if row in selected)


def run():
    identities = ((NORTH_STAR, NORTH_STAR_SHA256), (PRIOR044, PRIOR044_SHA256),
                  (PRIOR043, PRIOR043_SHA256), (PRIOR029, PRIOR029_SHA256),
                  (ERROR_GUIDED, ERROR_GUIDED_SHA256), (SEALED069, SEALED069_SHA256))
    if any(sha256(path) != expected for path, expected in identities):
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed069 = json.loads(SEALED069.read_text(encoding="utf-8"))
    if sealed069.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-AUXILIARY-CALLSITE-ATTRIBUTION-069":
        raise RuntimeError("SEALED_069_EXPERIMENT_MISMATCH")
    prior044 = load(PRIOR044, "prior044_model_fraction_rows_070")
    prior043 = load(PRIOR043, "prior043_model_fraction_rows_070")
    prior043.ORDERS, prior043.DEMAND_FILES = prior044.ORDERS, prior044.DEMAND_FILES
    orders = tuple(tuple(order) for order in prior044.ORDERS)
    scheduled = schedule(orders)
    observations = []

    def profile(frame, event, _arg):
        if (event == "call" and frame.f_code.co_name == "model_fraction"
                and normalized(frame.f_code.co_filename).endswith(normalized(ERROR_GUIDED))):
            caller = frame.f_back
            if (caller is None or not normalized(caller.f_code.co_filename).endswith(normalized(PRIOR029))
                    or caller.f_lineno != FROZEN_CALLER_LINE):
                observations.append((None, None))
                return profile
            local_order = tuple(caller.f_locals.get("order", ()))
            seen = tuple(caller.f_locals.get("seen", ()))
            name = caller.f_locals.get("name")
            selected_increment = caller.f_locals.get("selected_increment")
            try:
                key = (orders.index(local_order), len(seen), name)
            except ValueError:
                key = None
            observations.append((key, selected_increment))
        return profile

    previous_profile = sys.getprofile()
    sys.setprofile(profile)
    try:
        gated, _calls, _blocks = prior043.gated_run()
    finally:
        sys.setprofile(previous_profile)
    old = gated["metrics"]
    control_keys = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
                    "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
                    "valid_stage_count", "valid_seen_domain_evaluation_count", "matched_assignment_failure_count",
                    "capacity_growth_event_count", "retained_record_integrity_mismatch_count",
                    "state_partition_mismatch_count")
    metrics = {key: old[key] for key in control_keys}
    scheduled_set = set(scheduled)
    invoked_keys = [key for key, _increment in observations if key in scheduled_set]
    counts = Counter(invoked_keys)
    invoked_set = set(invoked_keys)
    uninvoked_set = scheduled_set - invoked_set
    unknown = sum(key not in scheduled_set for key, _increment in observations)
    duplicate = sum(count - 1 for count in counts.values() if count > 1)
    positive = sum(isinstance(increment, (int, float)) and increment > 0
                   for key, increment in observations if key in scheduled_set)
    nonpositive = len(invoked_keys) - positive
    sealed_invocations = sealed069["metrics"]["inferred_model_fraction_invocation_count"]
    metrics.update({
        "scheduled_row_count": float(len(scheduled)),
        "observed_model_fraction_invocation_count": float(len(observations)),
        "unique_invoked_row_count": float(len(invoked_set)),
        "uninvoked_row_count": float(len(uninvoked_set)),
        "positive_selected_increment_invoked_row_count": float(positive),
        "nonpositive_selected_increment_invoked_row_count": float(nonpositive),
        "duplicate_invoked_row_count": float(duplicate),
        "unknown_invoked_row_count": float(unknown),
        "row_accounting_mismatch_count": float(
            len(scheduled) != 12 or len(scheduled_set) != len(scheduled)
            or len(invoked_set) + len(uninvoked_set) != len(scheduled_set)
            or invoked_set & uninvoked_set != set()
            or len(invoked_keys) + unknown != len(observations)),
        "sealed069_invocation_reproduction_mismatch_count": float(len(observations) != sealed_invocations),
        "order0_invoked_row_mask": float(row_mask(scheduled, invoked_set, 0)),
        "order1_invoked_row_mask": float(row_mask(scheduled, invoked_set, 1)),
        "order0_uninvoked_row_mask": float(row_mask(scheduled, uninvoked_set, 0)),
        "order1_uninvoked_row_mask": float(row_mask(scheduled, uninvoked_set, 1)),
        "domain_y_invoked_row_count": float(sum(row[2] == "Y" for row in invoked_set)),
        "domain_z_invoked_row_count": float(sum(row[2] == "Z" for row in invoked_set)),
        "domain_aa_invoked_row_count": float(sum(row[2] == "AA" for row in invoked_set)),
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
