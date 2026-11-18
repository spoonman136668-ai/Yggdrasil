"""CKAD25-T: source-frozen prospective evidence certificate for native sparse repair.

Development-only, one Yggdrasil NativeCumulativeLearner, existing CKAD25
checkpoint and source code, four NEW procedural causal laws.
Never use held outcomes to choose a repair or change the original model.
This is an external diagnostic readout, not an accepted native modification.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import time

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE = Path(__file__).resolve().parent
S_MODULE = HERE.parent / "CKAD25-S" / "run.py"
CKAD_CHECKPOINT = "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS = (4409, 5519, 6637)
FAMILIES = ("xor4", "nand2", "cross_mux", "threshold4")
METHODS = ("certified_repair", "unconditional_repair", "native_degree", "exact_sparse3",
           "agreement_certificate", "cart", "forest", "logistic", "frequency", "uniform")
SOURCE_NAMESPACE = "ckad25t-unfamiliar-consumed-fixture-root"


def need(condition, message):
    if not condition:
        raise ValueError("CKAD25T_" + message)


def load_predecessor():
    # Reuse only pure input/scoring and baseline fitting helpers. DO NOT call
    # CKAD25-S prospective() or rescore its consumed four-law cohorts.
    spec = importlib.util.spec_from_file_location("ckad25s_helpers_readonly", S_MODULE)
    need(spec is not None and spec.loader is not None, "PREDECESSOR_HELPER_ABSENT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.ORIGINAL_CHECKPOINT == CKAD_CHECKPOINT
         and module.SEEDS == (1103,2207,3301)
         and module.LAWS == ("parity3","majority3","conditional-mux","mixed4"),
         "PARENT_BASELINE_DRIFT")
    return module


def truth(name, mask):
    c0, c1, c2, a = ((mask >> bit) & 1 for bit in range(4))
    if name == "xor4":
        return c0 ^ c1 ^ c2 ^ a
    if name == "nand2":
        return 1 ^ (c0 & c2)
    if name == "cross_mux":
        return (c0 & a) ^ (c2 & (1 ^ a))
    if name == "threshold4":
        return int(c0 + c1 + c2 + a >= 3)
    raise ValueError("CKAD25T_INVALID_EVALUATOR_LAW")


def split(name, seed):
    # Interventions are public only when supplied with the corresponding
    # revealed outcome to native observe. Future outcomes never reach learner.
    import random
    key = digest(canonical([SOURCE_NAMESPACE,seed,name]))
    order = list(range(16))
    random.Random(int(key[:16],16)).shuffle(order)
    rows = [[mask & 7, mask >> 3, truth(name,mask)] for mask in order]
    train, held = rows[:12], rows[12:]
    need(len(train) == 12 and len(held) == 4
         and len({(c,a) for c,a,_ in rows}) == 16,
         "TRAIN_HELD_SPLIT")
    return train, held


def sparse_certificate(helper, observed, query):
    # All 697 conventional <=3-term four-variable ANF candidates, not just
    # a selected minimum-support solution. No held outcome is an input.
    feature_observed = [(helper.terms(c,a), y) for c,a,y in observed]
    compatible = []
    for k in range(4):
        for active in itertools.combinations(range(16),k):
            if all((sum(features[i] for i in active)&1) == y
                   for features,y in feature_observed):
                compatible.append(active)
    outcome = []
    for c,a in query:
        if not compatible:
            outcome.append(None)
            continue
        features = helper.terms(c,a)
        votes = [(sum(features[i] for i in active)&1) for active in compatible]
        outcome.append(votes[0] if all(v==votes[0] for v in votes) else None)
    return outcome, len(compatible)


def run():
    start = time.monotonic()
    h = load_predecessor()
    base = h.snapshot()
    original_raw = base.checkpoint()
    need(digest(original_raw) == CKAD_CHECKPOINT, "EXACT_PARENT_CHECKPOINT")
    original_predictions = [base.predict(0,c,a) for a in (0,1) for c in range(8)]
    results = []

    for seed in SEEDS:
        parent = NativeCumulativeLearner.restore(original_raw,CKAD_CHECKPOINT)
        working = parent
        exposed, helds, source_packets = {}, {}, {}
        for slot,name in enumerate(FAMILIES,start=1):
            train, held = split(name,seed)
            source_ref = digest(canonical([SOURCE_NAMESPACE,seed,slot]))
            source_packets[slot] = source_ref
            for packet in (train[:8],train[8:]):
                working = working.observe(slot,packet,digest(canonical(packet)),
                                          source_ref=source_ref)
            exposed[slot] = train
            helds[slot] = held

        before_raw = working.checkpoint()
        before = NativeCumulativeLearner.restore(before_raw,digest(before_raw))
        repaired = before
        mode={}
        for slot in range(1,5):
            old_h = repaired._hypotheses[slot]
            need(old_h is not None,"NO_NATIVE_DEGREE_HYPOTHESIS")
            if old_h.eligible:
                mode[slot] = "native_degree_eligible"
            else:
                next_model, sparse, _ = repaired.repair_sparse(slot)
                mode[slot] = ("sparse_eligible" if next_model is not repaired
                              and sparse.eligible else "sparse_declined")
                repaired = next_model
        repaired_raw = repaired.checkpoint()
        cold = NativeCumulativeLearner.restore(repaired_raw,digest(repaired_raw))

        retention = (
            base.checkpoint() == original_raw
            and cold._properties.checkpoint()==base._properties.checkpoint()
            and cold._source._seen[0]==base._source._seen[0]
            and cold._source._model._profiles[0]==base._source._model._profiles[0]
            and cold._hypotheses[0].checkpoint()==base._hypotheses[0].checkpoint()
            and cold._events[:len(base._events)]==base._events
            and [cold.predict(0,c,a) for a in (0,1) for c in range(8)]
                 == original_predictions
            and cold.checkpoint()==repaired_raw
            and len(cold._events)==len(base._events)+8
            and all(cold.info()["observed_inputs"][slot]==12 for slot in range(1,5))
            and not any(cold.info()["quarantined"][:5])
        )
        need(retention,"OLD_NATIVE_KNOWLEDGE_OR_COLD_STATE_DRIFT")

        for slot,name in enumerate(FAMILIES,start=1):
            train,held=exposed[slot],helds[slot]
            queries=[(c,a) for c,a,_ in held]
            certified,version_space = sparse_certificate(h,train,queries)
            control,supported = h.conventional(train,held,seed)
            degree=[before.predict(slot,c,a) for c,a in queries]
            ungated=[cold.predict(slot,c,a) for c,a in queries]
            selected=[]
            for a,(c1,c2) in enumerate(zip(degree,certified)):
                if c1 is not None:
                    selected.append(c1)
                elif c2 is not None and c2==ungated[a] and mode[slot]=="sparse_eligible":
                    selected.append(c2)
                else:
                    selected.append(None)
            control["native_degree"]=degree
            control["unconditional_repair"]=ungated
            control["certified_repair"]=selected
            control["agreement_certificate"]=certified
            metrics={m:h.score(control[m],held) for m in METHODS}
            results.append({
                "seed":seed,"law_family":name,"slot":slot,"training_rows":12,
                "train_sha256":digest(canonical(train)),
                "held_inputs_sha256":digest(canonical([[c,a] for c,a,_ in held])),
                "held_truth_sha256":digest(canonical([y for _,_,y in held])),
                "source_ref_sha256":source_packets[slot],
                "native_mode":mode[slot],
                "supporting_sparse_hypotheses":version_space,
                "sparse_posterior_has_models":supported,
                "old_knowledge_retained":retention,
                "methods":metrics
            })

    need(len(results)==12,"SCORED_COHORT_COUNT")
    means={m:round(sum(r["methods"][m]["brier"] for r in results)/12,9)
           for m in METHODS}
    coverage=sum(r["methods"]["certified_repair"]["answered"] for r in results)
    correct=sum(r["methods"]["certified_repair"]["correct_answered"] for r in results)
    wrong=sum(r["methods"]["certified_repair"]["incorrect_answered"] for r in results)
    wrong_by_family={fam:sum(r["methods"]["certified_repair"]["incorrect_answered"]
                             for r in results if r["law_family"]==fam)
                     for fam in FAMILIES}
    best_control=min(means[m] for m in ("cart","forest","logistic","exact_sparse3"))
    gates={
        "preserved_original_native_knowledge":all(r["old_knowledge_retained"] for r in results),
        "answered_min_12_of_48":coverage>=12,
        "confident_wrong_at_most_2_of_48":wrong<=2,
        "confident_wrong_each_family_at_most_1":max(wrong_by_family.values())<=1,
        "brier_improved_0_02_vs_unconditional_native_repair":
            means["certified_repair"]<=means["unconditional_repair"]-0.02+1e-12,
        "brier_at_most_native_degree_plus_0_01":
            means["certified_repair"]<=means["native_degree"]+0.01+1e-12,
        "brier_at_most_exact_sparse3_plus_0_02":
            means["certified_repair"]<=means["exact_sparse3"]+0.02+1e-12,
        "brier_better_than_uniform_by_0_02":
            means["certified_repair"]<=0.23+1e-12,
    }
    disposition="DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_MIXED_NO_GO"
    return {
        "schema":"yggdrasil.ckad25t.evidence-certified-repair-dev.v1",
        "parent_ckad_checkpoint_sha256":CKAD_CHECKPOINT,
        "source_script_sha256":digest(Path(__file__).read_bytes()),
        "reused_scoring_helpers_sha256":digest(S_MODULE.read_bytes()),
        "law_families":list(FAMILIES),
        "seeds":list(SEEDS),
        "seed_law_cases":12,
        "new_synthetic_training_interventions":144,
        "new_synthetic_held_actions":48,
        "original_world_interventions":0,
        "native_source_modified":False,
        "candidate_is_external_readout_only":True,
        "original_checkpoint_unchanged":True,
        "cold_native_retention_pass":True,
        "source_first_use":False,
        "original_held_cohorts_reused":False,
        "candidate_answered":coverage,
        "candidate_correct_answered":correct,
        "candidate_confident_wrong":wrong,
        "confident_wrong_by_family":wrong_by_family,
        "brier_means":means,
        "best_independent_fitted_control_brier":best_control,
        "gates":gates,
        "per_seed_law":results,
        "disposition":disposition,
        "scientific_pass":False,
        "native_promotion_authorized":False,
        "accepted_model":False,
        "forge_dispatch_authorized":False,
        "deployment_authorized":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=run()
    raw=canonical(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25T_DISPOSITION="+result["disposition"])
    print("CKAD25T_CONFIDENT_ANSWERED="+str(result["candidate_answered"]))
    print("CKAD25T_CONFIDENT_CORRECT="+str(result["candidate_correct_answered"]))
    print("CKAD25T_CONFIDENT_WRONG="+str(result["candidate_confident_wrong"]))
    print("CKAD25T_MEAN_BRIER="+json.dumps(result["brier_means"],sort_keys=True))
    print("CKAD25T_FROZEN_GATES="+json.dumps(result["gates"],sort_keys=True))
    print("CKAD25T_RESULT_SHA256="+digest(raw))


if __name__=="__main__":
    main()
