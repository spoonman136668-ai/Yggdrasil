"""WSP130 source-safe original development comparison, fixed prereg budgets.

Discovery means constructing a high interaction mask from actual probes, not
inventing conjunction or GF2 algebra. Impossible withheld-point worlds are
separately scored; no scientific original first-use, promotion or model merge.
"""
from __future__ import annotations
import argparse
import random
import time
import tracemalloc

import source as S
import learner as N
import controls as C

ARMS=("DIRECT_NUMERIC","SAME_ACTION_EXACT_SYMBOLIC",
      "FIXED_EXACT_SYMBOLIC","SAFE_ABORT","STALE_PRIOR","NO_UPDATE")
MODES=("none","quartic","quintic","double","stealth")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def _models():
    return {"DIRECT_NUMERIC":N.DirectInducer("active"),
            "SAME_ACTION_EXACT_SYMBOLIC":C.ExactSymbolic(),
            "FIXED_EXACT_SYMBOLIC":C.ExactSymbolic(),
            "SAFE_ABORT":C.SafeAbort(),
            "STALE_PRIOR":C.StalePrior(),
            "NO_UPDATE":C.NoUpdate()}

def _scores():
    return {kind:{arm:{k:0 for k in FIELDS} for arm in ARMS} for kind in MODES}

def _add(totals,result):
    for field in FIELDS:
        totals[field]+=result[field]

def _fixed_action(view,used,n):
    if n<93: x=S.LOW[n]
    elif n<102: x=S.CORE[n-93]
    else: x=next(x for x in S.HASH_AUDIT if x not in used)
    return view.subject(x)

def _bootstrap(paired):
    rng=random.Random(130)
    n=len(paired)
    diff=[d-s for d,s in paired]
    samples=[]
    for _ in range(10000):
        samples.append(100*sum(diff[rng.randrange(n)]
                               for i in range(n))/(n*128))
    samples.sort()
    return {"seed":130,"resamples":10000,
            "low_95_percentile_pp":samples[250],
            "high_95_percentile_pp":samples[9749]}

