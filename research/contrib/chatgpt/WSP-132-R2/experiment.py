"""WSP132-R2 active challenger audit: independently frozen public development.

R1 exposed worlds are diagnostic replay only; new disjoint synthetic worlds
are prospectively preregistered but not scientific original first-use.
R2 changes which 32 consequences it buys; no extra queries, no new physics.
"""
from __future__ import annotations
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import argparse,json,random,sys,time,tracemalloc

import source as S
import binder as N
import controls as C

ROOT=Path(__file__).resolve().parents[1]
def _load(module,path):
    sp=spec_from_file_location(module,ROOT/path)
    z=module_from_spec(sp);sys.modules[module]=z;sp.loader.exec_module(z)
    return z

N130=_load("_wsp130_num_wsp132r2","WSP-130/learner.py")
C130=_load("_wsp130_sym_wsp132r2","WSP-130/controls.py")
N131=_load("_wsp131_num_wsp132r2","WSP-131/binder.py")
C131=_load("_wsp131_sym_wsp132r2","WSP-131/controls.py")
R1=_load("_wsp132_r1_repair_for_r2","WSP-132/repair.py")
ARMS=("R2_ACTIVE_NUMERIC","R2_SAME_ACTION_SYMBOLIC","R2_FIXED_SYMBOLIC",
      "R1_PASSIVE","ORIGINAL_NUMERIC","FULLY_FITTED_CART","NO_UPDATE")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")
COHORTS=("EXPOSED_DIAGNOSTIC","NEW_PROSPECTIVE_SYNTHETIC")

def _warm():
    n=N130.DirectInducer()
    s=C130.ExactSymbolic()
    proof=[]
    for law in S.S._origins():
        v=S.S.warm_world(law)
        a,b=S.S.warm_custodian(v),S.S.warm_custodian(v)
        used=set()
        for step in range(128):
            action=n.choose(v,v.legal-used)
            if action is None or action in used:raise AssertionError("R2_WARM_ACTION_DRIFT")
            used.add(action)
            n.observe(v,a.query(action));s.observe(v,b.query(action))
        if a.receipt!=b.receipt:raise AssertionError("R2_WARM_SYMBOLIC_PARITY")
        for _,x in v.records:
            if n.infer(v,v.subject(x))!=s.infer(v,v.subject(x)):
                raise AssertionError("R2_WARM_KNOWLEDGE_DISAGREEMENT")
        proof.append([law,a.receipt])
    return n,s,S.digest(proof)

def _count():
    return {kind:{arm:{k:0 for k in FIELDS} for arm in ARMS}
            for kind in ("known","shear")}
def _sum(into,one):
    for field in FIELDS:into[field]+=one[field]

