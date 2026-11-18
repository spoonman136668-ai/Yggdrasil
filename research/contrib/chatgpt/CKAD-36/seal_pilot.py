"""CKAD36 independent read-only provenance, policy and held-score audit.

Never imports the source generator or candidate native learner. Reimplements
GF(2) source identification, conventional binary hypothesis tables, input-only
SHA ordering, source-only active policy and all Brier/coverage scores.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

HERE=Path(__file__).resolve().parent
PILOT=(13961,13962)
DONORS=(0,1,2)
TARGETS=(3,4,5,6,7,8)
PRESSURE=(9,10,11,12)
POLICIES=("active","fixed","random")
ARMS={"analogue","native_target","target_gf2","polynomial_logistic",
      "frequency","sham","conventional_active","initial10"}
FAMILIES=("isomorphic","quartic_shift")
MONOMIALS=tuple(i for i in range(64) if i.bit_count()<=3)
TRANSFORMS=tuple((perm,mask,flip) for perm in itertools.permutations(range(5))
                 for mask in range(32) for flip in (0,1))


def require(ok,label):
    if not ok:raise ValueError("CKAD36_INDEPENDENT_EVIDENCE_"+label)


def order(*parts):
    values=["ckad35-fresh-public-worlds-v1",
            "ckad36-independent-source-input-v1",*parts]
    raw=json.dumps(values,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big")


def degree3(x):
    return sum(1<<i for i,m in enumerate(MONOMIALS) if x&m==m)


def conventional_fit(rows):
    pivots={};seen=set()
    for c,a,y in rows:
        require(type(c) is int and 0<=c<32 and
                type(a) is int and a in (0,1) and
                type(y) is int and y in (0,1),"INVALID_PUBLIC_WITNESS")
        x=c|(a<<5)
        require(x not in seen,"SOURCE_DUPLICATE")
        seen.add(x)
        row,rhs=degree3(x),y
        while row:
            k=row.bit_length()-1
            if k not in pivots:
                pivots[k]=(row,rhs)
                break
            p,v=pivots[k]
            row^=p;rhs^=v
        require(row!=0 or rhs==0,"OUTSIDE_SOURCE_GF2_CLASS")
    return pivots


def conventional_predict(pivots,x):
    v=degree3(x);y=0
    while v:
        k=v.bit_length()-1
        if k not in pivots:return .5
        p,b=pivots[k]
        v^=p;y^=b
    return float(y)


def relabel(x,perm,mask):
    out=sum(((x>>old)&1)<<new for new,old in enumerate(perm))
    return ((out^mask)&31)|(x&32)


def bitmaps(tables):
    all_rows=[]
    for donor in DONORS:
        for perm,mask,flip in TRANSFORMS:
            b=0
            for x in range(64):
                b|=(int(tables[donor][relabel(x,perm,mask)])^flip)<<x
            all_rows.append(b)
    require(len(all_rows)==23040,"HYPOTHESIS_UNIVERSE")
    return tuple(all_rows)


def conditioned(hypotheses,observations):
    for x,y in observations:
        hypotheses=tuple(h for h in hypotheses if ((h>>x)&1)==y)
    return hypotheses


def forecast(posterior,held):
    if not posterior:return [.5]*len(held)
    return [sum((h>>x)&1 for h in posterior)/len(posterior) for x in held]


def choice(posterior,pool,seed,slot,iteration):
    if not posterior:
        return min(pool,key=lambda x:(order("empty-posterior",seed,slot,iteration,x),x))
    n=len(posterior)
    return min(pool,key=lambda x:(
        -sum((h>>x)&1 for h in posterior) *
         (n-sum((h>>x)&1 for h in posterior)),
        order("entropy-tie",seed,slot,iteration,x),x))


def compose(graph,values):
    a,b,c=values
    if graph=="xor3":return a+b+c-2*(a*b+a*c+b*c)+4*a*b*c
    if graph=="majority3":return a*b+a*c+b*c-2*a*b*c
    if graph=="gate3":return a*b+c-2*a*b*c
    raise ValueError("UNKNOWN_GRAPH")


def valid_sha(x):
    return type(x) is str and len(x)==64 and all(t in "0123456789abcdef" for t in x)


def public_rows(name,rows,expected):
    require(type(rows) is list and len(rows)==len(expected),name+"_COUNT")
    require(all(type(r) is list and len(r)==3 for r in rows),name+"_STRUCT")
    require([c|(a<<5) for c,a,y in rows]==list(expected),name+"_INPUT_ORDER")
    require(all(type(c) is int and 0<=c<32 and
                type(a) is int and a in (0,1) and
                type(y) is int and y in (0,1) for c,a,y in rows),name+"_BINARY")


def audit_case(raw,seed,lock):
    doc=json.loads(raw)
    require(doc.get("schema")=="yggdrasil.ckad36.active-causal-probes.v1"
            and doc.get("mode")=="pilot" and doc.get("seed")==seed
            and doc.get("lock")==lock and doc.get("primary_scored") is False,
            "FROZEN_ENVELOPE")
    c=doc["case"]
    require(c.get("seed")==seed and c.get("primary_scored") is False and
            c["source_outcomes_per_policy"]==390 and
            c["donor_source_outcomes"]==126 and
            c["target_source_outcomes_per_policy"]==96 and
            c["pressure_source_outcomes"]==168 and
            c["held_composites_per_family"]==48,"FROZEN_ACTION_BUDGET")
    donor,initial,held,pool=(c["donor_source_inputs"],
                             c["target_initial_inputs"],c["target_held_inputs"],
                             c["target_action_pool"])
    require(len(donor)==42 and len(set(donor))==42 and len(initial)==10
            and len(held)==16 and len(pool)==38
            and len(set(initial+held+pool))==64
            and all(type(x) is int and 0<=x<64 for x in donor+initial+held+pool),
            "HELD_ACTION_PARTITION")
    require(sorted(range(64),key=lambda x:(order("target-split",seed,x),x))
            ==initial+held+pool,"INPUT_ONLY_SPLIT_IDENTITY")
    require(set(c["donor_source_witness"])=={str(s) for s in DONORS} and
            set(c["pressure_source_witness"])=={str(s) for s in PRESSURE},
            "PUBLIC_SOURCE_SLOTS")
    for slot in DONORS:
        public_rows("DONOR",c["donor_source_witness"][str(slot)],donor)
    for slot in PRESSURE:
        public_rows("PRESSURE",c["pressure_source_witness"][str(slot)],donor)
    check=c["native_custody"]
    require(all(check[k] is True for k in
                ("cold_restore_exact","all_64_donor_readouts_retained",
                 "contradiction_atomic"))
            and valid_sha(check["donor_source_sha256"])
            and valid_sha(check["post_pressure_checkpoint_sha256"])
            and check["post_pressure_checkpoint_bytes"]>0,"NATIVE_COLD_STATE")
    tables=c["donor_native_tables"];control=c["donor_conventional_tables"]
    require(len(tables)==len(control)==3,"DONOR_TABLES")
    for slot in DONORS:
        a=conventional_fit(c["donor_source_witness"][str(slot)])
        predicted=[conventional_predict(a,x) for x in range(64)]
        require(len(a)==42 and tables[slot]==control[slot]==predicted and
                all(v in (0.,1.) for v in predicted),"INDEPENDENT_DONOR_SOURCE_GF2")
    hypotheses=bitmaps(control)
    require(set(c["policy_source_cases"])==
            set(c["policy_target_controls"])==
            set(c["target_native_custody"])==set(POLICIES),"POLICY_SET")
    for policy in POLICIES:
        require(c["target_native_custody"][policy]["cold_exact"] is True,"NATIVE_TARGET_COLD")
        cases=c["policy_source_cases"][policy]
        require(set(cases)==set(c["policy_target_controls"][policy])==
                {str(s) for s in TARGETS},"TARGET_SLOT_SET")
        for slot in TARGETS:
            item=cases[str(slot)]
            base=item["initial_source"];acts=item["actions"];trace=item["source_trace"]
            require(len(base)==10 and len(acts)==len(trace)==6 and
                    item["source_count"]==16 and
                    [x for x,y in base]==initial and
                    all(type(x) is int and type(y) is int and y in (0,1)
                        for x,y in base+acts),"POLICY_SOURCE_BUDGET")
            require(len(set(x for x,y in acts))==6 and
                    set(x for x,y in acts).issubset(set(pool)) and
                    not (set(x for x,y in acts)&set(held)),"NO_HELD_ACTION_LEAK")
            before=conditioned(hypotheses,base)
            require(item["initial_survivors"]==len(before),"PRE_ACTION_POSTERIOR")
            expected_initial=forecast(before,held)
            require(all(abs(a-b)<=1e-12 for a,b in
                        zip(expected_initial,item["initial10_forecast"])),
                    "INITIAL10_PREDICTIONS")
            random_actions=(random.Random(order("random-action-seed",seed,slot))
                             .sample(pool,6) if policy=="random" else None)
            remaining=list(pool)
            for i,((x,y),entry) in enumerate(zip(acts,trace)):
                expected= (choice(before,remaining,seed,slot,i) if policy=="active"
                           else remaining[0] if policy=="fixed" else random_actions[i])
                require(expected==x,"POLICY_INTERVENTION_SELECTED_INDEPENDENTLY")
                require(entry=={"action":x,"outcome":y,
                               "posterior_before":len(before),
                               "posterior_after":len(conditioned(before,[(x,y)]))},
                        "POSTERIOR_UPDATE_SOURCE_ONLY")
                before=conditioned(before,[(x,y)])
                remaining.remove(x)
            expected_final=forecast(before,held)
            require(len(before)==item["final_survivors"] and
                    len(expected_final)==len(item["forecast"])==16 and
                    all(abs(a-b)<=1e-12 for a,b in zip(expected_final,item["forecast"])),
                    "INDEPENDENT_POSTERIOR_FORECAST")
            # Two conventional source-only target controls are recomputed here.
            rows=[[x&31,x>>5,y] for x,y in base+acts]
            try:
                gf2=conventional_fit(rows)
            except ValueError as exc:
                if str(exc)!="CKAD36_INDEPENDENT_AUDIT_OUTSIDE_SOURCE_GF2_CLASS":
                    raise
                gf2=None
            expected_gf2=[conventional_predict(gf2,x) if gf2 is not None
                          else .5 for x in held]
            ctl=c["policy_target_controls"][policy][str(slot)]
            require(all(abs(a-b)<=1e-12 for a,b in
                        zip(ctl["target_gf2"],expected_gf2)),"TARGET_GF2_PARITY")
            require(len(ctl["native_target"])==16 and len(ctl["sham"])==16 and
                    ctl["sham"]==[.5]*16,"CONTROL_PROVENANCE")
    require(set(c["held_truth"])==
            set(c["held_forecasts"])==
            set(c["metrics"])==
            set(c["committed_coverage"])==
            set(c["confident_wrong"])==set(FAMILIES),"HELD_FAMILY_SET")
    for idx,family in enumerate(FAMILIES):
        truth=c["held_truth"][family]
        require(len(truth)==16 and all(len(row)==3 and
                all(type(v) is int and v in (0,1) for v in row)
                for row in truth),"HELD_TRUTH_SHAPE")
        require(set(c["held_forecasts"][family])==
                set(c["metrics"][family])==
                set(c["committed_coverage"][family])==
                set(c["confident_wrong"][family])==set(POLICIES),
                "HELD_POLICY_SET")
        for policy in POLICIES:
            preds=c["held_forecasts"][family][policy]
            require(set(preds)==set(c["metrics"][family][policy])==
                    set(c["committed_coverage"][family][policy])==
                    set(c["confident_wrong"][family][policy])==ARMS,
                    "HELD_CONTROL_ARMS")
            for arm,rows in preds.items():
                require(len(rows)==16 and all(len(r)==3 and
                        all(type(p) in (int,float) and 0<=p<=1 for p in r)
                        for r in rows),"HELD_PROBABILITY_BOUNDS")
                total=0.;committed=0;wrong=0
                for i,(p,y) in enumerate(zip(rows,truth)):
                    if arm in ("analogue","conventional_active","initial10"):
                        expected=[]
                        for slot in range(3+3*idx,6+3*idx):
                            target=c["policy_source_cases"][policy][str(slot)]
                            field="initial10_forecast" if arm=="initial10" else "forecast"
                            expected.append(target[field][i])
                        require(all(abs(a-b)<=1e-12 for a,b in zip(p,expected)),
                                "AGGREGATED_ANALOGUE_READOUT")
                    for probability,label in zip(p,y):
                        if probability<=.1 or probability>=.9:
                            committed+=1
                            wrong+=int((probability>=.5)!=label)
                    for g in ("xor3","majority3","gate3"):
                        estimate=compose(g,p)
                        require(-1e-9<=estimate<=1+1e-9,"COMPOSITE_PROBABILITY")
                        total+=(max(0.,min(1.,estimate))-compose(g,y))**2
                metric=c["metrics"][family][policy][arm]
                require(metric["cases"]==48 and
                        abs(metric["brier"]-round(total/48,10))<=1e-9 and
                        abs(c["committed_coverage"][family][policy][arm]-
                            round(committed/48,10))<=1e-9 and
                        c["confident_wrong"][family][policy][arm]==wrong,
                        "RECONSTRUCTED_BRIER_CONFIDENCE_"+family+"_"+policy+"_"+arm)
    require(c["cpu_seconds"]>=0 and c["wall_seconds"]>=0,"WALL_CPU_COST")
    return c


def frozen_screen(cases):
    require(tuple(c["seed"] for c in cases)==PILOT,"ORIGINAL_SEED_ORDER")
    def is_go(c):
        a=c["metrics"]["isomorphic"];o=c["metrics"]["quartic_shift"]
        active=a["active"]["analogue"]["brier"]
        return (
            active<=.08
            and active<=a["fixed"]["analogue"]["brier"]-.03
            and active<=a["random"]["analogue"]["brier"]-.03
            and active<=a["active"]["native_target"]["brier"]-.03
            and active<=a["active"]["target_gf2"]["brier"]-.03
            and active==a["active"]["conventional_active"]["brier"]
            and c["committed_coverage"]["isomorphic"]["active"]["analogue"]>=.5
            and c["confident_wrong"]["isomorphic"]["active"]["analogue"]==0
            and sum(c["policy_source_cases"]["active"][str(s)]["final_survivors"]==0
                    for s in (6,7,8))>=2
            and c["confident_wrong"]["quartic_shift"]["active"]["analogue"]==0
            and o["active"]["analogue"]["brier"]<=o["fixed"]["analogue"]["brier"]
        )
    success=all(is_go(c) for c in cases)
    return ("ENGINEERING_FEASIBLE" if success else "SCREEN_NO_GO"),success


def report(pairs,raw_lock):
    decision,go=frozen_screen([c for _,_,c in pairs])
    return {
        "schema":"yggdrasil.ckad36.pilot-screen.v1",
        "decision":decision,"engineering_feasible":go,
        "scientific_pass":False,"conventional_superiority":False,
        "pilot_seeds":list(PILOT),"reserved_primary_untouched":[23961,23962,23963],
        "primary_scored":False,
        "source_lock_sha256":hashlib.sha256(raw_lock).hexdigest(),
        "pilot_receipt_sha256":{str(s):hashlib.sha256(raw).hexdigest()
                                for s,raw,_ in pairs},
        "scores":{str(c["seed"]):{
            "active_brier":c["metrics"]["isomorphic"]["active"]["analogue"]["brier"],
            "fixed_brier":c["metrics"]["isomorphic"]["fixed"]["analogue"]["brier"],
            "random_brier":c["metrics"]["isomorphic"]["random"]["analogue"]["brier"],
            "native_target_only_brier":c["metrics"]["isomorphic"]["active"]["native_target"]["brier"],
            "conventional_target_only_brier":c["metrics"]["isomorphic"]["active"]["target_gf2"]["brier"],
            "conventional_active_brier":c["metrics"]["isomorphic"]["active"]["conventional_active"]["brier"],
            "active_committed_coverage":c["committed_coverage"]["isomorphic"]["active"]["analogue"],
            "active_confident_wrong":c["confident_wrong"]["isomorphic"]["active"]["analogue"],
            "active_ood_veto_count":sum(c["policy_source_cases"]["active"][str(s)]["final_survivors"]==0
                                        for s in (6,7,8)),
            "active_ood_brier":c["metrics"]["quartic_shift"]["active"]["analogue"]["brier"],
            "fixed_ood_brier":c["metrics"]["quartic_shift"]["fixed"]["analogue"]["brier"],
            "active_ood_confident_wrong":c["confident_wrong"]["quartic_shift"]["active"]["analogue"],
            "wall_seconds":c["wall_seconds"],"cpu_seconds":c["cpu_seconds"]
        } for _,_,c in pairs}
    }


def audit():
    raw_lock=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(raw_lock)
    pairs=[]
    for seed in PILOT:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        pairs.append((seed,raw,audit_case(raw,seed,lock)))
    result=report(pairs,raw_lock)
    require(json.loads((HERE/"pilot_screen_report.json").read_bytes())==result,
            "SEALED_ORIGINAL_RECEIPT_MISMATCH")
    require(not (HERE/"pilot_certificate.json").exists(),"RESERVED_PRIMARY_DISPATCH")
    return result


def seal(root):
    raw_lock=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(raw_lock)
    pairs=[]
    for seed in PILOT:
        raw=(root/f"ckad36-pilot-{seed}"/"result.json").read_bytes()
        pairs.append((seed,raw,audit_case(raw,seed,lock)))
    result=report(pairs,raw_lock)
    for seed,raw,_ in pairs:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    require(audit()==result,"INDEPENDENT_SEAL_REPEAT")
    print(json.dumps(result,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path)
    args=ap.parse_args()
    if args.root is None:print(json.dumps(audit(),sort_keys=True))
    else:seal(args.root)


if __name__=="__main__":
    main()
