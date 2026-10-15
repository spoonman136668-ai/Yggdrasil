"""Frozen auxiliary call-site attribution for experiment 044's observer."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

EXPERIMENT = "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-AUXILIARY-CALLSITE-ATTRIBUTION-069"
PRIOR044 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py")
PRIOR044_SHA256 = "cb94042dbd75be2a4220a8ac1ee1008f2608dec3fb615e47d3534657c0518d9f"
PRIOR043 = Path("research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-git-identity-replication-043.py")
PRIOR043_SHA256 = "5ca6ee9378581f2e577ca707e79beccec5f6750ce530b17a160c0e511abe2b6b"
PRIOR029 = Path("research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-029.py")
PRIOR029_SHA256 = "e9d0034be1ebf12bce7f781752a802256fac450fe35c3ad3b89e2f618e925196"
ERROR_GUIDED = Path("research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py")
ERROR_GUIDED_SHA256 = "5f42794cbb81866dbb3540499ca42a1355f8b217164eb3e02b7a0b7d18ee075a"
SEALED068 = Path(".research-autonomy/evidence/EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-ORIGIN-ATTRIBUTION-068-38782544088/result.json")
SEALED068_SHA256 = "8712b9f2ff3bb24d98aed64c58c1679a385c3cd51df824ba1a36ba12b70e772f"
NORTH_STAR = Path("research/architecture/yggdrasil-north-star.ice")
NORTH_STAR_SHA256 = "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c"
DIRECT_LINES = frozenset((303, 306, 309, 312, 330, 333, 337, 340))
FULL_LINE, ACTIVE_LINE = 39, 40


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
                  (ERROR_GUIDED, ERROR_GUIDED_SHA256), (SEALED068, SEALED068_SHA256))
    if any(sha256(path) != expected for path, expected in identities):
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    sealed068 = json.loads(SEALED068.read_text(encoding="utf-8"))
    if sealed068.get("experiment") != "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-ORIGIN-ATTRIBUTION-068":
        raise RuntimeError("SEALED_068_EXPERIMENT_MISMATCH")
    prior044 = load(PRIOR044, "prior044_auxiliary_callsite_069")
    prior043 = load(PRIOR043, "prior043_auxiliary_callsite_069")
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
    auxiliary = [(path, line) for path, line in origins
                 if not (path is not None and path.endswith(normalized(PRIOR029)) and line in DIRECT_LINES)]
    full_calls = sum(path is not None and path.endswith(normalized(ERROR_GUIDED)) and line == FULL_LINE
                     for path, line in auxiliary)
    active_calls = sum(path is not None and path.endswith(normalized(ERROR_GUIDED)) and line == ACTIVE_LINE
                       for path, line in auxiliary)
    other_auxiliary = len(auxiliary) - full_calls - active_calls
    sealed = sealed068["metrics"]
    old = gated["metrics"]
    control_keys = ("training_file_identity_mismatch_count", "evaluation_file_identity_mismatch_count",
                    "future_stage_adaptation_access_count", "second_half_adaptation_access_count",
                    "valid_stage_count", "valid_seen_domain_evaluation_count", "matched_assignment_failure_count",
                    "capacity_growth_event_count", "retained_record_integrity_mismatch_count",
                    "state_partition_mismatch_count")
    metrics = {key: old[key] for key in control_keys}
    metrics.update({
        "observed_call_count": float(len(calls)), "direct_staged_call_count": float(direct),
        "auxiliary_call_count": float(len(auxiliary)), "model_fraction_full_call_count": float(full_calls),
        "model_fraction_active_call_count": float(active_calls), "other_auxiliary_call_count": float(other_auxiliary),
        "inferred_model_fraction_invocation_count": float(min(full_calls, active_calls)),
        "paired_call_count_mismatch": float(full_calls != active_calls),
        "auxiliary_accounting_mismatch_count": float(direct + len(auxiliary) != len(origins) or len(origins) != len(calls)),
        "sealed068_reproduction_mismatch_count": float(
            len(calls) != sealed["observed_call_count"] or direct != sealed["direct_staged_call_count"]
            or len(auxiliary) != sealed["auxiliary_call_count"]),
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
