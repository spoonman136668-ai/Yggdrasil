"""CKAD25-V: source-frozen prospective native causal relation compilation assay.

This uses one existing NativeCumulativeLearner and its actual source-owned
checkpoint, opt-in learned numeric weight committees, and completely distinct
public synthetic intervention outcomes. The supplied <=3-term ANF grammar
is conventional; exact Bayes over that grammar is a mandatory matched control.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE = Path(__file__).resolve().parent
HELPERS = HERE.parent / "CKAD25-S" / "run.py"
CHECKPOINT = "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS = (41017, 42017, 43017)
LAWS = ("xor_pair_with_offset", "double_interaction", "conditional_conjunction",
        "crossed_relation", "negated_relation", "high_order_threshold")
METHODS = ("native_compiled", "native_degree", "native_sparse",
           "exact_sparse3", "cart", "forest", "logistic", "frequency", "uniform")


def need(cond, message):
    if not cond:
        raise ValueError("CKAD25V_" + message)


def load_helpers():
    spec = importlib.util.spec_from_file_location("ckad25s_source_helpers_readonly", HELPERS)
    need(spec is not None and spec.loader is not None, "MISSING_INDEPENDENT_CONTROLS")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.ORIGINAL_CHECKPOINT == CHECKPOINT
         and module.SEEDS == (1103, 2207, 3301),
         "CONTROL_HELPER_DRIFT")
    return module


def outcome(law, x):
    c0, c1, c2, a = ((x >> i) & 1 for i in range(4))
    if law == "xor_pair_with_offset":
        return 1 ^ c0 ^ a
    if law == "double_interaction":
        return (c0 & c2) ^ (c1 & a)
    if law == "conditional_conjunction":
        return c0 & (c1 | a)
    if law == "crossed_relation":
        return (c0 & c1) ^ (c2 & a) ^ 1
    if law == "negated_relation":
        return 1 ^ (c2 & a)
    if law == "high_order_threshold":
        return int(c0 + c1 + c2 + a >= 3)
    raise ValueError("CKAD25V_UNKNOWN_GENERATOR")


def source_split(law, seed):
    seed_hash = digest(canonical(["CKAD25-V-disjoint-source", seed, law]))
    masks = list(range(16))
    random.Random(int(seed_hash[:16], 16)).shuffle(masks)
    train = [[x & 7, x >> 3, outcome(law, x)] for x in masks[:12]]
    held = [[x & 7, x >> 3, outcome(law, x)] for x in masks[12:]]
    need(len(train) == 12 and len(held) == 4 and
         len(set((c, a) for c, a, _ in train + held)) == 16, "TRAIN_HELD_OVERLAP")
    return train, held


def probability_score(probabilities, held):
    need(len(probabilities) == len(held) == 4, "PROBABILITY_COUNT")
    values = [p[0] / p[1] if p is not None else 0.5 for p in probabilities]
    need(all(isinstance(v, (float, int)) and 0 <= v <= 1 for v in values),
         "INVALID_PROBABILITY")
    brier = round(sum((p - row[2]) ** 2 for p, row in zip(values, held)) / 4, 9)
    confident = sum(p is not None and p[0] in (0, p[1]) for p in probabilities)
    confident_wrong = sum(p is not None and p[0] in (0, p[1])
                          and p[0] // p[1] != row[2] for p, row in zip(probabilities, held))
    return {"brier": brier, "answered": confident,
            "correct_answered": confident - confident_wrong,
            "incorrect_answered": confident_wrong}


def validate_native_continuation(start_state, train):
    # Engineering negative uses only already-provided 8+4 TRAIN rows, never held labels.
    first = train[:8]; later = train[8:]
    source = digest(canonical(["CKAD25-V-CONTINUATION-NONPRIMARY", 1]))
    stage = start_state.observe(1, first, digest(canonical(first)), source_ref=source)
    stage = stage.compile_causal_relations(1)
    need(stage._compiled[1] is not None, "CONTINUATION_NOT_COMPILED")
    raw = stage.checkpoint()
    stage = NativeCumulativeLearner.restore(raw, digest(raw))
    next_state = stage.observe(1, later, digest(canonical(later)), source_ref=source)
    need(next_state._compiled[1] is None and next_state.info()["observed_inputs"][1] == 12
         and next_state._source._seen[0] == start_state._source._seen[0],
         "CONTINUATION_DID_NOT_INVALIDATE_STALE_WEIGHTS")
    renewed = next_state.compile_causal_relations(1)
    raw2 = renewed.checkpoint()
    cold = NativeCumulativeLearner.restore(raw2, digest(raw2))
    need(cold.checkpoint() == raw2 and cold._compiled[1] is not None,
         "CONTINUATION_RECOMPILE_RESTORE")
    return True


def main_score():
    start = time.monotonic()
    h = load_helpers()
    base = h.snapshot()
    old_raw = base.checkpoint()
    need(digest(old_raw) == CHECKPOINT, "ORIGINAL_NATIVE_COLD_CHECKPOINT_DRIFT")
    old_predictions = [base.predict(0, c, a) for a in (0, 1) for c in range(8)]
    rows = []
    per_seed_committees = {}
    continuation_verified = False
    for seed in SEEDS:
        working = NativeCumulativeLearner.restore(old_raw, CHECKPOINT)
        train_by_slot = {}
        held_by_slot = {}
        for slot, law in enumerate(LAWS, start=1):
            train, held = source_split(law, seed)
            source_ref = digest(canonical(["CKAD25-V-PUBLIC", seed, slot]))
            working = working.observe(slot, train[:8], digest(canonical(train[:8])),
                                      source_ref=source_ref)
            working = working.observe(slot, train[8:], digest(canonical(train[8:])),
                                      source_ref=source_ref)
            train_by_slot[slot] = train
            held_by_slot[slot] = held
        if not continuation_verified:
            continuation_verified = validate_native_continuation(
                NativeCumulativeLearner.restore(old_raw, CHECKPOINT),
                train_by_slot[1])

        before = NativeCumulativeLearner.restore(working.checkpoint(),
                                                  digest(working.checkpoint()))
        # Separate opt-in conventional sparse arm, no model mutation or extra actions.
        sparse = before
        for slot in range(1, len(LAWS) + 1):
            hyp = sparse._hypotheses[slot]
            need(hyp is not None, "NATIVE_SOURCE_HYPOTHESIS_ABSENT")
            if not hyp.eligible:
                sparse, _, _ = sparse.repair_sparse(slot)
        compiled = before
        for slot in range(1, len(LAWS) + 1):
            compiled = compiled.compile_causal_relations(slot)
        compiled_raw = compiled.checkpoint()
        cold = NativeCumulativeLearner.restore(compiled_raw, digest(compiled_raw))

        retention = (base.checkpoint() == old_raw
                     and cold.checkpoint() == compiled_raw
                     and cold._properties.checkpoint() == base._properties.checkpoint()
                     and cold._source._seen[0] == base._source._seen[0]
                     and cold._hypotheses[0].checkpoint() == base._hypotheses[0].checkpoint()
                     and cold._events[:len(base._events)] == base._events
                     and [cold.predict(0,c,a) for a in (0,1) for c in range(8)] ==
                     old_predictions
                     and all(cold.info()["observed_inputs"][slot] == 12
                             for slot in range(1, len(LAWS) + 1))
                     and all(cold._compiled[slot] is not None
                             for slot in range(1, len(LAWS) + 1))
                     and not any(cold.info()["quarantined"][:7]))
        need(retention, "CUMULATIVE_NATIVE_RETENTION")
        per_seed_committees[str(seed)] = {
            "cold_checkpoint_sha256": digest(compiled_raw),
            "total_numeric_models_stored": sum(cold._compiled[j].model_count
                                               for j in range(1, len(LAWS) + 1))
        }

        for slot, law in enumerate(LAWS, start=1):
            train, held = train_by_slot[slot], held_by_slot[slot]
            predictions = [cold.causal_relation_probability(slot,c,a) for c,a,_ in held]
            controls, exact_supported = h.conventional(train, held, seed)
            # Independent exact full ≤3-term ANF Bayesian control must agree
            # with the programmatically learned native numeric weights.
            differences = [abs((ones/total) - expected)
                           for (ones,total), expected in zip(predictions,
                                                             controls["exact_sparse3"])]
            parity = max(differences, default=0.0)
            need(parity <= 1e-12, "NATIVE_CONVENTIONAL_EXACT_PARITY")
            controls["native_degree"] = [before.predict(slot,c,a) for c,a,_ in held]
            controls["native_sparse"] = [sparse.predict(slot,c,a) for c,a,_ in held]
            values = {name: h.score(controls[name], held) for name in METHODS
                      if name != "native_compiled"}
            values["native_compiled"] = probability_score(predictions, held)
            rows.append({
                "seed": seed, "slot": slot, "generator_family": law,
                "train_sha256": digest(canonical(train)),
                "held_inputs_sha256": digest(canonical([[c,a] for c,a,_ in held])),
                "held_truth_sha256": digest(canonical([y for _,_,y in held])),
                "source_ref_sha256": digest(canonical(["CKAD25-V-PUBLIC", seed, slot])),
                "native_learner_cold_retention": retention,
                "compiled_numeric_model_count": cold._compiled[slot].model_count,
                "conventional_exact_hypotheses_present": exact_supported,
                "native_held_fraction_predictions": predictions,
                "exact_probability_max_disagreement": round(parity, 15),
                "metrics": values
            })
    need(len(rows) == 18 and continuation_verified, "COHORT_COUNT_OR_CONTINUATION")
    mean_brier = {name:round(sum(r["metrics"][name]["brier"] for r in rows)/len(rows), 9)
                  for name in METHODS}
    confident = sum(r["metrics"]["native_compiled"]["answered"] for r in rows)
    wrong = sum(r["metrics"]["native_compiled"]["incorrect_answered"] for r in rows)
    best_fitted = min(mean_brier[name] for name in ("cart","forest","logistic"))
    gates = {
        "native_old_knowledge_retained": all(r["native_learner_cold_retention"] for r in rows),
        "source_compilation_continuation_recomputes": continuation_verified,
        "compiled_improves_0_025_over_native_degree":
            mean_brier["native_compiled"] <= mean_brier["native_degree"] - 0.025 + 1e-12,
        "compiled_brier_le_0_23": mean_brier["native_compiled"] <= 0.23 + 1e-12,
        "exact_bayesian_parity_all_72": all(r["exact_probability_max_disagreement"] <= 1e-12
                                            for r in rows),
        "no_more_than_4_confident_wrong": wrong <= 4,
        "within_0_03_of_best_fitted_nonsymbolic_control":
            mean_brier["native_compiled"] <= best_fitted + 0.03 + 1e-12
    }
    disposition = ("DEVELOPMENT_SIGNAL" if all(gates.values())
                   else "DEVELOPMENT_MIXED_NO_GO")
    result = {
        "schema":"yggdrasil.ckad25v.native-persistent-relational-compiler.v1",
        "source_script_sha256": digest(Path(__file__).read_bytes()),
        "control_helper_sha256": digest(HELPERS.read_bytes()),
        "native_model_source_mode": "engineering_fixture_only",
        "parent_native_checkpoint_sha256": CHECKPOINT,
        "seed_roster": list(SEEDS), "law_families": list(LAWS),
        "one_cumulative_native_learner_per_seed": True,
        "synthetic_training_observations":216,
        "synthetic_held_interventions":72,
        "protected_original_source_actions":0,
        "source_first_use":False,
        "model_compilation_opt_in_only":True,
        "accepted_main_changed":False,
        "per_seed_checkpoints":per_seed_committees,
        "per_seed_law":rows,
        "mean_brier":mean_brier,
        "best_fitted_non_symbolic_brier":best_fitted,
        "compiled_fully_confident_answered":confident,
        "compiled_confident_wrong":wrong,
        "gates":gates, "disposition":disposition,
        "scientific_pass":False,"owner_acceptance":False,
        "forge_dispatch":False,"native_promotion":False,
        "deployment":False
    }
    return result, time.monotonic()-start


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result, seconds = main_score()
    raw=canonical(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25V_SOURCE_SHA256="+result["source_script_sha256"])
    print("CKAD25V_HOLDOUT="+str(result["synthetic_held_interventions"]))
    print("CKAD25V_METRICS="+json.dumps(result["mean_brier"],sort_keys=True))
    print("CKAD25V_CONFIDENT="+str(result["compiled_fully_confident_answered"]))
    print("CKAD25V_CONFIDENT_WRONG="+str(result["compiled_confident_wrong"]))
    print("CKAD25V_GATES="+json.dumps(result["gates"],sort_keys=True))
    print("CKAD25V_DISPOSITION="+result["disposition"])
    print("CKAD25V_RESULT_SHA256="+digest(raw))
    print("CKAD25V_DEV_ELAPSED="+str(round(seconds,3)))


if __name__=="__main__":
    main()
