"""Y047 independent audit measurement versus cross-channel correlated corruption."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y040-hibernation"/"execute.py"
_spec=importlib.util.spec_from_file_location("y040_frozen",PREVIOUS)
assert _spec and _spec.loader
y40=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y40)
ARMS=("PRIMARY_FOUR","DUAL_CHANNEL_FIVE")
CONDITIONS=("CLEAN","PRIMARY_CORRUPT","BOTH_CORRUPT")


def groups(seed):
    assert 176<=seed<=183
    core=y40.active(seed,10)
    even=[k for k in core if k%2==0]
    odd=[k for k in core if k%2==1]
    if not even or not odd:
        return None
    return (even,odd) if len(even)>len(odd) else (odd,even)


def target(seed,key,ep):
    prior=y40.target(seed,key,0,"STABLE")
    if ep<6 or key not in y40.permutation(seed)[:7]:
        return prior
    return (prior+2)%4


def fingerprint(seed):
    values={"order":y40.permutation(seed),
            "initial":[target(seed,k,0) for k in range(16)]}
    return hashlib.sha256(json.dumps(
        values,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,arm):
    majority,minority=groups(seed)
    live={}
    dormant=OrderedDict()
    pretrace=hashlib.sha256()
    records=[]
    for ep in range(12):
        keys=y40.active(seed,ep)
        assert len(keys)==7
        reports={}
        audit=None
        remaining=list(keys)
        if ep==10:
            sampled=majority[:3]+minority[:1]
            assert len(sampled)==4 and all(k in dormant for k in sampled)
            reports={k:target(seed,k,ep) for k in sampled}
            if condition!="CLEAN":
                for k in majority[:3]:
                    reports[k]=(reports[k]+1)%4
            if arm=="DUAL_CHANNEL_FIVE":
                audit=target(seed,majority[0],ep)
                if condition=="BOTH_CORRUPT":
                    audit=(audit+1)%4
            remaining=[k for k in keys if k not in reports]
        major_deltas=[(reports[k]-dormant[k])%4 for k in majority if k in reports]
        minor_deltas=[(reports[k]-dormant[k])%4 for k in minority if k in reports]
        if ep==10:
            assert len(major_deltas)==3 and len(minor_deltas)==1
        within_group_conflict=len(set(major_deltas))>1
        audit_conflict=(audit is not None and audit!=reports[majority[0]])
        guesses={}
        for k in remaining:
            remembered=live[k] if k in live else dormant.get(k,0)
            if ep!=10:
                pred=remembered
            elif k in majority and (within_group_conflict or audit_conflict):
                pred=None
            else:
                delta=major_deltas[0] if k in majority else minor_deltas[0]
                pred=(remembered+delta)%4
            guesses[k]=pred
        assert len(guesses)+len(reports)==7
        assert not set(guesses).intersection(reports)
        # All unsampled truth remains hidden until after predictions freeze.
        truth={k:target(seed,k,ep) for k in keys}
        correct=sum(guesses[k]==truth[k] for k in remaining)
        abstained=sum(guesses[k] is None for k in remaining)
        wrong=len(remaining)-correct-abstained
        if ep<=9:
            pretrace.update(bytes((ep,))+bytes(
                part for k in keys for part in (k,truth[k])))
        for k in keys:
            dormant.pop(k,None)
        writes=0
        for k in sorted(set(live)-set(keys)):
            dormant.pop(k,None)
            dormant[k]=live[k]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        live=truth
        assert len(live)==7 and len(dormant)<=9
        assert not set(live).intersection(dormant)
        records.append({"episode":ep,"early_reports":len(reports)+(audit is not None),
                        "distinct_cues":len(reports),"scored":len(remaining),
                        "correct":correct,"wrong":wrong,"abstained":abstained,
                        "audit_conflict":audit_conflict,
                        "within_group_conflict":within_group_conflict,
                        "cache_writes":writes,"dormant_size":len(dormant)})
    return {"seed":seed,"cohort":"development" if seed<180 else "heldout",
            "condition":condition,"arm":arm,
            "pre_feedback_sha256":pretrace.hexdigest(),
            "return":records[10],"recover":records[11],"episodes":records}


def run():
    fingers={str(seed):fingerprint(seed) for seed in range(176,184)}
    if len(set(fingers.values()))!=8:
        return {"schema":"yggdrasil.y047-audit-channel.v1",
                "classification":"NONUNIQUE_FINGERPRINT","fingerprints":fingers,
                "rows":[],"model_calls":0}
    selection={str(seed):groups(seed) for seed in range(176,184)}
    if any(g is None for g in selection.values()):
        return {"schema":"yggdrasil.y047-audit-channel.v1",
                "classification":"INSUFFICIENT_GROUP_SUPPORT","groups":selection,
                "rows":[],"model_calls":0}
    rows=[evaluate(seed,c,a) for seed in range(176,184)
          for c in CONDITIONS for a in ARMS]
    by={(r["seed"],r["condition"],r["arm"]):r for r in rows}
    valid=True
    for seed in range(176,184):
        stable={by[seed,c,"PRIMARY_FOUR"]["pre_feedback_sha256"]
                for c in CONDITIONS}
        valid &= len(stable)==1
        for c in CONDITIONS:
            first,second=(by[seed,c,arm] for arm in ARMS)
            valid &= ([r["cache_writes"] for r in first["episodes"]]==
                      [r["cache_writes"] for r in second["episodes"]])
            valid &= ([r["dormant_size"] for r in first["episodes"]]==
                      [r["dormant_size"] for r in second["episodes"]])
            valid &= first["recover"]["correct"]==second["recover"]["correct"]==7
            valid &= first["return"]["distinct_cues"]==second["return"]["distinct_cues"]==4
    held=[r for r in rows if r["seed"]>=180]
    stats={c:{a:{field:sum(r["return"][field] for r in held
                      if r["condition"]==c and r["arm"]==a)
                 for field in ("early_reports","distinct_cues","scored",
                               "correct","wrong","abstained","audit_conflict")}
              for a in ARMS} for c in CONDITIONS}
    clean=stats["CLEAN"]["DUAL_CHANNEL_FIVE"]
    primary=stats["PRIMARY_CORRUPT"]
    both=stats["BOTH_CORRUPT"]["DUAL_CHANNEL_FIVE"]
    if not valid:
        classification="INVALID_HISTORY"
    elif (clean["correct"]==12 and primary["PRIMARY_FOUR"]["wrong"]>=1
          and primary["DUAL_CHANNEL_FIVE"]["wrong"]==0
          and primary["DUAL_CHANNEL_FIVE"]["abstained"]>=1
          and both["wrong"]>=1):
        classification="DUAL_CHANNEL_BOUNDARY"
    else:
        classification="NO_GAIN"
    return {"schema":"yggdrasil.y047-audit-channel.v1",
            "parent":"c1492958622f4420b9e8c21704dd8cff9b6d770f",
            "classification":classification,"fingerprints":fingers,
            "groups":selection,"paired_history_valid":bool(valid),
            "heldout":stats,"rows":rows,"model_calls":0,
            "claim_limit":"Fixed parity-group synthetic duplicate channel report. Extra sampled audit truth in one condition and compromised audit in another."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
