"""Read-only CKAD29 independent result accounting. Never reruns consumed B cohort."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREREG = "022d7477de56bb2793b52d2ae3a02e86bbf73bdd"
SOURCE_BLOB = "f32f523766368f1c7ea6cc387c5bb663e6a17282"
ARMS = ("native_composed", "fitted_logistic", "fitted_frequency",
        "exact_bayesian", "no_composition_sham")


def require(ok, why):
    if not ok:
        raise RuntimeError("CKAD29_AUDIT_" + why)


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def audit():
    prereg = json.loads((HERE / "prereg.json").read_text())
    lock = json.loads((HERE / "source_lock.json").read_text())
    scored = json.loads((HERE / "result.json").read_text())
    require(prereg["schema"] == "yggdrasil.external-research-prereg.v1", "SCHEMA")
    require(prereg["experiment_id"] == "CKAD29", "PROTOCOL_ID")
    require(lock["prereg_commit"] == PREREG, "PREREG_ID")
    require(lock["campaign_blob_sha1"] == SOURCE_BLOB, "LOCKED_SOURCE_ID")
    require(git_blob(HERE / "campaign.py") == SOURCE_BLOB, "SOURCE_BLOB_DRIFT")
    require(scored["source_lock"] == lock, "SCORE_LOCK_DRIFT")
    require(scored["schema"] == "yggdrasil.ckad29.composition.v1", "RESULT_SCHEMA")
    require(scored["native_model_mutated"] is False, "UNAUTHORIZED_NATIVE_CHANGE")
    require(scored["protected_first_use"] is False, "UNAUTHORIZED_FIRST_USE")
    cases = scored["cases"]
    require(len(cases) == 3 and [c["seed"] for c in cases] == [404, 505, 606],
            "SEEDS")
    require(scored["training_rows"] == 432 and scored["held_cases"] == 96,
            "BUDGET_ACCOUNTING")
    for c in cases:
        require(c["revealed_source_rows"] == 144 and
                c["held_composite_cases"] == 32, "CASE_BUDGET")
        require(c["cold_restore_exact"] is True and
                c["old_prediction_retention_exact"] is True and
                c["contradiction_quarantine_local"] is True, "CHECKPOINT_OR_NEGATIVE")
        require(0 <= c["native_primitive_held_coverage"] <= 1, "COVERAGE")
        require(set(c["metrics"]) == set(ARMS), "CONTROL_MISSING")
        for arm in ARMS:
            row = c["metrics"][arm]
            require(row["cases"] == 32 and 0 <= row["brier"] <= 1
                    and 0 <= row["accuracy"] <= 1, "METRIC_RANGE")
    means = {arm: sum(c["metrics"][arm]["brier"] for c in cases) / 3
             for arm in ARMS}
    claimed = scored["summary"]
    for arm in ARMS:
        require(abs(means[arm] - claimed["mean_brier_equal_seed"][arm]) < 1e-9,
                "MEAN_" + arm)
    native = means["native_composed"]
    conventional = min(means["fitted_logistic"], means["fitted_frequency"])
    exact = means["exact_bayesian"]
    per_seed = sum(c["metrics"]["native_composed"]["brier"] <
                   min(c["metrics"]["fitted_logistic"]["brier"],
                       c["metrics"]["fitted_frequency"]["brier"])
                   for c in cases)
    require(abs(conventional - claimed["strongest_conventional_brier"]) < 1e-9,
            "BEST_CONVENTIONAL")
    require(abs(exact - claimed["exact_bayes_brier"]) < 1e-9, "EXACT_CONTROL")
    require(per_seed == claimed["per_seed_native_beats_strongest"],
            "PER_SEED_CLASSIFICATION")
    require(abs((native - conventional) -
                claimed["native_minus_strongest_conventional"]) < 1e-9,
            "CONVENTIONAL_DELTA")
    require(abs((native - exact) - claimed["native_minus_exact"]) < 1e-9,
            "EXACT_DELTA")
    keep = all(c["cold_restore_exact"] and c["old_prediction_retention_exact"]
               and c["contradiction_quarantine_local"] for c in cases)
    pass_all = (native <= conventional - .03 and native <= exact + .02 and
                per_seed >= 2 and keep)
    mixed = native <= conventional - .01 and not pass_all
    outcome = ("DEVELOPMENT_GO" if pass_all else
               "DEVELOPMENT_MIXED" if mixed else "DEVELOPMENT_NO_GO")
    require(outcome == claimed["decision"], "FROZEN_CLASSIFICATION")
    require(claimed["scientific_pass"] is False and
            claimed["accepted_native"] is False and
            claimed["deployment"] == "NONE", "SCIENTIFIC_BOUNDARY")
    return {"status": "PASS", "decision": outcome,
            "native_brier": round(native, 10),
            "best_conventional_brier": round(conventional, 10),
            "exact_bayes_brier": round(exact, 10),
            "seeds": len(cases), "source_episodes": scored["training_rows"],
            "held_composite_cases": scored["held_cases"],
            "per_seed_wins": per_seed, "independent_rerun_of_B": False}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
