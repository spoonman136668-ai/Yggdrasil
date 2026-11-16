"""FKP-22 first prospective public TRAIN experiment on active causal interventions.

Each learner receives a COMMON fully physical 16-world support corpus. Each
then independently fits 12 prior action/outcome observations in a fresh known
or shifted public evaluation world, chooses exactly TWO physical interventions
and predicts TWO remaining unobserved consequences BEFORE source actions.

This is NOT private DEV/TRANSFER or unprovided-operator scientific first use.
Independent exhaustive GF2 base learner + Bayes entropy is a strong control.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import random
import sys
import time

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-21"))
import rule_learning as base_rules

import active_policy as policies
import public_active_source as source

ARMS=policies.MODES
PREREG="c05d9002ab63163e8b4e296c02dda1f2b8134cb0"


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _digest(obj):
    return sha256(_canonical(obj)).hexdigest()


def _bit(rows):
    _x,result,_trace=base_rules._actual(rows)
    return result


def _frozen_base(seed,mode):
    base_mode=("INDEPENDENT_GF2_ELIMINATION" if
               mode=="INDEPENDENT_BAYES_ENTROPY" else "INNOVATION_GF2")
    model=base_rules.PublicRuleArm(base_mode)
    recorded=[]
    for event_id,x in enumerate(source.TRAIN):
        # World is created only for an ACTUAL chosen intervention.
        actual=source.physically_apply(seed,x)
        y=_bit(actual)
        model.observe_train(actual,event_id=event_id)
        recorded.append([x,y])
    model.freeze()
    if model.observations!=12:
        raise AssertionError("FKP22_BASE_FIT_MISSING_PHYSICAL_EVIDENCE")
    return model,recorded


def _physical_support():
    start=time.perf_counter()
    signatures=[]
    evidence=[]
    for seed in source.SUPPORT:
        model,train=_frozen_base(seed,"SPARSE_PARTITION_GAIN")
        bits=[]
        for x in source.PROBES:
            p=model.predict_first(x)
            actual=_bit(source.physically_apply(seed,x))
            bits.append(actual^p)
        signature=sum(b<<i for i,b in enumerate(bits))
        signatures.append(signature)
        evidence.append({"public_train_sha256":_digest(train),
                         "physically_observed_residual_signature":signature,
                         "all_four_support_interventions_physically_applied":True})
    if len(signatures)!=16:
        raise AssertionError("FKP22_INCOMPLETE_PUBLIC_SUPPORT")
    return signatures,evidence,time.perf_counter()-start


def _run_world(seed,ordinal,mode,signatures):
    start=time.perf_counter()
    base,train=_frozen_base(seed,mode)
    support=policies.ActiveResidualPolicy(
        mode,signatures,public_ordinal=ordinal)
    base_receipt=base.state_receipt()
    training_sha=_digest(train)
    fit_time=time.perf_counter()-start
    experiment=[]
    start=time.perf_counter()
    for step in range(2):
        chosen=support.choose_query()  # choice BEFORE any source action
        x=source.PROBES[chosen]
        p=base.predict_first(x)
        # NO future value access: selected action first, actual earned later.
        actual=_bit(source.physically_apply(seed,x))
        support.observe_actual_query(chosen,actual^p)
        experiment.append([chosen,x,p,actual,actual^p])
    if len(set(entry[0] for entry in experiment))!=2:
        raise AssertionError("FKP22_NOT_TWO_DISTINCT_PHYSICAL_PROBES")
    frozen=support.semantic_receipt()
    cold=policies.ActiveResidualPolicy.restore(support.checkpoint())
    if cold.semantic_receipt()!=frozen or cold.checkpoint()!=support.checkpoint():
        raise AssertionError("FKP22_COLD_PROBE_EVIDENCE_NOT_IDENTICAL")
    score=[]
    for i,x in enumerate(source.PROBES):
        if i in support.chosen_queries:
            continue
        # Prediction MUST be made before its own physical source action.
        expected_base=base.predict_first(x)
        expected_residual=cold.predict_unqueried(i)
        prediction=expected_base^expected_residual
        physical=source.physically_apply(seed,x)
        actual=_bit(physical)
        score.append([i,x,prediction,actual,int(prediction==actual)])
    if len(score)!=2 or base.state_receipt()!=base_receipt or (
            cold.semantic_receipt()!=frozen):
        raise AssertionError("FKP22_SCORED_OUTCOME_TOUCHED_FROZEN_POLICY")
    score_time=time.perf_counter()-start
    count=cold.posterior_support_count
    return {
        "public_training_sha256":training_sha,
        "frozen_base_fit_sha256":base_receipt,
        "chosen_physical_queries":experiment,
        "scored_preaction_physical_outcomes":score,
        "correct_unqueried":sum(x[-1] for x in score),
        "posterior_supported_worlds":count,
        "trained_query_policy_cold_sha256":frozen,
        "checkpoint_sha256":sha256(cold.checkpoint()).hexdigest(),
        "logical_learned_bytes":base.logical_learned_bytes+cold.logical_bytes,
        "fit_wall_seconds":fit_time,
        "probe_and_score_wall_seconds":score_time,
        "score_used_to_update_model":False
    }


def _bootstrap(known):
    if len(known)!=16:
        raise ValueError("FKP22_KNOWN_FAMILY_WORLD_COUNT")
    rng=random.Random(2222)
    diffs=[]
    fixed=[]
    for _ in range(10000):
        s=[known[rng.randrange(16)] for __ in range(16)]
        diff=sum(w["arms"]["SPARSE_PARTITION_GAIN"]["correct_unqueried"]-
                 w["arms"]["INDEPENDENT_BAYES_ENTROPY"]["correct_unqueried"]
                 for w in s)
        base=sum(w["arms"]["SPARSE_PARTITION_GAIN"]["correct_unqueried"]-
                 w["arms"]["FIXED_0_1"]["correct_unqueried"] for w in s)
        diffs.append(diff)
        fixed.append(base)
    diffs.sort()
    fixed.sort()
    return {
        "bootstrap_seed":2222,"draws":10000,
        "candidate_minus_independent_strong_95_interval":[diffs[249],diffs[9749]],
        "candidate_minus_fixed_95_interval":[fixed[249],fixed[9749]],
        "scientific_pass":False
    }


def run():
    source_sha=os.environ.get("FKP22_SOURCE_SHA","")
    if len(source_sha)!=40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("FKP22_SOURCE_NOT_EXACT_PINNED")
    started=time.perf_counter()
    started_cpu=time.process_time()
    signatures,support_evidence,support_wall=_physical_support()
    by_world=[]
    for ordinal,seed in enumerate(source.KNOWN+source.SHIFT):
        arms={mode:_run_world(seed,ordinal,mode,signatures) for mode in ARMS}
        if len({v["public_training_sha256"] for v in arms.values()})!=1:
            raise AssertionError("FKP22_DIFFERENT_REAL_TRAINING_INFORMATION")
        by_world.append({
            "world_ordinal":ordinal,
            "cohort":"known_family" if ordinal<16 else "prior_shift",
            "arms":arms,
            "common_source_training_sha256":arms[ARMS[0]]["public_training_sha256"]
        })
    known=by_world[:16]
    shift=by_world[16:]
    totals={}
    for mode in ARMS:
        for name,worlds in (("known_family",known),("prior_shift",shift)):
            data=[w["arms"][mode] for w in worlds]
            totals.setdefault(mode,{})[name]={
                "correct_unqueried":sum(w["correct_unqueried"] for w in data),
                "total_first_unqueried":len(data)*2,
                "singleton_posterior_count":sum(w["posterior_supported_worlds"]==1
                    for w in data),
                "inconsistent_posterior_count":sum(w["posterior_supported_worlds"]==0
                    for w in data),
                "max_logical_learned_bytes":max(w["logical_learned_bytes"]
                    for w in data),
                "fit_wall_seconds":sum(w["fit_wall_seconds"] for w in data),
                "probe_and_score_wall_seconds":sum(w["probe_and_score_wall_seconds"]
                    for w in data)
            }
    if totals["SPARSE_PARTITION_GAIN"]["known_family"]["correct_unqueried"]!=32:
        raise AssertionError("FKP22_PUBLIC_KNOWN_FAMILY_ACTIVE_RESULT_DRIFT")
    if totals["INDEPENDENT_BAYES_ENTROPY"]["known_family"]["correct_unqueried"]!=32:
        raise AssertionError("FKP22_STRONG_CONTROL_UNDERFITTED")
    if totals["SPARSE_PARTITION_GAIN"]["prior_shift"]["correct_unqueried"]!=8:
        raise AssertionError("FKP22_SHIFT_NEGATIVE_NOT_REPRODUCED")
    return {
        "schema":"fkp22.active-physical-info-value.v1",
        "classification":"SOURCE_SAFE_TRAIN_ACTIVE_INFORMATION_EXPERIMENT_ONLY",
        "source_sha":source_sha,"prereg_first":PREREG,
        "support_source_evidence":support_evidence,
        "support_signature_multiset_sha256":_digest(sorted(signatures)),
        "same_support_signatures_for_all_methods":True,
        "physical_actions":(len(source.SUPPORT)*16+
                            len(ARMS)*(len(source.KNOWN)+len(source.SHIFT))*16)*4,
        "support_wall_seconds":support_wall,
        "scores_by_method":totals,
        "paired_known_bootstrap":_bootstrap(known),
        "per_world":by_world,
        "process_wall_seconds":time.perf_counter()-started,
        "process_cpu_seconds":time.process_time()-started_cpu,
        "held_dev_first_use":False,
        "protected_transfer_opened":False,
        "unfamiliar_law_scientific_pass":False,
        "accepted_native_changed":False
    }


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    r=run()
    p=Path(a.output_json)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,sort_keys=True,allow_nan=False,indent=2)+"\n",
                 encoding="utf-8")
    print("FKP22_SOURCE_SAFE_ACTIVE_INTERVENTION="+json.dumps(
        {k:r[k] for k in (
            "classification","source_sha","physical_actions",
            "scores_by_method","paired_known_bootstrap",
            "process_wall_seconds","process_cpu_seconds",
            "held_dev_first_use","protected_transfer_opened",
            "unfamiliar_law_scientific_pass","accepted_native_changed")},
        sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
