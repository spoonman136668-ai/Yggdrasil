"""Y035 heterogeneous-switch falsification for fixed feedback repair policy."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

prior=Path(__file__).resolve().parent.parent/"20261013-y034-feedback-repair"/"execute.py"
spec=importlib.util.spec_from_file_location("y034_frozen",prior)
assert spec and spec.loader
y34=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y34)
y33=y34.y33

def truth(seed,key,ep,condition):
    initial=y33.target(seed,key,0,"STABLE")
    if ep<6 or condition=="STABLE": return initial
    if condition=="UNIFORM_SWITCH": return (initial+2)%4
    assert condition=="HETEROGENEOUS_SWITCH"
    return (initial+(2 if key%2==0 else 1))%4

def signature(seed):
    sample={"active":[y33.active_keys(seed,e) for e in range(12)],
            "targets":[truth(seed,k,0,"STABLE") for k in range(16)]}
    return hashlib.sha256(json.dumps(sample,sort_keys=True).encode()).hexdigest()

def evaluate(seed,condition,repair):
    live={}
    dormant=OrderedDict()
    records=[]
    for ep in range(12):
        active=y33.active_keys(seed,ep)
        guesses={k:(live[k] if k in live else dormant.get(k,0)) for k in active}
        labels={k:truth(seed,k,ep,condition) for k in active}
        correct=sum(guesses[k]==labels[k] for k in active)
        overlap=[k for k in active if k in live]
        deltas=[(labels[k]-live[k])%4 for k in overlap]
        delta=deltas[0] if deltas and len(set(deltas))==1 and deltas[0]!=0 else 0
        for k in active: dormant.pop(k,None)
        writes=0
        for k in sorted(set(live)-set(active)):
            dormant.pop(k,None)
            dormant[k]=live[k]
            writes+=1
            while len(dormant)>9: dormant.popitem(last=False)
        maintenance=0
        if repair and delta:
            maintenance=len(dormant)
            for k in tuple(dormant): dormant[k]=(dormant[k]+delta)%4
        live=labels
        assert len(live)==7 and len(dormant)<=9 and len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        records.append({"episode":ep,"correct":correct,"writes":writes,
                        "occupancy":len(dormant),"repair_delta":delta if repair else 0,
                        "maintenance":maintenance})
    return {"seed":seed,"condition":condition,"arm":"repair" if repair else "baseline",
            "correct":sum(x["correct"] for x in records),
            "post_correct":sum(x["correct"] for x in records[6:]),
            "events":sum(x["repair_delta"]!=0 for x in records),
            "maintenance":sum(x["maintenance"] for x in records),
            "episodes":records}

def run():
    fingerprints={str(s):signature(s) for s in range(80,88)}
    if len(set(fingerprints.values()))!=8:
        return {"classification":"NONUNIQUE_INPUT_FINGERPRINT","fingerprints":fingerprints}
    rows=[]
    for c in ("STABLE","UNIFORM_SWITCH","HETEROGENEOUS_SWITCH"):
        for seed in range(80,88):
            a=evaluate(seed,c,False)
            b=evaluate(seed,c,True)
            assert [x["writes"] for x in a["episodes"]]==[x["writes"] for x in b["episodes"]]
            assert [x["occupancy"] for x in a["episodes"]]==[x["occupancy"] for x in b["episodes"]]
            rows.extend((a,b))
    held=[x for x in rows if x["seed"]>=84]
    def agg(c,arm,metric):
        return sum(x[metric] for x in held if x["condition"]==c and x["arm"]==arm)
    metrics={c:{arm:{m:agg(c,arm,m) for m in ("correct","post_correct","events","maintenance")}
              for arm in ("baseline","repair")}
             for c in ("STABLE","UNIFORM_SWITCH","HETEROGENEOUS_SWITCH")}
    u=metrics["UNIFORM_SWITCH"]
    h=metrics["HETEROGENEOUS_SWITCH"]
    if u["repair"]["post_correct"]>u["baseline"]["post_correct"] and h["repair"]["events"]==0:
        verdict="SELECTIVE_REPAIR"
    elif h["repair"]["events"]>0 and h["repair"]["post_correct"]<h["baseline"]["post_correct"]:
        verdict="FALSE_GENERALIZATION"
    else: verdict="MIXED"
    return {"id":"Y035","classification":verdict,"fingerprints":fingerprints,
            "metrics":metrics,"rows":rows,"model_calls":0,
            "claim_limit":"Fixed finite synthetic cue-value reassignment and feedback only."}

if __name__=="__main__":
    outcome=run()
    assert outcome==run()
    print(json.dumps(outcome,sort_keys=True,indent=2))
