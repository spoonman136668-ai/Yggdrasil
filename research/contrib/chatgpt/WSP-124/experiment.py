"""WSP124 preregistered largest-first *engineering-only* causal-repair screen.

16 independent hidden-threshold domains, 23 paid source actions each,
1,024 unfamiliar-identity transfer worlds and 256 off-family negative worlds.
No original science first-use, native weight promotion or hidden-label import
by learners. Reporting is observation- and cost-honest development only.
"""
from __future__ import annotations
import argparse

import source as S
import numeric as N
import controls as C

ARMS=("NUMERIC_REPAIR","SYMBOLIC_STRONG","SYMBOLIC_PASSIVE",
      "XOR_ONLY","NO_UPDATE")
ACTIVE=("NUMERIC_REPAIR","SYMBOLIC_STRONG","XOR_ONLY","NO_UPDATE")


def _models():
    return {"NUMERIC_REPAIR":N.NumericRepair(),
            "SYMBOLIC_STRONG":C.StrongSymbolic(),
            "SYMBOLIC_PASSIVE":C.StrongSymbolic(),
            "XOR_ONLY":C.XorOnly(),
            "NO_UPDATE":C.NoUpdate()}


def _fit(models):
    receipts=[]
    scores={name:{"held":0,"correct":0,"wrong_confident":0,"abstained":0}
            for name in ARMS}
    actions=0
    for d in range(16):
        public=S.world(128900+d)
        owners={name:S.Custodian(public) for name in ARMS}
        pending=set(public.legal)
        passive=C.passive_order(public)
        if len(passive)!=23 or len(set(passive))!=23:
            raise AssertionError("WSP124_PASSIVE_BUDGET")
        for step in range(23):
            subject=models["NUMERIC_REPAIR"].choose(public,pending)
            if subject is None or subject not in pending:
                raise AssertionError("WSP124_ACTIVE_ACTION_EXHAUSTED")
            pending.remove(subject)
            for name in ACTIVE:
                observation=owners[name].query(subject)
                models[name].observe(public,observation)
            passive_observation=owners["SYMBOLIC_PASSIVE"].query(passive[step])
            models["SYMBOLIC_PASSIVE"].observe(public,passive_observation)
        actions+=23
        if models["NUMERIC_REPAIR"].choose(public,pending) is not None:
            raise AssertionError("WSP124_ACTIVE_QUERY_BUDGET_EXCEEDED")
        active_receipts={owners[name].receipt for name in ACTIVE}
        if len(active_receipts)!=1:
            raise AssertionError("WSP124_MATCHED_EVIDENCE_RECEIPT")
        per_arm={}
        for name in ARMS:
            owner=owners[name]
            predictions={subject:models[name].infer(public,subject)
                         for subject in owner.held}
            scored=owner.score_once(predictions)
            if scored["held"]!=41 or scored["source_calls"]!=23:
                raise AssertionError("WSP124_FIT_HELD_OR_ACTIONS")
            per_arm[name]=scored
            for field in scores[name]:
                scores[name][field]+=scored[field]
        if per_arm["NUMERIC_REPAIR"]!=per_arm["SYMBOLIC_STRONG"]:
            raise AssertionError("WSP124_STRONG_CONTROL_FIT_PARITY")
        if models["SYMBOLIC_STRONG"].candidate_count(d)!=1:
            raise AssertionError("WSP124_ACTIVE_REPAIR_NOT_IDENTIFIED")
        receipts.append([d,next(iter(active_receipts)),
                         [per_arm[n]["correct"] for n in ARMS],
                         [per_arm[n]["wrong_confident"] for n in ARMS],
                         [per_arm[n]["abstained"] for n in ARMS]])
    if actions!=368 or scores["NUMERIC_REPAIR"]!={
            "held":656,"correct":656,"wrong_confident":0,"abstained":0}:
        raise AssertionError("WSP124_PRIMARY_FIT_DEVELOPMENT_THRESHOLD")
    return scores,S.digest(receipts),actions


