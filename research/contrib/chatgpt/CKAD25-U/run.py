"""CKAD25-U: fixed-budget native causal intervention selection, source-free.

Frozen developer-only test of the EXISTING NativeCumulativeLearner.propose()
policy. It never changes native source, uses protected original environments,
or adds an independent cognitive architecture. Interventions reveal outcomes
only after their choice; held inputs are disjoint and identical across arms.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import random
import time
from pathlib import Path
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
HELPERS=HERE.parent/"CKAD25-S"/"run.py"
CKPT="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS=(7129,8137,9143)
LAWS=("affine_bias","negated_gate","two_conjunctions","selector","threshold2","composed_parity")
POLICIES=("native_propose","random","fixed","exact_eig")
METHODS=("native_degree","native_sparse","cart","forest","logistic","frequency","exact_sparse3","uniform")
N_MODELS=697


def need(ok, msg):
    if not ok: raise ValueError("CKAD25U_"+msg)


def helper():
    spec=importlib.util.spec_from_file_location("ckad25s_frozen_helpers",HELPERS)
    need(spec is not None and spec.loader is not None,"HELPERS_NOT_FOUND")
    h=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    need(h.ORIGINAL_CHECKPOINT==CKPT
         and h.SEEDS==(1103,2207,3301)
         and h.LAWS==("parity3","majority3","conditional-mux","mixed4"),
         "HELPER_VERSION_DRIFT")
    return h


def truth(law,mask):
    c0,c1,c2,a=((mask>>j)&1 for j in range(4))
    if law=="affine_bias": return 1^c0^c2^a
    if law=="negated_gate": return 1^(c0&a)
    if law=="two_conjunctions": return (c0&c1)^(c2&a)
    if law=="selector": return c1 if c0 else a
    if law=="threshold2": return int(c0+c1+c2+a>=2)
    if law=="composed_parity": return (c0^c1)&(c2^a)
    raise ValueError("CKAD25U_INVALID_EVALUATOR_LAW")


def roster(law,seed):
    key=digest(canonical(["CKAD25-U-SPLIT",law,seed]))
    order=list(range(16))
    random.Random(int(key[:16],16)).shuffle(order)
    held=order[:4]
    initial=order[4:8]
    choices=order[8:]
    need(len(held)==4 and len(initial)==4 and len(choices)==8
         and set(held).isdisjoint(initial+choices)
         and len(set(order))==16,"SPLIT_LEAK")
    return held,initial,choices


def public(mask):
    return [mask&7,mask>>3]


def witnessed(law,mask):
    return [mask&7,mask>>3,truth(law,mask)]


def anf_space(h,rows):
    """Conventional 697-rule prior; only previous revealed consequences."""
    features=[(h.terms(c,a),y) for c,a,y in rows]
    models=[]
    for degree in range(4):
        for active in itertools.combinations(range(16),degree):
            if all((sum(f[i] for i in active)&1)==y for f,y in features):
                models.append(active)
    return models


def exact_eig_probe(h, rows, choices):
    """Myopic entropy (balanced split) under a fixed exact conventional prior."""
    models=anf_space(h,rows)
    if not models:
        return min(choices),True,0
    # Balanced hypothetical labels maximize expected information under noiseless
    # binary hypotheses; never read the generator's outcome before selecting.
    scored=[]
    for mask in sorted(choices):
        feats=h.terms(*public(mask))
        ones=sum(sum(feats[i] for i in active)&1 for active in models)
        uncertainty=ones*(len(models)-ones)
        scored.append((-uncertainty,mask))
    return min(scored)[1],False,len(models)


def select(policy, state, slot, pool, observed, h, rng):
    if policy=="native_propose":
        proposed=state.propose(slot,[public(mask) for mask in pool],1)
        need(len(proposed)==1 and len(proposed[0])==2,"UNTRUSTED_NATIVE_PROPOSAL")
        mask=proposed[0][0]|(proposed[0][1]<<3)
        need(mask in pool,"PROPOSE_OUTSIDE_PUBLIC_POOL")
        return mask,False,0
    if policy=="random":
        return rng.choice(sorted(pool)),False,0
    if policy=="fixed":
        return min(pool),False,0
    if policy=="exact_eig":
        return exact_eig_probe(h,observed,pool)
    raise ValueError("UNKNOWN_ACQUISITION_ARM")


def negative_controls():
    h=helper()
    need(sum(1 for degree in range(4)
             for _ in itertools.combinations(range(16),degree))==N_MODELS,
         "HYPOTHESIS_CAPACITY")
    # A contradictory same-address source cannot acquire an exact hypothesis.
    need(anf_space(h,[[0,0,0],[0,0,1]])==[],"CONTRADICTION_NOT_DETECTED")
    # No family-identifying generator labels or hidden answer may enter native
    # proposal contract (only [context, action] pairs are admissible).
    parent=h.snapshot()
    try:
        parent.propose(1,[[0,0,1]],1)
    except Exception:
        pass
    else:
        raise ValueError("CKAD25U_PUBLIC_ACTION_LABEL_LEAK")
    need(parent.checkpoint()==h.snapshot().checkpoint(),"SELFTEST_MUTATED_SOURCE")
    return True


def evaluate():
    start=time.monotonic()
    h=helper()
    parent=h.snapshot()
    parent_bytes=parent.checkpoint()
    need(digest(parent_bytes)==CKPT,"ORIGINAL_CHECKPOINT_MISMATCH")
    old_preds=[parent.predict(0,c,a) for a in (0,1) for c in range(8)]
    records=[]
    for seed in SEEDS:
        for policy in POLICIES:
            state=NativeCumulativeLearner.restore(parent_bytes,CKPT)
            all_train={}
            all_held={}
            all_hashes={}
            aig_fallbacks=0
            for slot,law in enumerate(LAWS,start=1):
                held,initial,choices=roster(law,seed)
                ref=digest(canonical(["CKAD25-U-DEV",seed,policy,slot]))
                first=[witnessed(law,mask) for mask in initial]
                state=state.observe(slot,first,digest(canonical(first)),source_ref=ref)
                train=list(first)
                pool=set(choices)
                random_seed=int(digest(canonical(["CKAD25-U-ARM-RNG",seed,law]))[:16],16)
                rng=random.Random(random_seed)
                for _ in range(4):
                    chosen,fallback,_count=select(policy,state,slot,pool,train,h,rng)
                    aig_fallbacks+=int(fallback)
                    need(chosen in pool and chosen not in held,"ACQUISITION_LEAK_OR_DUP")
                    newrow=witnessed(law,chosen)
                    state=state.observe(slot,[newrow],digest(canonical([newrow])),
                                        source_ref=ref)
                    train.append(newrow)
                    pool.remove(chosen)
                need(len(train)==8 and len(pool)==4
                     and len({(c,a) for c,a,_ in train})==8
                     and not set(held)&{c|(a<<3) for c,a,_ in train},
                     "ACTION_BUDGET_OR_HELD_LEAK")
                all_train[slot]=train
                all_held[slot]=[witnessed(law,mask) for mask in held]
                all_hashes[slot]=digest(canonical([[mask&7,mask>>3] for mask in held]))
            before_bytes=state.checkpoint()
            before=NativeCumulativeLearner.restore(before_bytes,digest(before_bytes))
            repaired=before
            repairs=0
            for slot in range(1,len(LAWS)+1):
                hyp=repaired._hypotheses[slot]
                need(hyp is not None,"MISSING_NATIVE_EIGHT_ROW_HYPOTHESIS")
                if not hyp.eligible:
                    repaired_next, sparse, _=repaired.repair_sparse(slot)
                    if repaired_next is not repaired:
                        need(sparse.eligible,"INELIGIBLE_SPARSE_PROMOTION")
                        repairs+=1
                    repaired=repaired_next
            final_bytes=repaired.checkpoint()
            cold=NativeCumulativeLearner.restore(final_bytes,digest(final_bytes))
            retention=(
                parent.checkpoint()==parent_bytes
                and cold._properties.checkpoint()==parent._properties.checkpoint()
                and cold._source._seen[0]==parent._source._seen[0]
                and cold._hypotheses[0].checkpoint()==parent._hypotheses[0].checkpoint()
                and cold._events[:len(parent._events)]==parent._events
                and [cold.predict(0,c,a) for a in (0,1) for c in range(8)]==old_preds
                and cold.checkpoint()==final_bytes
                and all(cold.info()["observed_inputs"][slot]==8
                        for slot in range(1,len(LAWS)+1))
                and not any(cold.info()["quarantined"][:len(LAWS)+1])
            )
            need(retention,"RETENTION_OR_COLD_REPLAY")
            for slot,law in enumerate(LAWS,start=1):
                train,held=all_train[slot],all_held[slot]
                conventional,supported=h.conventional(train,held,seed)
                addrs=[(c,a) for c,a,_ in held]
                conventional["native_degree"]=[before.predict(slot,c,a) for c,a in addrs]
                conventional["native_sparse"]=[cold.predict(slot,c,a) for c,a in addrs]
                metrics={method:h.score(conventional[method],held) for method in METHODS}
                records.append({
                    "seed":seed,"policy":policy,"slot":slot,
                    "held_inputs_sha256":all_hashes[slot],
                    "train_sha256":digest(canonical(train)),
                    "train_rows":len(train),"held_rows":len(held),
                    "law_family":law,"native_cold_retention":retention,
                    "exact_sparse3_supported":supported,
                    "metrics":metrics,
                })
    need(len(records)==len(SEEDS)*len(POLICIES)*len(LAWS),"COHORT_COUNT")
    held_fingerprints={}
    for r in records:
        idx=(r["seed"],r["law_family"])
        held_fingerprints.setdefault(idx,set()).add(r["held_inputs_sha256"])
    need(all(len(v)==1 for v in held_fingerprints.values()),"POLICY_HELD_ADDRESS_DRIFT")
    means={
        policy:{
            method:round(sum(r["metrics"][method]["brier"] for r in records
                             if r["policy"]==policy)/(len(SEEDS)*len(LAWS)),9)
            for method in METHODS
        } for policy in POLICIES
    }
    coverage={
        policy:{key:sum(r["metrics"]["native_degree"][key] for r in records
                         if r["policy"]==policy)
                for key in ("answered","correct_answered","incorrect_answered")}
        for policy in POLICIES
    }
    def pred(policy):return means[policy]["native_degree"]
    gates={
        "old_native_knowledge_retained":all(r["native_cold_retention"] for r in records),
        "gain_0_03_vs_random":pred("native_propose") <= pred("random")-0.03+1e-12,
        "gain_0_03_vs_fixed":pred("native_propose") <= pred("fixed")-0.03+1e-12,
        "near_eig_within_0_03":pred("native_propose") <= pred("exact_eig")+0.03+1e-12,
        "at_least_18_correct_answered":coverage["native_propose"]["correct_answered"]>=18,
        "wrong_no_more_than_random_plus_2":coverage["native_propose"]["incorrect_answered"]<=coverage["random"]["incorrect_answered"]+2,
        "within_0_02_of_exact_sparse_on_same_actions":
            pred("native_propose") <= means["native_propose"]["exact_sparse3"]+0.02+1e-12,
    }
    return {
      "schema":"yggdrasil.ckad25u.prospective-native-acquisition.v1",
      "frozen_source_sha256":digest(Path(__file__).read_bytes()),
      "helper_source_sha256":digest(HELPERS.read_bytes()),
      "original_native_checkpoint_sha256":CKPT,
      "seeds":list(SEEDS),"law_families":list(LAWS),
      "policies":list(POLICIES),
      "experimental_arm_count":len(POLICIES),
      "seed_law_cases_per_arm":len(SEEDS)*len(LAWS),
      "new_synthetic_observations_all_arms":len(POLICIES)*len(SEEDS)*len(LAWS)*8,
      "same_held_test_actions_per_arm":len(SEEDS)*len(LAWS)*4,
      "original_protected_actions":0,
      "original_held_outcome_reused":False,
      "native_source_changed":False,"candidate_policy_is_existing_native_propose":True,
      "per_seed_policy_law":records,
      "brier_by_policy_method":means,
      "native_coverage_by_policy":coverage,
      "gates":gates,
      "disposition":"DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_NO_GO",
      "scientific_pass":False,"accepted_model":False,"forge_dispatch_authorized":False,
      "native_promotion_authorized":False,"deployment_authorized":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--selfcheck",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.selfcheck:
        need(not args.output,"SELFTEST_NO_RESULT")
        negative_controls()
        print("CKAD25U_SOURCE_NEGATIVES_PASS")
        return
    need(args.output is not None,"RESULT_OUTPUT_REQUIRED")
    start=time.monotonic()
    result=evaluate()
    raw=canonical(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25U_DISPOSITION="+result["disposition"])
    print("CKAD25U_BRIER_BY_POLICY="+json.dumps(result["brier_by_policy_method"],sort_keys=True))
    print("CKAD25U_NATIVE_COVERAGE="+json.dumps(result["native_coverage_by_policy"],sort_keys=True))
    print("CKAD25U_FROZEN_GATES="+json.dumps(result["gates"],sort_keys=True))
    print("CKAD25U_RESULT_SHA256="+digest(raw))
    print("CKAD25U_WALL_SECONDS="+str(round(time.monotonic()-start,3)))


if __name__=="__main__":
    main()
