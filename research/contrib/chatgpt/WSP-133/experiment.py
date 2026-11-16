"""WSP133 R2 source-safe full active audit vs equal-information strong controls.

R1 source failure preserved. R2 starts a NEW prospectively frozen synthetic
mapping cohort: 64 positive permuted original relationships +32 changed shear
relationships. Every model is charged exactly 32 real effect consequences/world.
Neither candidate ever sees hidden evaluator mapping labels or scorer results.
"""
from __future__ import annotations
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from hashlib import sha256
import argparse
import json
import random
import sys
import time
import tracemalloc

import source as S
import learner as N
import controls as C

ROOT=Path(__file__).resolve().parents[1]
def _load(name,relative):
    spec=spec_from_file_location(name,ROOT/relative)
    m=module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m
N130=_load("_wsp130_native_wsp133","WSP-130/learner.py")
C130=_load("_wsp130_ref_wsp133","WSP-130/controls.py")
N131=_load("_wsp131_native_wsp133","WSP-131/binder.py")
C131=_load("_wsp131_ref_wsp133","WSP-131/controls.py")
R132=_load("_wsp132_repair_wsp133","WSP-132/repair.py")
RC132=_load("_wsp132_reference_wsp133","WSP-132/controls.py")

ARMS=("R2_ACTIVE_NUMERIC","R2_INDEPENDENT_EXACT_SYMBOLIC",
      "R1_FROZEN_NUMERIC","R1_INDEPENDENT_EXACT_SYMBOLIC",
      "LEGACY_WSP131_NUMERIC","OPTIMIZED_FIXED_SYMBOLIC",
      "FULLY_FITTED_CART","NO_UPDATE")
MODES=("known","shear")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def _scores():
    return {mode:{arm:{k:0 for k in FIELDS}
                  for arm in ARMS} for mode in MODES}
def _sum(dst,src):
    for k in FIELDS:dst[k]+=src[k]

def _warm():
    native=N130.DirectInducer()
    symbolic=C130.ExactSymbolic()
    original=[]
    old_signatures={}
    for law in S.S._origins():
        v=S.S.warm_world(law)
        a=S.S.warm_custodian(v)
        b=S.S.warm_custodian(v)
        remaining=set(v.legal)
        for _ in range(128):
            action=native.choose(v,remaining)
            if action not in remaining:
                raise AssertionError("WSP133_WARM_INVALID_ACTION")
            remaining.remove(action)
            native.observe(v,a.query(action))
            symbolic.observe(v,b.query(action))
        if a.receipt!=b.receipt:
            raise AssertionError("WSP133_WARM_EQUAL_SOURCE_BROKEN")
        na=tuple(native.infer(v,v.subject(x)) for x in range(256))
        sy=tuple(symbolic.infer(v,v.subject(x)) for x in range(256))
        if na!=sy or any(v not in (0,1) for v in na):
            raise AssertionError("WSP133_WARM_CAUSAL_PRIOR_INCOMPLETE")
        old_signatures[law]=na
        original.append([law,a.receipt,S.digest(na)])
    return native,symbolic,S.digest(original),old_signatures

def _bootstrap(rows):
    rng=random.Random(133)
    n=len(rows)
    vals=[a-b for a,b in rows]
    results=[]
    for _ in range(10000):
        results.append(100*sum(vals[rng.randrange(n)]
                               for k in range(n))/(n*224))
    results.sort()
    return {"seed":133,"resamples":10000,
            "gain_low_95pp":results[250],
            "gain_high_95pp":results[9749]}

