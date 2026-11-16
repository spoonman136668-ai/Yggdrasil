"""WSP132 bounded repair R1: original WSP131 outcome retained, edit isolated.

Two cohorts: exposed WSP131 only development diagnostic; fresh preregistered
public synthetic source only prospective DEVELOPMENT confirmation (not new
scientific original first-use). Strong independent exact symbolic controls see
identical 32 paid effects, and any 'zero wrong by abstaining always' fails
the frozen useful-coverage/retention thresholds.
"""
from __future__ import annotations
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import json
import sys
import time
import tracemalloc

import source as S
import repair as R
import controls as RC

ROOT=Path(__file__).resolve().parents[1]
def _load(name,rel):
    sp=spec_from_file_location(name,ROOT/rel)
    m=module_from_spec(sp)
    sys.modules[name]=m
    sp.loader.exec_module(m)
    return m
N130=_load("_wsp130_numerical_wsp132","WSP-130/learner.py")
C130=_load("_wsp130_strong_wsp132","WSP-130/controls.py")
N131=_load("_wsp131_numerical_wsp132","WSP-131/binder.py")
C131=_load("_wsp131_strong_wsp132","WSP-131/controls.py")

ARMS=("REPAIRED_NUMERIC","REPAIRED_INDEPENDENT_SYMBOLIC",
      "ORIGINAL_NUMERIC","ORIGINAL_EXACT_SYMBOLIC",
      "FIXED_OPTIMIZED_SYMBOLIC","FULLY_FITTED_CART","NO_UPDATE")
KINDS=("known","shear")
COHORTS=("EXPOSED_DIAGNOSTIC","PROSPECTIVE_SYNTHETIC")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def _counter():
    return {kind:{arm:{f:0 for f in FIELDS} for arm in ARMS} for kind in KINDS}
def _add(total,metrics):
    for k in FIELDS:total[k]+=metrics[k]

def _warm():
    origin_native=N130.DirectInducer()
    origin_symbolic=C130.ExactSymbolic()
    seen=[]
    signatures={}
    for law in S.S._origins():
        view=S.S.warm_world(law)
        c1=S.S.warm_custodian(view)
        c2=S.S.warm_custodian(view)
        unspent=set(view.legal)
        for _ in range(128):
            action=origin_native.choose(view,unspent)
            if action not in unspent:
                raise AssertionError("WSP132_WARM_PRIOR_EVIDENCE_DRIFT")
            unspent.remove(action)
            a,b=c1.query(action),c2.query(action)
            origin_native.observe(view,a)
            origin_symbolic.observe(view,b)
        if c1.receipt!=c2.receipt:
            raise AssertionError("WSP132_PRIOR_SOURCE_TRANSCRIPT_NOT_MATCHED")
        prior=tuple(origin_native.infer(view,view.subject(x))
                    for x in range(256))
        symbolic=tuple(origin_symbolic.infer(view,view.subject(x))
                       for x in range(256))
        if prior!=symbolic or any(bit not in (0,1) for bit in prior):
            raise AssertionError("WSP132_PRIOR_INCOMPLETELY_LEARNED")
        signatures[law]=prior
        seen.append([law,c1.receipt,S.digest(prior)])
    return origin_native,origin_symbolic,S.digest(seen),signatures

