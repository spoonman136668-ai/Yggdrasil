"""WSP125 source-safe max-first dynamic causal relationship screen.

All masks and held labels belong to source.Custodian. Learners cannot import
the hidden-law module. This script is development only: no original source.
"""
from __future__ import annotations
import argparse

import source as S
import numeric as N
import controls as C

ARMS=("NUMERIC_GROW","STRONG_SYMBOLIC_MATCHED",
      "STRONG_SYMBOLIC_PASSIVE","FIXED_BASE","NO_UPDATE")
MATCHED=("NUMERIC_GROW","STRONG_SYMBOLIC_MATCHED","FIXED_BASE","NO_UPDATE")
FIELDS=("held","correct","wrong_confident","abstained","source_calls")


def _models():
    return {
      "NUMERIC_GROW":N.DirectFeatureGrowth(),
      "STRONG_SYMBOLIC_MATCHED":C.ExactSymbolicSupports(),
      "STRONG_SYMBOLIC_PASSIVE":C.ExactSymbolicSupports(),
      "FIXED_BASE":C.FixedBaseline(),
      "NO_UPDATE":C.NoUpdate(),
    }


def _empty_scores():
    return {name:{k:0 for k in FIELDS} for name in ARMS}


def _add(into,arm,scored):
    for key in FIELDS:
        into[arm][key]+=scored[key]


def _fit(models):
    scores=_empty_scores()
    receipts=[]
    call_count=0
    for law in range(128):
        view=S.world(125900+law)
        owners={arm:S.Custodian(view) for arm in ARMS}
        passive=C.passive_sequence(view)
        if len(passive)!=32 or len(set(passive))!=32:
            raise AssertionError("WSP125_PASSIVE_ACTION_BUDGET")
        allowed=set(view.legal)
        for step in range(32):
            subject=models["NUMERIC_GROW"].choose(view,allowed)
            if subject is None or subject not in allowed:
                raise AssertionError("WSP125_ACTIVE_ACTION_NOT_LEGAL")
            allowed.remove(subject)
            for arm in MATCHED:
                evidence=owners[arm].query(subject)
                models[arm].observe(view,evidence)
            other=owners["STRONG_SYMBOLIC_PASSIVE"].query(passive[step])
            models["STRONG_SYMBOLIC_PASSIVE"].observe(view,other)
        call_count+=32
        if models["NUMERIC_GROW"].choose(view,allowed) is not None:
            raise AssertionError("WSP125_ACTIVE_SOURCE_OVER_BUDGET")
        source_receipts={owners[arm].receipt for arm in MATCHED}
        if len(source_receipts)!=1:
            raise AssertionError("WSP125_MATCHED_SOURCE_RECEIPTS")
        predictions={}
        for arm in ARMS:
            predictions[arm]={
                subject:models[arm].infer(view,subject)
                for subject in owners[arm].held
            }
        for subject,numeric_value in predictions["NUMERIC_GROW"].items():
            if (numeric_value is not None and numeric_value !=
                    predictions["STRONG_SYMBOLIC_MATCHED"][subject]):
                raise AssertionError("WSP125_NUMERIC_NOT_ENTAILED_BY_EXACT_CONTROL")
        per_arm={}
        for arm in ARMS:
            result=owners[arm].score_once(predictions[arm])
            if result["held"]!=32 or result["source_calls"]!=32:
                raise AssertionError("WSP125_SOURCE_BUDGET_DRIFT")
            per_arm[arm]=result
            _add(scores,arm,result)
        for arm in ("NUMERIC_GROW","STRONG_SYMBOLIC_MATCHED",
                    "STRONG_SYMBOLIC_PASSIVE"):
            if per_arm[arm]["wrong_confident"]!=0:
                raise AssertionError("WSP125_IN_FAMILY_STRONG_WRONG")
        receipts.append([law,next(iter(source_receipts)),
                         [(per_arm[arm]["correct"],
                           per_arm[arm]["wrong_confident"],
                           per_arm[arm]["abstained"]) for arm in ARMS]])
    if call_count!=4096:
        raise AssertionError("WSP125_FIT_SOURCE_TOTAL_DRIFT")
    return scores,S.digest(receipts),call_count


