"""WSP131 source-safe prior-to-target structural semantic binding experiment.

Already exposed WSP130 synthetic source trained FIRST on real public effects.
Hidden feature permutation/sheer source is independent of learner implementations.
All arms receive equal charged source actions; milestone scores are computed ONLY
after the full source-action budget, with earlier predictions frozen unchanged.
"""
from __future__ import annotations
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import random
import time
import tracemalloc

import source as S
import binder as N
import controls as C

def _parent(name,filename):
    p=Path(__file__).resolve().parents[1]/"WSP-130"/filename
    s=spec_from_file_location(name,p)
    m=module_from_spec(s)
    s.loader.exec_module(m)
    return m

N130=_parent("_wsp130_direct_for_wsp131","learner.py")
C130=_parent("_wsp130_symbolic_for_wsp131","controls.py")

ARMS=("ACTIVE_NUMERIC_BINDER","ACTIVE_EXACT_SYMBOLIC",
      "FIXED_EXACT_SYMBOLIC","FULLY_TRAINED_CART","STALE_PRIOR","NO_UPDATE")
CONDITIONS=("known","shear")
STAGES=(0,4,8,16,32)
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def _stats():
    return {kind:{arm:{str(stage):{f:0 for f in FIELDS}
                       for stage in STAGES} for arm in ARMS}
            for kind in CONDITIONS}
def _update(acc,score):
    for field in FIELDS:acc[field]+=score[field]

def _warm():
    native=N130.DirectInducer()
    symbolic=C130.ExactSymbolic()
    original_hash=[]
    signatures={}
    for law in S._origins():
        view=S.warm_world(law)
        a=S.warm_custodian(view)
        b=S.warm_custodian(view)
        remaining=set(view.legal)
        for _ in range(128):
            subject=native.choose(view,remaining)
            if subject is None or subject not in remaining:
                raise AssertionError("WSP131_WARM_SOURCE_ORDER_INVALID")
            remaining.remove(subject)
            native.observe(view,a.query(subject))
            symbolic.observe(view,b.query(subject))
        if a.receipt!=b.receipt:
            raise AssertionError("WSP131_WARM_NUMERIC_SYMBOLIC_SOURCE_NONPARITY")
        truth=[]
        for subject,x in view.records:
            na=native.infer(view,subject)
            sy=symbolic.infer(view,subject)
            if na!=sy or na is None:
                raise AssertionError("WSP131_WARM_CAUSAL_MEMORY_NOT_QUALIFIED")
            truth.append((x,na))
        signatures[law]=tuple(v for x,v in sorted(truth))
        original_hash.append([law,a.receipt,S.digest(signatures[law])])
    return native,symbolic,S.digest(original_hash),signatures

def _bootstrap(pairs):
    rng=random.Random(131)
    delta=[a-b for a,b in pairs]
    n=len(delta)
    samples=[]
    for _ in range(10000):
        samples.append(100*sum(delta[rng.randrange(n)]
                               for i in range(n))/(n*224))
    samples.sort()
    return {"seed":131,"resamples":10000,
            "low_95_percentile_pp":samples[250],
            "high_95_percentile_pp":samples[9749]}

