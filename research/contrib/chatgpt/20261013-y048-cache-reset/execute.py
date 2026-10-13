"""Y048: matched canonical interventions locate persistent postshock cache error."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y047-periodic-probes"/"execute.py"
spec=importlib.util.spec_from_file_location("y47_pinned",SOURCE)
assert spec and spec.loader
y47=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y47)
y46=y47.y46
y25=y47.y25
y36=y47.y36

DEV=tuple(range(1520,1528))
HELDOUT=tuple(range(1528,1544))
FAMILIES=((3,5,1),(5,3,7),(7,11,5),(13,9,3))
REGIMES=("steady","late_shock")
POLICIES=y47.POLICIES
INTERVENTIONS=("continue","flush","quarantine")
MODES=("reference","periodic")


def evaluate(seed,regime,policy,mode,intervention,family):
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    physical_history={}
    calibration=(None,None,None,None)
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        true_graph=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,true_graph)==7
        visible_graph={k:{y46.coordinate(v,seed,episode,family,regime)
                         for v in cells} for k,cells in true_graph.items()}
        assert y25.hall_cardinality(active,visible_graph)==7
        anchors=0
        if mode=="reference":
            graph=true_graph
            predicted_frame=None
        else:
            assert mode=="periodic"
            predicted_frame,calibration,anchors=y47.calibrator(
                "periodic",seed,episode,family,regime,calibration)
            a,b=predicted_frame
            invert=pow(a,-1,16)
            graph={k:{(invert*(v-b))%16 for v in cells}
                   for k,cells in visible_graph.items()}
        assert y25.hall_cardinality(active,graph)==7

        # This operation is precommitted to episode 5 in BOTH the canonical
        # control and periodic arm, not triggered by scientific outcomes.
        flushed=episode==5 and intervention!="continue"
        if flushed:
            cache.clear()
        preferences={k:cache[k] for k in active
                     if k in cache and cache[k] in graph[k]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        pref=preferences if len(preferences)>=threshold else {}
        assigned,calls=y25.match(active,graph,pref)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        if mode=="reference":
            physical=dict(assigned)
        else:
            a,b=predicted_frame
            physical={k:y46.physical_coordinate((a*v+b)%16,seed,episode,family,regime)
                      for k,v in assigned.items()}
        assert set(physical)==set(active)
        assert all(physical[k] in true_graph[k] for k in active)
        returning=[k for k in active if k in physical_history]
        churn=sum(physical[k]!=physical_history[k] for k in returning)
        physical_history.update(physical)
        for k in active:
            cache.pop(k,None)
        departing=sorted(previous_active.difference(active))
        skip_departures=(episode==5 and intervention=="quarantine")
        writes=0
        for k in departing:
            if skip_departures:
                continue
            cache.pop(k,None)
            cache[k]=previous_assignment[k]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=dict(assigned)
        rows.append({"episode":episode,"physical_assignment":{str(k):physical[k] for k in sorted(active)},
                     "churn":churn,"cache_writes":writes,"cache_occupancy":len(cache),
                     "skipped_departures":len(departing) if skip_departures else 0,
                     "flushed":flushed,"search_calls":calls,
                     "landmark_readings":anchors,"matched":len(assigned)})
    assert sum(r["landmark_readings"] for r in rows)==(8 if mode=="periodic" else 0)
    return {"seed":seed,"mode":mode,"intervention":intervention,"policy":policy,
            "regime":regime,"rows":rows}


def run():
    aggregate={regime:{intv:{"pre5":0,"post5":0,"at4":0}
                       for intv in INTERVENTIONS} for regime in REGIMES}
    by_family=[]
    for family in FAMILIES:
        records=[]
        for regime in REGIMES:
            for seed in DEV+HELDOUT:
                for policy in POLICIES:
                    comparisons={}
                    for intervention in INTERVENTIONS:
                        reference=evaluate(seed,regime,policy,"reference",intervention,family)
                        periodic=evaluate(seed,regime,policy,"periodic",intervention,family)
                        seed_pre=seed_post=at4=0
                        for a,b in zip(reference["rows"],periodic["rows"]):
                            assert a["episode"]==b["episode"]
                            assert a["cache_writes"]==b["cache_writes"]
                            assert a["cache_occupancy"]==b["cache_occupancy"]
                            assert a["skipped_departures"]==b["skipped_departures"]
                            assert a["flushed"]==b["flushed"]
                            assert a["matched"]==b["matched"]==7
                            different=a["physical_assignment"]!=b["physical_assignment"]
                            if seed in HELDOUT and different:
                                if a["episode"]<5:seed_pre+=1
                                else:seed_post+=1
                                if a["episode"]==4:at4+=1
                        if seed in HELDOUT:
                            aggregate[regime][intervention]["pre5"]+=seed_pre
                            aggregate[regime][intervention]["post5"]+=seed_post
                            aggregate[regime][intervention]["at4"]+=at4
                        comparisons[intervention]={
                            "mismatches_pre5":seed_pre,"mismatches_post5":seed_post,
                            "physical_churn_reference":sum(x["churn"] for x in reference["rows"]),
                            "physical_churn_periodic":sum(x["churn"] for x in periodic["rows"]),
                            "write_count":sum(x["cache_writes"] for x in reference["rows"]),
                            "intervention_flushes":sum(x["flushed"] for x in reference["rows"]),
                            "skipped_departures":sum(x["skipped_departures"] for x in reference["rows"])}
                    records.append({"regime":regime,"seed":seed,
                                    "cohort":"heldout" if seed in HELDOUT else "development",
                                    "policy":policy,"comparisons":comparisons})
        by_family.append({"family":family,"records":records})
    current=aggregate["late_shock"]
    if current["continue"]["post5"]>0 and current["quarantine"]["post5"]==0:
        classification="BOUNDED_RESET_RESCUE"
    elif min(current["flush"]["post5"],current["quarantine"]["post5"])<current["continue"]["post5"]:
        classification="PARTIAL_RESET_RESCUE"
    else:
        classification="NO_RESET_BENEFIT"
    return {"schema":"yggdrasil.y048-matched-cache-reset.v1",
            "parent_head":"c835fbfc7608dba59d68993228a4a567c0844645",
            "classification":classification,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"regimes":REGIMES,"interventions":INTERVENTIONS,
            "aggregate_paired_mismatches":aggregate,"by_family":by_family,
            "model_calls":0,
            "claim_limit":"Synthetic time-based cache reset ablation with matched controls; not autonomous error awareness or proven general repair."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
