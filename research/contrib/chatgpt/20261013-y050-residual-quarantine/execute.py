"""Y050: public observed-landmark phase innovation gates a one-episode quarantine."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y049-reset-timing"/"execute.py"
spec=importlib.util.spec_from_file_location("y49_pinned",SOURCE)
assert spec and spec.loader
y49=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y49)
y48=y49.y48
y47=y48.y47
y46=y49.y46
y25=y48.y25
y36=y48.y36

DEV=tuple(range(1728,1736))
HELDOUT=tuple(range(1736,1752))
FAMILIES=((3,1,5),(5,7,3),(7,11,1),(13,9,7))
REGIMES=(("steady",None),("onset3",3),("onset4",4),("onset6",6))
POLICIES=("matched_sham","full","quorum2")
INTERVENTIONS=("continue","fixed","trigger")
MODES=("canonical","periodic")
PROBES=(0,1,3,5,7)
RESET_EPISODES=(5,7)


def public_calibration(seed,episode,family,state):
    """No future observations; sample only current public anchor cells 0 and 1."""
    a,d,last_b,last_ep=state
    observed=0
    residual=False
    if episode in PROBES:
        now0,now1=y46.observed_landmarks(seed,episode,family,"late_shock")
        observed=2
        aa=(now1-now0)%16
        assert aa%2==1
        if a is not None:
            assert aa==a
        if a is None:
            a=aa
        if d is not None:
            projected=(last_b+(episode-last_ep)*d)%16
            residual=(now0!=projected)
        if episode==1:
            assert last_b is not None and last_ep==0
            d=(now0-last_b)%16
        last_b=now0
        last_ep=episode
        b=now0
    else:
        assert a is not None and d is not None
        b=(last_b+(episode-last_ep)*d)%16
    return (a,b),(a,d,last_b,last_ep),observed,residual


def evaluate(seed,policy,mode,intervention,family):
    """Exact shared physical task and matched time-/measurement-triggered controls."""
    cache=OrderedDict()
    previous_active=set()
    previous_assignment={}
    history={}
    calibration=(None,None,None,None)
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        physical_neighbors=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,physical_neighbors)==7
        observed_neighbors={key:{y46.coordinate(cell,seed,episode,family,"late_shock")
                                 for cell in allowed}
                            for key,allowed in physical_neighbors.items()}
        assert y25.hall_cardinality(active,observed_neighbors)==7

        estimated,calibration,reads,residual=public_calibration(
            seed,episode,family,calibration)
        a,b=estimated
        assert a is not None and a%2==1
        if mode=="canonical":
            working_neighbors=physical_neighbors
        else:
            assert mode=="periodic"
            inverse=pow(a,-1,16)
            working_neighbors={key:{(inverse*(cell-b))%16 for cell in allowed}
                               for key,allowed in observed_neighbors.items()}
        assert y25.hall_cardinality(active,working_neighbors)==7
        if intervention=="continue":
            do_reset=False
        elif intervention=="fixed":
            do_reset=episode in RESET_EPISODES
        else:
            assert intervention=="trigger"
            do_reset=episode in RESET_EPISODES and residual
        if do_reset:
            cache.clear()
        legal={key:cache[key] for key in active
               if key in cache and cache[key] in working_neighbors[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=threshold else {}
        assigned,calls=y25.match(active,working_neighbors,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        if mode=="canonical":
            physical=dict(assigned)
        else:
            physical={key:y46.physical_coordinate(
                        (a*cell+b)%16,seed,episode,family,"late_shock")
                      for key,cell in assigned.items()}
        assert set(physical)==set(active)
        assert all(physical[key] in physical_neighbors[key] for key in active)
        returning=[key for key in active if key in history]
        churn=sum(physical[key]!=history[key] for key in returning)
        history.update(physical)
        for key in active:
            cache.pop(key,None)
        departures=sorted(previous_active.difference(active))
        writes=0
        for key in departures:
            if do_reset:
                continue
            cache.pop(key,None)
            cache[key]=previous_assignment[key]
            writes+=1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        previous_active=set(active)
        previous_assignment=dict(assigned)
        rows.append({"episode":episode,
                     "physical_assignment":{str(k):physical[k] for k in sorted(active)},
                     "physical_churn":churn,"cache_writes":writes,
                     "cache_occupancy":len(cache),
                     "skipped_departures":len(departures) if do_reset else 0,
                     "flush":do_reset,"residual":residual,
                     "landmark_reads":reads,"search_calls":calls,"matched":len(assigned)})
    assert sum(row["landmark_reads"] for row in rows)==10
    return {"seed":seed,"mode":mode,"policy":policy,"intervention":intervention,
            "rows":rows}


def run():
    summaries={name:{action:{"pre5":0,"post5":0,"at7":0,"triggers":0}
                     for action in INTERVENTIONS} for name,_ in REGIMES}
    records=[]
    try:
        for regime,onset in REGIMES:
            y49.install_environment(onset)
            for family in FAMILIES:
                for seed in DEV+HELDOUT:
                    for policy in POLICIES:
                        pairs={}
                        for action in INTERVENTIONS:
                            ref=evaluate(seed,policy,"canonical",action,family)
                            candidate=evaluate(seed,policy,"periodic",action,family)
                            before=after=at7=triggered=0
                            for a,b in zip(ref["rows"],candidate["rows"]):
                                assert a["episode"]==b["episode"]
                                assert a["cache_writes"]==b["cache_writes"]
                                assert a["cache_occupancy"]==b["cache_occupancy"]
                                assert a["skipped_departures"]==b["skipped_departures"]
                                assert a["flush"]==b["flush"]
                                assert a["residual"]==b["residual"]
                                assert a["landmark_reads"]==b["landmark_reads"]
                                assert a["matched"]==b["matched"]==7
                                if seed in HELDOUT:
                                    triggered+=int(a["flush"])
                                    if a["physical_assignment"]!=b["physical_assignment"]:
                                        if a["episode"]<5:before+=1
                                        else:after+=1
                                        if a["episode"]==7:at7+=1
                            if seed in HELDOUT:
                                sums=summaries[regime][action]
                                sums["pre5"]+=before
                                sums["post5"]+=after
                                sums["at7"]+=at7
                                sums["triggers"]+=triggered
                            pairs[action]={"mismatches_pre5":before,
                                           "mismatches_post5":after,
                                           "mismatches_episode7":at7,
                                           "calibration_resets":triggered,
                                           "physical_churn_reference":sum(x["physical_churn"] for x in ref["rows"]),
                                           "physical_churn_candidate":sum(x["physical_churn"] for x in candidate["rows"]),
                                           "writes":sum(x["cache_writes"] for x in ref["rows"])}
                        records.append({"regime":regime,"family":family,"seed":seed,
                                        "cohort":"heldout" if seed in HELDOUT else "development",
                                        "policy":policy,"paired_results":pairs})
    finally:
        y49.restore_environment()
    on4=summaries["onset4"]
    on6=summaries["onset6"]
    steady=summaries["steady"]
    gain4=on4["continue"]["post5"]-on4["trigger"]["post5"]
    gain6=on6["continue"]["at7"]-on6["trigger"]["at7"]
    if gain4>0 and gain6>0 and steady["trigger"]["triggers"]==0 and steady["trigger"]["post5"]==0:
        label="RESIDUAL_TRIGGERED_GAIN"
    elif gain4>0 or gain6>0:
        label="PARTIAL_GAIN"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y050-public-residual-quarantine.v1",
            "parent_head":"a148fb90b4527ac5b0d60dd6e9aca4f32adf8833",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "observation_episodes":PROBES,"intervention_episodes":RESET_EPISODES,
            "resource_landmark_readings_per_8_episodes":10,
            "paired_mismatch_summary":summaries,"by_family_seed_policy":records,
            "model_calls":0,
            "claim_limit":"Synthetic public-anchor residual-driven bounded cache quarantine; not future event awareness or general autonomous regeneration."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
