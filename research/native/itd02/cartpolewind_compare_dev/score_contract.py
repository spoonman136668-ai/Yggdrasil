"""Pure three-arm comparison accounting, not FSA authority or original-world evidence.

Input must be an already-recorded, public-only, untrusted report. This module
NEVER imports the original source, starts an episode, signs or admits a cohort.
"""
import hashlib
import json
import math
import statistics

ARMS = ("native", "tabular", "recurrent")
SCHEMA = "ygg.itd02.cartpolewind.paired_public_accounting.v1"
STAGES = ("FIT", "VALID", "DEV")
MAX_PAIRS = 32


def _hex64(value):
    return (type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value))


def _finite(value):
    return type(value) in (float, int) and math.isfinite(value)


def score_untrusted_public_report(report):
    """Check parity and aggregate reported scores, never grant science admission.

    The unchanged FORCE/FSA owner must separately attest source birth,
    independent writer/witness, disjoint cohorts, budgets and original runs.
    No locally supplied report can satisfy that independent authority.
    """
    if type(report) is not dict or set(report) != {
        "schema", "source_kind", "stage", "fit_source_sha256",
        "fit_updates_per_arm", "paired_trial_budget", "rows",
    } or report["schema"] != SCHEMA:
        raise ValueError("MALFORMED_PUBLIC_ACCOUNTING_ENVELOPE")
    if (report["source_kind"] != "SYNTHETIC_ACCOUNTING_FIXTURES"
            or report["stage"] not in STAGES
            or not _hex64(report["fit_source_sha256"])
            or type(report["paired_trial_budget"]) is not int
            or not 1 <= report["paired_trial_budget"] <= MAX_PAIRS):
        raise ValueError("UNQUALIFIED_ACCOUNTING_SOURCE_OR_BUDGET")
    counts = report["fit_updates_per_arm"]
    if (type(counts) is not dict or set(counts) != set(ARMS)
            or any(type(counts[a]) is not int or
                   not 1 <= counts[a] <= 1000000 for a in ARMS)
            or len(set(counts.values())) != 1):
        raise ValueError("EQUAL_PUBLIC_FIT_RIGHTS_NOT_PROVEN")
    rows = report["rows"]
    budget = report["paired_trial_budget"]
    if type(rows) not in (list, tuple) or len(rows) != budget * len(ARMS):
        raise ValueError("EQUAL_EVALUATION_RIGHTS_NOT_PROVEN")
    required = {
        "arm", "trial_id", "paired_cohort_sha256", "return_total",
        "episode_length", "terminated", "truncated", "action_calls",
        "train_weight_sha256", "eval_weight_sha256", "cpu_ns",
        "peak_rss_bytes", "checkpoint_bytes"
    }
    buckets = {arm: {} for arm in ARMS}
    seen_pair_hash = {}
    frozen_weights = {}
    for row in rows:
        if type(row) is not dict or set(row) != required:
            raise ValueError("PRIVILEGED_OR_MISSING_EVALUATION_FIELD")
        arm = row["arm"]
        trial = row["trial_id"]
        cohort = row["paired_cohort_sha256"]
        if (arm not in ARMS or type(trial) is not str
                or not 1 <= len(trial) <= 60
                or any(x not in "0123456789abcdefghijklmnopqrstuvwxyz-_" for x in trial)
                or not _hex64(cohort)
                or cohort == report["fit_source_sha256"]
                or not _hex64(row["train_weight_sha256"])
                or row["train_weight_sha256"] != row["eval_weight_sha256"]
                or type(row["terminated"]) is not bool
                or type(row["truncated"]) is not bool
                or not (row["terminated"] or row["truncated"])
                or not _finite(row["return_total"])
                or abs(row["return_total"]) > 200000
                or type(row["episode_length"]) is not int
                or not 1 <= row["episode_length"] <= 200
                or type(row["action_calls"]) is not int
                or row["action_calls"] != row["episode_length"]
                or type(row["cpu_ns"]) is not int or row["cpu_ns"] < 0
                or type(row["peak_rss_bytes"]) is not int
                or not 0 < row["peak_rss_bytes"] <= 2**50
                or type(row["checkpoint_bytes"]) is not int
                or not 0 < row["checkpoint_bytes"] <= 262144):
            raise ValueError("INVALID_PUBLIC_EVALUATION_TRIAL")
        if trial in buckets[arm]:
            raise ValueError("DUPLICATE_ARM_TRIAL")
        if trial in seen_pair_hash and seen_pair_hash[trial] != cohort:
            raise ValueError("PAIRED_COHORT_IDENTITY_DRIFT")
        seen_pair_hash[trial] = cohort
        if arm in frozen_weights and frozen_weights[arm] != row["train_weight_sha256"]:
            raise ValueError("MODEL_WAS_CHANGED_BETWEEN_EVALUATION_TRIALS")
        frozen_weights[arm] = row["train_weight_sha256"]
        buckets[arm][trial] = row
    if len(seen_pair_hash) != budget or len(set(seen_pair_hash.values())) != budget:
        raise ValueError("COHORT_REUSE_OR_PAIR_MISMATCH")
    pairs = set(seen_pair_hash)
    if any(set(buckets[arm]) != pairs for arm in ARMS):
        raise ValueError("MISSING_MATCHED_ARM_TRIAL")
    per_arm = {}
    for arm in ARMS:
        trials = list(buckets[arm].values())
        per_arm[arm] = {
            "fit_updates_reported": counts[arm],
            "paired_trials_reported": len(trials),
            "mean_return_reported": statistics.fmean(t["return_total"] for t in trials),
            "mean_episode_length_reported": statistics.fmean(
                t["episode_length"] for t in trials),
            "action_calls_reported": sum(t["action_calls"] for t in trials),
            "total_cpu_ns_reported": sum(t["cpu_ns"] for t in trials),
            "max_peak_rss_bytes_reported": max(t["peak_rss_bytes"] for t in trials),
            "max_checkpoint_bytes_reported": max(t["checkpoint_bytes"] for t in trials),
            "train_weight_sha256_reported": frozen_weights[arm]
        }
    differences = {}
    for other in ("tabular", "recurrent"):
        diffs = [buckets["native"][trial]["return_total"] -
                 buckets[other][trial]["return_total"] for trial in sorted(pairs)]
        differences["native_minus_" + other] = statistics.fmean(diffs)
    # Fingerprint verifies only exact locally given bytes, NOT original
    # source integrity, signer provenance, FSA state or external authenticity.
    payload = json.dumps(report, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return {
        "schema": SCHEMA,
        "source_kind": "SYNTHETIC_ACCOUNTING_FIXTURES",
        "report_sha256": hashlib.sha256(payload).hexdigest(),
        "paired_trial_budget": budget,
        "per_arm": per_arm,
        "mean_paired_return_differences_reported": differences,
        "original_source_episodes_authenticated": 0,
        "real_fsa_signed_witness_verified": False,
        "scientific_go": False,
        "assertion": "ACCOUNTING_LOGIC_ONLY_NOT_PERFORMANCE_OR_CAUSAL_EVIDENCE",
    }
