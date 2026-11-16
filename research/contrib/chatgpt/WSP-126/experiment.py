"""WSP126 source-safe latent interaction-rank growth engineering experiment.

128 independent binary GF2-rank4 causal matrices, 160 actual paid source
interventions per world; a matched optimized symbolic solver, rank-one and
no-update controls; fresh opaque identities and rank5 negatives.
The source is inspectable DEVELOPMENT data, not original held science.
"""
from __future__ import annotations

import argparse

import source as S
import numeric as N
import controls as C

ARMS=("NUMERIC_RANK_GROW","SYMBOLIC_MATCHED","SYMBOLIC_PASSIVE_CONSERVATIVE",
      "RANK1_FIXED","MEMO_ONLY","NO_UPDATE")
MATCHED=("NUMERIC_RANK_GROW","SYMBOLIC_MATCHED","RANK1_FIXED",
         "MEMO_ONLY","NO_UPDATE")
FIELDS=("held","correct","wrong_confident","abstained","source_calls")


def _models():
    return {
        "NUMERIC_RANK_GROW":N.DirectRankGrowth(),
        "SYMBOLIC_MATCHED":C.OptimizedSymbolic(),
        "SYMBOLIC_PASSIVE_CONSERVATIVE":C.OptimizedSymbolic(),
        "RANK1_FIXED":C.RankOneAblation(),
        "MEMO_ONLY":C.MemoOnly(),
        "NO_UPDATE":C.NoUpdate(),
    }


def _scores():
    return {arm:{field:0 for field in FIELDS} for arm in ARMS}


def _collect(scores,arm,result):
    for field in FIELDS:
        scores[arm][field]+=result[field]


def _fit(models):
    summary=_scores()
    receipts=[]
    ranks={rank:0 for rank in range(5)}
    cost=0
    for law in range(128):
        public=S.world(132000+law)
        cust={arm:S.Custodian(public) for arm in ARMS}
        pending=set(public.legal)
        passive=C.passive_actions(public)
        if len(passive)!=160 or len(set(passive))!=160:
            raise AssertionError("WSP126_PASSIVE_SOURCE_BUDGET")
        for step in range(160):
            subject=models["NUMERIC_RANK_GROW"].choose(public,pending)
            if subject is None or subject not in pending:
                raise AssertionError("WSP126_SOURCE_CHOICE_INVALID")
            pending.remove(subject)
            for arm in MATCHED:
                evidence=cust[arm].query(subject)
                models[arm].observe(public,evidence)
            evidence=cust["SYMBOLIC_PASSIVE_CONSERVATIVE"].query(passive[step])
            models["SYMBOLIC_PASSIVE_CONSERVATIVE"].observe(public,evidence)
        cost+=160
        if models["NUMERIC_RANK_GROW"].choose(public,pending) is not None:
            raise AssertionError("WSP126_SOURCE_BUDGET_EXCEEDED")
        matched_receipts={cust[arm].receipt for arm in MATCHED}
        if len(matched_receipts)!=1:
            raise AssertionError("WSP126_MATCHED_SOURCE_TRANSCRIPTS_DIFFER")
        per_arm={}
        for arm in ARMS:
            predictions={subject:models[arm].infer(public,subject)
                         for subject in cust[arm].held}
            scored=cust[arm].score_once(predictions)
            if scored["held"]!=96 or scored["source_calls"]!=160:
                raise AssertionError("WSP126_FIT_HELD_COUNT_INVALID")
            per_arm[arm]=scored
            _collect(summary,arm,scored)
        strong=per_arm["SYMBOLIC_MATCHED"]
        native=per_arm["NUMERIC_RANK_GROW"]
        if (native["correct"],native["wrong_confident"],native["abstained"])!=(
                strong["correct"],strong["wrong_confident"],strong["abstained"]):
            raise AssertionError("WSP126_NUMERIC_STRONG_CONTROL_PARITY")
        rank=len(models["NUMERIC_RANK_GROW"]._state(law).factors)
        ranks[rank]+=1
        receipts.append([law,next(iter(matched_receipts)),
                         rank,[(per_arm[arm]["correct"],
                                per_arm[arm]["wrong_confident"],
                                per_arm[arm]["abstained"]) for arm in ARMS]])
    if cost!=20480 or summary["NUMERIC_RANK_GROW"]["wrong_confident"]!=0:
        raise AssertionError("WSP126_SOURCE_BUDGET_OR_CONFIDENT_ERROR")
    return {"arms":summary,"rank_histogram":ranks,
            "rows_sha256":S.digest(receipts),"calls_per_arm":cost}


