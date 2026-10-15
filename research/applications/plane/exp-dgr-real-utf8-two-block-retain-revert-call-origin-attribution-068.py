"""Frozen call-origin attribution for experiment 044's observer."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-ORIGIN-ATTRIBUTION-068"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
PRIOR044_SHA256 = "cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"
PRIOR043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
PRIOR043_SHA256 = "5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRIOR029_SHA256 = "e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"
SEALED067 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-CARDINALITY-ATTRIBUTION-067-38781890868/result.json")
SEALED067_SHA256 = "65ccf387512df01e99b990fc8eddf1150e796db93b9a7cd1b38584785f7a7dce"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"
DIRECT_LINES = frozenset((303, 306, 309, 312, 330, 333, 337, 340))
EXPECTED_SEEN_ROWS = 12


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


def run():
    identities = ((NORTH_STAR, NORTH_STAR_SHA256), (PRIOR044, PRIOR044_SHA256),
                  (PRIOR043, PRIOR043_SHA256), (PRIOR029, PRIOR029_SHA256),
                  (SEALED067, SEALED067_SHA256))
    if any(sha256(path) != expected for path, expected in identities):
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed067 = json.loads(SEALED067.read_text(encoding="utf-8"))
    if sealed067.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-CARDINALITY-ATTRIBUTION-067":
        raise RuntimeError("SEALED_067_EXPERIMENT_MISMATCH")
    prior044 = load(PRIOR044, "prior044_call_origin_068")
    prior043 = load(PRIOR043, "prior043_call_origin_068")
    prior043.ORDERS, prior043.DEMAND_FILES = prior044.ORDERS, prior044.DEMAND_FILES
    origins = []

    def profile(frame, event, _arg):
        if (event == "call" and frame.f_code.co_name == "gated_counts"
                and normalized(frame.f_code.co_filename).endswith(normalized(PRIOR043))):
            caller = frame.f_back
            origins.append((None, None) if caller is None else
                           (normalized(caller.f_code.co_filename), caller.f_lineno))
        return profile

    previous_profile = sys.getprofile()
    sys.setprofile(profile)
    try:
        gated, calls, _blocks = prior043.gated_run()
    finally:
        sys.setprofile(previous_profile)
    direct = sum(path is not None and path.endswith(normalized(PRIOR029)) and line in DIRECT_LINES
                 for path, line in origins)
    unclassified = sum(path is None or line is None for path, line in origins)
    auxiliary = len(origins) - direct - unclassified
    observed = len(calls)
    sealed_total = sealed067["metrics"]["observed_call_count"]
    expected_direct = EXPECTED_SEEN_ROWS * len(DIRECT_LINES)
    old = gated["metrics"]
    control_keys = (
        "training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
        "future_stage_adaptation_access_count", "second_half_adaptation_access_count", "valid_stage_count",
        "valid_seen_domain_evaluation_count", "matched_assignment_failure_count", "capacity_growth_event_count",
        "retained_record_integrity_mismatch_count", "state_partition_mismatch_count",
    )
    metrics = {key: old[key] for key in control_keys}
    metrics.update({
        "observed_call_count": float(observed), "sealed067_observed_call_count": float(sealed_total),
        "direct_staged_call_count": float(direct), "auxiliary_call_count": float(auxiliary),
        "unclassified_call_count": float(unclassified),
        "expected_direct_staged_call_count": float(expected_direct),
        "origin_accounting_mismatch_count": float(direct + auxiliary + unclassified != observed or len(origins) != observed),
        "sealed_total_reproduction_mismatch_count": float(observed != sealed_total),
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