def _cohort(models,kind):
    if kind=="transfer":
        seeds=range(129000,130024)
    elif kind=="offfamily":
        seeds=range(130100,130356)
    else:
        raise ValueError("WSP124_BAD_COHORT")
    summary={name:{"held":0,"correct":0,"wrong_confident":0,
                   "abstained":0,"source_calls":0} for name in ARMS}
    rows=[]
    count=0
    for seed in seeds:
        view=S.world(seed)
        per_arm={}
        for name in ARMS:
            # No fit-time source labels can be read in transfer worlds.
            owner=S.Custodian(view)
            if owner.budget!=0 or view.legal or len(owner.held)!=64:
                raise AssertionError("WSP124_ZERO_SHOT_SOURCE_CONTRACT")
            predictions={s:models[name].infer(view,s) for s in owner.held}
            scored=owner.score_once(predictions)
            per_arm[name]=scored
            for field in summary[name]:
                summary[name][field]+=scored[field]
        if per_arm["NUMERIC_REPAIR"]!=per_arm["SYMBOLIC_STRONG"]:
            raise AssertionError("WSP124_NEW_ENTITY_STRONG_PARITY")
        rows.append([seed,per_arm["NUMERIC_REPAIR"]["public_sha256"],
                     per_arm["NUMERIC_REPAIR"]["source_sha256"],
                     [per_arm[n]["correct"] for n in ARMS],
                     [per_arm[n]["wrong_confident"] for n in ARMS],
                     [per_arm[n]["abstained"] for n in ARMS]])
        count+=1
    return {"worlds":count,"rows_sha256":S.digest(rows),"arms":summary}


def run_engineering():
    if S.FIT & (S.ORIGINAL|S.PROTECTED) or S.TRANSFER & S.OFFFAMILY:
        raise PermissionError("WSP124_COHORT_FENCE")
    models=_models()
    fit,fit_digest,actions=_fit(models)
    numerical=models["NUMERIC_REPAIR"]
    cold=N.NumericRepair.restore(numerical.snapshot())
    if len(numerical.events)!=368 or sum(numerical.counts)!=368:
        raise AssertionError("WSP124_MISSING_SOURCE_EVIDENCE")
    for domain in range(16):
        source_view=S.world(128900+domain)
        for subject,_,_ in source_view.records:
            if cold.infer(source_view,subject)!=numerical.infer(source_view,subject):
                raise AssertionError("WSP124_COLD_DOMAIN_INTERFERENCE")
    transfer=_cohort(models,"transfer")
    off=_cohort(models,"offfamily")
    primary=transfer["arms"]["NUMERIC_REPAIR"]
    if (primary["held"],primary["correct"],
            primary["wrong_confident"],primary["source_calls"])!=(
            65536,65536,0,0):
        raise AssertionError("WSP124_IN_FAMILY_TRANSFER_THRESHOLD")
    unfamiliar=off["arms"]["NUMERIC_REPAIR"]
    if (unfamiliar["held"],unfamiliar["correct"],
            unfamiliar["wrong_confident"])!=(16384,12288,4096):
        raise AssertionError("WSP124_OFF_FAMILY_NEGATIVE_MISSING")
    if transfer["arms"]["NO_UPDATE"]["abstained"]!=65536:
        raise AssertionError("WSP124_NO_UPDATE_NEGATIVE")
    return {
       "schema":"wsp124.causal-structure-repair.engineering.v1",
       "status":"DEVELOPMENT_INFORMATION_ONLY",
       "scientific_pass":False,"source_first_use":False,"native_admission":False,
       "fit_source_calls":actions,"fit_scores":fit,
       "fit_receipts_sha256":fit_digest,
       "transfer":transfer,"offfamily":off,
       "independent_domains":16,"native_int32_slots":304,
       "native_slot_bytes_only":1216,"evidence_rows":368,
       "cold_retention":True,"domain_interference":False,
       "strong_symbolic_tie":True,
       "limitations":[
         "8x8 public typed relationships and conditional rectangle grammar pre-supplied",
         "XOR primitive, binary threshold search and 3-bit effect alphabet supplied",
         "Distinct thresholds/deltas inferred from charged consequences, not named in learner",
         "Source entirely inspectable engineering code; no independent original held source",
         "Equally expressive symbolic constraint model may tie all correct outcomes",
         "Off-family parity interaction causes confident errors and proves class limitation",
         "No fully trained conventional, native integration or calibrated RSS/energy",
         "No numerical speed superiority or intelligence claim",
       ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--engineering-only",action="store_true",required=True)
    parser.parse_args()
    print("WSP124_ENGINEERING_JSON="+S.canonical(run_engineering()))


if __name__=="__main__":
    main()
