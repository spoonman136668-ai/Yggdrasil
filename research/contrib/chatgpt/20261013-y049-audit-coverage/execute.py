"""Y049: group-audit budget tradeoff under audit-aware targeted corruption."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y040-hibernation" / "execute.py"
spec=importlib.util.spec_from_file_location("y040_pinned",PREVIOUS)
assert spec and spec.loader
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)
ARMS=("PRIMARY_ONLY","AUDIT_A","AUDIT_B","AUDIT_ROTATE","AUDIT_BOTH")
CONDITIONS=("CLEAN","A_CORRUPT","B_CORRUPT","ROTATE_TARGETED")


def groups(seed):
    assert 216<=seed<=223
    cues=y40.active(seed,10)
    assert len(cues)==7 and len(set(cues))==7
    return cues[:4],cues[4:]


def rotation(seed):
    return "A" if hashlib.sha256(
        ("Y049-audit/"+str(seed)).encode()).digest()[0]%2==0 else "B"


def target(seed,key,episode):
    initial=y40.target(seed,key,0,"STABLE")
    if episode<6 or key not in y40.permutation(seed)[:7]:
        return initial
    return (initial+2)%4


def fingerprint(seed):
    raw={"cue_order":y40.permutation(seed),
         "initial_truth":[target(seed,k,0) for k in range(16)]}
    return hashlib.sha256(json.dumps(raw,sort_keys=True,
                                    separators=(",",":")).encode()).hexdigest()


def corrupted_group(seed,condition):
    if condition=="A_CORRUPT":return "A"
    if condition=="B_CORRUPT":return "B"
    if condition=="ROTATE_TARGETED":
        return "B" if rotation(seed)=="A" else "A"
    return None


def evaluate(seed,condition,arm):
    a,b=groups(seed)
    live={}
    cache=OrderedDict()
    trace=hashlib.sha256()
    history=[]
    for ep in range(12):
        keys=y40.active(seed,ep)
        reports={}
        audit={}
        remaining=list(keys)
        if ep==10:
            sampled=a[:2]+b[:1]
            assert len(sampled)==3 and all(key in cache for key in sampled)
            reports={key:target(seed,key,ep) for key in sampled}
            corrupted=corrupted_group(seed,condition)
            if corrupted:
                for key in sampled:
                    if (key in a and corrupted=="A") or (key in b and corrupted=="B"):
                        reports[key]=(reports[key]+1)%4
            selection=(
                [] if arm=="PRIMARY_ONLY" else
                ["A"] if arm=="AUDIT_A" else
                ["B"] if arm=="AUDIT_B" else
                [rotation(seed)] if arm=="AUDIT_ROTATE" else ["A","B"])
            for chosen in selection:
                key=a[0] if chosen=="A" else b[0]
                audit[chosen]=target(seed,key,ep)  # explicitly sampled independently
            remaining=[key for key in keys if key not in reports]
        deltas_a=[(reports[key]-cache[key])%4 for key in a if key in reports]
        deltas_b=[(reports[key]-cache[key])%4 for key in b if key in reports]
        if ep==10:
            assert len(deltas_a)==2 and len(deltas_b)==1
        discordant_a=(len(set(deltas_a))>1 or
                      ("A" in audit and reports[a[0]]!=audit["A"]))
        discordant_b=("B" in audit and reports[b[0]]!=audit["B"])
        guesses={}
        for key in remaining:
            previous=live[key] if key in live else cache.get(key,0)
            if ep!=10:
                guess=previous
            elif (key in a and discordant_a) or (key in b and discordant_b):
                guess=None
            else:
                delta=deltas_a[0] if key in a else deltas_b[0]
                guess=(previous+delta)%4
            guesses[key]=guess
        assert len(guesses)+len(reports)==7
        assert set(guesses).isdisjoint(reports)
        # Remaining labels inaccessible to policy until these forecasts freeze.
        authoritative={key:target(seed,key,ep) for key in keys}
        correct=sum(guesses[key]==authoritative[key] for key in remaining)
        abstained=sum(guesses[key] is None for key in remaining)
        wrong=len(remaining)-correct-abstained
        if ep<=9:
            trace.update(bytes((ep,))+bytes(
                item for key in keys for item in (key,authoritative[key])))
        for key in keys:
            cache.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(keys)):
            cache.pop(key,None)
            cache[key]=live[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        live=authoritative
        assert len(live)==7 and len(cache)<=9 and len(live)+len(cache)<=16
        assert not set(live).intersection(cache)
        history.append({"episode":ep,"early_reports":len(reports)+len(audit),
                        "unique_early_cues":len(reports),"scored":len(remaining),
                        "correct":correct,"wrong":wrong,"abstained":abstained,
                        "a_conflict":bool(discordant_a),"b_conflict":bool(discordant_b),
                        "writes":writes,"occupancy":len(cache)})
    return {"seed":seed,"cohort":"development" if seed<220 else "heldout",
            "condition":condition,"arm":arm,
            "public_rotating_audit":rotation(seed),
            "pre_feedback_sha256":trace.hexdigest(),
            "return":history[10],"relearn":history[11],"history":history}


def run():
    fingerprints={str(seed):fingerprint(seed) for seed in range(216,224)}
    if len(set(fingerprints.values()))!=8:
        return {"schema":"yggdrasil.y049-audit-budget.v1",
                "classification":"NONUNIQUE_FINGERPRINT","fingerprints":fingerprints,
                "rows":[],"model_calls":0}
    records=[evaluate(seed,cond,arm) for seed in range(216,224)
             for cond in CONDITIONS for arm in ARMS]
    index={(r["seed"],r["condition"],r["arm"]):r for r in records}
    valid=True
    for seed in range(216,224):
        valid &= len({index[seed,cond,"PRIMARY_ONLY"]["pre_feedback_sha256"]
                      for cond in CONDITIONS})==1
        for cond in CONDITIONS:
            found=[index[seed,cond,arm] for arm in ARMS]
            for key in ("writes","occupancy"):
                traces=[[ep[key] for ep in x["history"]] for x in found]
                valid &= all(y==traces[0] for y in traces)
            valid &= all(x["relearn"]["correct"]==7 for x in found)
            valid &= all(x["return"]["unique_early_cues"]==3 and
                         x["return"]["scored"]==4 for x in found)
    held=[r for r in records if r["seed"]>=220]
    stats={cond:{arm:{
        key:sum(r["return"][key] for r in held
                if r["condition"]==cond and r["arm"]==arm)
        for key in ("early_reports","unique_early_cues","scored","correct",
                    "wrong","abstained","a_conflict","b_conflict")}
        for arm in ARMS} for cond in CONDITIONS}
    dual=stats["AUDIT_BOTH"] if "AUDIT_BOTH" in stats else None
    if not valid:
        classification="INVALID_HIDDEN_HISTORY"
    elif (all(stats[c]["AUDIT_BOTH"]["wrong"]==0 for c in CONDITIONS)
          and stats["ROTATE_TARGETED"]["AUDIT_ROTATE"]["wrong"]>=1
          and stats["CLEAN"]["AUDIT_BOTH"]["correct"]==16):
        classification="AUDIT_COVERAGE_BOUNDARY"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y049-audit-budget.v1",
            "parent":"2ab5044017e91e4f49da01f5a8e163c48b303f00",
            "classification":classification,
            "fingerprints":fingerprints,"rotation":{str(s):rotation(s) for s in range(216,224)},
            "matched_history":bool(valid),"heldout":stats,
            "rows":records,"model_calls":0,
            "claim_limit":"Two known cue groups and a public audit-aware adversary. Extra independent truth reports cost budget."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,indent=2,sort_keys=True))