def run_engineering():
    t0=time.perf_counter()
    p0=time.process_time()
    tracemalloc.start()
    if S.ALLOWED&S.DENIED:raise PermissionError("WSP133_PROTECTED_ORIGINAL_OVERLAP")
    warm,warm_sym,warm_sha,old_truths=_warm()
    warm_snapshot=warm.snapshot()
    models={
      "R2_ACTIVE_NUMERIC":N.ActiveCausalAudit(warm,N131.NativeBinder),
      "R2_INDEPENDENT_EXACT_SYMBOLIC":C.IndependentAuditedSymbolic(warm_sym),
      "R1_FROZEN_NUMERIC":R132.NumericBoundedRepair(N131.NativeBinder(warm)),
      "R1_INDEPENDENT_EXACT_SYMBOLIC":RC132.IndependentSymbolicRepair(C131.ExactPermutationSymbolic(warm_sym)),
      "LEGACY_WSP131_NUMERIC":None,
      "OPTIMIZED_FIXED_SYMBOLIC":C131.ExactPermutationSymbolic(warm_sym),
      "FULLY_FITTED_CART":C131.FullyFitCART(),
      "NO_UPDATE":C131.NoUpdate()
    }
    models["LEGACY_WSP131_NUMERIC"]=models["R1_FROZEN_NUMERIC"].original
    original_symbolic=models["R1_INDEPENDENT_EXACT_SYMBOLIC"].original
    fixed_schedule=C131.FixedSourceBlindSchedule(models["OPTIMIZED_FIXED_SYMBOLIC"])
    r2=models["R2_ACTIVE_NUMERIC"]
    r2strong=models["R2_INDEPENDENT_EXACT_SYMBOLIC"]
    r1=models["LEGACY_WSP131_NUMERIC"]
    score=_scores()
    worlds={mode:0 for mode in MODES}
    receipts=[]
    before_after=[]
    r2_survivors=[]
    for seed in (*range(169000,169064),*range(170000,170032)):
        v=S.world(seed)
        possible2=set(v.legal)
        possible1=set(v.legal)
        possible_strong=set(v.legal)
        used_fixed=set()
        costs={arm:S.Custodian(v) for arm in ARMS}
        for step in range(32):
            action2=r2.choose(v,possible2)
            actionstrong=r2strong.choose(v,possible_strong)
            action1=r1.choose(v,possible1)
            actionfix=fixed_schedule.choose(v,used_fixed)
            if (action2 not in possible2 or action2!=actionstrong or
                    actionstrong not in possible_strong or
                    action1 not in possible1 or actionfix not in v.legal or
                    v.input(actionfix) in used_fixed):
                raise AssertionError("WSP133_NUMERIC_SYMBOLIC_ACTIVE_ACTION_NONPARITY")
            possible2.remove(action2)
            possible_strong.remove(actionstrong)
            possible1.remove(action1)
            used_fixed.add(v.input(actionfix))
            for arm in ARMS:
                action=(actionfix if arm=="OPTIMIZED_FIXED_SYMBOLIC" else
                        action1 if arm in ("R1_FROZEN_NUMERIC",
                                          "R1_INDEPENDENT_EXACT_SYMBOLIC",
                                          "LEGACY_WSP131_NUMERIC") else action2)
                e=costs[arm].query(action)
                if arm=="R2_ACTIVE_NUMERIC":r2.observe(v,e)
                elif arm=="R2_INDEPENDENT_EXACT_SYMBOLIC":r2strong.observe(v,e)
                elif arm=="LEGACY_WSP131_NUMERIC":r1.observe(v,e)
                elif arm=="R1_INDEPENDENT_EXACT_SYMBOLIC":original_symbolic.observe(v,e)
                elif arm=="OPTIMIZED_FIXED_SYMBOLIC":models[arm].observe(v,e)
                elif arm=="FULLY_FITTED_CART":models[arm].observe(v,e)
        if r2.choose(v,possible2) is not None or r1.choose(v,possible1) is not None:
            raise AssertionError("WSP133_PAID_ACTION_BUDGET_OVERFLOW")
        models["R1_FROZEN_NUMERIC"].fit(v)
        models["R1_INDEPENDENT_EXACT_SYMBOLIC"].fit(v)
        if (r2.count(v)!=r2strong.count(v) or
                models["R1_FROZEN_NUMERIC"].counts(v)!=
                models["R1_INDEPENDENT_EXACT_SYMBOLIC"].counts(v)):
            raise AssertionError("WSP133_FULL_STRONG_HYPOTHESES_NONPARITY")
        if len({costs[arm].receipt for arm in ("R2_ACTIVE_NUMERIC",
                "R2_INDEPENDENT_EXACT_SYMBOLIC","FULLY_FITTED_CART","NO_UPDATE")})!=1:
            raise AssertionError("WSP133_R2_EQUAL_SOURCE_TRANSCRIPT_DRIFT")
        if len({costs[arm].receipt for arm in ("R1_FROZEN_NUMERIC",
                "R1_INDEPENDENT_EXACT_SYMBOLIC","LEGACY_WSP131_NUMERIC")})!=1:
            raise AssertionError("WSP133_R1_EQUAL_SOURCE_TRANSCRIPT_DRIFT")
        world={}
        outputs={}
        for arm in ARMS:
            c=costs[arm]
            if len(c.events)!=32 or len(tuple(c.held()))!=224:
                raise AssertionError("WSP133_WRONG_INTERVENTION_BUDGET")
            if arm=="LEGACY_WSP131_NUMERIC":
                model=r1
            else:model=models[arm]
            outputs[arm]={s:model.infer(v,s) for s,x in c.held()}
            world[arm]=c.score_once(outputs[arm])
            _sum(score[world[arm]["mode"]][arm],world[arm])
        if outputs["R2_ACTIVE_NUMERIC"]!=outputs["R2_INDEPENDENT_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP133_R2_INDEPENDENT_SYMBOLIC_PREDICTIONS_DIFFER")
        if outputs["R1_FROZEN_NUMERIC"]!=outputs["R1_INDEPENDENT_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP133_R1_INDEPENDENT_SYMBOLIC_PREDICTIONS_DIFFER")
        mode=world["R2_ACTIVE_NUMERIC"]["mode"]
        worlds[mode]+=1
        if mode=="known":
            before_after.append((world["R2_ACTIVE_NUMERIC"]["correct"],
                                 world["R1_FROZEN_NUMERIC"]["correct"]))
        r2_survivors.append([seed,mode,r2.count(v)])
        receipts.append([seed,mode,
            costs["R2_ACTIVE_NUMERIC"].receipt,
            costs["R1_FROZEN_NUMERIC"].receipt,
            costs["OPTIMIZED_FIXED_SYMBOLIC"].receipt,
            [[world[arm][k] for k in FIELDS] for arm in ARMS],
            r2.count(v)])
    if worlds!={"known":64,"shear":32}:raise AssertionError("WSP133_WRONG_WORLD_COUNTS")
    if warm.snapshot()!=warm_snapshot:raise AssertionError("WSP133_WARM_PRIOR_MUTATED")
    snap=r2.snapshot()
    cold=N.ActiveCausalAudit.restore(warm,N131.NativeBinder,snap,S.world)
    if cold.snapshot()!=snap:raise AssertionError("WSP133_COLD_WEIGHT_REPLAY_NOT_BITWISE")
    for seed in (*range(169000,169064),*range(170000,170032)):
        v=S.world(seed)
        for subject,x in v.records:
            if r2.infer(v,subject)!=cold.infer(v,subject):
                raise AssertionError("WSP133_CONSEQUENCE_MEMORY_LOST")
    transfer={arm:{k:0 for k in FIELDS} for arm in ARMS}
    transfer_records=[]
    for seed in range(171000,171016):
        v=S.world(seed)
        row={}
        for arm in ARMS:
            c=S.Custodian(v)
            if c.budget or c.events or v.legal:
                raise AssertionError("WSP133_TRANSFER_SOURCE_NOT_ZERO")
            model=models[arm]
            row[arm]=c.score_once({s:model.infer(v,s) for s,x in c.held()})
            _sum(transfer[arm],row[arm])
        if row["R2_ACTIVE_NUMERIC"]!=row["R2_INDEPENDENT_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP133_ZERO_SOURCE_TRANSFER_SYMBOLIC_NONPARITY")
        transfer_records.append([v.law_id,[[row[arm][k] for k in FIELDS] for arm in ARMS]])
    for law in S.S._origins():
        view=S.S.warm_world(law)
        if any(warm.infer(view,view.subject(x))!=old_truths[law][x]
               for x in range(256)):
            raise AssertionError("WSP133_OLD_CAUSAL_WEIGHTS_DAMAGED")
    if warm.snapshot()!=warm_snapshot:
        raise AssertionError("WSP133_PARENT_KNOWLEDGE_MUTATED_AT_END")
    known=score["known"]["R2_ACTIVE_NUMERIC"]
    negative=score["shear"]["R2_ACTIVE_NUMERIC"]
    r1known=score["known"]["R1_FROZEN_NUMERIC"]
    r1shear=score["shear"]["R1_FROZEN_NUMERIC"]
    transfer_native=transfer["R2_ACTIVE_NUMERIC"]
    known_pct=100*known["correct"]/14336
    shear_pct=100*negative["correct"]/7168
    wrong_pct=100*negative["wrong_confident"]/7168
    r1_known_pct=100*r1known["correct"]/14336
    gain=known_pct-r1_known_pct
    gate=(known_pct>=95 and known["wrong_confident"]==0 and
          wrong_pct<=1 and shear_pct>=25 and gain>=20 and
          negative["wrong_confident"]<=r1shear["wrong_confident"] and
          transfer_native["correct"]==4096 and
          transfer_native["abstained"]==0 and
          transfer_native["wrong_confident"]==0)
    status=("DEVELOPMENT_REPAIR_R2_SUPPORTED_WITHIN_SUPPLIED_PERMUTATION_PLUS_SHEAR"
            if gate else "DEVELOPMENT_REPAIR_R2_NO_GO")
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {
      "schema":"wsp133.bounded-r2-original-development.v1",
      "status":status,"scientific_pass":False,"native_admission":False,
      "original_first_use":False,"source_safe_public_synthetic_only":True,
      "repair_attempt":2,"repair_attempt_max":3,
      "wsp131_original_development":"NO_GO_240_CONFIDENT_SHEAR_ERRORS",
      "wsp132_r1_frozen":"NO_GO_52_6995_PERCENT_KNOWN_COVERAGE",
      "warm_paid_actions_per_arm":8192,
      "source_target_worlds":worlds,
      "source_paid_actions_per_arm":3072,
      "source_paid_actions_per_world_per_arm":32,
      "held_per_source_world":224,
      "world_scores":score,
      "r2_known_correct_percent":known_pct,
      "r2_known_wrong_confident":known["wrong_confident"],
      "r2_unfamiliar_correct_percent":shear_pct,
      "r2_unfamiliar_wrong_confident_percent":wrong_pct,
      "r1_same_source_known_correct_percent":r1_known_pct,
      "r1_same_source_unfamiliar_correct_percent":100*r1shear["correct"]/7168,
      "r2_minus_r1_known_gain_pp":gain,
      "gates_pass":gate,
      "independent_exact_symbolic_action_and_decision_parity":True,
      "transfer_relabel":transfer,
      "original_warm_weights_unchanged":True,
      "cold_replay_all_worlds":True,
      "paired_R2_R1_known_bootstrap":_bootstrap(before_after),
      "source_warm_receipt_sha256":warm_sha,
      "source_transcript_sha256":S.digest(receipts),
      "zero_source_transfer_sha256":S.digest(transfer_records),
      "learned_state_sha256":S.digest(snap),
      "source_hypothesis_support_sha256":S.digest(r2_survivors),
      "resource":{"wall_seconds_dev":round(time.perf_counter()-t0,3),
                  "process_cpu_seconds_dev":round(time.process_time()-p0,3),
                  "tracemalloc_peak_bytes":peak,
                  "whole_process_energy":"UNQUALIFIED",
                  "independent_fully_trained_deep_reference":"UNQUALIFIED"}
    }

if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--engineering",required=True,action="store_true")
    args.parse_args()
    print("WSP133_ENGINEERING_JSON="+S.canon(run_engineering()))
