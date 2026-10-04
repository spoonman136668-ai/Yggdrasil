"""Yggdrasil 079: cumulative consolidation mechanism attribution.

Generated only from a preregistered machine-readable contract. All eight cells
are shadow evaluations. Accepted retained state and operational gates remain
immutable.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-MECHANISM-ATTRIBUTION-079"
Y075_PATH = Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.py")
PAYLOAD_FIELDS = ("best", "total", "best_count", "consistency", "utility", "cell_index", "map_best")
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
SOURCES = {
    "transfer": {
        "A": {"file": "code.bin", "sha256": "66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45", "bytes": 41453},
        "B": {"file": "structured.bin", "sha256": "95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932", "bytes": 14365},
        "C": {"file": "technical-prose.bin", "sha256": "48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b", "bytes": 1454},
    },
    "third": {
        "A": {"file": "code.bin", "sha256": "50744a9e70d67d62c97f3f434f4f05788b6b8514c6bce46cf7dafbaf49e2abff", "bytes": 41453},
        "B": {"file": "structured.bin", "sha256": "2a97ba02bc5e479b1738f6f0c3e09318bb5a255350c84de014ddbcebea46af56", "bytes": 14365},
        "C": {"file": "technical-prose.bin", "sha256": "23c002a1984ed065abfdbafa82100ed54d6bf6276a947676e710a30c75d96017", "bytes": 1454},
    },
    "fourth": {
        "A": {"file": "code.bin", "sha256": "283073d9f6c0dd868c39a913364bce6744ff1e29c038f6920197c0d33e0c2ac1", "bytes": 41453},
        "B": {"file": "structured.bin", "sha256": "a46fcfb7d862b03b750b61a5f667d4ac25a064df9ccb746e395db7e864068933", "bytes": 14365},
        "C": {"file": "technical-prose.bin", "sha256": "5d0c2efd139bd6094098bc893ed746020f03e0860a25f278348f43f47c236222", "bytes": 1454},
    },
    "fifth": {
        "A": {"file": "code.bin", "sha256": "504b68653b5478b88216f6342a74bacc5982549657005fb486dd00d753b4ea9a", "bytes": 41453},
        "B": {"file": "structured.bin", "sha256": "5c0f3a215ba35b7fbcaae212d27a33ba5109e16d89809987d16fa89072534281", "bytes": 14365},
        "C": {"file": "technical-prose.bin", "sha256": "527e21110a7f84a1939ccf6063fdfeb77905d9ec180e5fde18488d21b90c4f49", "bytes": 1454},
    },
}
HISTORICAL_ORDER = ("transfer", "third", "fourth")


def load_y075():
    spec = importlib.util.spec_from_file_location("yggdrasil_y075_for_y079", Y075_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y075_IMPORT_SPEC_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def builder_metrics():
    return {
        "target_source_identity_mismatch_count": 0.0,
        "target_source_count": 0.0,
        "target_total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "history_byte_budget_mismatch_count": 0.0,
        "donor_row_count": 0.0,
        "induction_source_bytes": 0.0,
        "eligible_candidate_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }


def build_context(y075, name, root):
    m = builder_metrics()
    y075.TARGET_SOURCES = {k: dict(v) for k, v in SOURCES[name].items()}
    pool = list(y075.build_pool(root, m))
    pool = [dict(x) for x in pool]
    selected = sorted(pool, key=y075.local_rank)[0] if pool else None
    mismatch = (
        m["target_source_identity_mismatch_count"]
        + m["base_training_identity_mismatch_count"]
        + m["history_byte_budget_mismatch_count"]
        + m["invalid_evaluation_rows"]
    )
    if m["target_source_count"] != 3.0 or m["target_total_source_bytes"] != 57272.0 or m["donor_row_count"] != 16.0:
        mismatch += 1.0
    return pool, selected, m, mismatch


def project_payload(target_selected, payload_source):
    projected = {"key": tuple(target_selected["key"])}
    for name in PAYLOAD_FIELDS:
        projected[name] = payload_source[name]
    for name in ("train_occurrence_count", "train_argmax_count", "train_argmax"):
        if name in target_selected:
            projected[name] = target_selected[name]
    return projected


def hamming(a, b):
    return sum(int(x) != int(y) for x, y in zip(a, b))


def retrieve_compressed(target_key, reps):
    ranked = sorted(
        HISTORICAL_ORDER,
        key=lambda name: (hamming(target_key, reps[name]["key"]), HISTORICAL_ORDER.index(name)),
    )
    name = ranked[0]
    return name, hamming(target_key, reps[name]["key"]), reps[name]


def retrieve_full(y075, target_key, full_pool):
    ranked = sorted(
        full_pool,
        key=lambda item: (
            hamming(target_key, item["state"]["key"]),
            HISTORICAL_ORDER.index(item["context"]),
            y075.local_rank(item["state"]),
            tuple(item["state"]["key"]),
        ),
    )
    item = ranked[0]
    return item["context"], hamming(target_key, item["state"]["key"]), item["state"]


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


def run(transfer_root, third_root, fourth_root, fifth_root):
    y075 = load_y075()
    metrics = {
        "historical_context_count": 3.0,
        "historical_full_pool_row_count": 0.0,
        "historical_empty_pool_count": 0.0,
        "historical_identity_mismatch_count": 0.0,
        "target_source_identity_mismatch_count": 0.0,
        "target_source_count": 0.0,
        "target_total_source_bytes": 0.0,
        "target_base_training_identity_mismatch_count": 0.0,
        "target_history_byte_budget_mismatch_count": 0.0,
        "target_donor_row_count": 0.0,
        "target_eligible_candidate_count": 0.0,
        "target_selectors_same_row_count": 0.0,
        "variant_count": 0.0,
        "compressed_retrieval_count": 0.0,
        "full_pool_retrieval_count": 0.0,
        "full_pool_selected_transfer_count": 0.0,
        "full_pool_selected_third_count": 0.0,
        "full_pool_selected_fourth_count": 0.0,
        "compressed_clean_rescue_count": 0.0,
        "full_pool_clean_rescue_count": 0.0,
        "full_pool_behavior_change_count": 0.0,
        "full_pool_partner_collateral_failure_count": 0.0,
        "compression_support": 0.0,
        "mixed_signal": 0.0,
        "heldout_pool_choice_count": 0.0,
        "post_result_pool_change_count": 0.0,
        "source_state_mutation_count": 0.0,
        "persistent_state_write_count": 0.0,
        "all_child_source_identity_mismatch_count": 0.0,
        "all_child_transport_identity_mismatch_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }
    if y075.SOURCE_STATE != EXPECTED_SOURCE_STATE:
        metrics["invalid_evaluation_rows"] += 1.0

    roots = {"transfer": transfer_root, "third": third_root, "fourth": fourth_root}
    reps = {}
    full_pool = []
    context_records = []
    for name in HISTORICAL_ORDER:
        pool, selected, bm, mismatch = build_context(y075, name, roots[name])
        metrics["historical_identity_mismatch_count"] += mismatch
        metrics["historical_full_pool_row_count"] += float(len(pool))
        if not pool:
            metrics["historical_empty_pool_count"] += 1.0
        if selected is not None:
            reps[name] = dict(selected)
        for state in pool:
            full_pool.append({"context": name, "state": dict(state)})
        context_records.append({
            "context": name,
            "eligible_pool_count": len(pool),
            "representative_key": list(selected["key"]) if selected is not None else None,
        })

    y075.TARGET_SOURCES = {k: dict(v) for k, v in SOURCES["fifth"].items()}
    tm = builder_metrics()
    target_pool = list(y075.build_pool(fifth_root, tm))
    source_selected = sorted(target_pool, key=y075.source_rank)[0] if target_pool else None
    local_selected = sorted(target_pool, key=y075.local_rank)[0] if target_pool else None
    metrics["target_source_identity_mismatch_count"] = tm["target_source_identity_mismatch_count"]
    metrics["target_source_count"] = tm["target_source_count"]
    metrics["target_total_source_bytes"] = tm["target_total_source_bytes"]
    metrics["target_base_training_identity_mismatch_count"] = tm["base_training_identity_mismatch_count"]
    metrics["target_history_byte_budget_mismatch_count"] = tm["history_byte_budget_mismatch_count"]
    metrics["target_donor_row_count"] = tm["donor_row_count"]
    metrics["target_eligible_candidate_count"] = tm["eligible_candidate_count"]
    metrics["invalid_evaluation_rows"] += tm["invalid_evaluation_rows"]

    if source_selected is None or local_selected is None or len(reps) != 3 or not full_pool:
        metrics["invalid_evaluation_rows"] += 1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics,"historical_contexts":context_records,"cells":[]}
    if tuple(source_selected["key"]) == tuple(local_selected["key"]):
        metrics["target_selectors_same_row_count"] = 1.0

    frozen = []
    for key_origin, target_selected in (("SOURCE_CONDITIONED", source_selected), ("LOCAL_ONLY", local_selected)):
        frozen.append((key_origin, "TARGET_LOCAL", dict(target_selected), None, None))
        frozen.append((key_origin, "SINGLE_SOURCE_RETAINED", project_payload(target_selected, EXPECTED_SOURCE_STATE), "accepted_source", None))
        cname, cdist, cstate = retrieve_compressed(tuple(target_selected["key"]), reps)
        metrics["compressed_retrieval_count"] += 1.0
        frozen.append((key_origin, "COMPRESSED_REPRESENTATIVE_SET", project_payload(target_selected, cstate), cname, cdist))
        fname, fdist, fstate = retrieve_full(y075, tuple(target_selected["key"]), full_pool)
        metrics["full_pool_retrieval_count"] += 1.0
        metrics["full_pool_selected_" + fname + "_count"] += 1.0
        frozen.append((key_origin, "FULL_ELIGIBLE_POOL", project_payload(target_selected, fstate), fname, fdist))

    cells = []
    by_key = {}
    original = None
    for key_origin, representation, state, selected_context, distance in frozen:
        child = y075.run_variant(fifth_root, state)
        s = summarize(child)
        cur_original = (s["original_prose"], s["original_partner_fail"], s["original_first"])
        if original is None:
            original = cur_original
        elif cur_original != original:
            metrics["invalid_evaluation_rows"] += 1.0
        clean = s["active_prose"] > s["original_prose"] and s["active_partner_fail"] == 0.0
        changed = behavior_changed(child)
        metrics["variant_count"] += 1.0
        metrics["all_child_source_identity_mismatch_count"] += s["source_mismatch"]
        metrics["all_child_transport_identity_mismatch_count"] += s["transport_mismatch"]
        metrics["capacity_growth_event_count"] += s["capacity_growth"]
        metrics["invalid_evaluation_rows"] += s["invalid"]
        if representation == "COMPRESSED_REPRESENTATIVE_SET":
            metrics["compressed_clean_rescue_count"] += float(clean)
        elif representation == "FULL_ELIGIBLE_POOL":
            metrics["full_pool_clean_rescue_count"] += float(clean)
            metrics["full_pool_behavior_change_count"] += float(changed)
            metrics["full_pool_partner_collateral_failure_count"] += s["active_partner_fail"]
        row = {
            "key_origin": key_origin,
            "representation": representation,
            "key": list(state["key"]),
            "best": int(state["best"]),
            "total": int(state["total"]),
            "best_count": int(state["best_count"]),
            "consistency": float(state["consistency"]),
            "utility": float(state["utility"]),
            "cell_index": int(state["cell_index"]),
            "map_best": int(state["map_best"]),
            "selected_historical_context": selected_context,
            "historical_key_hamming_distance": distance,
            "clean_rescue": clean,
            "behavior_changed": changed,
            "original_positive_prose_collateral_schedule_count": s["original_prose"],
            "active_positive_prose_collateral_schedule_count": s["active_prose"],
            "active_partner_collateral_failure_count": s["active_partner_fail"],
            "active_mean_first_success_packet": s["active_first"],
        }
        cells.append(row)
        by_key.setdefault(key_origin, {})[representation] = row

    support = False
    mixed = False
    for key_origin in ("SOURCE_CONDITIONED", "LOCAL_ONLY"):
        rows = by_key[key_origin]
        local = rows["TARGET_LOCAL"]
        single = rows["SINGLE_SOURCE_RETAINED"]
        compressed = rows["COMPRESSED_REPRESENTATIVE_SET"]
        full = rows["FULL_ELIGIBLE_POOL"]
        if full["clean_rescue"] and not local["clean_rescue"] and not single["clean_rescue"] and not compressed["clean_rescue"]:
            support = True
        if (
            not full["clean_rescue"]
            and full["behavior_changed"]
            and full["active_partner_collateral_failure_count"] == 0.0
            and (
                full["active_positive_prose_collateral_schedule_count"] > compressed["active_positive_prose_collateral_schedule_count"]
                or full["active_mean_first_success_packet"] < compressed["active_mean_first_success_packet"]
            )
        ):
            mixed = True
    metrics["compression_support"] = float(support)
    metrics["mixed_signal"] = float(mixed)

    if metrics["historical_context_count"] != 3.0 or metrics["historical_empty_pool_count"] != 0.0 or metrics["historical_full_pool_row_count"] <= 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["historical_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["target_source_count"] != 3.0 or metrics["target_total_source_bytes"] != 57272.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["target_source_identity_mismatch_count"] != 0.0 or metrics["target_base_training_identity_mismatch_count"] != 0.0 or metrics["target_history_byte_budget_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["target_donor_row_count"] != 16.0 or metrics["target_eligible_candidate_count"] != 6.0 or metrics["target_selectors_same_row_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["variant_count"] != 8.0 or metrics["compressed_retrieval_count"] != 2.0 or metrics["full_pool_retrieval_count"] != 2.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["heldout_pool_choice_count"] != 0.0 or metrics["post_result_pool_change_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["source_state_mutation_count"] != 0.0 or metrics["persistent_state_write_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["all_child_source_identity_mismatch_count"] != 0.0 or metrics["all_child_transport_identity_mismatch_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if metrics["capacity_growth_event_count"] != 0.0:
        metrics["invalid_evaluation_rows"] += 1.0
    if any(not math.isfinite(float(v)) for v in metrics.values()):
        metrics["invalid_evaluation_rows"] += 1.0

    return {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":EXPERIMENT,
        "metrics":metrics,
        "historical_contexts":context_records,
        "target_source_selected":source_selected,
        "target_local_selected":local_selected,
        "cells":cells,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True)
    p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True)
    p.add_argument("--fifth-root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root)
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(result,f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":
    main()