def _one_cohort(cohort,oldN,oldS):
    exposed=cohort=="EXPOSED_DIAGNOSTIC"
    source=S.OLD if exposed else S
    n=N.ActiveChallengerRepair(oldN)
    symbolic=C.ExactChallengerSymbolic(oldS)
    fixed=C.ExactChallengerSymbolic(oldS)
    schedule=C.FixedChallengerSchedule(fixed)
    original=N131.NativeBinder(oldN)
    passive=R1.NumericBoundedRepair(original)
    cart=C131.FullyFitCART()
    quiet=C.NoUpdate()
    models=dict(zip(ARMS,(n,symbolic,fixed,passive,original,cart,quiet)))
    totals=_count()
    worlds={"known":0,"shear":0}
    confident_right_shear=0
    scores=[]
    source_receipts=[]
    target_seeds=(*range(165000,165064),*range(166000,166032)) if exposed else (
        *range(169000,169064),*range(170000,170032))
    for seed in target_seeds:
        v=source.world(seed)
        a_set=set(v.legal)
        o_set=set(v.legal)
        fixed_used=set()
        cust={arm:source.Custodian(v) for arm in ARMS}
        for step in range(32):
            a=n.choose(v,a_set)
            o=original.choose(v,o_set)
            f=schedule.choose(v,fixed_used)
            if (a not in a_set or o not in o_set or f not in v.legal or
                v.input(f) in fixed_used):
                raise AssertionError("WSP132R2_UNEQUAL_SOURCE_ACTION_BUDGET")
            a_set.remove(a);o_set.remove(o);fixed_used.add(v.input(f))
            for arm in ARMS:
                action=f if arm=="R2_FIXED_SYMBOLIC" else (
                       o if arm in ("ORIGINAL_NUMERIC","R1_PASSIVE") else a)
                e=cust[arm].query(action)
                if arm=="R2_ACTIVE_NUMERIC":n.observe(v,e)
                elif arm=="R2_SAME_ACTION_SYMBOLIC":symbolic.observe(v,e)
                elif arm=="R2_FIXED_SYMBOLIC":fixed.observe(v,e)
                elif arm=="ORIGINAL_NUMERIC":original.observe(v,e)
                elif arm=="FULLY_FITTED_CART":cart.observe(v,e)
        if n.choose(v,a_set) is not None or original.choose(v,o_set) is not None:
            raise AssertionError("WSP132R2_MORE_THAN_32_SOURCE_CALLS")
        passive.fit(v)
        if (cust["R2_ACTIVE_NUMERIC"].receipt!=cust["R2_SAME_ACTION_SYMBOLIC"].receipt or
            cust["R2_ACTIVE_NUMERIC"].receipt!=cust["FULLY_FITTED_CART"].receipt or
            cust["ORIGINAL_NUMERIC"].receipt!=cust["R1_PASSIVE"].receipt):
            raise AssertionError("WSP132R2_SOURCE_TRANSCRIPT_MISMATCH")
        measured={}
        predictions={}
        for arm in ARMS:
            held=tuple(cust[arm].held())
            if len(held)!=224:raise AssertionError("WSP132R2_HELD_SIZE_DRIFT")
            preds={subject:models[arm].infer(v,subject) for subject,x in held}
            z=cust[arm].score_once(preds)
            measured[arm]=z
            predictions[arm]=preds
            _sum(totals[z.get("kind",z.get("mode"))][arm],z)
        if predictions["R2_ACTIVE_NUMERIC"]!=predictions["R2_SAME_ACTION_SYMBOLIC"]:
            raise AssertionError("WSP132R2_EXACT_SYMBOLIC_MISMATCH")
        if n.compatible(v)!=symbolic.remaining(v):
            raise AssertionError("WSP132R2_SURVIVING_RULE_COUNT_MISMATCH")
        kind=measured["R2_ACTIVE_NUMERIC"].get("kind",measured["R2_ACTIVE_NUMERIC"].get("mode"))
        worlds[kind]+=1
        if kind=="shear" and measured["R2_ACTIVE_NUMERIC"]["correct"]>0:
            confident_right_shear+=1
        scores.append([v.law_id,kind,n.compatible(v),
            [tuple(measured[arm][k] for k in FIELDS) for arm in ARMS]])
        source_receipts.append([seed,cust["R2_ACTIVE_NUMERIC"].receipt,
                                cust["ORIGINAL_NUMERIC"].receipt,
                                cust["R2_FIXED_SYMBOLIC"].receipt])
    if worlds!={"known":64,"shear":32}:raise AssertionError("WSP132R2_WORLD_COUNTS_DRIFT")
    cold=N.ActiveChallengerRepair.restore(oldN,n.snapshot(),source.world)
    if cold.snapshot()!=n.snapshot():raise AssertionError("WSP132R2_COLD_SNAPSHOT_MISMATCH")
    for seed in target_seeds:
        v=source.world(seed)
        for subject,x in v.records:
            if n.infer(v,subject)!=cold.infer(v,subject):
                raise AssertionError("WSP132R2_EARLIER_CAUSAL_MEMORY_LOST")
    transfer={arm:{k:0 for k in FIELDS} for arm in ARMS}
    transfer_scores=[]
    if not exposed:
        for seed in range(171000,171016):
            v=S.world(seed)
            per={}
            for arm in ARMS:
                c=S.Custodian(v)
                if c.budget or v.legal:raise AssertionError("R2_TRANSFER_SOURCE_BUDGET_NOT_ZERO")
                pred={subject:models[arm].infer(v,subject)
                      for subject,x in c.held()}
                per[arm]=c.score_once(pred)
                _sum(transfer[arm],per[arm])
            if per["R2_ACTIVE_NUMERIC"]!=per["R2_SAME_ACTION_SYMBOLIC"]:
                raise AssertionError("R2_TRANSFER_SYMBOLIC_NONPARITY")
            transfer_scores.append([v.law_id,
                [tuple(per[arm][k] for k in FIELDS) for arm in ARMS]])
    return {"cohort":cohort,"scores":totals,"worlds":worlds,
            "shear_worlds_with_positive_coverage":confident_right_shear,
            "score_sha256":S.digest(scores),
            "source_transcript_sha256":S.digest(source_receipts),
            "cold_replay":True,"transfer":transfer,
            "transfer_sha256":S.digest(transfer_scores),
            "snapshot_sha256":S.digest(n.snapshot()),
            "same_evidence_exact_symbolic_tie":True}

