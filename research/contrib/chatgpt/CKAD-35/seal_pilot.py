"""CKAD35 independent evidence sealer: never imports generator or native learner.

Reconstructs all target analogical forecasts from original donor-source
witnesses and independent GF2; independently recomputes all held Brier,
confidence and abstention counts from original byte-for-byte evaluator receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SEEDS=(13851,13852)
DONORS=(0,1,2)
TARGETS=(3,4,5,6,7,8)
PRESSURE=(9,10,11,12)
FAMILIES=("isomorphic","quartic_shift")
ARMS={"native_analogy","conventional_analogy","native_target_only",
      "conventional_target_gf2","polynomial_logistic","smoothed_frequency",
      "sham","ungated_native_analogy"}
MONOMIALS=tuple(m for m in range(64) if m.bit_count()<=3)
TRANSFORMS=tuple((p,m,f) for p in itertools.permutations(range(5))
                 for m in range(32) for f in (0,1))


def require(ok,name):
    if not ok:raise ValueError("CKAD35_INDEPENDENT_AUDIT_"+name)


def model_fit(records):
    pivots={}
    seen=set()
    for c,a,y in records:
        x=c|(a<<5)
        require(x not in seen and type(y) is int and y in (0,1),"SOURCE_DUPLICATE")
        seen.add(x)
        r=sum(1<<i for i,t in enumerate(MONOMIALS) if (x&t)==t)
        v=r
        rhs=y
        while v:
            k=v.bit_length()-1
            if k not in pivots:
                pivots[k]=(v,rhs)
                break
            v^=pivots[k][0]
            rhs^=pivots[k][1]
        if not v and rhs:
            raise ValueError("CKAD35_INDEPENDENT_AUDIT_SOURCE_INCONSISTENT")
    return pivots


def model_read(pivots,x):
    v=sum(1<<i for i,t in enumerate(MONOMIALS) if (x&t)==t)
    y=0
    while v:
        k=v.bit_length()-1
        if k not in pivots:return .5
        p,rhs=pivots[k]
        v^=p
        y^=rhs
    return float(y)


def relabel(x,perm,mask):
    context=sum(((x>>source)&1)<<dest for dest,source in enumerate(perm))
    return ((context^mask)&31)|(x&32)


def donor_transfer(tables,fit,cal,held,check_cal=True):
    observed=[(c|(a<<5),y) for c,a,y in fit]
    validation=[(c|(a<<5),y) for c,a,y in cal]
    def probability(d,p,m,f,x):
        return int(tables[d][relabel(x,p,m)])^f
    prior=[]
    for d in DONORS:
        for p,m,f in TRANSFORMS:
            if all(probability(d,p,m,f,x)==y for x,y in observed):
                prior.append((d,p,m,f))
    compatible=([h for h in prior
                 if all(probability(*h,x)==y for x,y in validation)]
                if check_cal else prior)
    preds=[sum(probability(*h,x) for h in compatible)/len(compatible)
           if compatible else .5 for x in held]
    return preds,{"fit_survivors":len(prior),"calibrated_survivors":len(compatible),
                  "zero_survivor_veto":not compatible}


def compose(graph,vals):
    a,b,c=vals
    if graph=="xor3":return a+b+c-2*(a*b+a*c+b*c)+4*a*b*c
    if graph=="majority3":return a*b+a*c+b*c-2*a*b*c
    if graph=="gate3":return a*b+c-2*a*b*c
    raise ValueError("CKAD35_UNKNOWN_COMPOSITE_GRAPH")


def sha256_ok(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)


def source_check(name,entry,slots,width,public):
    require(set(entry)=={str(s) for s in slots},name+"_SLOTS")
    for slot in slots:
        rows=entry[str(slot)]
        require(type(rows) is list and len(rows)==width,name+"_ROW_COUNT")
        require([c|(a<<5) for c,a,y in rows]==public,name+"_PUBLIC_INPUT_ORDER")
        require(all(type(r) is list and len(r)==3 and type(r[0]) is int and
                    0<=r[0]<32 and type(r[1]) is int and r[1] in (0,1) and
                    type(r[2]) is int and r[2] in (0,1)
                    for r in rows),name+"_BINARY_REVEALED_DATA")


def read_pilot(raw,seed,lock):
    doc=json.loads(raw)
    require(doc.get("schema")=="yggdrasil.ckad35.cold-relational-transfer.v1"
            and doc.get("mode")=="pilot" and doc.get("seed")==seed
            and doc.get("primary_scored") is False
            and doc.get("lock")==lock,"EXACT_FROZEN_ENVELOPE")
    c=doc["case"]
    require(c["seed"]==seed and c["primary_scored"] is False and
            c["source_outcomes"]==390 and c["donor_source_outcomes"]==126
            and c["target_source_outcomes"]==96 and c["pressure_source_outcomes"]==168
            and c["held_composites_each_family"]==48,"BUDGET")
    donor=c["donor_public_inputs"];fit=c["target_fit_inputs"]
    cal=c["target_calibration_inputs"];held=c["target_held_inputs"]
    require(len(donor)==42 and len(set(donor))==42 and
            len(fit)==10 and len(cal)==6 and len(held)==16 and
            len(set(fit+cal+held))==32 and
            all(type(x) is int and 0<=x<64 for x in donor+fit+cal+held),
            "SOURCE_SPLIT_AND_HELD_DISJOINT")
    source_check("DONOR",c["donor_source_witness"],DONORS,42,donor)
    source_check("TARGET_FIT",c["target_fit_witness"],TARGETS,10,fit)
    source_check("TARGET_CAL",c["target_calibration_witness"],TARGETS,6,cal)
    source_check("PRESSURE",c["pressure_source_witness"],PRESSURE,42,donor)
    native=c["donor_native_tables"]
    conventional=c["donor_conventional_tables"]
    require(len(native)==len(conventional)==3,"THREE_DONOR_TABLES")
    for slot in DONORS:
        independent=model_fit(c["donor_source_witness"][str(slot)])
        require(len(independent)==42,"FULL_SOURCE_DONOR_RANK")
        expected=[model_read(independent,x) for x in range(64)]
        require(len(native[slot])==len(conventional[slot])==64 and
                native[slot]==conventional[slot]==expected
                and all(v in (0,1) for v in native[slot]),
                "INDEPENDENT_DONOR_CONVENTIONAL_PARITY")
    custody=c["native_custody"];target=c["target_native_custody"]
    require(all(custody.get(k) is True for k in
                ("donor_exact_retention","target_exact_retention",
                 "cold_bytes_exact","conflict_atomic"))
            and sha256_ok(custody["source_sha256"])
            and sha256_ok(custody["cold_sha256"]) and custody["cold_bytes"]>0
            and target["cold_exact"] is True
            and sha256_ok(target["checkpoint_sha256"]),"COLD_AND_CONFLICT_CUSTODY")
    require(set(c["target_compatible_counts"])=={str(x) for x in TARGETS},
            "COMPATIBLE_COUNT_SLOTS")
    fit_candidates={}
    for slot in TARGETS:
        f=c["target_fit_witness"][str(slot)]
        k=c["target_calibration_witness"][str(slot)]
        native_predictions,meta=donor_transfer(native,f,k,held)
        control_predictions,meta_c=donor_transfer(conventional,f,k,held)
        ungated,_=donor_transfer(native,f,k,held,check_cal=False)
        require(native_predictions==control_predictions and meta==meta_c
                and c["target_compatible_counts"][str(slot)]==meta,
                "SOURCE_ONLY_ANALOGUE_PARITY")
        require(meta["fit_survivors"]>=meta["calibrated_survivors"]>=0,
                "HYPOTHESIS_MONOTONICITY")
        fit_candidates[slot]={"native":native_predictions,"conventional":control_predictions,
                              "ungated":ungated}
    require(set(c["held_truth"])==set(c["held_forecasts"])==
            set(c["metrics"])==set(c["committed_primitive_coverage"])==
            set(c["confident_primitive_errors"])==set(FAMILIES),"FAMILY_SET")
    for index,family in enumerate(FAMILIES):
        truth=c["held_truth"][family]
        forecasts=c["held_forecasts"][family]
        require(len(truth)==16 and set(forecasts)==
                set(c["metrics"][family])==
                set(c["committed_primitive_coverage"][family])==
                set(c["confident_primitive_errors"][family])==ARMS,
                "SCORE_ARM_SHAPE")
        require(all(len(row)==3 and all(type(y) is int and y in (0,1) for y in row)
                    for row in truth),"HELD_TRUTH_BINARY")
        for arm,values in forecasts.items():
            require(len(values)==16 and
                    all(type(row) is list and len(row)==3 and
                        all(type(p) in (float,int) and 0<=p<=1 for p in row)
                        for row in values),"FORECAST_PROBABILITY_RANGE")
            if arm in ("native_analogy","conventional_analogy","ungated_native_analogy"):
                for i in range(16):
                    expected=[]
                    for slot in range(index*3+3,index*3+6):
                        key=("native" if arm=="native_analogy" else
                             "conventional" if arm=="conventional_analogy" else "ungated")
                        expected.append(fit_candidates[slot][key][i])
                    require(all(abs(a-b)<=1e-12 for a,b in zip(values[i],expected)),
                            "AUDITED_HYPOTHESIS_PREDICTION_"+arm)
            confident=0
            errors=0
            numerator=0.
            for actual,predicted in zip(truth,values):
                for y,p in zip(actual,predicted):
                    if p<=.1 or p>=.9:
                        confident+=1
                        errors+=int((p>=.5)!=y)
                for g in ("xor3","majority3","gate3"):
                    p=compose(g,predicted)
                    require(-1e-8<=p<=1+1e-8,"COMPOSED_RANGE")
                    numerator+=(max(0.,min(1.,p))-compose(g,actual))**2
            result=c["metrics"][family][arm]
            require(result["cases"]==48 and
                    abs(result["brier"]-round(numerator/48,10))<=1e-9 and
                    abs(c["committed_primitive_coverage"][family][arm]-round(confident/48,10))<=1e-9 and
                    c["confident_primitive_errors"][family][arm]==errors,
                    "INDEPENDENT_BRIER_AND_COVERAGE_"+family+"_"+arm)
    require(c["wall_seconds"]>=0 and c["cpu_seconds"]>=0,"COST_RECEIPT")
    return c


def frozen_decision(cases):
    require(tuple(c["seed"] for c in cases)==SEEDS,"FROZEN_PILOT_ORDER")
    def passes(c):
        a=c["metrics"]["isomorphic"];o=c["metrics"]["quartic_shift"]
        return (
            a["native_analogy"]["brier"]<=.08
            and a["native_analogy"]["brier"]<=a["native_target_only"]["brier"]-.05
            and a["native_analogy"]["brier"]<=a["conventional_target_gf2"]["brier"]-.05
            and abs(a["native_analogy"]["brier"]-a["conventional_analogy"]["brier"])<=1e-10
            and a["native_analogy"]["brier"]<=a["ungated_native_analogy"]["brier"]
            and c["committed_primitive_coverage"]["isomorphic"]["native_analogy"]>=.5
            and c["confident_primitive_errors"]["isomorphic"]["native_analogy"]==0
            and sum(c["target_compatible_counts"][str(s)]["zero_survivor_veto"]
                    for s in (6,7,8))>=2
            and c["confident_primitive_errors"]["quartic_shift"]["native_analogy"]==0
            and o["native_analogy"]["brier"]<=o["ungated_native_analogy"]["brier"]
        )
    go=all(passes(c) for c in cases)
    return ("ENGINEERING_FEASIBLE" if go else "SCREEN_NO_GO"),go


def expected_report(pairs,lock_raw):
    decision,go=frozen_decision([v for _,_,v in pairs])
    return {
        "schema":"yggdrasil.ckad35.pilot-screen.v1",
        "decision":decision,"engineering_feasible":go,
        "scientific_pass":False,"conventional_superiority":False,
        "pilot_seeds":list(SEEDS),"primary_seeds_untouched":[23851,23852,23853],
        "primary_scored":False,
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_receipt_sha256":{str(s):hashlib.sha256(raw).hexdigest() for s,raw,_ in pairs},
        "scores":{str(c["seed"]):{
            "inclass_transfer_brier":c["metrics"]["isomorphic"]["native_analogy"]["brier"],
            "inclass_target_native_brier":c["metrics"]["isomorphic"]["native_target_only"]["brier"],
            "inclass_conventional_target_brier":c["metrics"]["isomorphic"]["conventional_target_gf2"]["brier"],
            "inclass_analogue_conventional_brier":c["metrics"]["isomorphic"]["conventional_analogy"]["brier"],
            "inclass_analogue_commitment":c["committed_primitive_coverage"]["isomorphic"]["native_analogy"],
            "inclass_analogue_false_confident":c["confident_primitive_errors"]["isomorphic"]["native_analogy"],
            "ood_native_transfer_brier":c["metrics"]["quartic_shift"]["native_analogy"]["brier"],
            "ood_ungated_brier":c["metrics"]["quartic_shift"]["ungated_native_analogy"]["brier"],
            "ood_veto_slots":sum(c["target_compatible_counts"][str(s)]["zero_survivor_veto"]
                                  for s in (6,7,8)),
            "ood_false_confident":c["confident_primitive_errors"]["quartic_shift"]["native_analogy"],
            "native_checkpoint_bytes":c["native_custody"]["cold_bytes"],
            "cpu_seconds":c["cpu_seconds"],"wall_seconds":c["wall_seconds"]
        } for _,_,c in pairs}
    }


def audit():
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pair=[]
    for seed in SEEDS:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        pair.append((seed,raw,read_pilot(raw,seed,lock)))
    expected=expected_report(pair,lock_raw)
    require(json.loads((HERE/"pilot_screen_report.json").read_bytes())==expected,
            "GIT_SEALED_REPORT_DISAGREEMENT")
    require(not (HERE/"pilot_certificate.json").exists(),"NO_PRIMARY_SCHEDULER")
    return expected


def seal(root):
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pair=[]
    for seed in SEEDS:
        raw=(root/f"ckad35-pilot-{seed}"/"result.json").read_bytes()
        pair.append((seed,raw,read_pilot(raw,seed,lock)))
    report=expected_report(pair,lock_raw)
    for seed,raw,_ in pair:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    require(audit()==report,"CERTIFICATION_REPEAT_DIFFERENCE")
    print(json.dumps(report,sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path)
    args=p.parse_args()
    print(json.dumps(audit() if args.root is None else seal(args.root),sort_keys=True))


if __name__=="__main__":
    main()
