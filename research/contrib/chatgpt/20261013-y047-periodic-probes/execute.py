"""Y047 frozen scheduled landmark checks across a late coordinate offset shock."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y046-sparse-landmark"/"execute.py"
spec=importlib.util.spec_from_file_location("y46_pinned",SOURCE)
assert spec and spec.loader
y46=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y46)
y25=y46.y25
y36=y46.y36

DEV=tuple(range(1376,1384))
HELDOUT=tuple(range(1384,1400))
FAMILIES=((3,5,1),(5,3,7),(7,11,5),(13,9,3))
REGIMES=("steady","late_shock")
MODES=("reference","raw","sparse_first2","periodic","full_two_each_episode")
POLICIES=("matched_sham","full","quorum2")
PROBES=(0,1,3,5)
READINGS={"reference":0,"raw":0,"sparse_first2":4,"periodic":8,
          "full_two_each_episode":16}


def calibrator(mode,seed,episode,family,regime,state):
    """Candidate uses only current anchors at pre-scheduled observation times."""
    a,d,last_b,last_ep=state
    observed=0
    check=(mode=="full_two_each_episode" or
           (mode=="sparse_first2" and episode in (0,1)) or
           (mode=="periodic" and episode in PROBES))
    if check:
        b0,b1=y46.observed_landmarks(seed,episode,family,regime)
        a_new=(b1-b0)%16
        assert a_new%2==1
        if a is not None:
            assert a_new==a
        a=a_new
        if episode==1:
            assert last_b is not None and last_ep==0
            d=(b0-last_b)%16
        last_b=b0
        last_ep=episode
        b=b0
        observed=2
    else:
        assert a is not None and d is not None
        b=(last_b+(episode-last_ep)*d)%16
    return (a,b),(a,d,last_b,last_ep),observed


def evaluate(seed,regime,policy,mode,family):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history={}
    calibrator_state=(None,None,None,None)
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        true_graph=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,true_graph)==7
        observed_graph={key:{y46.coordinate(cell,seed,episode,family,regime) for cell in legal}
                        for key,legal in true_graph.items()}
        assert y25.hall_cardinality(active,observed_graph)==7
        anchor_reads=0
        if mode=="reference":
            graph=true_graph
            estimated=None
        elif mode=="raw":
            graph=observed_graph
            estimated=None
        else:
            estimated,calibrator_state,anchor_reads=calibrator(
                mode,seed,episode,family,regime,calibrator_state)
            a,b=estimated
            inv=pow(a,-1,16)
            graph={key:{(inv*(c-b))%16 for c in cells}
                   for key,cells in observed_graph.items()}
        assert y25.hall_cardinality(active,graph)==7
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in graph[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferences=legal if len(legal)>=minimum else {}
        assigned,calls=y25.match(active,graph,preferences)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        if mode=="reference":
            physical=dict(assigned)
        elif mode=="raw":
            physical={k:y46.physical_coordinate(v,seed,episode,family,regime)
                      for k,v in assigned.items()}
        else:
            a,b=estimated
            physical={k:y46.physical_coordinate((a*v+b)%16,seed,episode,family,regime)
                      for k,v in assigned.items()}
        assert set(physical)==set(active)
        assert all(physical[k] in true_graph[k] for k in active)
        returning=[k for k in active if k in history]
        churn=sum(physical[k]!=history[k] for k in returning)
        history.update(physical)
        for key in active:
            cache.pop(key,None)
        writes=0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=dict(assigned)
        rows.append({"episode":episode,
                     "physical_assignment":{str(k):physical[k] for k in sorted(active)},
                     "physical_churn":churn,"cache_writes":writes,
                     "cache_occupancy":len(cache),"search_calls":calls,
                     "anchor_observations":anchor_reads,"matched":len(assigned)})
    assert sum(x["anchor_observations"] for x in rows)==READINGS[mode]
    return {"seed":seed,"policy":policy,"regime":regime,"mode":mode,
            "physical_churn":sum(x["physical_churn"] for x in rows),
            "rows":rows}


def run():
    early={r:{mode:0 for mode in MODES if mode!="reference"} for r in REGIMES}
    post={r:{mode:0 for mode in MODES if mode!="reference"} for r in REGIMES}
    at4={mode:0 for mode in MODES if mode!="reference"}
    by_family=[]
    for family in FAMILIES:
        records=[]
        for regime in REGIMES:
            for seed in DEV+HELDOUT:
                for policy in POLICIES:
                    arms={mode:evaluate(seed,regime,policy,mode,family)
                          for mode in MODES}
                    reference=arms["reference"]
                    mismatch_by_mode={}
                    for mode,arm in arms.items():
                        assert sum(x["cache_writes"] for x in reference["rows"])==sum(x["cache_writes"] for x in arm["rows"])
                        mismatch_by_mode[mode]=0
                        for a,b in zip(reference["rows"],arm["rows"]):
                            assert a["cache_writes"]==b["cache_writes"]
                            assert a["cache_occupancy"]==b["cache_occupancy"]
                            assert a["matched"]==b["matched"]==7
                            if (mode!="reference" and seed in HELDOUT and
                                a["physical_assignment"]!=b["physical_assignment"]):
                                mismatch_by_mode[mode]+=1
                                if a["episode"]<5: early[regime][mode]+=1
                                else: post[regime][mode]+=1
                                if regime=="late_shock" and a["episode"]==4:
                                    at4[mode]+=1
                    records.append({"seed":seed,"regime":regime,
                                    "cohort":"heldout" if seed in HELDOUT else "development",
                                    "policy":policy,
                                    "mismatches":mismatch_by_mode,
                                    "churn":{m:arms[m]["physical_churn"] for m in MODES}})
        by_family.append({"family":family,"records":records})
    steady_zero=(early["steady"]["periodic"]==0 and post["steady"]["periodic"]==0 and
                 early["steady"]["sparse_first2"]==0 and post["steady"]["sparse_first2"]==0)
    full_zero=all(early[r]["full_two_each_episode"]==0 and
                  post[r]["full_two_each_episode"]==0 for r in REGIMES)
    if (steady_zero and full_zero and at4["periodic"]>0 and
        post["late_shock"]["periodic"]==0 and post["late_shock"]["sparse_first2"]>0):
        classification="PERIODIC_FULL_RECOVERY"
    elif (steady_zero and full_zero and
          post["late_shock"]["periodic"]<post["late_shock"]["sparse_first2"]):
        classification="PERIODIC_PARTIAL_RECOVERY"
    else:
        classification="NO_CONFIRMED_RECOVERY"
    return {"schema":"yggdrasil.y047-periodic-landmark-recovery.v1",
            "parent_head":"93270cc764290e63a83272c35a1ac9dfcb01615a",
            "classification":classification,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"probe_episodes":PROBES,
            "anchor_readings_per_8_episodes":READINGS,
            "mismatches_episodes0to4":early,"mismatches_episodes5to7":post,
            "mismatches_at_episode4_shock":at4,
            "by_family":by_family,"model_calls":0,
            "claim_limit":"Synthetic fixed periodic current-frame landmark checks, not hidden-shock detection or general autonomous adaptation."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
