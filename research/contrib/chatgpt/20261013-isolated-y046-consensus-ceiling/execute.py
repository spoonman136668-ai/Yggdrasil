"""Y046: three correlated majority sensor faults and a fourth independent check."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y040-hibernation" / "execute.py"
_spec = importlib.util.spec_from_file_location("y040_frozen", PREVIOUS)
assert _spec and _spec.loader
y40 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y40)
CONDITIONS = ("CLEAN", "CORRELATED_THREE_FALSE")
ARMS = ("NO_REPORT", "FOUR_REPORT", "FIVE_REPORT")


def groups(seed):
    assert 168 <= seed <= 175
    core = y40.active(seed, 10)
    even = [key for key in core if key % 2 == 0]
    odd = [key for key in core if key % 2 == 1]
    if not even or not odd:
        return None
    majority, minority = ((even, odd) if len(even)>len(odd)
                           else (odd, even))
    assert len(majority)>=4
    return majority, minority


def true_value(seed,key,ep):
    initial = y40.target(seed,key,0,"STABLE")
    if ep < 6 or key not in y40.permutation(seed)[:7]:
        return initial
    return (initial+2)%4


def fingerprint(seed):
    raw={"permutation":y40.permutation(seed),
         "initial":[true_value(seed,key,0) for key in range(16)]}
    return hashlib.sha256(json.dumps(raw,sort_keys=True,
                           separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,arm):
    majority, minority = groups(seed)
    live={}
    dormant=OrderedDict()
    pretrace=hashlib.sha256()
    history=[]
    for ep in range(12):
        keys=y40.active(seed,ep)
        assert len(keys)==7
        reports={}
        remaining=list(keys)
        if ep==10 and arm!="NO_REPORT":
            sampled = ([majority[0],majority[1],majority[2],minority[0]]
                       if arm=="FOUR_REPORT"
                       else [majority[0],majority[1],majority[2],
                             majority[3],minority[0]])
            assert all(k in dormant for k in sampled)
            # The learner receives only these reported sampled labels.
            reports={k:true_value(seed,k,ep) for k in sampled}
            if condition=="CORRELATED_THREE_FALSE":
                for k in majority[:3]:
                    reports[k]=(reports[k]+1)%4
            remaining=[k for k in keys if k not in reports]
        major_deltas=[(reports[k]-dormant[k])%4 for k in majority if k in reports]
        minor_deltas=[(reports[k]-dormant[k])%4 for k in minority if k in reports]
        if reports:
            assert len(minor_deltas)==1 and len(major_deltas) in (3,4)
        major_consistent=(len(set(major_deltas))==1) if major_deltas else True
        predictions={}
        for key in remaining:
            prior=live[key] if key in live else dormant.get(key,0)
            if not reports:
                forecast=prior
            elif key in majority and not major_consistent:
                forecast=None
            else:
                shift=major_deltas[0] if key in majority else minor_deltas[0]
                forecast=(prior+shift)%4
            predictions[key]=forecast
        assert len(predictions)+len(reports)==7
        assert not set(predictions).intersection(reports)
        # Authoritative labels, including replacement for corrupted reports,
        # become available after remaining predictions are fixed.
        feedback={key:true_value(seed,key,ep) for key in keys}
        correct=sum(predictions[key]==feedback[key] for key in remaining)
        abstained=sum(predictions[key] is None for key in remaining)
        wrong=len(remaining)-correct-abstained
        if ep<=9:
            pretrace.update(bytes((ep,))+bytes(
                part for key in keys for part in (key,feedback[key])))
        for key in keys:
            dormant.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(keys)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        live=feedback
        assert len(live)==7 and len(dormant)<=9
        assert not set(live).intersection(dormant)
        history.append({
            "episode":ep,"early_reports":len(reports),
            "scored_opportunities":len(remaining),
            "correct":correct,"wrong":wrong,"abstained":abstained,
            "majority_witness_conflict":bool(reports) and not major_consistent,
            "writes":writes,"cache_size":len(dormant),
        })
    return {
        "seed":seed,"cohort":"development" if seed<172 else "heldout",
        "condition":condition,"arm":arm,
        "pre_feedback_sha256":pretrace.hexdigest(),
        "first_return":history[10],"recovery":history[11],
        "episodes":history,
    }


def run():
    source_signatures={str(seed):fingerprint(seed) for seed in range(168,176)}
    cohort_groups={str(seed):groups(seed) for seed in range(168,176)}
    if any(g is None for g in cohort_groups.values()):
        return {"schema":"yggdrasil.y046-consensus-ceiling.v1",
                "classification":"INSUFFICIENT_MAJOR_GROUP",
                "groups":cohort_groups,"rows":[],"model_calls":0}
    if len(set(source_signatures.values()))!=8:
        return {"schema":"yggdrasil.y046-consensus-ceiling.v1",
                "classification":"NONUNIQUE_FINGERPRINT",
                "fingerprints":source_signatures,"rows":[],"model_calls":0}
    records=[evaluate(seed,condition,arm)
             for seed in range(168,176)
             for condition in CONDITIONS for arm in ARMS]
    lookup={(r["seed"],r["condition"],r["arm"]):r for r in records}
    histories_match=True
    for seed in range(168,176):
        hashes={lookup[seed,condition,"NO_REPORT"]["pre_feedback_sha256"]
                for condition in CONDITIONS}
        histories_match &= len(hashes)==1
        for condition in CONDITIONS:
            sampled=[lookup[seed,condition,arm] for arm in ARMS]
            writes=[[e["writes"] for e in x["episodes"]] for x in sampled]
            occupied=[[e["cache_size"] for e in x["episodes"]] for x in sampled]
            assert writes[0]==writes[1]==writes[2]
            assert occupied[0]==occupied[1]==occupied[2]
            assert all(x["recovery"]["correct"]==7 for x in sampled)
    heldout=[r for r in records if r["seed"]>=172]
    stats={condition:{arm:{metric:sum(
        x["first_return"][metric] for x in heldout
        if x["condition"]==condition and x["arm"]==arm)
        for metric in ("early_reports","scored_opportunities","correct","wrong",
                       "abstained","majority_witness_conflict")}
        for arm in ARMS} for condition in CONDITIONS}
    clean4=stats["CLEAN"]["FOUR_REPORT"]
    clean5=stats["CLEAN"]["FIVE_REPORT"]
    fault4=stats["CORRELATED_THREE_FALSE"]["FOUR_REPORT"]
    fault5=stats["CORRELATED_THREE_FALSE"]["FIVE_REPORT"]
    if not histories_match:
        classification="INVALID_HIDDEN_HISTORY"
    elif (clean4["correct"]==12 and clean4["abstained"]==0 and
          clean5["correct"]==8 and clean5["abstained"]==0 and
          fault4["wrong"]>=1 and fault5["majority_witness_conflict"]==4 and
          fault5["wrong"]==0):
        classification="COMMON_MODE_CEILING"
    else:
        classification="NO_GAIN"
    return {
        "schema":"yggdrasil.y046-consensus-ceiling.v1",
        "parent":"bcda00a10d98e7bd71a7d2af7ac508c2d156673f",
        "classification":classification,
        "input_fingerprints":source_signatures,"groups":cohort_groups,
        "pre_reactivation_history_equivalent":bool(histories_match),
        "heldout":stats,"rows":records,"model_calls":0,
        "claim_limit":"Synthetic correlated report errors; sampling more ground truth can expose a contradiction but never guarantees reliability against faults shared by all witnesses.",
    }


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
