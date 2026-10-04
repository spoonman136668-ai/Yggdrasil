"""Yggdrasil 076: compatibility diagnostic attribution.

Generated only from a preregistered machine-readable contract. This experiment
does not modify retained state or the operational compatibility gate.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-DIAGNOSTIC-ATTRIBUTION-076"
Y075_PATH = Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.py")
EXPECTED_SOURCE_STATE = {
    "key": (10, 32, 32, 32),
    "best": 32,
    "total": 112,
    "best_count": 112,
    "consistency": 1.0,
    "utility": 112.0,
    "cell_index": 12,
    "map_best": 32,
}
TARGET_SOURCES = {
    "A": {
        "file": "code.bin",
        "sha256": "504b68653b5478b88216f6342a74bacc5982549657005fb486dd00d753b4ea9a",
        "bytes": 41453,
    },
    "B": {
        "file": "structured.bin",
        "sha256": "5c0f3a215ba35b7fbcaae212d27a33ba5109e16d89809987d16fa89072534281",
        "bytes": 14365,
    },
    "C": {
        "file": "technical-prose.bin",
        "sha256": "527e21110a7f84a1939ccf6063fdfeb77905d9ec180e5fde18488d21b90c4f49",
        "bytes": 1454,
    },
}
DIAGNOSTICS = ("LOW_TARGET_SUPPORT", "SUCCESSOR_MISMATCH", "LOW_TARGET_PRECISION")


def load_y075():
    spec = importlib.util.spec_from_file_location("yggdrasil_y075_for_y076", Y075_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y075_IMPORT_SPEC_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def summarize_child(child):
    m = child["metrics"]
    return {
        "original_prose": float(m["original_positive_prose_collateral_schedule_count"]),
        "active_prose": float(m["active_positive_prose_collateral_schedule_count"]),
        "active_partner_fail": float(m["active_partner_collateral_failure_count"]),
        "source_mismatch": float(m["source_identity_mismatch_count"] + m["transfer_manifest_identity_mismatch_count"]),
        "transport_mismatch": float(m["transported_state_identity_mismatch_count"]),
        "capacity_growth": float(m["capacity_growth_event_count"]),
        "invalid": float(m["invalid_evaluation_rows"]),
    }


def fresh_agg():
    return {
        name: {
            "flagged": 0,
            "unflagged": 0,
            "flagged_non_rescue": 0,
            "unflagged_non_rescue": 0,
        }
        for name in DIAGNOSTICS
    }


def add_agg(agg, name, flag, non_rescue):
    bucket = "flagged" if flag else "unflagged"
    agg[name][bucket] += 1
    if non_rescue:
        agg[name][bucket + "_non_rescue"] += 1


def finalize_agg(agg, metrics, total):
    for name in DIAGNOSTICS:
        p = name.lower()
        row = agg[name]
        flagged = row["flagged"]
        unflagged = row["unflagged"]
        fr = (row["flagged_non_rescue"] / flagged) if flagged else 0.0
        ur = (row["unflagged_non_rescue"] / unflagged) if unflagged else 0.0
        metrics[p + "_flagged_count"] = float(flagged)
        metrics[p + "_unflagged_count"] = float(unflagged)
        metrics[p + "_coverage"] = float(flagged) / float(total) if total else 0.0
        metrics[p + "_flagged_non_rescue_rate"] = fr
        metrics[p + "_unflagged_non_rescue_rate"] = ur
        metrics[p + "_non_rescue_rate_delta"] = fr - ur


def run(root):
    y075 = load_y075()
    y075.TARGET_SOURCES = {k: dict(v) for k, v in TARGET_SOURCES.items()}

    metrics = {
        "target_source_identity_mismatch_count": 0.0,
        "target_source_count": 0.0,
        "target_total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "history_byte_budget_mismatch_count": 0.0,
        "donor_row_count": 0.0,
        "induction_source_bytes": 0.0,
        "eligible_candidate_count": 0.0,
        "source_state_identity_mismatch_count": 0.0,
        "source_state_mutation_count": 0.0,
        "heldout_diagnostic_input_count": 0.0,
        "post_result_diagnostic_change_count": 0.0,
        "all_child_source_identity_mismatch_count": 0.0,
        "all_child_transport_identity_mismatch_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "persistent_state_write_count": 0.0,
        "invalid_evaluation_rows": 0.0,
        "clean_rescue_count": 0.0,
        "non_rescue_count": 0.0,
    }

    if y075.SOURCE_STATE != EXPECTED_SOURCE_STATE:
        metrics["source_state_identity_mismatch_count"] += 1.0

    pool = list(y075.build_pool(root, metrics))
    pool.sort(key=lambda s: (tuple(s["key"]), int(s["best"]), int(s["cell_index"])))
    if not pool:
        metrics["invalid_evaluation_rows"] += 1.0
        return {
            "schema": "yggdrasil.research-scientific-result.v1",
            "experiment": EXPERIMENT,
            "metrics": metrics,
            "cases": [],
        }

    max_occ = max(int(s["train_occurrence_count"]) for s in pool)
    if max_occ <= 0:
        metrics["invalid_evaluation_rows"] += 1.0
        max_occ = 1

    # Freeze every diagnostic before any held-out/shadow outcome is opened.
    frozen = []
    for s in pool:
        occ = int(s["train_occurrence_count"])
        argmax_count = int(s["train_argmax_count"])
        support_ratio = float(occ) / float(max_occ)
        precision = float(argmax_count) / float(occ) if occ > 0 else 0.0
        flags = {
            "LOW_TARGET_SUPPORT": support_ratio < 0.25,
            "SUCCESSOR_MISMATCH": int(s["train_argmax"]) != int(s["best"]),
            "LOW_TARGET_PRECISION": precision < 0.90,
        }
        frozen.append({
            "state": dict(s),
            "support_ratio": support_ratio,
            "target_precision": precision,
            "flags": flags,
        })

    agg = fresh_agg()
    cases = []
    for item in frozen:
        child = y075.run_variant(root, item["state"])
        summary = summarize_child(child)
        clean_rescue = (
            summary["active_prose"] > summary["original_prose"]
            and summary["active_partner_fail"] == 0.0
        )
        non_rescue = not clean_rescue
        metrics["clean_rescue_count"] += float(clean_rescue)
        metrics["non_rescue_count"] += float(non_rescue)
        metrics["all_child_source_identity_mismatch_count"] += summary["source_mismatch"]
        metrics["all_child_transport_identity_mismatch_count"] += summary["transport_mismatch"]
        metrics["capacity_growth_event_count"] += summary["capacity_growth"]
        metrics["invalid_evaluation_rows"] += summary["invalid"]
        for name, flag in item["flags"].items():
            add_agg(agg, name, bool(flag), non_rescue)
        cases.append({
            "key": list(item["state"]["key"]),
            "best": int(item["state"]["best"]),
            "cell_index": int(item["state"]["cell_index"]),
            "train_occurrence_count": int(item["state"]["train_occurrence_count"]),
            "train_argmax_count": int(item["state"]["train_argmax_count"]),
            "train_argmax": int(item["state"]["train_argmax"]),
            "support_ratio": item["support_ratio"],
            "target_precision": item["target_precision"],
            "flags": item["flags"],
            "clean_rescue": clean_rescue,
            "original_positive_prose_collateral_schedule_count": summary["original_prose"],
            "active_positive_prose_collateral_schedule_count": summary["active_prose"],
            "active_partner_collateral_failure_count": summary["active_partner_fail"],
        })

    finalize_agg(agg, metrics, len(frozen))

    if metrics["target_source_count"] != 3.0 or metrics["target_total_source_bytes"] != 57272.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["source_state_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["all_child_source_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["all_child_transport_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["capacity_growth_event_count"] != 0.0 or metrics["persistent_state_write_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["heldout_diagnostic_input_count"] != 0.0 or metrics["post_result_diagnostic_change_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if len(cases) != int(metrics["eligible_candidate_count"]):
        metrics["invalid_evaluation_rows"] += 1.0
    if any(not math.isfinite(float(v)) for v in metrics.values()):
        metrics["invalid_evaluation_rows"] += 1.0

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "cases": cases,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = run(args.root)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, allow_nan=False, separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main()
