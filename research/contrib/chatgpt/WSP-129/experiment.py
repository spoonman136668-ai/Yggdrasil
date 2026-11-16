"""WSP129 frozen operator-inference / unfamiliar-grammar development experiment.

Strong exact-symbolic reference observes the SAME active action/effect trace,
while fixed reference gets exactly the same number of differently chosen calls.
No external scientific original first-use or native integration.
"""
from __future__ import annotations
import argparse
import random
import time
import tracemalloc

import source as S
import learner as N
import controls as C

ARMS=("ACTIVE_NUMERIC","ACTIVE_EXACT_SYMBOLIC",
      "FIXED_NUMERIC","FIXED_EXACT_SYMBOLIC",
      "FULLY_FIT_RIDGE","NO_UPDATE")
KINDS=("XOR","AND","OR","OFF")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def _totals():
    return {kind:{arm:{field:0 for field in FIELDS} for arm in ARMS}
            for kind in KINDS}

def _models():
    return {"ACTIVE_NUMERIC":N.HypothesisWeightBank("active"),
            "ACTIVE_EXACT_SYMBOLIC":C.OptimizedSymbolic(),
            "FIXED_NUMERIC":N.HypothesisWeightBank("fixed"),
            "FIXED_EXACT_SYMBOLIC":C.OptimizedSymbolic(),
            "FULLY_FIT_RIDGE":C.FullFitRidge(),
            "NO_UPDATE":C.NoUpdate()}

def _sum_metrics(total,part):
    for key in FIELDS:
        total[key]+=part[key]

def _bootstrap(pairs):
    randomizer=random.Random(129)
    delta=[first-second for first,second in pairs]
    trials=[]
    n=len(delta)
    for _ in range(10000):
        trials.append(100*sum(delta[randomizer.randrange(n)]
                               for j in range(n))/(n*232))
    trials.sort()
    return {"resamples":10000,"seed":129,
            "gain_95_percentile_low_pp":trials[250],
            "gain_95_percentile_high_pp":trials[9749]}

