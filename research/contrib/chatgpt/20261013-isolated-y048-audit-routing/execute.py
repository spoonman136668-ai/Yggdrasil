"""Y048: group-local corruption exposes a symmetric placement/coverage tradeoff."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y040-hibernation"/"execute.py"
spec=importlib.util.spec_from_file_location("y040_frozen",PREVIOUS)
assert spec and spec.loader
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)
ARMS=("PRIMARY_THREE","AUDIT_A_FOUR","AUDIT_B_FOUR")
CONDITIONS=("CLEAN","GROUP_A_CORRUPT","GROUP_B_CORRUPT")


def group_keys(seed):
    assert 184<=seed<=191
    core=y40.active(seed,10)
    assert len(core)==7 and len(set(core))==7
    return core[:4],core[4:]


def truth(seed,key,episode):
    original=y40.target(seed,key,0,"STABLE")
    if episode<6 or key not in y40.permutation(seed)[:7]:
        return original
    return (original+2)%4


def fingerprint(seed):
    source={"order":y40.permutation(seed),
            "base":[truth(seed,key,0) for key in range(16)]}
    return hashlib.sha256(json.dumps(source,sort_keys=True,
                                    separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,arm):
    ga,gb=group_keys(seed)
    live={}
    cache=OrderedDict()
    pretrace=hashlib.sha256()
    records=[]
    for episode in range(12):
        keys=y40.active(seed,episode)
        reports={}
        audit=None
        remaining=list(keys)
        if episode==10:
            sampled=ga[:2]+gb[:1]
            assert len(sampled)==3 and all(key in cache for key in sampled)
            reports={key:truth(seed,key,episode) for key in sampled}
            if condition=="GROUP_A_CORRUPT":
                for key in ga[:2]:
                    reports[key]=(reports[key]+1)%4
            elif condition=="GROUP_B_CORRUPT":
                reports[gb[0]]=(reports[gb[0]]+1)%4
            if arm=="AUDIT_A_FOUR":
                audit=(ga[0],truth(seed,ga[0],episode))
            elif arm=="AUDIT_B_FOUR":
                audit=(gb[0],truth(seed,gb[0],episode))
            remaining=[key for key in keys if key not in reports]
        delta_a=[(reports[key]-cache[key])%4 for key in ga if key in reports]
        delta_b=[(reports[key]-cache[key])%4 for key in gb if key in reports]
        if episode==10:
            assert len(delta_a)==2 and len(delta_b)==1
        contradiction_a=(len(set(delta_a))>1 or
                         (audit is not None and audit[0] in ga and
                          reports[audit[0]]!=audit[1]))
        contradiction_b=(audit is not None and audit[0] in gb and
                         reports[audit[0]]!=audit[1])
        forecasts={}
        for key in remaining:
            old=live[key] if key in live else cache.get(key,0)
            if episode!=10:
                prediction=old
            elif (key in ga and contradiction_a) or (key in gb and contradiction_b):
                prediction=None
            else:
                delta=delta_a[0] if key in ga else delta_b[0]
                prediction=(old+delta)%4
            forecasts[key]=prediction
        assert not set(forecasts).intersection(reports)
        assert len(forecasts)+len(reports)==7
        # Truth for unobserved remaining cues exposed ONLY after all forecasts.
        observed={key:truth(seed,key,episode) for key in keys}
        correct=sum(forecasts[key]==observed[key] for key in remaining)
        abstained=sum(forecasts[key] is None for key in remaining)
        wrong=len(remaining)-correct-abstained
        if episode<=9:
            pretrace.update(bytes((episode,))+bytes(
                item for key in keys for item in (key,observed[key])))
        for key in keys:
            cache.pop(key,None)
        writes=0
        for key in sorted(set(live)-set(keys)):
            cache.pop(key,None)
            cache[key]=live[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        live=observed
        assert len(live)==7 and len(cache)<=9
        assert not set(live).intersection(cache)
        records.append({"episode":episode,"reports":len(reports)+(audit is not None),
                        "unique_reported_cues":len(reports),
                        "scored_opportunities":len(remaining),
                        "correct":correct,"wrong":wrong,"abstained":abstained,
                        "audit_conflict":bool(audit and reports[audit[0]]!=audit[1]),
                        "writes":writes,"occupancy":len(cache)})
    return {"seed":seed,"cohort":"development" if seed<188 else "heldout",
            "condition":condition,"arm":arm,
            "pre_reactivation_feedback_sha256":pretrace.hexdigest(),
            "return":records[10],"relearn":records[11],"episodes":records}


def run():
    fingerprints={str(seed):fingerprint(seed) for seed in range(184,192)}
    if len(set(fingerprints.values()))!=8:
        return {"schema":"yggdrasil.y048-audit-placement.v1",
                "classification":"NONUNIQUE_FINGERPRINT","fingerprints":fingerprints,
                "rows":[],"model_calls":0}
    records=[evaluate(seed,condition,arm) for seed in range(184,192)
             for condition in CONDITIONS for arm in ARMS]
    by={(r["seed"],r["condition"],r["arm"]):r for r in records}
    valid=True
    for seed in range(184,192):
        valid &= len({by[seed,c,"PRIMARY_THREE"]["pre_reactivation_feedback_sha256"]
                      for c in CONDITIONS})==1
        for c in CONDITIONS:
            cases=[by[seed,c,arm] for arm in ARMS]
            for key in ("writes","occupancy"):
                trace=[[ep[key] for ep in r["episodes"]] for r in cases]
                valid &= trace[0]==trace[1]==trace[2]
            valid &= all(r["relearn"]["correct"]==7 for r in cases)
            valid &= all(r["return"]["unique_reported_cues"]==3 for r in cases)
    heldout=[r for r in records if r["seed"]>=188]
    stats={c:{arm:{
        key:sum(r["return"][key] for r in heldout
                if r["condition"]==c and r["arm"]==arm)
        for key in ("reports","unique_reported_cues","scored_opportunities",
                    "correct","wrong","abstained","audit_conflict")}
        for arm in ARMS} for c in CONDITIONS}
    aa=stats["GROUP_A_CORRUPT"]
    bb=stats["GROUP_B_CORRUPT"]
    clean=stats["CLEAN"]
    if not valid:
        classification="INVALID_HIDDEN_HISTORY"
    elif (clean["AUDIT_A_FOUR"]["correct"]==16
          and clean["AUDIT_B_FOUR"]["correct"]==16
          and aa["AUDIT_A_FOUR"]["wrong"]==0
          and aa["AUDIT_A_FOUR"]["abstained"]==8
          and aa["AUDIT_B_FOUR"]["wrong"]==8
          and bb["AUDIT_B_FOUR"]["wrong"]==0
          and bb["AUDIT_B_FOUR"]["abstained"]==8
          and bb["AUDIT_A_FOUR"]["wrong"]==8):
        classification="SYMMETRIC_AUDIT_TRADEOFF"
    else:
        classification="MIXED"
    return {"schema":"yggdrasil.y048-audit-placement.v1",
            "parent":"bc8529c54399c69e074c831bbc4204a8f1517f67",
            "classification":classification,
            "fingerprints":fingerprints,"paired_history_valid":bool(valid),
            "heldout":stats,"rows":records,"model_calls":0,
            "claim_limit":"Synthetic known four/three-cue groups and explicit independent audit label; routing cannot protect both groups under fixed single-audit budget."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
