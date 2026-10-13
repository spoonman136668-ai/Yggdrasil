"""Y037: observed mixed-feedback consensus versus unsupported plurality correction."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y036-hidden-subgroup"/"execute.py"
spec=importlib.util.spec_from_file_location("y036_frozen",PREVIOUS)
assert spec and spec.loader
y36=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y36)
y33=y36.y33

ARMS=("baseline","consensus","plurality")


def active_keys(seed,episode):
    return [(seed+3*episode+j)%16 for j in range(7)]


def true_label(seed,key,episode,condition):
    base=y33.target(seed,key,0,"STABLE")
    if condition=="MIXED_SWITCH" and episode>=6:
        return (base+(1 if key%2==0 else 2))%4
    return base


def fixture_geometry():
    for seed in range(96,104):
        for episode in range(1,12):
            before=set(active_keys(seed,episode-1))
            now=set(active_keys(seed,episode))
            overlap=before.intersection(now)
            assert len(overlap)==4
            assert sum(key%2==0 for key in overlap)==2
    return "PASS"


def choose_correction(deltas,arm):
    if arm=="baseline":
        return 0,False
    nonzero=[d for d in deltas if d]
    if arm=="consensus":
        return (deltas[0] if deltas and len(set(deltas))==1
                and deltas[0]!=0 else 0),False
    assert arm=="plurality"
    if not nonzero:
        return 0,False
    counts={d:nonzero.count(d) for d in set(nonzero)}
    best=min(counts,key=lambda d:(-counts[d],d))
    return best,len(set(deltas))>1


def evaluate(seed,condition,arm):
    live={}
    dormant=OrderedDict()
    seen=set()
    episodes=[]
    for episode in range(12):
        active=active_keys(seed,episode)
        guess={key:live[key] if key in live else dormant.get(key,0)
               for key in active}
        # Only observed active labels, and only after all predictions.
        truth={key:true_label(seed,key,episode,condition) for key in active}
        overlaps=[key for key in active if key in live]
        deltas=[(truth[key]-live[key])%4 for key in overlaps]
        correction,unsupported=choose_correction(deltas,arm)
        returning=[key for key in active if key in seen and key not in live]
        correct=sum(guess[key]==truth[key] for key in active)
        dormant_correct=sum(guess[key]==truth[key] for key in returning)
        for key in active:
            dormant.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        maintenance=0
        if correction:
            for key in tuple(dormant):
                dormant[key]=(dormant[key]+correction)%4
                maintenance+=1
        live=truth
        seen.update(active)
        assert len(live)==7 and len(dormant)<=9
        assert len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        episodes.append({
            "episode":episode,"correct":correct,"returning":len(returning),
            "dormant_correct":dormant_correct,"overlap":len(overlaps),
            "delta_counts":{str(i):deltas.count(i) for i in range(4)},
            "feedback_correction":correction,
            "unsupported_global_update":unsupported and correction!=0,
            "maintenance":maintenance,"writes":writes,"dormant_size":len(dormant),
        })
    return {
        "seed":seed,"condition":condition,"arm":arm,
        "cohort":"development" if seed<100 else "heldout",
        "total_correct":sum(e["correct"] for e in episodes),
        "post_correct":sum(e["correct"] for e in episodes[7:]),
        "post_dormant_correct":sum(e["dormant_correct"] for e in episodes[7:]),
        "maintenance":sum(e["maintenance"] for e in episodes),
        "writes":sum(e["writes"] for e in episodes),
        "unsupported_updates":sum(e["unsupported_global_update"] for e in episodes),
        "episodes":episodes,
    }


def run():
    assert fixture_geometry()=="PASS"
    signatures={
        str(seed):hashlib.sha256(json.dumps(
            [active_keys(seed,ep) for ep in range(12)]
            +[[true_label(seed,key,0,"STABLE") for key in range(16)]]
        ).encode()).hexdigest() for seed in range(96,104)
    }
    assert len(set(signatures.values()))==8
    rows=[]
    for condition in ("STABLE","MIXED_SWITCH"):
        for seed in range(96,104):
            cases=[evaluate(seed,condition,arm) for arm in ARMS]
            assert len({r["writes"] for r in cases})==1
            assert len({tuple(e["dormant_size"] for e in r["episodes"])
                        for r in cases})==1
            rows.extend(cases)
    def total(condition,arm,field):
        return sum(r[field] for r in rows if r["seed"]>=100
                   and r["condition"]==condition and r["arm"]==arm)
    stable={arm:total("STABLE",arm,"total_correct") for arm in ARMS}
    post={arm:total("MIXED_SWITCH",arm,"post_correct") for arm in ARMS}
    maintenance={arm:total("MIXED_SWITCH",arm,"maintenance") for arm in ARMS}
    mixed=[r for r in rows if r["seed"]>=100 and r["condition"]=="MIXED_SWITCH"]
    each_switch_has_conflict=all(
        dict((int(k),v) for k,v in r["episodes"][6]["delta_counts"].items())[1]==2
        and r["episodes"][6]["delta_counts"]["2"]==2
        for r in mixed
    )
    no_consensus_updates=all(r["episodes"][6]["feedback_correction"]==0
                             for r in mixed if r["arm"]=="consensus")
    plurality_updates=all(r["episodes"][6]["feedback_correction"]!=0
                          for r in mixed if r["arm"]=="plurality")
    if each_switch_has_conflict and no_consensus_updates and plurality_updates:
        outcome="CONSENSUS_ABSTAINS"
    elif post["plurality"]<post["consensus"]:
        outcome="HARMFUL_PLURALITY"
    else:
        outcome="OTHER"
    return {
        "schema":"yggdrasil.y037-conflict-gated-memory-correction.v1",
        "predecessor_head":"09079bfed6628dc06f70018bf40453d97c20c24a",
        "classification":outcome,"structural_fixture":"PASS",
        "heldout_stable_correct":stable,
        "heldout_mixed_post_correct":post,
        "heldout_mixed_maintenance":maintenance,
        "heldout_mixed_unsupported_plurality_updates":
            total("MIXED_SWITCH","plurality","unsupported_updates"),
        "each_switch_has_two_deltas":each_switch_has_conflict,
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic mixed-feedback abstention with predefined labels and fixed memory.",
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
