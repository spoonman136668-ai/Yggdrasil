"""WSP128 full high-first 192-world source-safe experiment.

One preregistered unmodified development comparison; no original held first-use.
Prior numeric and optimized symbolic models are actually re-learned from the
64 previously exposed WSP127 public development laws, with all costs counted.
"""
from __future__ import annotations
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import random
import time

import source as S
import repair as R
import controls as C

def _load_parent(name,filename):
    path=Path(__file__).resolve().parents[1]/"WSP-127"/filename
    spec=spec_from_file_location(name,path)
    obj=module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

N127=_load_parent("_wsp127_numeric_for_wsp128","numeric.py")
C127=_load_parent("_wsp127_controls_for_wsp128","controls.py")
ARMS=("NATIVE_REPAIR","SYMBOLIC_EXACT","SAFE_ABORT","STALE_PRIOR","NO_UPDATE")
CONDITIONS=("unchanged","rank9","rank10")
FIELDS=("held","correct","wrong_confident","abstained","source_calls")

def _empty():
    return {condition:{arm:{key:0 for key in FIELDS} for arm in ARMS}
            for condition in CONDITIONS}

def _training():
    numerical=N127.DirectRankEight("adaptive")
    symbolic=C127.OptimizedSymbolic()
    receipts=[]
    for law in range(64):
        view=S.training_view(law)
        native_c=S.training_custodian(view)
        strong_c=S.training_custodian(view)
        available=set(view.legal)
        for _ in range(1024):
            subject=numerical.choose(view,available)
            if subject is None or subject not in available:
                raise AssertionError("WSP128_INVALID_PARENT_SOURCE_CHOICE")
            available.remove(subject)
            numerical.observe(view,native_c.query(subject))
            symbolic.observe(view,strong_c.query(subject))
        if native_c.receipt!=strong_c.receipt:
            raise AssertionError("WSP128_PARENT_EQUAL_EVIDENCE_FAIL")
        if numerical._state(law).rank()!=8:
            raise AssertionError("WSP128_PARENT_RANK_INCOMPLETE")
        receipts.append([law,native_c.receipt])
    return numerical,symbolic,S._digest(receipts)

def _models(native,symbolic):
    return {
        "NATIVE_REPAIR":R.DirectResidualRepair(native),
        "SYMBOLIC_EXACT":C.SymbolicExact(symbolic),
        "SAFE_ABORT":C.SafeAbort(native),
        "STALE_PRIOR":C.StalePrior(native),
        "NO_UPDATE":C.NoUpdate()
    }

def _pair_bootstrap(paired):
    rng=random.Random(128)
    gain=[native-abort for native,abort in paired]
    n=len(gain)
    samples=[]
    for _ in range(10000):
        v=sum(gain[rng.randrange(n)] for _ in range(n))
        samples.append(100*v/(n*3584))
    samples.sort()
    return {"seed":128,"resamples":10000,
            "low_95_percentile":samples[250],
            "high_95_percentile":samples[9749]}

