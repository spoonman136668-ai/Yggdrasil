"""CKAD39: bounded DEV-only screen, never original pilots or reserved primary."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("ckad39_development", HERE / "campaign.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

REQUIRED = ("old_source_preserved", "retrieval_pure_read",
            "duplicate_idempotent", "conflict_atomic",
            "consolidated_exact", "cold_exact")


def run():
    cases = [C._dev_or_pilot(seed) for seed in C.DEV]
    results = []
    for case in cases:
        groups = case["metric_groups"]
        pooled = groups["pooled_late_shift_and_return"]
        old = pooled["native_stream"]["brier"]
        proposed = pooled["native_evidence"]["brier"]
        strongest = min(pooled[k]["brier"] for k in
                        (*C.CONVENTIONAL, "beta_hedge"))
        retained = all(all(w[key] is True for key in REQUIRED)
                       for w in case["worlds"])
        threshold = (proposed <= 0.145 and
                     proposed <= old - 0.025 and
                     proposed <= strongest - 0.025 and
                     groups["early_B"]["native_evidence"]["brier"]
                     <= groups["early_B"]["native_stream"]["brier"] and
                     groups["late_return_A"]["native_evidence"]["brier"]
                     <= groups["late_return_A"]["native_stream"]["brier"])
        results.append({
            "seed": case["seed"],
            "native_evidence_brier": proposed,
            "native_stream_brier": old,
            "strongest_fitted_conventional_brier": strongest,
            "delta_vs_native": round(old-proposed, 10),
            "delta_vs_conventional": round(strongest-proposed, 10),
            "source_integrity": retained,
            "threshold_met": threshold,
            "worlds": case["world_count"],
            "episodes": case["total_authentic_episodes"],
        })
    report = {
        "schema": "yggdrasil.ckad39.dev-screen.v1",
        "candidate_source": "CKAD39 development only",
        "source_parent": "0acaf48b6148f3241c3627a7f92c0db45009c543",
        "prereg_commit": C.PREREG,
        "primary_scored": False, "pilot_scored": False,
        "engineering_integrity": all(r["source_integrity"] for r in results),
        "decision": ("DEV_GO" if all(r["source_integrity"] and r["threshold_met"]
                                     for r in results) else "DEV_NO_GO"),
        "scientific_pass": False,
        "results": results,
    }
    print("CKAD39_DEV_REPORT=" + json.dumps(report, sort_keys=True))
    if not report["engineering_integrity"]:
        raise SystemExit("CKAD39_ENGINEERING_INTEGRITY_FAIL")
    return report


if __name__ == "__main__":
    run()
