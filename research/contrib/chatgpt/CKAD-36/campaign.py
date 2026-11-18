"""CKAD36 source-only active interventions on cold native causal memory.

External research only. Active intervention ranking is a conventional
source-consistent analogue committee over existing cold native checkpoints.
No native weights are modified from inferred counterfactuals; donor mapping,
OOD family and held labels are never model-visible.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_cumulative_learner import coordinates

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"CKAD-35"/"campaign.py"
SPEC=importlib.util.spec_from_file_location("ckad36_native_predecessor",PARENT)
C35=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C35)

SCHEMA="yggdrasil.ckad36.active-causal-probes.v1"
PREREG="029d74fe45f62ca7c0764b137136696761652ad3"
PILOT=(13961,13962)
PRIMARY=(23961,23962,23963)
FAMILIES=("isomorphic","quartic_shift")
POLICIES=("active","fixed","random")
ARM_NAMES=("analogue","native_target","target_gf2","polynomial_logistic",
           "frequency","sham","conventional_active","initial10")
TARGETS=C35.TARGETS
DONORS=C35.DONORS
PRESSURE=C35.PRESSURE
GRAPHS=C35.GRAPH


def order(*parts):
    return C35.seed_int("ckad36-independent-source-input-v1",*parts)


def design(seed):
    """Input-only immutable split, independent of ALL synthetic consequences."""
    donor,_,_,_=C35.source_partition(seed)
    pool=sorted(range(64),key=lambda x:(order("target-split",seed,x),x))
    initial=tuple(pool[:10])
    held=tuple(pool[10:26])
    choices=tuple(pool[26:])
    if len(choices)!=38 or len(held)!=16 or len(set(initial+held+choices))!=64:
        raise AssertionError("CKAD36_PUBLIC_INPUT_SPLIT_INVALID")
    return donor,initial,held,choices


def source_memory(seed,donor_inputs):
    """Fit only witnessed donor rules; byte-pin and retain old numeric state."""
    model=NativeContextAccumulator(5)
    source={s:C35.public_rows(seed,s,donor_inputs) for s in DONORS}
    for s in DONORS:model=C35.native_stage(model,s,source[s],3)
    donor_source_sha=digest(model.checkpoint())
    cold=NativeContextAccumulator.restore(model.checkpoint(),donor_source_sha)
    donor_tables=[[C35.native_prob(cold,s,x) for x in range(64)] for s in DONORS]
    independently_fitted=[[C35.predict_independent(C35.fit_independent(source[s]),x)
                           for x in range(64)] for s in DONORS]
    if donor_tables!=independently_fitted or any(
        p not in (0.,1.) for table in donor_tables for p in table
    ):raise AssertionError("CKAD36_UNQUALIFIED_SOURCE_DONOR_PARITY")
    baseline=[[C35.native_prob(cold,s,x) for x in range(64)] for s in DONORS]
    pressure={s:C35.public_rows(seed,s,donor_inputs) for s in PRESSURE}
    for s in PRESSURE:cold=C35.native_stage(cold,s,pressure[s],3)
    raw=cold.checkpoint()
    restored=NativeContextAccumulator.restore(raw,digest(raw))
    if restored.checkpoint()!=raw or any(
        baseline[s]!=[C35.native_prob(restored,s,x) for x in range(64)]
        for s in DONORS
    ):raise AssertionError("CKAD36_COLD_DONOR_INTERFERENCE")
    for s in (*DONORS,*PRESSURE):
        a,r=coordinates(s)
        if restored.profile_info(a,retained=r)["source_records"]!=42:
            raise AssertionError("CKAD36_DONOR_OR_PRESSURE_SOURCE_LOSS")
    conflict=[list(source[0][0])];conflict[0][2]^=1
    before=restored.checkpoint()
    try:C35.native_stage(restored,0,conflict,3)
    except ValueError:pass
    else:raise AssertionError("CKAD36_CONFLICTING_SOURCE_ADMITTED")
    if restored.checkpoint()!=before:
        raise AssertionError("CKAD36_CONTRADICTORY_WRITE_CHANGED_WEIGHTS")
    return donor_tables,independently_fitted,source,pressure,{
        "donor_source_sha256":donor_source_sha,
        "post_pressure_checkpoint_sha256":digest(raw),
        "post_pressure_checkpoint_bytes":len(raw),
        "cold_restore_exact":True,
        "all_64_donor_readouts_retained":True,
        "contradiction_atomic":True,
    }


def bitmaps(donor_tables):
    """23040 conventional relabeled donor hypotheses as 64-bit action tables."""
    if len(donor_tables)!=3 or any(len(t)!=64 for t in donor_tables):
        raise ValueError("CKAD36_DONOR_TABLE_SHAPE")
    rows=[]
    for donor in DONORS:
        for perm,mask,flip in C35.TRANSFORMS:
            bits=0
            for x in range(64):
                bits|=(int(donor_tables[donor][C35.context_transform(x,perm,mask)])
                       ^flip)<<x
            rows.append(bits)
    if len(rows)!=23040:
        raise AssertionError("CKAD36_CONVENTIONAL_COMMITTEE_SIZE")
    return tuple(rows)


def filter_known(hypotheses,source):
    """Observations are a list of (public input, authentic consequence) pairs."""
    remaining=hypotheses
    for x,y in source:
        if type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1):
            raise ValueError("CKAD36_UNTRUSTED_OBSERVATION")
        remaining=tuple(h for h in remaining if (h>>x)&1==y)
    return remaining


def entropy_probe(remaining,unqueried,seed,slot,iteration):
    """Choose the most outcome-discriminating input, never inspect its outcome."""
    if not unqueried:raise ValueError("CKAD36_NO_PUBLIC_PROBE_LEFT")
    n=len(remaining)
    if n==0:
        return min(unqueried,key=lambda x:(order("empty-posterior",seed,slot,iteration,x),x))
    def priority(x):
        ones=sum((h>>x)&1 for h in remaining)
        return (-ones*(n-ones),order("entropy-tie",seed,slot,iteration,x),x)
    return min(unqueried,key=priority)


def distribution(hypotheses,held):
    if not hypotheses:return [.5]*len(held)
    n=len(hypotheses)
    return [sum((h>>x)&1 for h in hypotheses)/n for x in held]


def public_interventions(seed,slot,initial,choices,policy,hypotheses,held):
    """Allocate exactly 6 source probes from the 38 allowed, not held inputs."""
    if policy not in POLICIES:raise ValueError("CKAD36_UNKNOWN_POLICY")
    observed=[(x,C35.reveal(seed,slot,x)) for x in initial]
    current=filter_known(hypotheses,observed)
    initial_prob=distribution(current,held)
    remaining=list(choices)
    r=random.Random(order("random-action-seed",seed,slot))
    random_choices=r.sample(remaining,6) if policy=="random" else None
    actions=[];trace=[]
    for i in range(6):
        before=len(current)
        if policy=="active":
            action=entropy_probe(current,remaining,seed,slot,i)
        elif policy=="fixed":
            action=remaining[0]
        else:
            action=random_choices[i]
        if action not in remaining or action in initial or action in held:
            raise AssertionError("CKAD36_PROBE_HELD_OR_DUPLICATED")
        remaining.remove(action)
        outcome=C35.reveal(seed,slot,action)
        current=filter_known(current,[(action,outcome)])
        actions.append([action,outcome])
        trace.append({"action":action,"outcome":outcome,
                      "posterior_before":before,"posterior_after":len(current)})
    return {
        "initial_source":[[x,y] for x,y in observed],
        "actions":actions,"source_trace":trace,
        "initial10_forecast":initial_prob,
        "forecast":distribution(current,held),
        "initial_survivors":len(filter_known(hypotheses,observed)),
        "final_survivors":len(current),
        "source_count":16
    }


def target_controls(seed,policy_data,held):
    """Each policy independently fits controls on precisely its own 16 witnesses."""
    fit={};cal={}
    for slot in TARGETS:
        d=policy_data[str(slot)]
        fit[slot]=[[x&31,x>>5,y] for x,y in d["initial_source"]]
        cal[slot]=[[x&31,x>>5,y] for x,y in d["actions"]]
    native,info=C35.native_target_control(seed,fit,cal,held)
    if not info["cold_exact"]:
        raise AssertionError("CKAD36_TARGET_NATIVE_COLD")
    controls={}
    for slot in TARGETS:
        rows=fit[slot]+cal[slot]
        pivots=C35.fit_independent(rows)
        logit=C35.logistic_fit(rows)
        controls[str(slot)]={
            "native_target":native[slot],
            "target_gf2":[C35.predict_independent(pivots,x) for x in held],
            "polynomial_logistic":[C35.logistic_prob(logit,x) for x in held],
            "frequency":[C35.source_frequency(rows,x) for x in held],
            "sham":[.5]*len(held)
        }
    return controls,info


def _development_fixture_or_science(seed):
    """Internal full pipeline permits fresh non-pilot DEV fixtures only in tests."""
    t0,c0=time.perf_counter(),time.process_time()
    donor,initial,held,choices=design(seed)
    donor_tables,conv_tables,source,pressure,custody=source_memory(seed,donor)
    native_bitmaps=bitmaps(donor_tables)
    conventional_bitmaps=bitmaps(conv_tables)
    if native_bitmaps!=conventional_bitmaps:
        raise AssertionError("CKAD36_SOURCE_CONVENTIONAL_HYPOTHESIS_DRIFT")
    all_data={};policy_controls={};target_cold={}
    for policy in POLICIES:
        cases={}
        for slot in TARGETS:
            candidate=public_interventions(seed,slot,initial,choices,policy,
                                           native_bitmaps,held)
            # Strongest conventional ACTIVE policy is independently trained
            # on source-identical donor GF2 and must match actions/answers.
            if policy=="active":
                traditional=public_interventions(seed,slot,initial,choices,policy,
                                                 conventional_bitmaps,held)
                if traditional!=candidate:
                    raise AssertionError("CKAD36_CONVENTIONAL_ACTIVE_NOT_IDENTICAL")
            cases[str(slot)]=candidate
        all_data[policy]=cases
        controls,target_cold[policy]=target_controls(seed,cases,held)
        policy_controls[policy]=controls
    truth={str(slot):[C35.reveal(seed,slot,x) for x in held] for slot in TARGETS}
    forecasts={};held_truth={};metrics={};coverage={};wrong={}
    for family_idx,family in enumerate(FAMILIES):
        slots=tuple(range(3+3*family_idx,6+3*family_idx))
        held_truth[family]=[[truth[str(s)][i] for s in slots] for i in range(len(held))]
        forecasts[family]={};metrics[family]={};coverage[family]={};wrong[family]={}
        for policy in POLICIES:
            cases=all_data[policy];controls=policy_controls[policy]
            by_arm={}
            for arm in ARM_NAMES:
                row=[]
                for i in range(len(held)):
                    vals=[]
                    for s in slots:
                        if arm=="analogue" or arm=="conventional_active":
                            pred=cases[str(s)]["forecast"][i]
                        elif arm=="initial10":
                            pred=cases[str(s)]["initial10_forecast"][i]
                        else:
                            pred=controls[str(s)][arm][i]
                        vals.append(pred)
                    row.append(vals)
                by_arm[arm]=row
            forecasts[family][policy]=by_arm
            metrics[family][policy]={};coverage[family][policy]={};wrong[family][policy]={}
            for arm,row in by_arm.items():
                brier=0.;committed=0;errors=0
                for pred,actual in zip(row,held_truth[family]):
                    for p,y in zip(pred,actual):
                        if p<=.1 or p>=.9:
                            committed+=1
                            errors+=int((p>=.5)!=y)
                    for g in GRAPHS:
                        p=C35.C30.composition(g,pred)
                        y=C35.C30.composition(g,actual)
                        if not -1e-9<=p<=1+1e-9:
                            raise AssertionError("CKAD36_COMPOSITE_OUT_OF_RANGE")
                        brier+=(max(0.,min(1.,p))-y)**2
                metrics[family][policy][arm]={"brier":round(brier/48,10),"cases":48}
                coverage[family][policy][arm]=round(committed/48,10)
                wrong[family][policy][arm]=errors
    return {
        "seed":seed,"source_outcomes_per_policy":390,
        "donor_source_outcomes":126,"target_source_outcomes_per_policy":96,
        "pressure_source_outcomes":168,"held_composites_per_family":48,
        "donor_source_inputs":list(donor),"target_initial_inputs":list(initial),
        "target_held_inputs":list(held),"target_action_pool":list(choices),
        "donor_source_witness":{str(s):source[s] for s in DONORS},
        "pressure_source_witness":{str(s):pressure[s] for s in PRESSURE},
        "donor_native_tables":donor_tables,
        "donor_conventional_tables":conv_tables,
        "policy_source_cases":all_data,
        "policy_target_controls":policy_controls,
        "target_native_custody":target_cold,
        "held_truth":held_truth,"held_forecasts":forecasts,
        "metrics":metrics,"committed_coverage":coverage,
        "confident_wrong":wrong,
        "native_custody":custody,
        "cpu_seconds":round(time.process_time()-c0,6),
        "wall_seconds":round(time.perf_counter()-t0,6),
        "primary_scored":False
    }


def score(seed):
    if seed not in PILOT:
        raise ValueError("CKAD36_ONLY_FROZEN_PILOT")
    return _development_fixture_or_science(seed)


def classify(cases):
    if tuple(case["seed"] for case in cases)!=PILOT:
        raise AssertionError("CKAD36_SEED_SCOPE")
    def passes(c):
        a=c["metrics"]["isomorphic"]
        out=c["metrics"]["quartic_shift"]
        active=a["active"]["analogue"]["brier"]
        if not (active<=.08
                and active<=a["fixed"]["analogue"]["brier"]-.03
                and active<=a["random"]["analogue"]["brier"]-.03
                and active<=a["active"]["native_target"]["brier"]-.03
                and active<=a["active"]["target_gf2"]["brier"]-.03
                and active==a["active"]["conventional_active"]["brier"]
                and c["committed_coverage"]["isomorphic"]["active"]["analogue"]>=.5
                and c["confident_wrong"]["isomorphic"]["active"]["analogue"]==0):
            return False
        if not (
            sum(c["policy_source_cases"]["active"][str(s)]["final_survivors"]==0
                for s in (6,7,8))>=2
            and c["confident_wrong"]["quartic_shift"]["active"]["analogue"]==0
            and out["active"]["analogue"]["brier"]<=out["fixed"]["analogue"]["brier"]
        ):return False
        return all(c["native_custody"][k] is True for k in
                   ("cold_restore_exact","all_64_donor_readouts_retained",
                    "contradiction_atomic")) and all(
                    c["target_native_custody"][p]["cold_exact"] for p in POLICIES)
    go=all(passes(c) for c in cases)
    return {"decision":"ENGINEERING_FEASIBLE" if go else "SCREEN_NO_GO",
            "engineering_feasible":go,"scientific_pass":False,
            "conventional_superiority":False,"primary_scored":False}


def locked():
    lock=json.loads((HERE/"source_lock.json").read_text())
    raw=Path(__file__).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if lock["campaign_blob_sha1"]!=sha or lock["prereg_commit"]!=PREREG:
        raise AssertionError("CKAD36_FROZEN_SOURCE_MISMATCH")
    return lock


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("preflight","pilot"),required=True)
    p.add_argument("--seed",type=int)
    a=p.parse_args()
    if a.mode=="preflight":
        if a.seed is not None:raise ValueError("CKAD36_NO_PREFLIGHT_SEED")
        assert len(C35.TRANSFORMS)==7680 and len(POLICIES)==3
        print(json.dumps({"schema":SCHEMA,"mode":"preflight","status":"PASS",
                          "original_seeds_untouched":list(PILOT),
                          "primary_seeds_untouched":list(PRIMARY)},
                         sort_keys=True))
        if (HERE/"source_lock.json").exists():locked()
    else:
        if a.seed not in PILOT:raise ValueError("CKAD36_PILOT_SEED_UNREGISTERED")
        print(json.dumps({"schema":SCHEMA,"mode":"pilot","seed":a.seed,
                          "lock":locked(),"primary_scored":False,
                          "case":score(a.seed)},sort_keys=True,indent=2))


if __name__=="__main__":
    main()