def run_engineering():
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    if S.ALLOWED & S.DENIED:
        raise PermissionError("WSP128_PROTECTED_SOURCE_OVERLAP")
    num,sym,fit_sha=_training()
    old_num=num.snapshot()
    models=_models(num,sym)
    totals=_empty()
    paired={}
    receipts=[]
    detection={k:{"worlds":0,"source_conflict":0,
                  "repaired":0,"invalid":0,"unresolved":0}
               for k in CONDITIONS}
    for seed in range(139000,139192):
        view=S.world(seed)
        custodians={arm:S.Custodian(view) for arm in ARMS}
        available=set(view.legal)
        for step in range(512):
            subject=models["NATIVE_REPAIR"].choose(view,available)
            if subject is None or subject not in available:
                raise AssertionError("WSP128_PROBING_BUDGET_OR_ID_FAILURE")
            available.remove(subject)
            for arm in ARMS:
                e=custodians[arm].query(subject)
                models[arm].observe(view,e)
        if models["NATIVE_REPAIR"].choose(view,available) is not None:
            raise AssertionError("WSP128_OVERBUDGET_QUERY_NOT_DENIED")
        shared={cust.receipt for cust in custodians.values()}
        if len(shared)!=1:
            raise AssertionError("WSP128_EQUAL_INFORMATION_ACTION_TRANSCRIPT_FAIL")
        scores={}
        for arm in ARMS:
            cust=custodians[arm]
            held=tuple(cust.held())
            if len(held)!=3584 or len(cust.events)!=512:
                raise AssertionError("WSP128_WITHHELD_BUDGET_DRIFT")
            predictions={subject:models[arm].infer(view,subject)
                         for subject,_,_ in held}
            scored=cust.score_once(predictions)
            condition=scored["condition"]
            scores[arm]=scored
            for field in FIELDS:
                totals[condition][arm][field]+=scored[field]
        if condition!=custodians["NATIVE_REPAIR"]._condition:
            raise AssertionError("WSP128_ORACLE_COHORT_ACCOUNTING")
        if tuple(scores["NATIVE_REPAIR"][k] for k in FIELDS)!=tuple(
                 scores["SYMBOLIC_EXACT"][k] for k in FIELDS):
            raise AssertionError("WSP128_INDEPENDENT_SYMBOLIC_PARITY_FAIL")
        st=models["NATIVE_REPAIR"]._state(view)
        data=st._compiled()
        d=detection[condition]
        d["worlds"]+=1
        d["source_conflict"]+=int(data["contradictions"]>0)
        d["repaired"]+=int(data["status"]=="REPAIRED")
        d["invalid"]+=int(data["inconsistent"])
        d["unresolved"]+=int(data["status"]=="SUSPECT_UNRESOLVED")
        if condition=="rank9":
            if view.law_id in paired:
                raise AssertionError("WSP128_DUPLICATE_RANK9_LAW")
            paired[view.law_id]=(scores["NATIVE_REPAIR"]["correct"],
                                 scores["SAFE_ABORT"]["correct"])
        receipts.append([seed,view.law_id,condition,custodians["NATIVE_REPAIR"].receipt,
                         [tuple(scores[arm][key] for key in FIELDS) for arm in ARMS]])
    if (len(paired)!=64 or any(v["worlds"]!=64 for v in detection.values())
            or old_num!=num.snapshot()):
        raise AssertionError("WSP128_RETENTION_OR_WORLD_COUNTS_DRIFT")
    rank9=totals["rank9"]["NATIVE_REPAIR"]
    null=totals["unchanged"]["NATIVE_REPAIR"]
    off=totals["rank10"]["NATIVE_REPAIR"]
    abort=totals["rank9"]["SAFE_ABORT"]
    rank9_cov=100*rank9["correct"]/229376
    null_cov=100*null["correct"]/229376
    rank9_wrong=100*rank9["wrong_confident"]/229376
    rank10_wrong=100*off["wrong_confident"]/229376
    gain=100*(rank9["correct"]-abort["correct"])/229376
    rank9_ok=(rank9_cov>=75 and rank9_wrong<=1 and gain>=15)
    null_ok=(null_cov>=80 and null["wrong_confident"]/229376<=.01 and
             detection["unchanged"]["source_conflict"]/64<=.01)
    rank10_ok=rank10_wrong<=1
    classification=("DEVELOPMENT_NO_GO" if not rank9_ok or not null_ok or not rank10_ok
                    else "DEVELOPMENT_MIXED_WITHIN_FAMILY_SYMBOLIC_TIE")
    return {
        "schema":"wsp128.high-first-engineering.v1",
        "status":classification,"scientific_pass":False,
        "original_first_use":False,"native_admission":False,
        "underlying_causal_laws":64,"source_action_calls_per_arm":65536+98304,
        "all_arm_source_probe_count":98304,"condition_held_per_arm":229376,
        "warm_fit_sha256":fit_sha,"matched_control_transcripts":True,
        "warm_prior_snapshot_sha256":S._digest(old_num),
        "cohorts":totals,"detector":detection,
        "rank9_correct_percent":rank9_cov,
        "rank9_wrong_confident_percent":rank9_wrong,
        "rank9_gain_over_safe_abort_pp":gain,
        "unchanged_correct_percent":null_cov,
        "rank10_wrong_confident_percent":rank10_wrong,
        "rank9_within_family_gate":rank9_ok,
        "unchanged_false_alarm_gate":null_ok,
        "rank10_unknown_law_gate":rank10_ok,
        "paired_bootstrap":_pair_bootstrap([paired[k] for k in sorted(paired)]),
        "source_result_digest":S._digest(receipts),
        "numerical_symbolic_exact_parity":True,
        "warm_original_knowledge_preserved":True,
        "strong_trained_conventional":"NOT_RUN_UNQUALIFIED",
        "resource":{"wall_seconds_development_only":round(time.perf_counter()-start_wall,3),
                    "process_cpu_seconds_development_only":round(time.process_time()-start_cpu,3),
                    "rss_peak_bytes":"UNVERIFIED",
                    "energy":"UNVERIFIED","full_resource_parity":"UNQUALIFIED"}
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering",action="store_true",required=True)
    parser.parse_args()
    print("WSP128_ENGINEERING_JSON="+S._canon(run_engineering()))