def _evaluate_zero_source(models,cohort):
    if cohort=="transfer":
        seeds=range(126200,126456)
    elif cohort=="negative":
        seeds=range(126500,126564)
    else:
        raise ValueError("WSP125_UNKNOWN_COHORT")
    scores=_empty_scores()
    audit=[]
    for seed in seeds:
        view=S.world(seed)
        per_arm={}
        predictions={}
        for arm in ARMS:
            owner=S.Custodian(view)
            if owner.budget!=0 or owner.held!=tuple(s for s,_,_ in view.records):
                raise AssertionError("WSP125_TRANSFER_MUST_BE_UNOPENED")
            predictions[arm]={
                subject:models[arm].infer(view,subject)
                for subject in owner.held
            }
            result=owner.score_once(predictions[arm])
            if result["source_calls"]!=0 or result["held"]!=64:
                raise AssertionError("WSP125_TRANSFER_SOURCE_USED")
            per_arm[arm]=result
            _add(scores,arm,result)
        for subject,numeric_value in predictions["NUMERIC_GROW"].items():
            if (numeric_value is not None and numeric_value!=
                    predictions["STRONG_SYMBOLIC_MATCHED"][subject]):
                raise AssertionError("WSP125_SYMBOLIC_MATCHED_ENTAILMENT")
        audit.append([seed,
                     per_arm["NUMERIC_GROW"]["public_sha256"],
                     per_arm["NUMERIC_GROW"]["source_sha256"],
                     [(per_arm[arm]["correct"],per_arm[arm]["wrong_confident"],
                       per_arm[arm]["abstained"]) for arm in ARMS]])
    return {"worlds":len(audit),"source_calls":0,
            "rows_sha256":S.digest(audit),"arms":scores}


def run_engineering():
    if S.ALLOWED & (S.ORIGINAL|S.PROTECTED):
        raise PermissionError("WSP125_FIRST_USE_COHORT_COLLISION")
    models=_models()
    fit,fit_hash,calls=_fit(models)
    direct=models["NUMERIC_GROW"]
    snapshot=direct.snapshot()
    cold=N.DirectFeatureGrowth.restore(snapshot)
    if cold.snapshot()!=snapshot:
        raise AssertionError("WSP125_COLD_IMAGE_UNSTABLE")
    for law in range(128):
        view=S.world(125900+law)
        for subject,_,_ in view.records:
            if cold.infer(view,subject)!=direct.infer(view,subject):
                raise AssertionError("WSP125_COLD_RETENTION_INTERFERENCE")
    transfer=_evaluate_zero_source(models,"transfer")
    negative=_evaluate_zero_source(models,"negative")
    for law in range(128):
        view=S.world(125900+law)
        for subject,_,_ in view.records:
            if cold.infer(view,subject)!=direct.infer(view,subject):
                raise AssertionError("WSP125_LATE_DOMAIN_RETENTION_DRIFT")
    f=fit["NUMERIC_GROW"]
    t=transfer["arms"]["NUMERIC_GROW"]
    development_go=(
        f["correct"]>=3892 and f["wrong_confident"]==0 and
        t["correct"]>=15565 and t["wrong_confident"]==0 and
        direct.learned_laws>=1 and direct.feature_slots>=17
    )
    if (f["held"]!=4096 or t["held"]!=16384 or
            fit["STRONG_SYMBOLIC_MATCHED"]["correct"]<f["correct"]):
        raise AssertionError("WSP125_EVAL_RECEIPT_OR_STRONG_CONTROL_INVALID")
    return {
      "schema":"wsp125.dynamic-residual-feature-growth.engineering.v1",
      "status":"DEVELOPMENT_GO" if development_go else "DEVELOPMENT_NO_GO",
      "scientific_pass":False,"source_first_use":False,"native_admission":False,
      "fit":fit,"fit_source_calls":calls,"fit_receipts_sha256":fit_hash,
      "transfer":transfer,"offfamily":negative,
      "learned_relation_features":direct.learned_laws,
      "coefficient_int32_slots":direct.feature_slots,
      "coefficient_bytes_only":direct.feature_slots*4,
      "cold_retention":True,"multi_law_interference":False,
      "numerical_unique_gain":False,
      "exact_strong_symbolic_is_not_weakened":True,
      "limitations":[
        "Known generic rank-one conjunction grammar; new support masks not known",
        "128 independent synthetic laws, transfer views are relabeled NOT new laws",
        "Strong symbolic full version space has same evidence, may be better",
        "In-family predicted masks do not constitute arbitrary new primitives",
        "Unrepresented off-family parity must preserve observed errors",
        "No fully trained conventional or independent original source",
        "No accepted native Yggdrasil weights or measured cost advantage",
      ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering-only",action="store_true",required=True)
    parser.parse_args()
    print("WSP125_ENGINEERING_JSON="+S.canonical(run_engineering()))


if __name__=="__main__":
    main()