def _holdout(models,cohort):
    if cohort=="transfer":
        seeds=range(133000,133256)
    elif cohort=="negative":
        seeds=range(134000,134064)
    else:
        raise ValueError("WSP126_BAD_COHORT")
    scores=_scores()
    receipts=[]
    for seed in seeds:
        public=S.world(seed)
        per_arm={}
        for arm in ARMS:
            cust=S.Custodian(public)
            if cust.budget!=0 or public.legal or len(cust.held)!=256:
                raise AssertionError("WSP126_TRANSFER_MUST_BE_ZERO_SOURCE")
            predictions={subject:models[arm].infer(public,subject)
                         for subject in cust.held}
            scored=cust.score_once(predictions)
            if scored["source_calls"]!=0 or scored["held"]!=256:
                raise AssertionError("WSP126_TRANSFER_SOURCE_USED")
            per_arm[arm]=scored
            _collect(scores,arm,scored)
        if (per_arm["NUMERIC_RANK_GROW"]["correct"],
            per_arm["NUMERIC_RANK_GROW"]["wrong_confident"],
            per_arm["NUMERIC_RANK_GROW"]["abstained"]) != (
            per_arm["SYMBOLIC_MATCHED"]["correct"],
            per_arm["SYMBOLIC_MATCHED"]["wrong_confident"],
            per_arm["SYMBOLIC_MATCHED"]["abstained"]):
            raise AssertionError("WSP126_TRANSFER_OPTIMIZED_SYMBOLIC_PARITY")
        receipts.append([
            seed,per_arm["NUMERIC_RANK_GROW"]["public_sha256"],
            per_arm["NUMERIC_RANK_GROW"]["source_sha256"],
            [(per_arm[arm]["correct"],per_arm[arm]["wrong_confident"],
              per_arm[arm]["abstained"]) for arm in ARMS]
        ])
    return {"worlds":len(receipts),"scores":scores,
            "rows_sha256":S.digest(receipts),"source_calls":0}


def run_engineering():
    if S.ALLOWED & (S.ORIGINAL|S.PROTECTED):
        raise PermissionError("WSP126_COHO​RT_SOURCE_OVERLAP")
    models=_models()
    fit=_fit(models)
    numeric=models["NUMERIC_RANK_GROW"]
    snapshot=numeric.snapshot()
    cold=N.DirectRankGrowth.restore(snapshot)
    if snapshot!=cold.snapshot():
        raise AssertionError("WSP126_COLD_SNAPSHOT_DRIFT")
    for law in range(128):
        view=S.world(132000+law)
        for subject,_,_ in view.records:
            if numeric.infer(view,subject)!=cold.infer(view,subject):
                raise AssertionError("WSP126_COLD_RETAINED_LAW_DRIFT")
    transfer=_holdout(models,"transfer")
    negative=_holdout(models,"negative")
    for law in range(128):
        view=S.world(132000+law)
        for subject,_,_ in view.records:
            if numeric.infer(view,subject)!=cold.infer(view,subject):
                raise AssertionError("WSP126_POST_INTERFERENCE_RETENTION_FAIL")
    native=fit["arms"]["NUMERIC_RANK_GROW"]
    transferred=transfer["scores"]["NUMERIC_RANK_GROW"]
    development_pass=(
        native["held"]==12288 and native["correct"]>=11674 and
        native["wrong_confident"]==0 and
        transferred["held"]==65536 and transferred["correct"]>=63570 and
        transferred["wrong_confident"]==0 and
        fit["rank_histogram"][4]>=118 and
        numeric.factor_slots>0
    )
    return {
        "schema":"wsp126.latent-rank-growth.engineering.v1",
        "status":"DEVELOPMENT_GO" if development_pass else "DEVELOPMENT_NO_GO",
        "scientific_pass":False,"source_first_use":False,"native_admission":False,
        "fit":fit,"transfer":transfer,"offfamily":negative,
        "number_of_laws":128,"feature_slots":numeric.factor_slots,
        "row_code_slots":numeric.row_code_slots,
        "coefficient_bytes_only":4*(numeric.factor_slots+numeric.row_code_slots),
        "cold_retention":True,"interference_detected":False,
        "unique_numerical_gain":False,
        "passive_policy_qualified":False,
        "limitations":[
            "Supplied GF2 and rank<=4 physics, source factors and row codes unknown",
            "Passive full rank4 matrix completion unqualified; no policy gain claim",
            "Exact optimized matched symbolic uses same observations, ties",
            "Transfer worlds are relabeled 128 laws, not new physical causal laws",
            "Negative rank5 violates supplied maximum rank, errors retained",
            "No independently trained conventional or original science first use",
            "No matched whole-process resource or native deployment claim",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering-only",action="store_true",required=True)
    parser.parse_args()
    print("WSP126_ENGINEERING_JSON="+S.canonical(run_engineering()))


if __name__=="__main__":
    main()
