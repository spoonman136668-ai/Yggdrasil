"""Y045: common-mode correlated sentinel faults under fixed finite dormant cache."""
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
CONDITIONS = ("CLEAN", "TWO_CORRELATED_FALSE")
ARMS = ("NO_EARLY_REPORT", "THREE_REPORT_UNANIMITY", "FOUR_REPORT_UNANIMITY")


def groups(seed):
    assert 160 <= seed <= 167
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
        if ep==10 and arm!="NO_EARLY_REPORT":
            sampled = ([majority[0], majority[1], minority[0]]
                       if arm=="THREE_REPORT_UNANIMITY"
                       else [majority[0],majority[1],majority[2],minority[0]])
            assert all(k in dormant for k in sampled)
            # The learner receives only these reported sampled labels.
            reports={k:true_value(seed,k,ep) for k in sampled}
            if condition=="TWO_CORRELATED_FALSE":
                for k in majority[:2]:
                    reports[k]=(reports[k]+1)%4
            remaining=[k for k in keys if k not in reports]
        major_deltas=[(reports[k]-dormant[k])%4 for k in majority if k in reports]
        minor_deltas=[(reports[k]-dormant[k])%4 for k in minority if k in reports]
        if reports:
            assert len(minor_deltas)==1 and len(major_deltas) in (2,3)
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
        "seed":seed,"cohort":"development" if seed<164 else "heldout",
        "condition":condition,"arm":arm,
        "pre_feedback_sha256":pretrace.hexdigest(),
        "first_return":history[10],"recovery":history[11],
        "episodes":history,
    }


def run():
    source_signatures={str(seed):fingerprint(seed) for seed in range(160,168)}
    cohort_groups={str(seed):groups(seed) for seed in range(160,168)}
    if any(g is None for g in cohort_groups.values()):
        return {"schema":"yggdrasil.y045-correlated-witness.v1",
                "classification":"INSUFFICIENT_MAJOR_GROUP",
                "groups":cohort_groups,"rows":[],"model_calls":0}
    if len(set(source_signatures.values()))!=8:
        return {"schema":"yggdrasil.y045-correlated-witness.v1",
                "classification":"NONUNIQUE_FINGERPRINT",
                "fingerprints":source_signatures,"rows":[],"model_calls":0}
    rows=[evaluate(seed,cond,arm) for seed in range(160,168)
          for cond in CONDITIONS for arm in ARMS]
    index={(r["seed"],r["condition"],r["arm"]):r for r in rows}
    history_matches=True
    for seed in range(160,168):
        historical={index[seed,cond,"NO_EARLY_REPORT"]["pre_feedback_sha256"]
                    for cond in CONDITIONS}
        history_matches &= len(historical)==1
        for condition in CONDITIONS:
            items=[index[seed,condition,arm] for arm in ARMS]
            writes=[[e["writes"] for e in r["episodes"]] for r in items]
            occupancy=[[e["cache_size"] for e in r["episodes"]] for r in items]
            assert writes[0]==writes[1]==writes[2]
            assert occupancy[0]==occupancy[1]==occupancy[2]
            assert all(r["recovery"]["correct"]==7 for r in items)
    heldout=[r for r in rows if r["seed"]>=164]
    stats={cond:{arm:{metric:sum(
        r["first_return"][metric] for r in heldout
        if r["condition"]==cond and r["arm"]==arm)
        for metric in ("early_reports","scored_opportunities","correct","wrong",
                       "abstained","majority_witness_conflict")}
        for arm in ARMS} for cond in CONDITIONS}
    clean_three=stats["CLEAN"]["THREE_REPORT_UNANIMITY"]
    clean_four=stats["CLEAN"]["FOUR_REPORT_UNANIMITY"]
    bad_three=stats["TWO_CORRELATED_FALSE"]["THREE_REPORT_UNANIMITY"]
    bad_four=stats["TWO_CORRELATED_FALSE"]["FOUR_REPORT_UNANIMITY"]
    if not history_matches:
        classification="INVALID_HIDDEN_HISTORY"
    elif (clean_three["correct"]==16 and clean_three["abstained"]==0
          and clean_four["correct"]==12 and clean_four["abstained"]==0
          and bad_three["wrong"]>=1 and bad_four["wrong"]==0
          and bad_four["abstained"]>=1):
        classification="COMMON_MODE_LIMIT_AND_DETECTION"
    else:
        classification="NO_GAIN"
    return {
        "schema":"yggdrasil.y045-correlated-witness.v1",
        "classification":classification,
        "parent":"55dc60e166034f1110d6d2ac152ab2acc1ae49d3",
        "input_fingerprints":source_signatures,"groups":cohort_groups,
        "pre_reactivation_history_equivalent":bool(history_matches),
        "heldout":stats,"rows":rows,"model_calls":0,
        "claim_limit":"Fixed parity groups and controlled correlated feedback; explicit unequal sensor budgets with abstention cost.",
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