def run_engineering():
    started=time.perf_counter()
    cpu_start=time.process_time()
    tracemalloc.start()
    if S.ALLOWED&S.DENIED:
        raise PermissionError("WSP129_PROTECTED_SOURCE_OVERLAP")
    models=_models()
    t=_totals()
    score_rows=[]
    paired=[]
    fingerprints=[]
    operator_identified=0
    world_count={kind:0 for kind in KINDS}
    off_eliminated=0
    ridge_training_correct=0
    action_count=0
    for seed in range(148000,148128):
        view=S.world(seed)
        legal_active=set(view.legal)
        legal_fixed=set(view.legal)
        custody={arm:S.Custodian(view) for arm in ARMS}
        active=models["ACTIVE_NUMERIC"]
        fixed=models["FIXED_NUMERIC"]
        for _ in range(24):
            active_subject=active.choose(view,legal_active)
            fixed_subject=fixed.choose(view,legal_fixed)
            if (active_subject is None or fixed_subject is None or
                    active_subject not in legal_active or
                    fixed_subject not in legal_fixed):
                raise AssertionError("WSP129_EVIDENCE_BUDGET_OR_DUPLICATE")
            legal_active.remove(active_subject)
            legal_fixed.remove(fixed_subject)
            for arm in ARMS:
                subject=fixed_subject if arm.startswith("FIXED") else active_subject
                evidence=custody[arm].query(subject)
                models[arm].observe(view,evidence)
                action_count+=1
        if active.choose(view,legal_active) is not None:
            raise AssertionError("WSP129_ACTIVE_OVERBUDGET")
        if fixed.choose(view,legal_fixed) is not None:
            raise AssertionError("WSP129_FIXED_OVERBUDGET")
        if len({custody[x].receipt for x in (
                "ACTIVE_NUMERIC","ACTIVE_EXACT_SYMBOLIC",
                "FULLY_FIT_RIDGE","NO_UPDATE")})!=1:
            raise AssertionError("WSP129_ACTIVE_EXACT_INFORMATION_MISMATCH")
        if custody["FIXED_NUMERIC"].receipt!=custody["FIXED_EXACT_SYMBOLIC"].receipt:
            raise AssertionError("WSP129_FIXED_EXACT_INFORMATION_MISMATCH")
        models["FULLY_FIT_RIDGE"].fit(view)
        ridge_training_correct+=models["FULLY_FIT_RIDGE"].training_correct(view)
        predictions={}
        current={}
        for arm in ARMS:
            held=tuple(custody[arm].held())
            if len(held)!=232 or len(custody[arm].events)!=24:
                raise AssertionError("WSP129_UNEQUAL_SOURCE_COUNTS")
            p={subject:models[arm].infer(view,subject) for subject,_,_ in held}
            s=custody[arm].score_once(p)
            current[arm]=s
            predictions[arm]=p
            _sum_metrics(t[s["kind"]][arm],s)
        if predictions["ACTIVE_NUMERIC"]!=predictions["ACTIVE_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP129_ADAPTIVE_STRONG_SYMBOLIC_NOT_IDENTICAL")
        if predictions["FIXED_NUMERIC"]!=predictions["FIXED_EXACT_SYMBOLIC"]:
            raise AssertionError("WSP129_FIXED_STRONG_SYMBOLIC_NOT_IDENTICAL")
        kind=current["ACTIVE_NUMERIC"]["kind"]
        world_count[kind]+=1
        if kind!="OFF":
            operator_identified+=int(models["ACTIVE_NUMERIC"].operator(view)==kind)
            paired.append((current["ACTIVE_NUMERIC"]["correct"],
                           current["FIXED_EXACT_SYMBOLIC"]["correct"]))
        else:
            off_eliminated+=int(models["ACTIVE_NUMERIC"].exhausted(view))
        score_rows.append([view.law_id,kind,
                           [tuple(current[arm][f] for f in FIELDS) for arm in ARMS],
                           models["ACTIVE_NUMERIC"].operator(view)])
        fingerprints.append([view.law_id,custody["ACTIVE_NUMERIC"].receipt,
                             custody["FIXED_NUMERIC"].receipt])
    if world_count!={"XOR":32,"AND":32,"OR":32,"OFF":32}:
        raise AssertionError("WSP129_WORLD_FAMILY_CUSTODY_DRIFT")
    if action_count!=128*24*len(ARMS):
        raise AssertionError("WSP129_TOTAL_CHARGED_EFFECT_DRIFT")
    # Immutable cold restore is tested AFTER every law has been learned.
    native=models["ACTIVE_NUMERIC"]
    snapshot=native.snapshot()
    restored=N.HypothesisWeightBank.restore(snapshot,S.world)
    if restored.snapshot()!=snapshot:
        raise AssertionError("WSP129_COLD_REPLAY_NOT_BITWISE_IDENTICAL")
    for seed in range(148000,148128):
        view=S.world(seed)
        for subject,_,_ in view.records:
            if restored.infer(view,subject)!=native.infer(view,subject):
                raise AssertionError("WSP129_LATE_INTERFERENCE_OR_COLD_LOSS")
    transfer={arm:{f:0 for f in FIELDS} for arm in ARMS}
    transfer_rows=[]
    for seed in range(150000,150032):
        view=S.world(seed)
        per={}
        for arm in ARMS:
            cust=S.Custodian(view)
            if cust.budget or view.legal or cust.events:
                raise AssertionError("WSP129_TRANSFER_HAS_PAID_DATA")
            score=cust.score_once({subject:models[arm].infer(view,subject)
                                   for subject,_,_ in cust.held()})
            _sum_metrics(transfer[arm],score)
            per[arm]=score
        if any(per[a][f]!=per[b][f] for a,b in (
            ("ACTIVE_NUMERIC","ACTIVE_EXACT_SYMBOLIC"),
            ("FIXED_NUMERIC","FIXED_EXACT_SYMBOLIC")) for f in FIELDS):
            raise AssertionError("WSP129_TRANSFER_SYMBOLIC_NONPARITY")
        transfer_rows.append([view.law_id,
            [tuple(per[arm][f] for f in FIELDS) for arm in ARMS]])
    if native.snapshot()!=snapshot:
        raise AssertionError("WSP129_ZERO_SHOT_TRANSFER_CHANGED_KNOWLEDGE")
    on_correct=sum(t[k]["ACTIVE_NUMERIC"]["correct"] for k in KINDS[:3])
    on_wrong=sum(t[k]["ACTIVE_NUMERIC"]["wrong_confident"] for k in KINDS[:3])
    fixed_correct=sum(t[k]["FIXED_EXACT_SYMBOLIC"]["correct"] for k in KINDS[:3])
    off_wrong=t["OFF"]["ACTIVE_NUMERIC"]["wrong_confident"]
    on_rate=100*on_correct/22272
    delta_pp=100*(on_correct-fixed_correct)/22272
    off_rate=100*off_wrong/7424
    off_exclusion=100*off_eliminated/32
    op_rate=100*operator_identified/96
    fit_pass=(on_rate>=95 and on_wrong==0 and op_rate>=90 and delta_pp>=-2)
    off_pass=(off_exclusion>=90 and off_rate<=1)
    status=("DEVELOPMENT_SUPPORTED_WITHIN_SUPPLIED_GRAMMAR_SYMBOLIC_TIE"
            if fit_pass and off_pass else
            "DEVELOPMENT_MIXED_ON_GRAMMAR_ONLY" if fit_pass else
            "DEVELOPMENT_NO_GO")
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
      "schema":"wsp129.engineering-only.v1","status":status,
      "scientific_pass":False,"native_admission":False,
      "original_first_use":False,"operator_library_supplied":True,
      "worlds_by_family":world_count,
      "in_grammar_held_per_arm":22272,
      "off_grammar_held_per_arm":7424,
      "paid_actions_per_arm":3072,
      "exact_symbolic_matched_on_all_predictions":True,
      "fit":{k:v for k,v in t.items() if k!="OFF"},
      "off_family":t["OFF"],
      "fit_correct_percent":on_rate,
      "fit_wrong_confident":on_wrong,
      "active_minus_fixed_strong_symbolic_pp":delta_pp,
      "uniquely_inferred_operator_worlds":operator_identified,
      "operator_identification_percent":op_rate,
      "off_family_candidate_elimination_worlds":off_eliminated,
      "off_family_elimination_percent":off_exclusion,
      "off_family_wrong_confident_percent":off_rate,
      "fit_gate_pass":fit_pass,"off_family_gate_pass":off_pass,
      "paired_active_fixed_bootstrap":_bootstrap(paired),
      "ridge":{ "fully_optimized_convex_ridge_not_neural":True,
                "train_correct":ridge_training_correct,
                "train_total":128*24,
                "full_fit_per_world":True},
      "transfer":transfer,
      "cold_restoration":True,"post_interference_retention":True,
      "cohort_score_sha256":S.digest(score_rows),
      "source_transcript_sha256":S.digest(fingerprints),
      "transfer_scores_sha256":S.digest(transfer_rows),
      "resource":{"wall_seconds_dev":round(time.perf_counter()-started,3),
                  "process_cpu_seconds_dev":round(time.process_time()-cpu_start,3),
                  "tracemalloc_peak_bytes":peak,
                  "whole_process_comparator_fairness":"UNQUALIFIED",
                  "energy":"NOT_MEASURED"}
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering",required=True,action="store_true")
    parser.parse_args()
    print("WSP129_ENGINEERING_JSON="+S.canon(run_engineering()))