def _measure_one_cohort(name,oldN,oldC):
    exposed=name=="EXPOSED_DIAGNOSTIC"
    source=S.S if exposed else S
    native=N131.NativeBinder(oldN)
    original_exact=C131.ExactPermutationSymbolic(oldC)
    fixed=C131.ExactPermutationSymbolic(oldC)
    fixed_plan=C131.FixedSourceBlindSchedule(fixed)
    cart=C131.FullyFitCART()
    quiet=C131.NoUpdate()
    amended=R.NumericBoundedRepair(native)
    independent=RC.IndependentSymbolicRepair(original_exact)
    scorers=_counter()
    receipts=[]
    counts={kind:{"worlds":0,"old_wrong_worlds":0,
                  "repaired_wrong_worlds":0,"repaired_abstained_worlds":0,
                  "repaired_zero_compatible":0} for kind in KINDS}
    for seed in (*range(160000,160064),*range(161000,161032)) if exposed else (
            *range(165000,165064),*range(166000,166032)):
        v=source.world(seed)
        available=set(v.legal)
        used_fixed=set()
        cost={arm:source.Custodian(v) for arm in ARMS}
        for _ in range(32):
            chosen=native.choose(v,available)
            independent_action=fixed_plan.choose(v,used_fixed)
            if chosen not in available or independent_action not in v.legal:
                raise AssertionError("WSP132_BAD_ACTION_SCHEDULE")
            available.remove(chosen)
            if v.input(independent_action) in used_fixed:
                raise AssertionError("WSP132_FIXED_REPEATED_ACTION")
            used_fixed.add(v.input(independent_action))
            for arm in ARMS:
                action=independent_action if arm=="FIXED_OPTIMIZED_SYMBOLIC" else chosen
                e=cost[arm].query(action)
                if arm=="ORIGINAL_NUMERIC":native.observe(v,e)
                elif arm=="ORIGINAL_EXACT_SYMBOLIC":original_exact.observe(v,e)
                elif arm=="FULLY_FITTED_CART":cart.observe(v,e)
                elif arm=="FIXED_OPTIMIZED_SYMBOLIC":fixed.observe(v,e)
                # New repairs inspect only the original fully learned
                # authenticated evidence; never access source labels/actions.
        if native.choose(v,available) is not None:
            raise AssertionError("WSP132_EXTRA_PAID_ACTION")
        amended.fit(v)
        independent.fit(v)
        repairs=amended.counts(v)
        if repairs!=independent.counts(v):
            raise AssertionError("WSP132_CHALLENGER_SET_DISAGREES_WITH_STRONG_CONTROL")
        rcpt={cost[a].receipt for a in ARMS if a!="FIXED_OPTIMIZED_SYMBOLIC"}
        if len(rcpt)!=1 or any(len(cost[a].events)!=32 for a in ARMS):
            raise AssertionError("WSP132_PAID_ACTION_MATCHED_RECEIPTS_FAILED")
        pred={}
        pred["REPAIRED_NUMERIC"]={s:amended.infer(v,s) for s,x in cost["REPAIRED_NUMERIC"].held()}
        pred["REPAIRED_INDEPENDENT_SYMBOLIC"]={s:independent.infer(v,s) for s,x in cost["REPAIRED_INDEPENDENT_SYMBOLIC"].held()}
        pred["ORIGINAL_NUMERIC"]={s:native.infer(v,s) for s,x in cost["ORIGINAL_NUMERIC"].held()}
        pred["ORIGINAL_EXACT_SYMBOLIC"]={s:original_exact.infer(v,s) for s,x in cost["ORIGINAL_EXACT_SYMBOLIC"].held()}
        pred["FIXED_OPTIMIZED_SYMBOLIC"]={s:fixed.infer(v,s) for s,x in cost["FIXED_OPTIMIZED_SYMBOLIC"].held()}
        pred["FULLY_FITTED_CART"]={s:cart.infer(v,s) for s,x in cost["FULLY_FITTED_CART"].held()}
        pred["NO_UPDATE"]={s:quiet.infer(v,s) for s,x in cost["NO_UPDATE"].held()}
        if pred["REPAIRED_NUMERIC"]!=pred["REPAIRED_INDEPENDENT_SYMBOLIC"]:
            raise AssertionError("WSP132_REPAIR_INDEPENDENT_SYMBOLIC_DECISION_NONPARITY")
        if pred["ORIGINAL_NUMERIC"]!=pred["ORIGINAL_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP132_ORIGINAL_SAME_ACTION_SYMBOLIC_NONPARITY")
        scores={}
        for arm in ARMS:
            cust=cost[arm]
            result=cust.score_once(pred[arm]) if not exposed else cust.score_once({
                stage:pred[arm] for stage in (0,4,8,16,32)})["stages"][32]
            scores[arm]=result
        kind="known" if seed in (
            range(160000,160064) if exposed else range(165000,165064)) else "shear"
        counts[kind]["worlds"]+=1
        for arm in ARMS:_add(scorers[kind][arm],scores[arm])
        counts[kind]["old_wrong_worlds"]+=int(scores["ORIGINAL_NUMERIC"]["wrong_confident"]>0)
        counts[kind]["repaired_wrong_worlds"]+=int(scores["REPAIRED_NUMERIC"]["wrong_confident"]>0)
        counts[kind]["repaired_abstained_worlds"]+=int(scores["REPAIRED_NUMERIC"]["abstained"]>0)
        counts[kind]["repaired_zero_compatible"]+=int(
            repairs["pure_compatible"]+repairs["shear_compatible"]==0)
        receipts.append([seed,kind,cost["ORIGINAL_NUMERIC"].receipt,
                         cost["FIXED_OPTIMIZED_SYMBOLIC"].receipt,
                         repairs,
                         [[scores[arm][f] for f in FIELDS] for arm in ARMS]])
    snap_native=amended.snapshot()
    cold=R.NumericBoundedRepair.restore(oldN,snap_native,source.world,N131.NativeBinder)
    if cold.snapshot()!=snap_native:
        raise AssertionError("WSP132_NUMERIC_REPAIR_COLD_REPLAY_FAILED")
    for seed in (*range(160000,160064),*range(161000,161032)) if exposed else (
            *range(165000,165064),*range(166000,166032)):
        view=source.world(seed)
        for subject,x in view.records:
            if cold.infer(view,subject)!=amended.infer(view,subject):
                raise AssertionError("WSP132_NUMERIC_REPAIR_COLD_RETENTION_LOSS")
    transfer={arm:{f:0 for f in FIELDS} for arm in ARMS}
    transfer_rows=[]
    if not exposed:
        for seed in range(167000,167016):
            v=S.world(seed)
            row={}
            for arm in ARMS:
                c=S.Custodian(v)
                if c.budget or v.legal or c.events:
                    raise AssertionError("WSP132_TRANSFER_SOURCE_ZERO_INVARIANT")
                model={"REPAIRED_NUMERIC":amended,
                       "REPAIRED_INDEPENDENT_SYMBOLIC":independent,
                       "ORIGINAL_NUMERIC":native,
                       "ORIGINAL_EXACT_SYMBOLIC":original_exact,
                       "FIXED_OPTIMIZED_SYMBOLIC":fixed,
                       "FULLY_FITTED_CART":cart,
                       "NO_UPDATE":quiet}[arm]
                row[arm]=c.score_once({s:model.infer(v,s) for s,x in c.held()})
                _add(transfer[arm],row[arm])
            if row["REPAIRED_NUMERIC"]!=row["REPAIRED_INDEPENDENT_SYMBOLIC"]:
                raise AssertionError("WSP132_ZERO_SOURCE_SYMBOLIC_NONPARITY")
            transfer_rows.append([v.law_id,
                [[row[arm][f] for f in FIELDS] for arm in ARMS]])
    return {"cohort":name,"scores":scorers,"counts":counts,
            "cold_replay":True,"repaired_symbolic_parity":True,
            "source_sha256":S.digest(receipts),
            "numeric_snapshot_sha256":S.digest(snap_native),
            "zero_source_transfer":transfer,"transfer_sha256":S.digest(transfer_rows)}

