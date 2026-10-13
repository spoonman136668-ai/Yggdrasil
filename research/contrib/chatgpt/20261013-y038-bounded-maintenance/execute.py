"""Y038: newest-three capped plurality repair, same nine dormant slots."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parent.parent/"20261013-y037-consensus"/"execute.py"
spec=importlib.util.spec_from_file_location("y037_frozen",PREVIOUS)
assert spec and spec.loader
y37=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y37)

ARMS=("baseline","full_plurality","capped_three")


def evaluate(seed,condition,arm):
    live={}
    dormant=OrderedDict()
    seen=set()
    episodes=[]
    for episode in range(12):
        active=y37.active_keys(seed,episode)
        guesses={
            key:live[key] if key in live else dormant.get(key,0)
            for key in active
        }
        observed={
            key:y37.true_label(seed,key,episode,condition)
            for key in active
        }
        overlaps=[key for key in active if key in live]
        deltas=[(observed[key]-live[key])%4 for key in overlaps]
        correction,unsupported=(
            (0,False) if arm=="baseline" else
            y37.choose_correction(deltas,"plurality")
        )
        returning=[key for key in active if key in seen and key not in live]
        correct=sum(guesses[key]==observed[key] for key in active)
        returning_correct=sum(guesses[key]==observed[key] for key in returning)
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
            selected=list(dormant) if arm=="full_plurality" else list(dormant)[-3:]
            for key in selected:
                dormant[key]=(dormant[key]+correction)%4
                maintenance+=1
        live=observed
        seen.update(active)
        assert len(live)==7 and len(dormant)<=9
        assert len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        episodes.append({
            "episode":episode,"correct":correct,"returning":len(returning),
            "returning_correct":returning_correct,
            "overlap":len(overlaps),"correction":correction,
            "unsupported":bool(unsupported and correction),
            "maintenance":maintenance,"writes":writes,
            "dormant_entries":len(dormant),
        })
    return {
        "seed":seed,"cohort":"development" if seed<108 else "heldout",
        "condition":condition,"arm":arm,
        "total_correct":sum(r["correct"] for r in episodes),
        "post_correct":sum(r["correct"] for r in episodes[7:]),
        "post_returning_correct":sum(r["returning_correct"] for r in episodes[7:]),
        "maintenance":sum(r["maintenance"] for r in episodes),
        "writes":sum(r["writes"] for r in episodes),
        "unsupported":sum(r["unsupported"] for r in episodes),
        "episodes":episodes,
    }


def run():
    assert y37.fixture_geometry()=="PASS"  # purely structural 7+4 overlap check
    signatures={
        str(seed):hashlib.sha256(json.dumps([
            y37.active_keys(seed,ep) for ep in range(12)
        ]+[[y37.true_label(seed,key,0,"STABLE") for key in range(16)]]).encode()).hexdigest()
        for seed in range(104,112)
    }
    assert len(set(signatures.values()))==8
    rows=[]
    for condition in ("STABLE","MIXED_SWITCH"):
        for seed in range(104,112):
            cases=[evaluate(seed,condition,arm) for arm in ARMS]
            assert len({case["writes"] for case in cases})==1
            assert len({tuple(x["dormant_entries"] for x in case["episodes"])
                        for case in cases})==1
            rows.extend(cases)
    def total(condition,arm,metric):
        return sum(r[metric] for r in rows if r["seed"]>=108
                   and r["condition"]==condition and r["arm"]==arm)
    stable={arm:total("STABLE",arm,"total_correct") for arm in ARMS}
    post={arm:total("MIXED_SWITCH",arm,"post_correct") for arm in ARMS}
    maintenance={arm:total("MIXED_SWITCH",arm,"maintenance") for arm in ARMS}
    gain_full=post["full_plurality"]-post["baseline"]
    gain_capped=post["capped_three"]-post["baseline"]
    if gain_full>0 and gain_capped*2>=gain_full and maintenance["capped_three"]*3<=maintenance["full_plurality"]:
        label="CAPPED_EFFICIENCY"
    elif gain_capped<0:
        label="HARM"
    else:
        label="MIXED"
    return {
        "schema":"yggdrasil.y038-capped-recency-maintenance.v1",
        "predecessor_head":"d38b5b04b2caf5151ad320e760a65d95e89b8850",
        "classification":label,"unique_signatures":True,
        "heldout_stable_correct":stable,
        "heldout_mixed_post_correct":post,
        "heldout_mixed_maintenance":maintenance,
        "full_gain":gain_full,"capped_gain":gain_capped,
        "rows":rows,"model_calls":0,
        "claim_limit":"Fixed three-write recency policy in synthetic cue memory; not generalized resource-aware cognition.",
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
