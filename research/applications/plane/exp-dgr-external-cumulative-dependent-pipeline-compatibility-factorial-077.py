"""Yggdrasil 077: compatibility key x payload factorial.

Generated only from a preregistered machine-readable contract. All four cells
are shadow evaluations. Accepted retained state and operational gates remain
immutable.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-FACTORIAL-077"
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
    "A": {"file": "code.bin", "sha256": "504b68653b5478b88216f6342a74bacc5982549657005fb486dd00d753b4ea9a", "bytes": 41453},
    "B": {"file": "structured.bin", "sha256": "5c0f3a215ba35b7fbcaae212d27a33ba5109e16d89809987d16fa89072534281", "bytes": 14365},
    "C": {"file": "technical-prose.bin", "sha256": "527e21110a7f84a1939ccf6063fdfeb77905d9ec180e5fde18488d21b90c4f49", "bytes": 1454},
}
PAYLOAD_FIELDS = ("best", "total", "best_count", "consistency", "utility", "cell_index", "map_best")


def load_y075():
    spec = importlib.util.spec_from_file_location("yggdrasil_y075_for_y077", Y075_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y075_IMPORT_SPEC_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def source_payload_projection(selected):
    projected = {"key": tuple(selected["key"])}
    for name in PAYLOAD_FIELDS:
        projected[name] = EXPECTED_SOURCE_STATE[name]
    for name in ("train_occurrence_count", "train_argmax_count", "train_argmax"):
        if name in selected:
            projected[name] = selected[name]
    return projected


def summarize(child):
    m = child["metrics"]
    return {
        "original_prose": float(m["original_positive_prose_collateral_schedule_count"]),
        "active_prose": float(m["active_positive_prose_collateral_schedule_count"]),
        "original_partner_fail": float(m["original_partner_collateral_failure_count"]),
        "active_partner_fail": float(m["active_partner_collateral_failure_count"]),
        "original_first": float(m["original_mean_first_success_packet"]),
        "active_first": float(m["active_mean_first_success_packet"]),
        "source_mismatch": float(m["source_identity_mismatch_count"] + m["transfer_manifest_identity_mismatch_count"]),
        "transport_mismatch": float(m["transported_state_identity_mismatch_count"]),
        "capacity_growth": float(m["capacity_growth_event_count"]),
        "invalid": float(m["invalid_evaluation_rows"]),
    }


def behavior_changed(child):
    m = child["metrics"]
    if m["active_positive_prose_collateral_schedule_count"] != m["original_positive_prose_collateral_schedule_count"]:
        return True
    if m["active_mean_first_success_packet"] != m["original_mean_first_success_packet"]:
        return True
    if m["active_partner_collateral_failure_count"] != m["original_partner_collateral_failure_count"]:
        return True
    for d in child.get("diagnostics", []):
        for p in d.get("packets", []):
            if p["active"] != p["original"]:
                return True
    return False


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
        "selectors_same_row_count": 0.0,
        "variant_count": 0.0,
        "clean_rescue_count": 0.0,
        "behavior_change_count": 0.0,
        "source_key_clean_rescue_count": 0.0,
        "local_key_clean_rescue_count": 0.0,
        "local_payload_clean_rescue_count": 0.0,
        "source_payload_clean_rescue_count": 0.0,
        "source_key_local_payload_clean_rescue": 0.0,
        "source_key_source_payload_clean_rescue": 0.0,
        "local_key_local_payload_clean_rescue": 0.0,
        "local_key_source_payload_clean_rescue": 0.0,
        "key_main_effect": 0.0,
        "payload_main_effect": 0.0,
        "interaction_effect": 0.0,
        "source_payload_projection_count": 0.0,
        "heldout_factor_choice_count": 0.0,
        "post_result_factor_change_count": 0.0,
        "all_child_source_identity_mismatch_count": 0.0,
        "all_child_transport_identity_mismatch_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "persistent_state_write_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }
    if y075.SOURCE_STATE != EXPECTED_SOURCE_STATE:
        metrics["source_state_identity_mismatch_count"] += 1.0

    pool = list(y075.build_pool(root, metrics))
    source_selected = sorted(pool, key=y075.source_rank)[0] if pool else None
    local_selected = sorted(pool, key=y075.local_rank)[0] if pool else None
    if source_selected is None or local_selected is None:
        metrics["invalid_evaluation_rows"] += 1.0
        return {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics, "cells": []}

    if tuple(source_selected["key"]) == tuple(local_selected["key"]):
        metrics["selectors_same_row_count"] = 1.0

    source_projected = source_payload_projection(source_selected)
    local_projected = source_payload_projection(local_selected)
    metrics["source_payload_projection_count"] = 2.0

    # Freeze all four cells before any child shadow outcome is opened.
    frozen = [
        ("SOURCE_CONDITIONED", "TARGET_LOCAL", dict(source_selected)),
        ("SOURCE_CONDITIONED", "SOURCE_RETAINED_PROJECTION", source_projected),
        ("LOCAL_ONLY", "TARGET_LOCAL", dict(local_selected)),
        ("LOCAL_ONLY", "SOURCE_RETAINED_PROJECTION", local_projected),
    ]

    cells = []
    outcome = {}
    original = None
    for key_origin, payload_origin, state in frozen:
        child = y075.run_variant(root, state)
        s = summarize(child)
        cur_original = (s["original_prose"], s["original_partner_fail"], s["original_first"])
        if original is None:
            original = cur_original
        elif cur_original != original:
            metrics["invalid_evaluation_rows"] += 1.0
        clean = s["active_prose"] > s["original_prose"] and s["active_partner_fail"] == 0.0
        changed = behavior_changed(child)
        metrics["variant_count"] += 1.0
        metrics["clean_rescue_count"] += float(clean)
        metrics["behavior_change_count"] += float(changed)
        metrics["all_child_source_identity_mismatch_count"] += s["source_mismatch"]
        metrics["all_child_transport_identity_mismatch_count"] += s["transport_mismatch"]
        metrics["capacity_growth_event_count"] += s["capacity_growth"]
        metrics["invalid_evaluation_rows"] += s["invalid"]
        if key_origin == "SOURCE_CONDITIONED":
            metrics["source_key_clean_rescue_count"] += float(clean)
        else:
            metrics["local_key_clean_rescue_count"] += float(clean)
        if payload_origin == "TARGET_LOCAL":
            metrics["local_payload_clean_rescue_count"] += float(clean)
        else:
            metrics["source_payload_clean_rescue_count"] += float(clean)
        cell_name = (
            ("source_key" if key_origin == "SOURCE_CONDITIONED" else "local_key")
            + "_"
            + ("local_payload" if payload_origin == "TARGET_LOCAL" else "source_payload")
        )
        metrics[cell_name + "_clean_rescue"] = float(clean)
        outcome[cell_name] = int(clean)
        cells.append({
            "key_origin": key_origin,
            "payload_origin": payload_origin,
            "key": list(state["key"]),
            "best": int(state["best"]),
            "total": int(state["total"]),
            "best_count": int(state["best_count"]),
            "consistency": float(state["consistency"]),
            "utility": float(state["utility"]),
            "cell_index": int(state["cell_index"]),
            "map_best": int(state["map_best"]),
            "clean_rescue": clean,
            "behavior_changed": changed,
            "original_positive_prose_collateral_schedule_count": s["original_prose"],
            "active_positive_prose_collateral_schedule_count": s["active_prose"],
            "active_partner_collateral_failure_count": s["active_partner_fail"],
            "active_mean_first_success_packet": s["active_first"],
        })

    a = outcome.get("source_key_local_payload", 0)
    b = outcome.get("source_key_source_payload", 0)
    c = outcome.get("local_key_local_payload", 0)
    d = outcome.get("local_key_source_payload", 0)
    key_effect = int(a == b and c == d and a != c)
    payload_effect = int(a == c and b == d and a != b)
    interaction = int(0 < (a + b + c + d) < 4 and key_effect == 0 and payload_effect == 0)
    metrics["key_main_effect"] = float(key_effect)
    metrics["payload_main_effect"] = float(payload_effect)
    metrics["interaction_effect"] = float(interaction)

    if metrics["target_source_count"] != 3.0 or metrics["target_total_source_bytes"] != 57272.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["donor_row_count"] != 16.0 or metrics["eligible_candidate_count"] != 6.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["selectors_same_row_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["variant_count"] != 4.0 or metrics["source_payload_projection_count"] != 2.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["source_state_identity_mismatch_count"] != 0.0 or metrics["source_state_mutation_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["heldout_factor_choice_count"] != 0.0 or metrics["post_result_factor_change_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["all_child_source_identity_mismatch_count"] != 0.0 or metrics["all_child_transport_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["capacity_growth_event_count"] != 0.0 or metrics["persistent_state_write_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if any(not math.isfinite(float(v)) for v in metrics.values()):
        metrics["invalid_evaluation_rows"] += 1.0

    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": metrics,
        "source_selected": source_selected,
        "local_selected": local_selected,
        "cells": cells,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(run(a.root), f, allow_nan=False, separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main()