def run_engineering():
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    tracemalloc.start()
    if S.ALLOWED&S.DENIED:
        raise PermissionError("WSP130_PROTECTED_FIRST_USE_OVERLAP")
    models=_models()
    totals=_scores()
    counts={mode:0 for mode in MODES}
    detection={mode:{"SINGLE":0,"NONE":0,"UNSUPPORTED":0}
               for mode in MODES}
    high_exact_masks=0
    false_high_masks=0
    strong_tie=True
    receipts=[]
    paired=[]
    confident_stealth_worlds=0
    for seed in (*range(154000,154128),*range(154500,154516)):
        view=S.world(seed)
        cust={arm:S.Custodian(view) for arm in ARMS}
        available=set(view.legal)
        used_fixed=set()
        fixed_available=set(view.legal)
        for step in range(128):
            direct_action=models["DIRECT_NUMERIC"].choose(view,available)
            fixed_action=_fixed_action(view,used_fixed,step)
            if (direct_action is None or direct_action not in available or
                    fixed_action not in fixed_available):
                raise AssertionError("WSP130_DUPLICATE_OR_BUDGET_MISMATCH")
            available.remove(direct_action)
            fixed_available.remove(fixed_action)
            used_fixed.add(view.input(fixed_action))
            for arm in ARMS:
                action=fixed_action if arm=="FIXED_EXACT_SYMBOLIC" else direct_action
                evidence=cust[arm].query(action)
                models[arm].observe(view,evidence)
        if models["DIRECT_NUMERIC"].choose(view,available) is not None:
            raise AssertionError("WSP130_MORE_THAN_128_ACTIONS")
        shared={cust[arm].receipt for arm in ARMS if arm!="FIXED_EXACT_SYMBOLIC"}
        if len(shared)!=1 or any(len(c.events)!=128 for c in cust.values()):
            raise AssertionError("WSP130_MATCHED_SOURCE_ACTIONS_FAILED")
        per={}
        predictions={}
        for arm in ARMS:
            held=tuple(cust[arm].held())
            if len(held)!=128:
                raise AssertionError("WSP130_WITHHELD_SIZE_DRIFT")
            predictions[arm]={s:models[arm].infer(view,s) for s,x in held}
            score=cust[arm].score_once(predictions[arm])
            _add(totals[score["kind"]][arm],score)
            per[arm]=score
        if predictions["DIRECT_NUMERIC"]!=predictions["SAME_ACTION_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP130_INDEPENDENT_STRONG_SYMBOLIC_PREDICTION_MISMATCH")
        kind=per["DIRECT_NUMERIC"]["kind"]
        counts[kind]+=1
        status=models["DIRECT_NUMERIC"].status(view)
        detection[kind][status]+=1
        if status!=models["SAME_ACTION_EXACT_SYMBOLIC"].status(view):
            raise AssertionError("WSP130_STRUCTURAL_STATUS_SYMBOLIC_NONPARITY")
        mask=models["DIRECT_NUMERIC"].support(view)
        if kind in ("quartic","quintic"):
            if mask==S._law(view.law_id)["high"][0]:
                high_exact_masks+=1
            paired.append((per["DIRECT_NUMERIC"]["correct"],
                           per["SAFE_ABORT"]["correct"]))
        elif kind=="none" and mask is not None:
            false_high_masks+=1
        if kind=="stealth" and per["DIRECT_NUMERIC"]["wrong_confident"]:
            confident_stealth_worlds+=1
        receipts.append([view.law_id,kind,
                         cust["DIRECT_NUMERIC"].receipt,
                         cust["FIXED_EXACT_SYMBOLIC"].receipt,
                         [tuple(per[arm][k] for k in FIELDS) for arm in ARMS],
                         status,mask])
    if (counts!={"none":32,"quartic":32,"quintic":32,"double":32,"stealth":16} or
            len(paired)!=64):
        raise AssertionError("WSP130_HIDDEN_WORLD_ACCOUNTING_DRIFT")
    direct=models["DIRECT_NUMERIC"]
    old_snapshot=direct.snapshot()
    cold=N.DirectInducer.restore(old_snapshot,S.world)
    if cold.snapshot()!=old_snapshot:
        raise AssertionError("WSP130_COLD_RESTORATION_FAILED")
    for seed in (*range(154000,154128),*range(154500,154516)):
        view=S.world(seed)
        for subject,x in view.records:
            if direct.infer(view,subject)!=cold.infer(view,subject):
                raise AssertionError("WSP130_LATE_LAW_INTERFERENCE")
    transfer={arm:{k:0 for k in FIELDS} for arm in ARMS}
    transfer_rows=[]
    for seed in range(155000,155032):
        view=S.world(seed)
        per={}
        for arm in ARMS:
            c=S.Custodian(view)
            if c.budget or view.legal or c.events:
                raise AssertionError("WSP130_TRANSFER_SOURCE_NOT_ZERO")
            predictions={subject:models[arm].infer(view,subject)
                         for subject,x in c.held()}
            result=c.score_once(predictions)
            _add(transfer[arm],result)
            per[arm]=result
        if any(per["DIRECT_NUMERIC"][k]!=per["SAME_ACTION_EXACT_SYMBOLIC"][k]
               for k in FIELDS):
            raise AssertionError("WSP130_TRANSFER_STRONG_SYMBOLIC_NONPARITY")
        transfer_rows.append([view.law_id,
                 [tuple(per[arm][k] for k in FIELDS) for arm in ARMS]])
    if direct.snapshot()!=old_snapshot:
        raise AssertionError("WSP130_ZERO_SOURCE_TRANSFER_MUTATED_WEIGHTS")
    changed_correct=sum(totals[mode]["DIRECT_NUMERIC"]["correct"]
                        for mode in ("quartic","quintic"))
    changed_wrong=sum(totals[mode]["DIRECT_NUMERIC"]["wrong_confident"]
                      for mode in ("quartic","quintic"))
    safe_correct=sum(totals[mode]["SAFE_ABORT"]["correct"]
                     for mode in ("quartic","quintic"))
    unchanged=totals["none"]["DIRECT_NUMERIC"]
    off=totals["double"]["DIRECT_NUMERIC"]
    stealth=totals["stealth"]["DIRECT_NUMERIC"]
    changed_rate=100*changed_correct/8192
    gain=100*(changed_correct-safe_correct)/8192
    unchanged_rate=100*unchanged["correct"]/4096
    positive_pass=(changed_rate>=95 and changed_wrong==0 and
                   high_exact_masks>=60 and gain>=25 and
                   unchanged_rate>=95 and unchanged["wrong_confident"]==0 and
                   false_high_masks==0)
    negative_pass=(off["wrong_confident"]==0 and
                   detection["double"]["UNSUPPORTED"]>=30 and
                   transfer["DIRECT_NUMERIC"]["correct"]==8192 and
                   transfer["DIRECT_NUMERIC"]["wrong_confident"]==0)
    if stealth["wrong_confident"]<1 or confident_stealth_worlds<1:
        raise AssertionError("WSP130_STEALTH_IMPOSSIBILITY_NOT_WITNESSED")
    classification=("DEVELOPMENT_MIXED_WITHIN_SUPPLIED_ANF_FAMILY"
                    if positive_pass and negative_pass else "DEVELOPMENT_NO_GO")
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "schema":"wsp130.development-only.v1","status":classification,
        "scientific_pass":False,"original_first_use":False,
        "native_admission":False,"grammar_supplied":True,
        "learned_high_masks_from_consequences":high_exact_masks,
        "new_high_mask_correct_percent":100*high_exact_masks/64,
        "source_actions_per_arm":18432,"main_source_worlds":128,
        "adversarial_stealth_worlds":16,"source_actions_per_world":128,
        "condition_counts":counts,"scores":totals,"detection":detection,
        "changed_correct_percent":changed_rate,
        "changed_wrong_confident":changed_wrong,
        "changed_gain_over_safe_abort_pp":gain,
        "unchanged_correct_percent":unchanged_rate,
        "false_high_masks_on_unchanged":false_high_masks,
        "two_high_wrong_confident":off["wrong_confident"],
        "two_high_unsupported_worlds":detection["double"]["UNSUPPORTED"],
        "stealth_confident_wrong":stealth["wrong_confident"],
        "stealth_worlds_with_confident_wrong":confident_stealth_worlds,
        "universal_source_safety_proven":False,
        "positive_gate_pass":positive_pass,"negative_gate_pass":negative_pass,
        "same_evidence_symbolic_exact_parity":strong_tie,
        "cold_state_replay":True,"retention_after_interference":True,
        "paired_bootstrap":_bootstrap(paired),"transfer":transfer,
        "source_score_sha256":S.digest(receipts),
        "transfer_score_sha256":S.digest(transfer_rows),
        "numeric_snapshot_sha256":S.digest(old_snapshot),
        "numeric_snapshot_bytes":len(old_snapshot.encode()),
        "strong_conventional_trained_baseline":"UNQUALIFIED_NOT_RUN",
        "resource":{"wall_seconds_development_only":round(time.perf_counter()-start_wall,3),
                    "cpu_seconds_development_only":round(time.process_time()-start_cpu,3),
                    "tracemalloc_peak_bytes":peak,
                    "matched_full_process_cost":"UNQUALIFIED",
                    "energy":"NOT_MEASURED"}
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering",action="store_true",required=True)
    parser.parse_args()
    print("WSP130_ENGINEERING_JSON="+S.canon(run_engineering()))
