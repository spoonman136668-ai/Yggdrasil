"""Y051: past sensor errors route a scarce independent audit; drift breaks reuse."""
import hashlib, importlib.util, json
from collections import OrderedDict
from pathlib import Path

parent=Path(__file__).resolve().parent.parent/"20261013-y040-hibernation"/"execute.py"
spec=importlib.util.spec_from_file_location("y040_frozen",parent)
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)

CONDITIONS=("PERSISTENT","FLIPPED","CLEAN")
ARMS=("FIXED_A","FIXED_B","HISTORY_ROUTED","DUAL_AUDIT")


def groups(seed):
    assert 240<=seed<=247
    active=y40.active(seed,10)
    assert len(active)==7
    return active[:4],active[4:]


def baseline(seed,key,ep):
    init=y40.target(seed,key,0,"STABLE")
    if ep<6 or key not in y40.permutation(seed)[:7]:
        return init
    return (init+2)%4


def historical_fault(seed):
    return "A" if seed%2==0 else "B"


def e10_fault(seed,condition):
    old=historical_fault(seed)
    if condition=="CLEAN":return None
    if condition=="PERSISTENT":return old
    return "B" if old=="A" else "A"


def fingerprints(seed):
    source={"cue_order":y40.permutation(seed),
            "initial":[baseline(seed,k,0) for k in range(16)]}
    return hashlib.sha256(json.dumps(source,sort_keys=True,
                                    separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,arm):
    a,b=groups(seed)
    live={}
    dormant=OrderedDict()
    earlier_errors={"A":0,"B":0}
    earlier_trace=hashlib.sha256()
    episodes=[]
    for ep in range(12):
        current=y40.active(seed,ep)
        assert len(current)==len(set(current))==7
        primary={}
        audit={}
        remain=list(current)
        fault=None
        if ep==10:
            fault=e10_fault(seed,condition)
            selected=a[:2]+b[:1]
            assert len(selected)==3 and all(k in dormant for k in selected)
            # First only three queried primary labels become visible.
            primary={k:baseline(seed,k,ep) for k in selected}
            if fault is not None:
                for k in selected:
                    if (fault=="A" and k in a) or (fault=="B" and k in b):
                        primary[k]=(primary[k]+1)%4
            if arm=="FIXED_A":groups_to_audit=["A"]
            elif arm=="FIXED_B":groups_to_audit=["B"]
            elif arm=="HISTORY_ROUTED":
                chosen=("A" if earlier_errors["A"]>=earlier_errors["B"] else "B")
                groups_to_audit=[chosen]
            else:groups_to_audit=["A","B"]
            for chosen in groups_to_audit:
                key=a[0] if chosen=="A" else b[0]
                audit[chosen]=baseline(seed,key,ep)  # explicitly sampled truth
            remain=[k for k in current if k not in primary]
        da=[(primary[k]-dormant[k])%4 for k in a if k in primary]
        db=[(primary[k]-dormant[k])%4 for k in b if k in primary]
        if ep==10:
            assert len(da)==2 and len(db)==1
        conflict_a=(len(set(da))>1 or
                    ("A" in audit and primary[a[0]]!=audit["A"]))
        conflict_b=("B" in audit and primary[b[0]]!=audit["B"])
        # The remaining four cue labels are never read to select an audit,
        # choose an action, or form any prediction.
        forecasts={}
        for k in remain:
            old=live[k] if k in live else dormant.get(k,0)
            if ep!=10:pred=old
            elif (k in a and conflict_a) or (k in b and conflict_b):
                pred=None
            else:
                pred=(old+(da[0] if k in a else db[0]))%4
            forecasts[k]=pred
        assert len(remain)+len(primary)==7
        assert not set(remain).intersection(primary)
        # Authoritative complete feedback is revealed only AFTER forecasts.
        true={k:baseline(seed,k,ep) for k in current}
        if ep in (0,1):
            selected=a[:2]+b[:1]
            historic_reports={k:(true[k]+1)%4 if (
                (historical_fault(seed)=="A" and k in a) or
                (historical_fault(seed)=="B" and k in b)) else true[k]
                for k in selected}
            for k in selected:
                if historic_reports[k]!=true[k]:
                    earlier_errors["A" if k in a else "B"]+=1
            earlier_trace.update(bytes((ep,))+bytes(
                part for k in current for part in (k,true[k])))
            earlier_trace.update(bytes(
                part for k in selected for part in (k,historic_reports[k])))
        elif ep<=9:
            earlier_trace.update(bytes((ep,))+bytes(
                part for k in current for part in (k,true[k])))
        correct=sum(forecasts[k]==true[k] for k in remain)
        abstained=sum(forecasts[k] is None for k in remain)
        wrong=len(remain)-correct-abstained
        for k in current:dormant.pop(k,None)
        writes=0
        for k in sorted(set(live)-set(current)):
            dormant.pop(k,None)
            dormant[k]=live[k]
            writes+=1
            while len(dormant)>9:dormant.popitem(last=False)
        live=true
        assert len(live)==7 and len(dormant)<=9
        assert not set(live).intersection(dormant)
        episodes.append({"ep":ep,"early_reports":len(primary)+len(audit),
                         "sampled_keys":len(primary),"scored":len(remain),
                         "correct":correct,"wrong":wrong,"abstained":abstained,
                         "audit_choice":list(audit.keys()),
                         "a_conflict":bool(conflict_a),
                         "b_conflict":bool(conflict_b),
                         "cache_writes":writes,"occupancy":len(dormant)})
    return {"seed":seed,"cohort":"development" if seed<244 else "heldout",
            "condition":condition,"arm":arm,"history_errors":earlier_errors,
            "pre_e10_feedback_sha256":earlier_trace.hexdigest(),
            "return":episodes[10],"relearn":episodes[11],"episodes":episodes}


def run():
    inputs={str(s):fingerprints(s) for s in range(240,248)}
    if len(set(inputs.values()))!=8:
        return {"schema":"yggdrasil.y051-history-routing.v1",
                "classification":"NONUNIQUE_FINGERPRINT",
                "fingerprints":inputs,"rows":[],"model_calls":0}
    rows=[evaluate(s,c,a) for s in range(240,248)
          for c in CONDITIONS for a in ARMS]
    by={(r["seed"],r["condition"],r["arm"]):r for r in rows}
    valid=True
    for seed in range(240,248):
        traces={by[seed,c,"HISTORY_ROUTED"]["pre_e10_feedback_sha256"]
                for c in CONDITIONS}
        valid &= len(traces)==1
        route={tuple(by[seed,c,"HISTORY_ROUTED"]["return"]["audit_choice"])
               for c in CONDITIONS}
        valid &= len(route)==1
        route_group=next(iter(route))[0]
        valid &= route_group==historical_fault(seed)
        for c in CONDITIONS:
            arms=[by[seed,c,a] for a in ARMS]
            for field in ("cache_writes","occupancy"):
                seqs=[[e[field] for e in r["episodes"]] for r in arms]
                valid &= all(x==seqs[0] for x in seqs)
            valid &= all(r["return"]["sampled_keys"]==3 and
                         r["return"]["scored"]==4 and
                         r["relearn"]["correct"]==7 for r in arms)
    heldout=[r for r in rows if r["seed"]>=244]
    stats={c:{a:{field:sum(r["return"][field] for r in heldout
                           if r["condition"]==c and r["arm"]==a)
                  for field in ("early_reports","sampled_keys","scored",
                                "correct","wrong","abstained",
                                "a_conflict","b_conflict")}
              for a in ARMS} for c in CONDITIONS}
    if not valid:
        outcome="INVALID_PAIRED_HISTORY"
    elif (stats["PERSISTENT"]["HISTORY_ROUTED"]["wrong"]==0
          and stats["FLIPPED"]["HISTORY_ROUTED"]["wrong"]>=1
          and all(stats[c]["DUAL_AUDIT"]["wrong"]==0
                  for c in ("PERSISTENT","FLIPPED"))
          and all(stats["CLEAN"][a]["correct"]==16 for a in ARMS)):
        outcome="HISTORY_DRIFT_BOUNDARY"
    else:outcome="MIXED"
    return {"schema":"yggdrasil.y051-history-routing.v1",
            "classification":outcome,
            "parent":"eaa86ff9a69b750bc6fe59e93b53eb04e301fb61",
            "fingerprints":inputs,"paired_history_valid":bool(valid),
            "heldout":stats,"rows":rows,"model_calls":0,
            "claim_limit":"One synthetic previously labeled sensor-history routing task; corruption may move at e10."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
