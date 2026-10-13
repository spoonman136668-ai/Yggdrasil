"""Y045: two current-episode landmarks recover unknown affine cell coordinates."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "20261013-y040-affine-family" / "execute.py"
spec = importlib.util.spec_from_file_location("y040_pinned", SOURCE)
assert spec and spec.loader
y40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)
y39 = y40.y39
y25 = y39.y25
y36 = y39.y36

DEV = tuple(range(1160,1168))
HELDOUT = tuple(range(1168,1184))
FAMILIES = ((3,1,5),(5,5,3),(7,7,11),(9,9,13))
MODES = ("reference_numeric","moving_raw_numeric","one_landmark","two_landmark")
POLICIES = y39.POLICIES
OBSERVATIONS = {"reference_numeric":0,"moving_raw_numeric":0,
                "one_landmark":1,"two_landmark":2}


def encode(cell, seed, episode, family):
    a,s,t=family
    return (a*cell+s*seed+t*episode)%16


def truth_physical_cell(observed_cell, seed, episode, family):
    """Evaluator-only readout; never called before or within the candidate matcher."""
    a,s,t=family
    return (pow(a,-1,16)*(observed_cell-s*seed-t*episode))%16


def infer_frame(mode, anchor0, anchor1):
    """Returns a candidate mapping using ONLY the declared observable anchors."""
    if mode=="moving_raw_numeric":
        return (1,0)
    if mode=="one_landmark":
        assert anchor0 is not None
        return (1,anchor0)
    assert mode=="two_landmark"
    assert anchor0 is not None and anchor1 is not None
    b=anchor0
    a=(anchor1-anchor0)%16
    assert a%2==1
    return (a,b)


def evaluate(seed, mode, policy, family):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        physical_graph=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,physical_graph)==7
        observed_graph={key:{encode(c,seed,episode,family) for c in legal}
                        for key,legal in physical_graph.items()}
        assert y25.hall_cardinality(active,observed_graph)==7
        if mode=="reference_numeric":
            working_graph=physical_graph
        elif mode=="moving_raw_numeric":
            working_graph=observed_graph
        else:
            # The experimenter produces publicly observable landmark coordinates;
            # the candidate learns NOTHING from the actual hidden allocation.
            anchor0=encode(0,seed,episode,family)
            anchor1=(encode(1,seed,episode,family)
                     if mode=="two_landmark" else None)
            a,b=infer_frame(mode,anchor0,anchor1)
            inverse=pow(a,-1,16)
            working_graph={key:{(inverse*(v-b))%16 for v in observed}
                           for key,observed in observed_graph.items()}
        assert y25.hall_cardinality(active,working_graph)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in working_graph[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        pref=legal if len(legal)>=threshold else {}
        assigned,calls=y25.match(active,working_graph,pref)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        # Truth readout is only used after all matching decisions.
        if mode=="reference_numeric" or mode=="two_landmark":
            physical=dict(assigned)
        elif mode=="moving_raw_numeric":
            physical={key:truth_physical_cell(cell,seed,episode,family)
                      for key,cell in assigned.items()}
        else:
            # The one-landmark candidate assumes a=1, so its coordinates
            # are actually a*physical rather than physical.
            b=encode(0,seed,episode,family)
            physical={key:truth_physical_cell((cell+b)%16,seed,episode,family)
                      for key,cell in assigned.items()}
        assert set(physical)==set(active)
        assert all(physical[k] in physical_graph[k] for k in active)
        returning=[key for key in active if key in history]
        churn=sum(physical[key]!=history[key] for key in returning)
        history.update(physical)
        for key in active: cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9: cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=dict(assigned)
        rows.append({"episode":episode,"physical_assignment":{str(k):physical[k] for k in sorted(active)},
                     "physical_churn":churn,"cache_writes":writes,
                     "cache_occupancy":len(cache),"search_calls":calls,
                     "legal_preferences":len(legal),"matched":len(assigned),
                     "anchor_observations":OBSERVATIONS[mode]})
    return {"seed":seed,"mode":mode,"policy":policy,"family":family,
            "physical_churn":sum(x["physical_churn"] for x in rows),
            "cache_writes":sum(x["cache_writes"] for x in rows),
            "anchor_observations":sum(x["anchor_observations"] for x in rows),
            "rows":rows}


def run():
    mismatches={m:0 for m in MODES if m!="reference_numeric"}
    by_family=[]
    for family in FAMILIES:
        seed_rows=[]
        family_mismatches={m:0 for m in mismatches}
        for seed in DEV+HELDOUT:
            for policy in POLICIES:
                arms={m:evaluate(seed,m,policy,family) for m in MODES}
                reference=arms["reference_numeric"]
                for mode,other in arms.items():
                    assert reference["cache_writes"]==other["cache_writes"]
                    for a,b in zip(reference["rows"],other["rows"]):
                        assert a["cache_writes"]==b["cache_writes"]
                        assert a["cache_occupancy"]==b["cache_occupancy"]
                        assert a["matched"]==b["matched"]==7
                        if mode!="reference_numeric" and seed in HELDOUT and a["physical_assignment"]!=b["physical_assignment"]:
                            mismatches[mode]+=1
                            family_mismatches[mode]+=1
                seed_rows.append({"seed":seed,"cohort":"development" if seed in DEV else "heldout",
                                  "policy":policy,"churn":{m:arms[m]["physical_churn"] for m in MODES},
                                  "cache_writes":reference["cache_writes"]})
        by_family.append({"family":family,"heldout_mismatches":family_mismatches,
                          "seed_rows":seed_rows})
    if mismatches["two_landmark"]==0 and mismatches["one_landmark"]>0 and mismatches["moving_raw_numeric"]>0:
        label="TWO_LANDMARK_IDENTIFIABILITY"
    elif mismatches["two_landmark"]<min(mismatches["one_landmark"],mismatches["moving_raw_numeric"]):
        label="PARTIAL"
    else:
        label="NO_TRANSFER"
    return {"schema":"yggdrasil.y045-landmark-calibrated-affine.v1",
            "parent_head":"2db6dfe3e464531f60531dc1c75416ea3d276e75",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "heldout_assignment_mismatches":mismatches,
            "anchor_observations_per_episode":OBSERVATIONS,
            "by_family":by_family,"model_calls":0,
            "claim_limit":"Two visible stable landmarks reveal deterministic coordinate metadata with extra sensor cost; no learned inference from hidden frames"}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
