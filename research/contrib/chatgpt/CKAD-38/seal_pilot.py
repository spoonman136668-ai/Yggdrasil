"""Independent CKAD38 evidence audit: no native learner or campaign imports.

Reconstruct public synthetic source truth from a separate deterministic
reference generator, independently fit all four fully observed conventional
models and recompute every prequential Brier before incorporating outcomes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

HERE=Path(__file__).resolve().parent
PILOT=(14181,14182)
ARMS=("native_recall","native_stream","native_no_repair","native_global",
      "beta_full","beta_window12","beta_window24","beta_window48",
      "beta_discount85","beta_discount95","beta_hedge","sham")
CONVENTIONAL=("beta_full","beta_window12","beta_window24","beta_window48",
              "beta_discount85","beta_discount95")
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")


def require(value,label):
    if not value:raise ValueError("CKAD38_INDEPENDENT_"+label)


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")


def seedint(*parts):
    return int.from_bytes(hashlib.sha256(
        canonical(["ckad38-source-v1",*parts])).digest()[:8],"big")


def reference(seed,world):
    bounds=random.Random(seedint("private-regime-boundaries",seed,world))
    a=96+bounds.randrange(-8,9)
    b=a+72+bounds.randrange(-8,9)
    inp=random.Random(seedint("public-input-policy",seed,world))
    outcome=random.Random(seedint("hidden-bernoulli-world",seed,world))
    rows=[]
    for t in range(b+64):
        mode="B" if a<=t<b else "A"
        s1=inp.randrange(2)
        x1=inp.randrange(2)
        x2=inp.randrange(2)
        view1=inp.randrange(2)
        view2=inp.randrange(2)
        variant=(seed+world)&1
        if variant==0:
            transition=(s1^x1)^int(mode=="B")
        else:
            transition=(s1&x1 if mode=="A" else (s1 ^ (x1 & (1-s1))))
        s2=int(outcome.random()<(.85 if transition else .15))
        if variant==0:
            consequence=((s1&x1)^(s2&x2)) if mode=="A" else ((s1&s2)|(x1&x2))
        else:
            consequence=((s1^(s2&x2)) if mode=="A" else ((s1&s2)^(x1|x2)))
        y=int(outcome.random()<(.9 if consequence else .1))
        source=hashlib.sha256(f"ckad38|{seed}|{world}|{t}".encode("ascii")).hexdigest()
        phase=("stable_A" if 48<=t<a else "early_B" if a<=t<a+24 else
               "late_B" if a+24<=t<b else "early_return_A" if b<=t<b+24
               else "late_return_A" if b+24<=t else "warm")
        rows.append({
            "world":world,"index":t,"phase":phase,"source_id":source,
            "public_views":[[s1,view1],[s1,view2]],
            "public_row":{"s1":s1,"x1":x1,"s2":s2,"x2":x2,"y":y}
        })
    return rows,{"world":world,"boundary_A_to_B":a,"boundary_B_to_A":b,
                 "total_episodes":b+64}


def conventional_predict(history,which,mode,row):
    s1,x1,s2,x2=row["s1"],row["x1"],row["s2"],row["x2"]
    if which=="sham":return .5
    if which=="beta_full":history=history
    elif which=="beta_window12":history=history[-12:]
    elif which=="beta_window24":history=history[-24:]
    elif which=="beta_window48":history=history[-48:]
    else:raise ValueError("UNEXPECTED_CONVENTIONAL_ARM")
    if mode=="transition":
        data=[r["s2"] for r in history if r["s1"]==s1 and r["x1"]==x1]
    else:
        data=[r["y"] for r in history if r["s1"]==s1 and r["x1"]==x1
              and r["s2"]==s2 and r["x2"]==x2]
    return (1+sum(data))/(2+len(data))


def discounted(bank,key):
    failure,success=bank.get(key,(0.,0.))
    return (1+success)/(2+failure+success)


def discount_update(bank,key,outcome):
    a,b=bank.get(key,(0.,0.))
    bank[key]=(a+int(outcome==0),b+int(outcome==1))


def audit_case(raw,seed,lock):
    data=json.loads(raw)
    require(data.get("schema")=="yggdrasil.ckad38.native-unannounced-rule-shifts.v1"
            and data.get("mode")=="pilot" and data.get("seed")==seed
            and data.get("source_lock")==lock and data.get("primary_scored") is False,
            "PILOT_ENVELOPE")
    c=data["case"];require(c.get("seed")==seed and
            c["world_count"]==2 and c["primary_scored"] is False,"SOURCE_IDENTITY")
    seen=set()
    expected=[]
    for world in (0,1):
        anticipated,metadata=reference(seed,world)
        reported=c["worlds"][world]
        require(reported["world"]==world and
                reported["eval_boundaries_private"]==metadata
                and reported["episodes"]==len(anticipated)
                and reported["source_count"]==len(anticipated)
                and reported["old_source_preserved"] is True
                and reported["duplicate_idempotent"] is True
                and reported["conflict_atomic"] is True
                and reported["consolidated_exact"] is True
                and reported["cold_exact"] is True
                and reported["recall_pure_read"] is True
                and len(reported["old_source_ranges"])==1 and
                reported["old_source_ranges"][0][0:2]==[0,32],"COLD_AND_OLD_SOURCE")
        first48_pin=hashlib.sha256(canonical([
            [r["source_id"],r["public_views"],r["public_row"]["x1"],
             r["public_row"]["s2"],r["public_row"]["x2"],r["public_row"]["y"]]
            for r in anticipated[:48]
        ])).hexdigest()
        require(reported["original_first48_sha256"]==first48_pin,
                "OLD_SOURCE_PREFIX_HASH")
        require(len(reported["checkpoint_records"])>=3 and
                all(type(v["bytes"]) is int and v["bytes"]>0 and
                    type(v["sha256"]) is str and len(v["sha256"])==64
                    for v in reported["checkpoint_records"].values()),
                "NATIVE_CHECKPOINT_RECEIPTS")
        expected+=anticipated
    actual=c["original_episode_receipts"]
    require(len(actual)==len(expected)==c["total_authentic_episodes"] and
            c["total_authentic_consequences"]==2*len(expected),
            "AUTHENTIC_SOURCE_COUNTS")
    histories={0:[],1:[]}
    discounted={w:{rate:{"transition":{},"terminal":{}} for rate in (.85,.95)}
                for w in (0,1)}
    hedges={w:{a:1.0 for a in CONVENTIONAL} for w in (0,1)}
    for orig,record in zip(expected,actual):
        require(set(record)==(set(orig)|{"forecasts","prequential_brier"}),
                "RECEIPT_FIELDS")
        for key,val in orig.items():
            require(record[key]==val,"ORIGINAL_CAUSAL_SOURCE_"+key)
        require(record["source_id"] not in seen,"DUPLICATE_EVENT_ID")
        seen.add(record["source_id"])
        w=orig["world"];row=orig["public_row"]
        require(set(record["forecasts"])==set(record["prequential_brier"])==
                set(ARMS),"SAME_ARM_SET")
        expected_conventional={}
        for arm in CONVENTIONAL:
            if arm.startswith("beta_discount"):
                rate=.85 if arm=="beta_discount85" else .95
                banks=discounted[w][rate]
                proposed=[
                    discounted_prob(banks["transition"],(row["s1"],row["x1"])),
                    discounted_prob(banks["terminal"],
                      (row["s1"],row["x1"],row["s2"],row["x2"]))
                ]
            else:
                proposed=[
                    conventional_predict(histories[w],arm,"transition",row),
                    conventional_predict(histories[w],arm,"terminal",row)
                ]
            expected_conventional[arm]=proposed
        norm=sum(hedges[w].values())
        hedge_expected=[
            sum(hedges[w][arm]*expected_conventional[arm][j]
                for arm in CONVENTIONAL)/norm for j in (0,1)
        ]
        for arm,values in record["forecasts"].items():
            require(type(values) is list and len(values)==2 and
                    all(type(p) in (int,float) and 0<=p<=1 for p in values),
                    "PREQUENTIAL_PREDICTION_BOUNDS")
            if arm in CONVENTIONAL:
                expected_pair=expected_conventional[arm]
                require(all(abs(x-y)<=1e-12 for x,y in zip(values,expected_pair)),
                        "FULLY_TRAINED_CONVENTIONAL_"+arm)
            elif arm=="beta_hedge":
                require(all(abs(x-y)<=1e-12 for x,y in zip(values,hedge_expected)),
                        "INDEPENDENT_ONLINE_HEDGE")
            elif arm=="sham":
                require(values==[.5,.5],"SHAM_SOURCE_INDEPENDENCE")
            if orig["index"]<48 and arm=="native_recall":
                require(values==record["forecasts"]["native_stream"],
                        "PRESTREAM_NATIVE_PARITY")
            loss=((values[0]-row["s2"])**2+(values[1]-row["y"])**2)/2
            require(abs(loss-record["prequential_brier"][arm])<=1e-12,
                    "PREQUENTIAL_LOSS_RECONSTRUCTION")
        # All conventional updates happen only AFTER both source consequences.
        histories[w].append(row)
        for arm in CONVENTIONAL:
            hedges[w][arm]*=math.exp(-4.0*record["prequential_brier"][arm])
        scale=max(hedges[w].values())
        for arm in CONVENTIONAL:hedges[w][arm]/=scale
        for rate,banks in discounted[w].items():
            for bank in banks.values():
                for key,(neg,pos) in list(bank.items()):
                    bank[key]=(neg*rate,pos*rate)
            discount_update(banks["transition"],(row["s1"],row["x1"]),row["s2"])
            discount_update(banks["terminal"],
                (row["s1"],row["x1"],row["s2"],row["x2"]),row["y"])
    require(set(c["metric_groups"])==set(PHASES)|{"pooled_late_shift_and_return"},
            "PHASE_SET")
    for group,metric in c["metric_groups"].items():
        phases=(("late_B","late_return_A") if group=="pooled_late_shift_and_return"
                else (group,))
        rows=[r for r in actual if r["phase"] in phases]
        require(rows and set(metric)==set(ARMS),"METRIC_SOURCE")
        for arm in ARMS:
            val=sum(r["prequential_brier"][arm] for r in rows)/len(rows)
            require(metric[arm]["episodes"]==len(rows) and
                    abs(metric[arm]["brier"]-round(val,10))<=1e-9,
                    "ALL_PHASE_BRIER_"+group+"_"+arm)
    require(c["cpu_seconds"]>=0 and c["wall_seconds"]>=0,"COMPUTE_COST")
    return c


def discounted_prob(bank,key):
    neg,pos=bank.get(key,(0.,0.))
    return (1+pos)/(2+neg+pos)


def decide(cases):
    require(tuple(c["seed"] for c in cases)==PILOT,"FROZEN_SEED_ORDER")
    def pass_one(c):
        m=c["metric_groups"];p=m["pooled_late_shift_and_return"]
        n=p["native_recall"]["brier"]
        conv=min(p[k]["brier"] for k in CONVENTIONAL+("beta_hedge",))
        return (n<=.145 and n<=conv-.025 and
                n<=p["native_stream"]["brier"]-.025
                and m["early_B"]["native_recall"]["brier"]<=
                    m["early_B"]["native_stream"]["brier"]
                and m["late_return_A"]["native_recall"]["brier"]<=
                    m["late_return_A"]["native_stream"]["brier"])
    all_pass=all(pass_one(c) for c in cases)
    return ("ENGINEERING_FEASIBLE" if all_pass else "SCREEN_NO_GO"),all_pass


def report(pairs,raw_lock):
    decision,go=decide([x for _,_,x in pairs])
    return {
        "schema":"yggdrasil.ckad38.pilot-screen.v1",
        "decision":decision,"engineering_feasible":go,
        "scientific_pass":False,"pilot_seeds":list(PILOT),
        "primary_reserved_unconsumed":[24181,24182,24183],
        "primary_scored":False,"source_lock_sha256":hashlib.sha256(raw_lock).hexdigest(),
        "pilot_sha256":{str(s):hashlib.sha256(raw).hexdigest() for s,raw,_ in pairs},
        "scores":{str(c["seed"]):{
            "phase_brier":{phase:{a:val["brier"] for a,val in arms.items()}
                           for phase,arms in c["metric_groups"].items()},
            "episodes":c["total_authentic_episodes"],
            "old_source_preserved":all(w["old_source_preserved"] for w in c["worlds"]),
            "recall_pure_read":all(w["recall_pure_read"] for w in c["worlds"]),
            "cold_exact":all(w["cold_exact"] for w in c["worlds"]),
            "total_detections":sum(len(w["detected_events"]) for w in c["worlds"]),
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
    expected=report(pairs,raw_lock)
    require(json.loads((HERE/"pilot_screen_report.json").read_bytes())==expected,
            "GIT_SEALED_EVIDENCE_MISMATCH")
    require(not (HERE/"pilot_certificate.json").exists(),
            "PROTECTED_PRIMARY_FORBIDDEN")
    return expected


def seal(root):
    raw_lock=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(raw_lock)
    pairs=[]
    for seed in PILOT:
        raw=(root/f"ckad38-pilot-{seed}"/"result.json").read_bytes()
        pairs.append((seed,raw,audit_case(raw,seed,lock)))
    expected=report(pairs,raw_lock)
    for seed,raw,_ in pairs:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(
        json.dumps(expected,sort_keys=True,indent=2)+"\n")
    require(audit()==expected,"SEALED_COPY_RECHECK")
    print(json.dumps(expected,sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path)
    args=p.parse_args()
    if args.root is None:print(json.dumps(audit(),sort_keys=True))
    else:seal(args.root)


if __name__=="__main__":
    main()
