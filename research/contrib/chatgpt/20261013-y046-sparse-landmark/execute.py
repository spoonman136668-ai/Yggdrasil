"""Y046: fixed-budget sparse landmark extrapolation under hidden offset shock."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y045-landmark-calibration"/"execute.py"
spec=importlib.util.spec_from_file_location("y45_pinned",SOURCE)
assert spec and spec.loader
y45=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y45)
y25=y45.y25
y36=y45.y36

DEV=tuple(range(1312,1320))
HELDOUT=tuple(range(1320,1336))
FAMILIES=((3,3,1),(5,1,7),(7,9,5),(11,11,3))
REGIMES=("steady","late_shock")
MODES=("reference","raw","sparse_first2","full_two_each_episode")
POLICIES=("matched_sham","full","quorum2")
OBSERVATION_COST={"reference":0,"raw":0,"sparse_first2":4,
                  "full_two_each_episode":16}


def coordinate(cell,seed,episode,family,regime):
    a,s,t=family
    shock=5 if regime=="late_shock" and episode>=4 else 0
    return (a*cell+s*seed+t*episode+shock)%16


def physical_coordinate(observed,seed,episode,family,regime):
    a,s,t=family
    shock=5 if regime=="late_shock" and episode>=4 else 0
    return (pow(a,-1,16)*(observed-s*seed-t*episode-shock))%16


def observed_landmarks(seed,episode,family,regime):
    return (coordinate(0,seed,episode,family,regime),
            coordinate(1,seed,episode,family,regime))


def evaluate(seed,regime,policy,mode,family):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history={}
    rows=[]
    sparse_initial=None
    sparse_followup=None
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        actual_graph=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,actual_graph)==7
        visible_graph={key:{coordinate(cell,seed,episode,family,regime)
                            for cell in legal}
                       for key,legal in actual_graph.items()}
        assert y25.hall_cardinality(active,visible_graph)==7
        anchors=0
        if mode=="reference":
            working_graph=actual_graph
            estimate=None
        elif mode=="raw":
            working_graph=visible_graph
            estimate=None
        else:
            if mode=="full_two_each_episode":
                current0,current1=observed_landmarks(seed,episode,family,regime)
                anchors=2
                a=(current1-current0)%16
                b=current0
            else:
                assert mode=="sparse_first2"
                if episode==0:
                    sparse_initial=observed_landmarks(seed,episode,family,regime)
                    anchors=2
                elif episode==1:
                    sparse_followup=observed_landmarks(seed,episode,family,regime)
                    anchors=2
                if episode==0:
                    b=sparse_initial[0]
                    a=(sparse_initial[1]-sparse_initial[0])%16
                else:
                    assert sparse_initial is not None and sparse_followup is not None
                    b0=sparse_initial[0]
                    b1=sparse_followup[0]
                    a=(sparse_followup[1]-sparse_followup[0])%16
                    b=(b1+(episode-1)*(b1-b0))%16
            assert a%2==1
            estimate=(a,b)
            inv=pow(a,-1,16)
            working_graph={key:{(inv*(cell-b))%16 for cell in cells}
                           for key,cells in visible_graph.items()}
        assert y25.hall_cardinality(active,working_graph)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in working_graph[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        pref=legal if len(legal)>=threshold else {}
        assigned,calls=y25.match(active,working_graph,pref)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        if mode=="reference":
            physical=dict(assigned)
        elif mode=="raw":
            physical={key:physical_coordinate(cell,seed,episode,family,regime)
                      for key,cell in assigned.items()}
        else:
            a,b=estimate
            physical={key:physical_coordinate((a*cell+b)%16,seed,episode,family,regime)
                      for key,cell in assigned.items()}
        assert set(physical)==set(active)
        assert all(physical[key] in actual_graph[key] for key in active)
        returning=[key for key in active if key in history]
        churn=sum(physical[key]!=history[key] for key in returning)
        history.update(physical)
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=dict(assigned)
        rows.append({"episode":episode,"physical_assignment":{str(k):physical[k] for k in sorted(active)},
                     "cache_writes":writes,"cache_occupancy":len(cache),
                     "physical_churn":churn,"search_calls":calls,
                     "anchor_observations":anchors,"matched":len(assigned)})
    assert sum(row["anchor_observations"] for row in rows)==OBSERVATION_COST[mode]
    return {"seed":seed,"regime":regime,"policy":policy,"mode":mode,
            "physical_churn":sum(row["physical_churn"] for row in rows),
            "cache_writes":sum(row["cache_writes"] for row in rows),
            "rows":rows}


def run():
    mismatches={regime:{mode:0 for mode in MODES if mode!="reference"}
                for regime in REGIMES}
    late_mismatches={mode:0 for mode in MODES if mode!="reference"}
    by_family=[]
    for family in FAMILIES:
        family_rows=[]
        for regime in REGIMES:
            for seed in DEV+HELDOUT:
                for policy in POLICIES:
                    arms={mode:evaluate(seed,regime,policy,mode,family)
                          for mode in MODES}
                    reference=arms["reference"]
                    for mode,arm in arms.items():
                        assert reference["cache_writes"]==arm["cache_writes"]
                        for a,b in zip(reference["rows"],arm["rows"]):
                            assert a["cache_writes"]==b["cache_writes"]
                            assert a["cache_occupancy"]==b["cache_occupancy"]
                            assert a["matched"]==b["matched"]==7
                            if mode!="reference" and seed in HELDOUT and a["physical_assignment"]!=b["physical_assignment"]:
                                mismatches[regime][mode]+=1
                                if regime=="late_shock" and a["episode"]>=4:
                                    late_mismatches[mode]+=1
                    family_rows.append({"regime":regime,"seed":seed,"cohort":"heldout" if seed in HELDOUT else "development",
                                        "policy":policy,"churn":{mode:arms[mode]["physical_churn"] for mode in MODES},
                                        "reference_writes":reference["cache_writes"]})
        by_family.append({"family":family,"rows":family_rows})
    if (mismatches["steady"]["sparse_first2"]==0 and
        late_mismatches["sparse_first2"]>0 and
        mismatches["steady"]["full_two_each_episode"]==0 and
        mismatches["late_shock"]["full_two_each_episode"]==0):
        classification="SPARSE_CALIBRATION_FRAGILE"
    else:
        classification="NO_STEADY_TRANSFER"
    return {"schema":"yggdrasil.y046-sparse-landmark-fragility.v1",
            "parent_head":"54eece368ec286bc42b17073ec9336aed324be89",
            "classification":classification,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "regimes":REGIMES,"anchor_readings_per_8_episodes":OBSERVATION_COST,
            "heldout_assignment_mismatches":mismatches,
            "after_episode4_shock_mismatches":late_mismatches,
            "by_family":by_family,"model_calls":0,
            "claim_limit":"Synthetic fixed affine clock extrapolation with an unannounced shock, not robust learned online calibration."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
