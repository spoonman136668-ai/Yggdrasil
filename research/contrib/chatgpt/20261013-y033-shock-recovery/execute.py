"""Y033: causal paper-only matched-cache shock and recovery."""
import importlib.util
import hashlib
import json
from collections import OrderedDict
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261012-y030-new-family"/"execute.py"
spec=importlib.util.spec_from_file_location("y030_frozen",PARENT)
assert spec and spec.loader
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

PROGRAM=((0,0),(1,0),(2,0),(3,0),(4,5),(5,5),
         (0,0),(1,0),(2,0),(3,0),(4,0),(5,0))


def geometry(seed,observed_idx):
    logical,shift=PROGRAM[observed_idx]
    active,neighbors=prior.geometry(seed,logical)
    shifted={key:{(cell+shift)%16 for cell in neighbors[key]}
             for key in active}
    return active,shifted


def signature(seed):
    canonical=[]
    for ep in range(len(PROGRAM)):
        active,adj=geometry(seed,ep)
        canonical.append((active,[sorted(adj[k]) for k in active]))
    return hashlib.sha256(json.dumps(canonical,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,retained):
    cache=OrderedDict()
    prev_active=set()
    prev_assigned={}
    evaluator_history={}
    baseline_evaluator={}
    trace=[]
    for ep in range(len(PROGRAM)):
        active,adj=geometry(seed,ep)
        oracle=prior.hall_cardinality(active,adj)
        pref={k:cache[k] for k in active if k in cache and cache[k] in adj[k]} if retained else {}
        assigned,calls=prior.match(active,adj,pref)
        returning=[key for key in assigned if key in evaluator_history]
        churn=sum(assigned[key]!=evaluator_history[key] for key in returning)
        for key in assigned:evaluator_history[key]=assigned[key]
        if ep<4:
            for key in assigned:baseline_evaluator.setdefault(key,assigned[key])
        overlap=[key for key in assigned if ep>=6 and key in baseline_evaluator]
        baseline_drift=sum(assigned[key]!=baseline_evaluator[key] for key in overlap)
        for key in active:cache.pop(key,None)
        writes=0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key,None)
            if key in prev_assigned:
                cache[key]=prev_assigned[key]
                writes+=1
                while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assigned=assigned
        trace.append({
            "observation":ep,"logical":PROGRAM[ep][0],
            "shock_offset":PROGRAM[ep][1],
            "phase":"baseline" if ep<4 else "shock" if ep<6 else "recovery",
            "matched":len(assigned),"oracle":oracle,
            "returning":len(returning),"churn":churn,
            "baseline_return_overlap":len(overlap),
            "baseline_identity_drift":baseline_drift,
            "calls":calls,"writes":writes,
            "cache_entries":len(cache),"legal_preferences":len(pref)
        })
    phases={phase:{"churn":sum(t["churn"] for t in trace if t["phase"]==phase),
                   "identity_drift":sum(t["baseline_identity_drift"] for t in trace
                                        if t["phase"]==phase)}
            for phase in ("baseline","shock","recovery")}
    return {
        "seed":seed,"cohort":"development" if seed<68 else "heldout",
        "arm":"retained" if retained else "sham",
        "phases":phases,
        "writes":sum(t["writes"] for t in trace),
        "search_calls":sum(t["calls"] for t in trace),
        "legal_preferences":sum(t["legal_preferences"] for t in trace),
        "episodes":trace
    }


def run():
    sig={str(s):signature(s) for s in range(64,72)}
    unique=len(set(sig.values()))==8
    rows=[evaluate(s,ret) for s in range(64,72)
          for ret in (False,True)]
    pairs={seed:(rows[2*(seed-64)],rows[2*(seed-64)+1])
           for seed in range(64,72)}
    parity=True
    oracle=True
    full=True
    for a,b in pairs.values():
        if [e["writes"] for e in a["episodes"]]!=[e["writes"] for e in b["episodes"]]:
            parity=False
        if [e["cache_entries"] for e in a["episodes"]]!=[
           e["cache_entries"] for e in b["episodes"]]:
            parity=False
        for arm in (a,b):
            for ep in arm["episodes"]:
                if ep["matched"]!=ep["oracle"]:oracle=False
                if ep["matched"]!=7:full=False
    heldout=[pairs[s] for s in range(68,72)]
    churn_savings=[a["phases"]["recovery"]["churn"]-b["phases"]["recovery"]["churn"]
                   for a,b in heldout]
    baseline_savings=[a["phases"]["recovery"]["identity_drift"]-
                      b["phases"]["recovery"]["identity_drift"]
                      for a,b in heldout]
    if not unique or not parity or not oracle:
        label="INVALID"
    elif not full:
        label="GEOMETRY_DEFICIENCY"
    elif (sum(churn_savings)>0 and sum(baseline_savings)>0
          and all(v>=0 for v in churn_savings)):
        label="RECOVERY_BENEFIT"
    elif sum(churn_savings)<0:
        label="RECOVERY_HARM"
    else:
        label="MIXED"
    return {
        "schema":"yggdrasil.y033-shock-recovery.v1",
        "predecessor_head":"d821f293fec9b229aa485771128f77e3304b9494",
        "classification":label,
        "unique_geometry_signatures":unique,
        "geometry_signatures":sig,
        "full_match":full,"hall_oracle_agrees":oracle,
        "matched_cache_bookkeeping":parity,
        "heldout_recovery_churn_savings":churn_savings,
        "heldout_baseline_identity_drift_savings":baseline_savings,
        "heldout_sham_recovery_churn":sum(a["phases"]["recovery"]["churn"] for a,b in heldout),
        "heldout_retained_recovery_churn":sum(b["phases"]["recovery"]["churn"] for a,b in heldout),
        "rows":rows,"model_calls":0,
        "scope":"Causal synthetic episodic recovery, not real-world semantic consolidation"
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