def run_engineering():
    beginning=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    if S.ALLOWED&S.DENIED:
        raise PermissionError("WSP132_ORIGINAL_FIRST_USE_SOURCE_OVERLAP")
    native,control,warm_sha,old_signatures=_warm()
    frozen=native.snapshot()
    original_source=_measure_one_cohort("EXPOSED_DIAGNOSTIC",native,control)
    if frozen!=native.snapshot():
        raise AssertionError("WSP132_PARENT_PRIOR_MUTATED_AFTER_EXPOSED")
    # New genuinely different random permutation/shear mapping and opaque
    # source/action IDs. This is still only PUBLIC SYNTHETIC validation.
    prospect=_measure_one_cohort("PROSPECTIVE_SYNTHETIC",native,control)
    if frozen!=native.snapshot():
        raise AssertionError("WSP132_PARENT_PRIOR_MUTATED_AFTER_NEW_SOURCE")
    for law in S.S._origins():
        old=S.S.warm_world(law)
        if any(native.infer(old,old.subject(x))!=old_signatures[law][x]
               for x in range(256)):
            raise AssertionError("WSP132_WARM_KNOWLEDGE_INTERFERENCE")
    known=prospect["scores"]["known"]["REPAIRED_NUMERIC"]
    negative=prospect["scores"]["shear"]["REPAIRED_NUMERIC"]
    baseknown=prospect["scores"]["known"]["ORIGINAL_NUMERIC"]
    basenegative=prospect["scores"]["shear"]["ORIGINAL_NUMERIC"]
    transfer=prospect["zero_source_transfer"]["REPAIRED_NUMERIC"]
    known_pct=100*known["correct"]/14336
    wrong_pct=100*negative["wrong_confident"]/7168
    shear_pct=100*negative["correct"]/7168
    old_negative_pct=100*basenegative["wrong_confident"]/7168
    criteria=(known_pct>=95 and known["wrong_confident"]==0 and
              wrong_pct<=1 and shear_pct>=25 and
              transfer["correct"]==4096 and
              transfer["abstained"]==0 and transfer["wrong_confident"]==0)
    # Frozen original development failure and all old result digests are kept
    # separate from this prospective score. Never reinterpret original as PASS.
    status=("DEVELOPMENT_REPAIR_SUPPORTED_ONLY" if criteria else
            "DEVELOPMENT_REPAIR_PARTIAL" if
            wrong_pct<old_negative_pct and known_pct>=95 else
            "DEVELOPMENT_REPAIR_NO_GO")
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"schema":"wsp132.bounded-repair-r1-result.v1",
            "status":status,"scientific_pass":False,
            "native_admission":False,"original_first_use":False,
            "original_wsp131_frozen_status":"DEVELOPMENT_NO_GO",
            "repair_attempt":1,"max_algorithmic_edits":3,
            "warm_actions_per_arm":8192,
            "each_target_world_paid_actions_per_arm":32,
            "each_cohort_paid_actions_per_arm":3072,
            "source_safe_only":True,
            "exposed_diagnostic":original_source,
            "new_synthetic_prospective":prospect,
            "source_warm_receipt_sha256":warm_sha,
            "known_correct_percent":known_pct,
            "known_wrong_confident":known["wrong_confident"],
            "negative_correct_percent":shear_pct,
            "negative_wrong_confident_percent":wrong_pct,
            "baseline_negative_wrong_confident_percent":old_negative_pct,
            "baseline_new_known_correct_percent":100*baseknown["correct"]/14336,
            "repaired_new_transfer_correct":transfer["correct"],
            "repair_gate_met":criteria,
            "independent_repaired_symbolic_prediction_tie":True,
            "warm_original_weights_immutable":True,
            "cold_replay_both_cohorts":True,
            "resource":{"wall_seconds_dev":round(time.perf_counter()-beginning,3),
                        "process_cpu_seconds_dev":round(time.process_time()-cpu,3),
                        "tracemalloc_peak_bytes":peak,
                        "matched_whole_process_energy":"UNQUALIFIED",
                        "strong_conventional_neural_baseline":"UNQUALIFIED"}}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering",action="store_true",required=True)
    parser.parse_args()
    print("WSP132_ENGINEERING_JSON="+S.canon(run_engineering()))
