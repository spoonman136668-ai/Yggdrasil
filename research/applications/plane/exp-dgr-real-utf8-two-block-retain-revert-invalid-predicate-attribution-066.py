"""Frozen attribution replay for experiment 044's aggregate invalid row."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-066"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
SEALED044 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-GIT-REPLICATION-044-38694585500/result.json")
SEALED044_SHA256 = "5d896e07e9ea1bab17a27a1ea3e822e7b4d8869f2e35ccb23a984442ed078f9f"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_provenance():
    if sha256(NORTH_STAR) != NORTH_STAR_SHA256:
        raise RuntimeError("NORTH_STAR_IDENTITY_MISMATCH")
    if sha256(SEALED044) != SEALED044_SHA256:
        raise RuntimeError("SEALED_044_IDENTITY_MISMATCH")
    blocked = []
    for path in Path(".research-autonomy/evidence").glob("blocked-*.json"):
        record = json.loads(path.read_text(encoding="utf-8-sig"))
        experiment = str(record.get("experiment", ""))
        if (experiment.startswith("EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-")
                and experiment.endswith(tuple(f"-{number:03d}" for number in range(45, 66)))):
            blocked.append(record)
    ids = {record["experiment"] for record in blocked}
    expected = {
        ("EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-ATTRIBUTION-"
         if number < 55 else
         "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-")
        + f"{number:03d}" for number in range(45, 66)
    }
    if ids != expected or any(record.get("scientific_claim") is not False for record in blocked):
        raise RuntimeError("BLOCKED_PREDECESSOR_PROVENANCE_MISMATCH")


def run():
    verify_provenance()
    prior044 = load(PRIOR044, "prior044_predicate_attribution_066")
    prior043 = prior044.load(prior044.PRIOR043, "prior043_predicate_attribution_066")
    prior043.ORDERS, prior043.DEMAND_FILES = prior044.ORDERS, prior044.DEMAND_FILES
    gated, calls, blocks = prior043.gated_run()
    old = gated["metrics"]
    inherited = old["invalid_evaluation_rows"]
    predicates = {
        "experiment_identity_mismatch_event_count": float(gated.get("experiment") != "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-029"),
        "call_count_mismatch_event_count": float(len(calls) != 120),
        "block_count_mismatch_event_count": float(len(blocks) != 12),
        "malformed_block_event_count": float(any(len(block) != 3 for block in blocks)),
        "gate_decision_mismatch_event_count": float(old["gate_decision_mismatch_count"] != 0.0),
    }
    reproduced = inherited + float(any(value != 0.0 for value in predicates.values()))
    sealed_invalid = json.loads(SEALED044.read_text(encoding="utf-8"))["metrics"]["invalid_evaluation_rows"]
    control_keys = (
        "training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
        "future_stage_adaptation_access_count", "second_half_adaptation_access_count", "valid_stage_count",
        "matched_assignment_failure_count", "capacity_growth_event_count",
        "retained_record_integrity_mismatch_count", "state_partition_mismatch_count",
    )
    metrics = {key: old[key] for key in control_keys}
    metrics.update(predicates)
    metrics.update({
        "inherited_core_invalid_event_count": inherited,
        "reproduced_invalid_evaluation_rows": reproduced,
        "predicate_accounting_mismatch_count": float(reproduced != sealed_invalid),
        "nonzero_predicate_count": float((inherited != 0.0) + sum(value != 0.0 for value in predicates.values())),
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
