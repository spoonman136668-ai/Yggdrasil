"""CKAD34 independent cold-evidence audit: no generator, native code or rerun.

Original one-time pilot receipts are kept byte-for-byte in Git. All held
metrics are recomputed from captured evaluator truth and per-arm readouts.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SEEDS=(13741,13742)
FAMILIES=("affine","quadratic","cubic","quartic_ood")
ARMS={"compiled_selected","conventional_mdl","conventional_full_degree3",
      "native_unmodified","polynomial_logistic","smoothed_frequency",
      "sham","compiled_ungated"}
OLD=tuple(range(12))
PRESSURE=tuple(range(12,16))


def require(ok,label):
    if not ok:raise ValueError("CKAD34_EVIDENCE_"+label)


def vector(x,degree):
    masks=[m for m in range(64) if m.bit_count()<=degree]
    return sum(1<<i for i,m in enumerate(masks) if (x&m)==m)


def fit(rows,degree):
    pivots={}
    seen=set()
    for context,action,outcome in rows:
        x=context|(action<<5)
        require(x not in seen and type(outcome) is int and outcome in (0,1),
                "SOURCE_WITNESS_DUP_OR_VALUE")
        seen.add(x)
        row=vector(x,degree)
        rhs=outcome
        while row:
            pivot=row.bit_length()-1
            if pivot not in pivots:
                pivots[pivot]=(row,rhs)
                break
            old,y=pivots[pivot]
            row^=old
            rhs^=y
        if row==0 and rhs:
            return None
    return pivots


def read(pivots,degree,x):
    v=vector(x,degree)
    y=0
    while v:
        pivot=v.bit_length()-1
        if pivot not in pivots:return .5
        row,rhs=pivots[pivot]
        v^=row
        y^=rhs
    return float(y)


def compose(which,triple):
    a,b,c=triple
    if which=="xor3":return a+b+c-2*(a*b+a*c+b*c)+4*a*b*c
    if which=="majority3":return a*b+a*c+b*c-2*a*b*c
    if which=="gate3":return a*b+c-2*a*b*c
    raise ValueError("CKAD34_GRAPH_INVALID")


def check_sha(h):
    return type(h) is str and len(h)==64 and all(c in "0123456789abcdef" for c in h)


def case(raw,seed,lock):
    doc=json.loads(raw)
    require(doc.get("schema")=="yggdrasil.ckad34.source-class-selection.v1"
            and doc.get("mode")=="pilot" and doc.get("seed")==seed
            and doc.get("primary_scored") is False and doc.get("source_lock")==lock,
            "PILOT_IDENTITY")
    c=doc["case"]
    require(c.get("seed")==seed and c["primary_scored"] is False and
            c["public_source_outcomes"]==744 and
            c["old_fit_source_outcomes"]==504 and
            c["old_calibration_source_outcomes"]==72 and
            c["pressure_source_outcomes"]==168 and
            c["held_composites_each_family"]==48,"SOURCE_AND_EVAL_BUDGET")
    xs=c["fit_public_inputs"];cal=c["cal_public_inputs"];held=c["held_inputs"]
    require(len(xs)==42 and len(cal)==6 and len(held)==16 and
            len(set(xs+cal+held))==64 and
            all(type(x) is int and 0<=x<64 for x in xs+cal+held),"NO_HELD_SOURCE_OVERLAP")
    require(len(fit([[x&31,x>>5,0] for x in xs],3))==42,"INPUT_RANK")
    for key,ids,width,expected in (
        ("source_witnesses",OLD,42,xs),
        ("calibration_witnesses",OLD,6,cal),
        ("pressure_witnesses",PRESSURE,42,xs)):
        target=c[key]
        require(set(target)=={str(s) for s in ids},"WITNESS_SLOTS_"+key)
        for slot in ids:
            rows=target[str(slot)]
            require(len(rows)==width and all(type(r) is list and len(r)==3
                    for r in rows) and
                    [r[0]|(r[1]<<5) for r in rows]==expected and
                    all(type(r[0]) is int and 0<=r[0]<32 and
                        type(r[1]) is int and r[1] in (0,1) and
                        type(r[2]) is int and r[2] in (0,1) for r in rows),
                    "WITNESS_INTEGRITY_"+key)
    choose=c["selected_degrees"];admit=c["source_only_admitted"]
    require(set(choose)==set(admit)=={str(i) for i in OLD}
            and all(type(v) is bool for v in admit.values()),"MODEL_CLASS_FIELDS")
    ct=c["native_checkpoint"]
    require(ct["cold_exact"] is True and ct["retention_all64_exact"] is True
            and ct["conflict_atomic"] is True and ct["pressure_slots"]==4
            and ct["full_checkpoint_bytes"]>0 and
            c["old_native_checkpoint"]["cold_exact"] is True
            and check_sha(c["old_native_checkpoint"]["before_sha256"]),"COLD_AND_PRESSURE")
    require(all(check_sha(ct[k]) for k in
                ("before_pressure_sha256","after_pressure_sha256")),"NUMERIC_SHA")
    require(set(ct["ranks"])==set(choose) and
            set(ct["profile_selected_bytes"])==set(choose) and
            set(ct["profile_fixed_degree3_bytes"])==set(choose),"PROFILE_METADATA")
    for slot in OLD:
        key=str(slot)
        records=c["source_witnesses"][key]
        candidates=[degree for degree in (1,2,3) if fit(records,degree) is not None]
        require(candidates and choose[key]==candidates[0],"HIDDEN_CLASS_OR_NATIVE_SELECTION_DRIFT")
        pivots=fit(records,choose[key])
        require(len(pivots)==ct["ranks"][key],"PROFILE_RANK")
        expected=all(read(pivots,choose[key],r[0]|(r[1]<<5))==float(r[2])
                     for r in c["calibration_witnesses"][key])
        require(expected==admit[key],"PUBLIC_CALIBRATION_GATE")
        require(0<ct["profile_selected_bytes"][key]<=ct["profile_fixed_degree3_bytes"][key],
                "WEIGHT_PROFILE_SIZE")
        # Even evaluator labels are used ONLY here, not for model selection.
        if slot<9:
            require(choose[key]==1+slot//3 and admit[key],"INCLASS_CLASS_DISCRIMINATION")
    require(set(c["metrics"])==set(c["primitive_coverage"])==
            set(c["primitive_confident_wrong"])==set(FAMILIES),"FAMILY_METRIC_SET")
    require(set(c["held_truth"])==set(c["held_forecasts"])==set(FAMILIES),
            "EVALUATOR_CAPTURES")
    for family in FAMILIES:
        truth=c["held_truth"][family]
        forecasts=c["held_forecasts"][family]
        require(len(truth)==16 and
                all(type(row) is list and len(row)==3 and
                    all(type(y) is int and y in (0,1) for y in row)
                    for row in truth),"HELD_TRUTH_SHAPE")
        require(set(forecasts)==set(c["metrics"][family])==ARMS,"ARM_SET")
        require(set(c["primitive_coverage"][family])==
                set(c["primitive_confident_wrong"][family])==ARMS,"ARM_COVERAGE_SET")
        for arm,values in forecasts.items():
            require(len(values)==16 and
                    all(type(row) is list and len(row)==3 and
                        all(type(x) in (float,int) and 0<=x<=1 for x in row)
                        for row in values),"PREDICTION_BOUNDS")
            numerator=0.
            coverage=0
            confident_errors=0
            for t,row in zip(truth,values):
                for y,p in zip(t,row):
                    if p!=.5:
                        coverage+=1
                        confident_errors+=int(abs(p-y)>=.5)
                for g in ("xor3","majority3","gate3"):
                    p=compose(g,row)
                    target=compose(g,t)
                    require(-1e-9<=p<=1+1e-9,"COMPOSITION_RANGE")
                    numerator+=(max(0.,min(1.,p))-target)**2
            m=c["metrics"][family][arm]
            require(m["cases"]==48 and
                    abs(m["brier"]-round(numerator/48,10))<=1e-9 and
                    abs(c["primitive_coverage"][family][arm]-round(coverage/48,10))<=1e-9 and
                    c["primitive_confident_wrong"][family][arm]==confident_errors,
                    "INDEPENDENT_HELD_SCORE_"+family+"_"+arm)
        require(c["metrics"][family]["compiled_selected"]["brier"]==
                c["metrics"][family]["conventional_mdl"]["brier"],
                "NATIVE_CONVENTIONAL_PARITY")
        i=FAMILIES.index(family)
        for t in range(16):
            v=forecasts["compiled_selected"][t]
            ungated=forecasts["compiled_ungated"][t]
            for s in range(3):
                require(v[s]==(ungated[s] if admit[str(i*3+s)] else .5),
                        "COLD_CALIBRATION_ADMISSION")
    require(c["wall_seconds"]>=0 and c["cpu_seconds"]>=0,"PERFORMANCE_RECEIPT")
    return c


def outcome(cases):
    require(tuple(c["seed"] for c in cases)==SEEDS,"SEED_ORDER")
    def qualified(c):
        for i,f in enumerate(FAMILIES[:3]):
            for s in range(3):
                slot=str(i*3+s)
                if c["selected_degrees"][slot]!=i+1 or not c["source_only_admitted"][slot]:
                    return False
            m=c["metrics"][f]
            if not (m["compiled_selected"]["brier"]<=.01 and
                    c["primitive_coverage"][f]["compiled_selected"]>=.95 and
                    m["compiled_selected"]["brier"]==m["conventional_mdl"]["brier"]==
                         m["conventional_full_degree3"]["brier"]):
                return False
        if not any(c["metrics"][f]["compiled_selected"]["brier"]
                   <=c["metrics"][f]["native_unmodified"]["brier"]-.10
                   for f in ("quadratic","cubic")):return False
        sizes=c["native_checkpoint"]
        a=sum(sizes["profile_selected_bytes"][str(i)] for i in range(6))
        b=sum(sizes["profile_fixed_degree3_bytes"][str(i)] for i in range(6))
        if a>.90*b:return False
        o=c["metrics"]["quartic_ood"]
        return (sum(c["source_only_admitted"][str(s)] is False for s in (9,10,11))>=2
                and c["primitive_confident_wrong"]["quartic_ood"]["compiled_selected"]==0
                and o["compiled_selected"]["brier"]<=o["compiled_ungated"]["brier"])
    good=all(qualified(c) for c in cases)
    return "ENGINEERING_FEASIBLE" if good else "SCREEN_NO_GO",good


def report(pairs,raw_lock):
    classification,good=outcome([v for _,_,v in pairs])
    return {
        "schema":"yggdrasil.ckad34.pilot-screen.v1",
        "decision":classification,"engineering_feasible":good,
        "scientific_pass":False,"conventional_superiority":False,
        "pilot_seeds":list(SEEDS),"reserved_primary_untouched":[23741,23742,23743],
        "primary_scored":False,"source_lock_sha256":hashlib.sha256(raw_lock).hexdigest(),
        "pilot_receipt_sha256":{str(seed):hashlib.sha256(raw).hexdigest()
                                for seed,raw,_ in pairs},
        "scores":{str(c["seed"]):{
            "selected_degrees":c["selected_degrees"],
            "calibration_admitted":c["source_only_admitted"],
            "native_compiled_brier":{f:c["metrics"][f]["compiled_selected"]["brier"] for f in FAMILIES},
            "unmodified_native_brier":{f:c["metrics"][f]["native_unmodified"]["brier"] for f in FAMILIES},
            "full_degree3_brier":{f:c["metrics"][f]["conventional_full_degree3"]["brier"] for f in FAMILIES},
            "profile_bytes_selected":sum(c["native_checkpoint"]["profile_selected_bytes"][str(i)] for i in range(6)),
            "profile_bytes_forced":sum(c["native_checkpoint"]["profile_fixed_degree3_bytes"][str(i)] for i in range(6)),
            "ood_false_confident":c["primitive_confident_wrong"]["quartic_ood"]["compiled_selected"],
            "cpu_seconds":c["cpu_seconds"],"wall_seconds":c["wall_seconds"]
        } for _,_,c in pairs}
    }


def audit():
    raw_lock=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(raw_lock)
    pairs=[]
    for seed in SEEDS:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        pairs.append((seed,raw,case(raw,seed,lock)))
    expected=report(pairs,raw_lock)
    require(json.loads((HERE/"pilot_screen_report.json").read_bytes())==expected,
            "SEALED_REPORT_IDENTITY")
    require(not (HERE/"pilot_certificate.json").exists(),"NO_PRIMARY_AUTOMATION")
    return expected


def seal(root):
    raw_lock=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(raw_lock)
    pairs=[]
    for seed in SEEDS:
        raw=(root/f"ckad34-pilot-{seed}"/"result.json").read_bytes()
        pairs.append((seed,raw,case(raw,seed,lock)))
    result=report(pairs,raw_lock)
    for seed,raw,_ in pairs:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    require(audit()==result,"INDEPENDENT_SOURCE_RECONCILIATION")
    print(json.dumps(result,sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path)
    args=p.parse_args()
    if args.root is None:
        print(json.dumps(audit(),sort_keys=True))
    else:
        seal(args.root)


if __name__=="__main__":
    main()
