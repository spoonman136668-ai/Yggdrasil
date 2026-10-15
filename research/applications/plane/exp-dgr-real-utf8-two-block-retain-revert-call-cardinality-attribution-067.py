"""Frozen call-cardinality attribution for experiment 044's observer."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-CARDINALITY-ATTRIBUTION-067"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
SEALED066 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-066-38781285787/result.json")
SEALED066_SHA256 = "106d3c01db06c3c2f315030b7fede72c0fa0ef7a8ece38ffa9c73b75250db556"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"
EXPECTED_CALL_COUNT = 120


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    if sha256(NORTH_STAR) != NORTH_STAR_SHA256:
        raise RuntimeError("NORTH_STAR_IDENTITY_MISMATCH")
    if sha256(SEALED066) != SEALED066_SHA256:
        raise RuntimeError("SEALED_066_IDENTITY_MISMATCH")
    sealed066 = json.loads(SEALED066.read_text(encoding="utf-8"))
    if sealed066.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-066":
        raise RuntimeError("SEALED_066_EXPERIMENT_MISMATCH")
    prior044 = load(PRIOR044, "prior044_call_cardinality_067")
    prior043 = prior044.load(prior044.PRIOR043, "prior043_call_cardinality_067")
    prior043.ORDERS, prior043.DEMAND_FILES = prior044.ORDERS, prior044.DEMAND_FILES
    gated, calls, _blocks = prior043.gated_run()
    old = gated["metrics"]
    observed = len(calls)
    signed = observed - EXPECTED_CALL_COUNT
    mismatch = float(observed != EXPECTED_CALL_COUNT)
    prior_mismatch = sealed066["metrics"]["call_count_mismatch_event_count"]
    control_keys = (
        "training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
        "future_stage_adaptation_access_count", "second_half_adaptation_access_count", "valid_stage_count",
        "matched_assignment_failure_count", "capacity_growth_event_count",
        "retained_record_integrity_mismatch_count", "state_partition_mismatch_count",
    )
    metrics = {key: old[key] for key in control_keys}
    metrics.update({
        "observed_call_count": float(observed), "expected_call_count": float(EXPECTED_CALL_COUNT),
        "signed_call_count_difference": float(signed), "absolute_call_count_difference": float(abs(signed)),
        "call_count_mismatch_event_count": mismatch,
        "prior066_call_count_mismatch_event_count": float(prior_mismatch),
        "predicate_reproduction_mismatch_count": float(mismatch != prior_mismatch),
    })
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("NONFINITE_METRIC")
    if observed < 0 or int(observed) != observed or abs(signed) != abs(observed - EXPECTED_CALL_COUNT):
        raise RuntimeError("CALL_CARDINALITY_ACCOUNTING_MISMATCH")
    return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
