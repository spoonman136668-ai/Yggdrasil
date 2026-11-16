"""WSP-123 high-first source-safe microfeedback causal transfer demonstration.

Four independently unknown domain factor relations; 256 disjoint transfer
worlds and 64 out-of-family negative worlds. No original scientific first use.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

import source as S
import weights as W
import symbolic as Y

ARMS=("NUMERIC_FACTOR_GROW","SYMBOLIC_FACTOR_STRONG",
      "SYMBOLIC_PASSIVE","MEMO_ONLY","NO_UPDATE")


def _arm_models():
    return {"NUMERIC_FACTOR_GROW":W.NumericCausalBank(),
            "SYMBOLIC_FACTOR_STRONG":Y.StrongSymbolicFactors(),
            "SYMBOLIC_PASSIVE":Y.StrongSymbolicFactors(),
            "MEMO_ONLY":Y.MemoOnly(),
            "NO_UPDATE":Y.NoUpdate()}


def _run_fit(models):
    rows=[]
    for d in range(4):
        public=S.world(123900+d)
        assert public.domain==d and len(public.legal)==48 and len(public.held)==16
        custodians={name:S.Custodian(public) for name in ARMS}
        remaining=set(public.legal)
        passive=Y.passive_selection(public,d)
        assert len(passive)==15 and len(set(passive))==15
        for idx in range(15):
            subject=models["NUMERIC_FACTOR_GROW"].choose(public,remaining)
            if subject!=models["SYMBOLIC_FACTOR_STRONG"].choose(public,remaining):
                raise AssertionError("WSP123_ACTIVE_SELECTION_MISMATCH")
            if subject is None or subject not in remaining:
                raise AssertionError("WSP123_ACTIVE_QUERY_EXHAUSTED")
            remaining.remove(subject)
            for name in ("NUMERIC_FACTOR_GROW","SYMBOLIC_FACTOR_STRONG",
                         "MEMO_ONLY","NO_UPDATE"):
                observation=custodians[name].query(subject)
                models[name].observe(public,observation)
            passive_observation=custodians["SYMBOLIC_PASSIVE"].query(passive[idx])
            models["SYMBOLIC_PASSIVE"].observe(public,passive_observation)
        active_receipts={custodians[name].receipt
            for name in ("NUMERIC_FACTOR_GROW","SYMBOLIC_FACTOR_STRONG",
                         "MEMO_ONLY","NO_UPDATE")}
        if len(active_receipts)!=1:
            raise AssertionError("WSP123_EQUAL_EVIDENCE_SOURCE_PARITY")
        scores={}
        for name in ARMS:
            predictions={subject:models[name].infer(public,subject)
                         for subject in public.held}
            scores[name]=custodians[name].score_once(predictions)
        if scores["NUMERIC_FACTOR_GROW"]!=scores["SYMBOLIC_FACTOR_STRONG"]:
            raise AssertionError("WSP123_MATCHED_NUMERIC_SYMBOLIC_FIT_PARITY")
        rows.append({"domain":d,"evidence":next(iter(active_receipts)),
                     "scores":scores})
    return rows


def _score_worlds(models,kind):
    if kind=="transfer":
        ids=range(124000,124256)
    elif kind=="offfamily":
        ids=range(124400,124464)
    else:
        raise ValueError("WSP123_UNKNOWN_COHORT")
    summary={name:{"held":0,"correct":0,"wrong_confident":0,
                   "abstained":0,"source_calls":0} for name in ARMS}
    receipts=[]
    for seed in ids:
        public=S.world(seed)
        per_arm={}
        for name,model in models.items():
            custody=S.Custodian(public)
            if custody.budget!=0 or public.legal or len(public.held)!=64:
                raise AssertionError("WSP123_ZERO_SHOT_SOURCE_FENCE")
            prediction={s:model.infer(public,s) for s in public.held}
            per_arm[name]=custody.score_once(prediction)
            for key in summary[name]:
                summary[name][key]+=per_arm[name][key]
        if per_arm["NUMERIC_FACTOR_GROW"]!=per_arm["SYMBOLIC_FACTOR_STRONG"]:
            raise AssertionError("WSP123_MATCHED_NUMERIC_SYMBOLIC_TRANSFER_PARITY")
        receipts.append([seed,per_arm["NUMERIC_FACTOR_GROW"]["public_sha256"],
                        per_arm["NUMERIC_FACTOR_GROW"]["source_sha256"],
                        [per_arm[name]["correct"] for name in ARMS],
                        [per_arm[name]["wrong_confident"] for name in ARMS],
                        [per_arm[name]["abstained"] for name in ARMS]])
    return {"worlds":len(ids),"rows_sha256":S.digest(receipts),
            "arms":summary}


def run_engineering():
    models=_arm_models()
    fit=_run_fit(models)
    cold=W.NumericCausalBank.restore(models["NUMERIC_FACTOR_GROW"].snapshot())
    for d in range(4):
        view=S.world(123900+d)
        for s in view.held:
            if cold.infer(view,s)!=models["NUMERIC_FACTOR_GROW"].infer(view,s):
                raise AssertionError("WSP123_COLD_FIT_PREDICTION_DRIFT")
    if len(models["NUMERIC_FACTOR_GROW"].events)!=60:
        raise AssertionError("WSP123_SOURCE_BUDGET_DRIFT")
    transfer=_score_worlds(models,"transfer")
    offfamily=_score_worlds(models,"offfamily")
    for d in range(4):
        view=S.world(123900+d)
        for s in view.held:
            if cold.infer(view,s)!=models["NUMERIC_FACTOR_GROW"].infer(view,s):
                raise AssertionError("WSP123_DOMAIN_INTERFERENCE")
    for name in ARMS:
        if name not in ("NUMERIC_FACTOR_GROW","SYMBOLIC_FACTOR_STRONG"):
            continue
        if (transfer["arms"][name]["correct"]!=16384
                or transfer["arms"][name]["wrong_confident"]!=0
                or offfamily["arms"][name]["wrong_confident"]!=1024):
            raise AssertionError("WSP123_STRONG_ARM_COHORT_CONTRACT_DRIFT")
    n, strong=transfer["arms"]["NUMERIC_FACTOR_GROW"],transfer["arms"]["SYMBOLIC_FACTOR_STRONG"]
    if n!=strong:
        raise AssertionError("WSP123_STRONG_CONTROL_TIE_REQUIRED")
    # A reset/no-update baseline must not produce unsupported predictions.
    if transfer["arms"]["NO_UPDATE"]["abstained"]!=16384:
        raise AssertionError("WSP123_NO_UPDATE_NEGATIVE")
    fit_counts={name:{"correct":sum(row["scores"][name]["correct"] for row in fit),
                      "wrong_confident":sum(row["scores"][name]["wrong_confident"] for row in fit),
                      "abstained":sum(row["scores"][name]["abstained"] for row in fit)}
                for name in ARMS}
    for name in ("NUMERIC_FACTOR_GROW","SYMBOLIC_FACTOR_STRONG"):
        if fit_counts[name] != {"correct":64,"wrong_confident":0,"abstained":0}:
            raise AssertionError("WSP123_FIT_CONTRACT")
    return {
        "schema":"wsp123.engineering-intervention-transfer.v1",
        "status":"DEVELOPMENT_INFORMATION_ONLY",
        "scientific_pass":False,"source_first_use":False,"native_admission":False,
        "source_generation":"independently coded but inspectable source; not sealed",
        "fit_source_calls":60,"fit_held":64,
        "fit":fit_counts,"fit_receipts_sha256":S.digest(
            [[r["domain"],r["evidence"]] for r in fit]),
        "transfer":transfer,"offfamily":offfamily,
        "native_int32_slots":4*16,"native_slot_bytes_only":4*4*16,
        "evidence_rows":60,"cold_retention":True,"domain_interference":False,
        "strong_control_parity":True,
        "limitations":[
          "XOR factor-separability prior is supplied; no new unsupplied primitive invented",
          "Hidden numeric row/column coefficients and correct pair table not supplied",
          "Equal-information optimized symbolic factor solver ties all positive answers",
          "Off-family negative worlds reveal confident errors on unseen interactions",
          "No original scientific first-use, trained conventional model or sealed source",
          "No matched process cost, calibrated energy, full process RSS or AGI claim",
        ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering-only",action="store_true",required=True)
    args=parser.parse_args()
    result=run_engineering()
    print("WSP123_ENGINEERING_JSON="+S.canonical(result))


if __name__=="__main__":
    main()