def run_engineering():
    start=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    if S.NEW&S.PROTECTED:raise PermissionError("WSP132R2_PROTECTED_SOURCE_COLLISION")
    oldN,oldS,warm_sha=_warm()
    original_frozen=oldN.snapshot()
    exposed=_one_cohort("EXPOSED_DIAGNOSTIC",oldN,oldS)
    prospective=_one_cohort("NEW_PROSPECTIVE_SYNTHETIC",oldN,oldS)
    if oldN.snapshot()!=original_frozen:
        raise AssertionError("WSP132R2_INHERITED_WARM_WEIGHTS_CHANGED")
    known=prospective["scores"]["known"]["R2_ACTIVE_NUMERIC"]
    negative=prospective["scores"]["shear"]["R2_ACTIVE_NUMERIC"]
    fixed=prospective["scores"]["known"]["R2_FIXED_SYMBOLIC"]
    transfer=prospective["transfer"]["R2_ACTIVE_NUMERIC"]
    percent=lambda numerator,denominator:100*numerator/denominator
    positive_ok=(percent(known["correct"],14336)>=95 and
                 percent(known["wrong_confident"],14336)<=1 and
                 transfer["correct"]==4096 and transfer["wrong_confident"]==0)
    negative_ok=(percent(negative["wrong_confident"],7168)<=1 and
                 percent(negative["correct"],7168)>=25 and
                 prospective["shear_worlds_with_positive_coverage"]>=20)
    controls_ok=(prospective["same_evidence_exact_symbolic_tie"] and
                 percent(known["correct"]-fixed["correct"],14336)>=-2)
    status=("DEVELOPMENT_R2_REPAIR_SUPPORTED_ON_PUBLIC_SYNTHETIC_ONLY"
            if positive_ok and negative_ok and controls_ok
            else "DEVELOPMENT_R2_REPAIR_PARTIAL"
            if negative["wrong_confident"]<240 and known["correct"]>0
            else "DEVELOPMENT_R2_REPAIR_NO_GO")
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {"schema":"wsp132.r2.bounded-active-repair.dev-result.v1",
      "status":status,"scientific_pass":False,"original_first_use":False,
      "native_admission":False,"algorithmic_repair_number":2,"repair_limit":3,
      "original_wsp131_frozen_negative":"DEVELOPMENT_NO_GO_UNCHANGED",
      "r1_frozen_negative":"DEVELOPMENT_REPAIR_NO_GO_UNCHANGED",
      "old_warm_model_retained":True,
      "source_warm_receipt_sha256":warm_sha,
      "paid_actions_per_target_world_per_arm":32,
      "each_cohort_target_paid_actions_per_arm":3072,
      "exposed_diagnostic":exposed,"new_prospective_synthetic":prospective,
      "positive_gate":positive_ok,"negative_gate":negative_ok,
      "strong_control_gate":controls_ok,
      "known_correct_percent":percent(known["correct"],14336),
      "negative_correct_percent":percent(negative["correct"],7168),
      "negative_wrong_confident_percent":percent(negative["wrong_confident"],7168),
      "fixed_correct_percent":percent(fixed["correct"],14336),
      "new_zero_source_transfer_correct":transfer["correct"],
      "resource":{"wall_seconds":round(time.perf_counter()-start,3),
                  "process_cpu_seconds":round(time.process_time()-cpu,3),
                  "tracemalloc_peak_bytes":peak,
                  "whole_process_energy":"UNQUALIFIED",
                  "science_conventional_strong_baseline":"UNQUALIFIED"}
     }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering",required=True,action="store_true")
    parser.parse_args()
    print("WSP132_R2_ENGINEERING_JSON="+S.canon(run_engineering()))