def run_engineering():
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    tracemalloc.start()
    if S.ALLOWED&S.PROTECTED:
        raise PermissionError("WSP131_ORIGINAL_PROTECTED_SOURCE_OVERLAP")
    native_prior,symbol_prior,warm_hash,warm_signatures=_warm()
    warm_snapshot=native_prior.snapshot()
    native=N.NativeBinder(native_prior)
    strong=C.ExactPermutationSymbolic(symbol_prior)
    fixed=C.ExactPermutationSymbolic(symbol_prior)
    schedule=C.FixedSourceBlindSchedule(fixed)
    cart=C.FullyFitCART()
    stale=C.StalePrior(native_prior)
    inactive=C.NoUpdate()
    models=dict(zip(ARMS,(native,strong,fixed,cart,stale,inactive)))
    totals=_stats()
    status={kind:{"worlds":0,"resolved":0,"eliminated":0,
                  "false_confident_worlds":0} for kind in CONDITIONS}
    positive_paired=[]
    receipts=[]
    scored_worlds=[]
    for seed in (*range(160000,160064),*range(161000,161032)):
        view=S.world(seed)
        available_active=set(view.legal)
        available_fixed=set(view.legal)
        used_fixed=set()
        cust={arm:S.Custodian(view) for arm in ARMS}
        # Any checkpoint predictions from earlier stages are retained as
        # immutable snapshots in memory; future effects cannot change them.
        predictions={arm:{} for arm in ARMS}
        for stage_index in range(33):
            if stage_index in STAGES:
                for arm in ARMS:
                    predictions[arm][stage_index]={
                        subject:models[arm].infer(view,subject)
                        for subject,x in view.records}
            if stage_index==32:break
            active_subject=native.choose(view,available_active)
            fixed_subject=schedule.choose(view,used_fixed)
            if (active_subject is None or fixed_subject is None or
                    active_subject not in available_active or
                    fixed_subject not in available_fixed):
                raise AssertionError("WSP131_DUPLICATE_OR_BAD_ACTION")
            available_active.remove(active_subject)
            available_fixed.remove(fixed_subject)
            used_fixed.add(view.input(fixed_subject))
            for arm in ARMS:
                chosen=fixed_subject if arm=="FIXED_EXACT_SYMBOLIC" else active_subject
                e=cust[arm].query(chosen)
                models[arm].observe(view,e)
        if native.choose(view,available_active) is not None:
            raise AssertionError("WSP131_MORE_THAN_32_ACTIONS")
        if len({cust[arm].receipt for arm in ARMS
                if arm!="FIXED_EXACT_SYMBOLIC"})!=1:
            raise AssertionError("WSP131_SAME_ACTION_EQUAL_EVIDENCE_FAIL")
        for arm in ARMS:
            if len(cust[arm].events)!=32:raise AssertionError("WSP131_ACTION_BUDGET_DRIFT")
        per={}
        for arm in ARMS:
            held={subject for subject,x in cust[arm].held()}
            if len(held)!=224:
                raise AssertionError("WSP131_TEST_HELD_SET_DRIFT")
            frozen={stage:{s:predictions[arm][stage][s] for s in held}
                    for stage in STAGES}
            per[arm]=cust[arm].score_once(frozen)
            kind=per[arm]["condition"]
            for stage in STAGES:
                _update(totals[kind][arm][str(stage)],per[arm]["stages"][stage])
        kind=per["ACTIVE_NUMERIC_BINDER"]["condition"]
        status[kind]["worlds"]+=1
        for stage in STAGES:
            matched={s:predictions["ACTIVE_NUMERIC_BINDER"][stage][s]
                     for s,x in cust["ACTIVE_NUMERIC_BINDER"].held()}
            exact={s:predictions["ACTIVE_EXACT_SYMBOLIC"][stage][s]
                   for s,x in cust["ACTIVE_EXACT_SYMBOLIC"].held()}
            if matched!=exact:
                raise AssertionError("WSP131_SAME_SOURCE_STRONG_SYMBOLIC_DECISION_MISMATCH")
        if native.resolved(view)!=strong.resolved(view):
            raise AssertionError("WSP131_SYMBOLIC_FUNCTIONAL_IDENTIFIABILITY_MISMATCH")
        remaining=native.remaining(view)
        if remaining==0:
            status[kind]["eliminated"]+=1
        if kind=="known":
            if native.resolved(view):
                truth=S._physical_law(seed)["truth"]
                if all(native.infer(view,view.subject(x))==truth[x]
                       for x in range(256)):
                    status[kind]["resolved"]+=1
                else:
                    raise AssertionError("WSP131_CONFIDENTLY_WRONG_RECOVERED_BINDING")
            positive_paired.append((
                per["ACTIVE_NUMERIC_BINDER"]["stages"][32]["correct"],
                per["FIXED_EXACT_SYMBOLIC"]["stages"][32]["correct"]))
        elif per["ACTIVE_NUMERIC_BINDER"]["stages"][32]["wrong_confident"]:
            status[kind]["false_confident_worlds"]+=1
        receipts.append([seed,view.law_id,kind,
            cust["ACTIVE_NUMERIC_BINDER"].receipt,
            cust["FIXED_EXACT_SYMBOLIC"].receipt,
            [[per[arm]["stages"][k][f] for k in STAGES for f in FIELDS]
                for arm in ARMS],remaining])
    if status["known"]["worlds"]!=64 or status["shear"]["worlds"]!=32:
        raise AssertionError("WSP131_WORLD_ALLOCATION_DRIFT")
    if native_prior.snapshot()!=warm_snapshot:
        raise AssertionError("WSP131_SHARED_PRIOR_CHANGED_DURING_TRANSFER")
    for law in S._origins():
        view=S.warm_world(law)
        for subject,x in view.records:
            if native_prior.infer(view,subject)!=warm_signatures[law][x]:
                raise AssertionError("WSP131_PRIOR_CAUSAL_KNOWLEDGE_LOST")
    cold=N.NativeBinder.restore(native_prior,native.snapshot(),S.world)
    if cold.snapshot()!=native.snapshot():
        raise AssertionError("WSP131_COLD_REPLAY_BITWISE_MISMATCH")
    for seed in (*range(160000,160064),*range(161000,161032)):
        v=S.world(seed)
        for subject,x in v.records:
            if native.infer(v,subject)!=cold.infer(v,subject):
                raise AssertionError("WSP131_COLD_TRANSFER_INFERENCE_DRIFT")
    transfer={arm:{f:0 for f in FIELDS} for arm in ARMS}
    transfer_rows=[]
    for seed in range(162000,162016):
        v=S.world(seed)
        per={}
        for arm in ARMS:
            scorer=S.Custodian(v)
            if scorer.budget or v.legal or scorer.events:
                raise AssertionError("WSP131_TRANSFER_PAID_CONSEQUENCES")
            pred={subject:models[arm].infer(v,subject)
                  for subject,x in scorer.held()}
            per[arm]=scorer.score_once({stage:pred for stage in STAGES})["stages"][32]
            _update(transfer[arm],per[arm])
        if per["ACTIVE_NUMERIC_BINDER"]!=per["ACTIVE_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP131_TRANSFER_STRONG_SYMBOLIC_NONPARITY")
        transfer_rows.append([v.law_id,[tuple(per[arm][f] for f in FIELDS)
                                         for arm in ARMS]])
    if native_prior.snapshot()!=warm_snapshot:
        raise AssertionError("WSP131_TRANSFER_MUTATED_OLD_KNOWLEDGE")
    fit=totals["known"]["ACTIVE_NUMERIC_BINDER"]["32"]
    neg=totals["shear"]["ACTIVE_NUMERIC_BINDER"]["32"]
    frozen_fixed=totals["known"]["FIXED_EXACT_SYMBOLIC"]["32"]
    old=totals["known"]["STALE_PRIOR"]["32"]
    fit_pct=100*fit["correct"]/14336
    wrong_pct=100*fit["wrong_confident"]/14336
    gain=100*(fit["correct"]-old["correct"])/14336
    neg_wrong_pct=100*neg["wrong_confident"]/7168
    compare_pct=100*(fit["correct"]-frozen_fixed["correct"])/14336
    fit_ok=(fit_pct>=95 and wrong_pct<=1 and
            status["known"]["resolved"]>=58 and gain>=20 and
            transfer["ACTIVE_NUMERIC_BINDER"]["correct"]==4096 and
            transfer["ACTIVE_NUMERIC_BINDER"]["wrong_confident"]==0)
    negative_ok=(status["shear"]["eliminated"]>=30 and neg_wrong_pct<=1)
    comparison_ok=compare_pct>=-2
    classification=("DEVELOPMENT_SUPPORTED_SEMANTIC_REBINDING_WITHIN_SUPPLIED_PERMUTATION"
                    if fit_ok and negative_ok and comparison_ok
                    else "DEVELOPMENT_NO_GO")
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "schema":"wsp131.source-safe-rebinding-engineering.v1",
        "status":classification,"scientific_pass":False,
        "original_first_use":False,"native_admission":False,
        "original_source_used":"WSP130_CONSUMED_SYNTHETIC_ONLY",
        "parent_learning_warm_actions_per_arm":8192,
        "rebinding_actions_per_arm":3072,
        "rebinding_worlds":{"known":64,"shear":32},
        "held_per_target_world":224,
        "checkpoints":STAGES,"scores":totals,"world_dispositions":status,
        "fit_correct_percent":fit_pct,"fit_confident_wrong_percent":wrong_pct,
        "active_vs_stale_gain_pp":gain,
        "active_vs_fixed_strong_symbolic_gain_pp":compare_pct,
        "negative_confident_wrong_percent":neg_wrong_pct,
        "resolved_compatible_target_functions":status["known"]["resolved"],
        "negative_shears_fully_rejected":status["shear"]["eliminated"],
        "positive_gate":fit_ok,"negative_gate":negative_ok,
        "strong_comparison_gate":comparison_ok,
        "active_exact_symbolic_decision_tie":True,
        "fully_fitted_cart_reported":True,
        "zero_source_transfer":transfer,
        "inherited_source_snapshot_unchanged":True,
        "cold_replay_all_target_worlds":True,
        "paired_active_vs_fixed_bootstrap":_bootstrap(positive_paired),
        "origin_source_receipt_sha256":warm_hash,
        "source_score_receipt_sha256":S.digest(receipts),
        "transfer_scores_sha256":S.digest(transfer_rows),
        "candidate_snapshot_sha256":S.digest(native.snapshot()),
        "resource":{"wall_seconds_dev":round(time.perf_counter()-start_wall,3),
                    "process_cpu_seconds_dev":round(time.process_time()-start_cpu,3),
                    "tracemalloc_peak_bytes":peak,
                    "computation_matched_to_strong_control":False,
                    "whole_process_energy":"UNQUALIFIED"}
    }

if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--engineering",required=True,action="store_true")
    arg.parse_args()
    print("WSP131_ENGINEERING_JSON="+S.canon(run_engineering()))
