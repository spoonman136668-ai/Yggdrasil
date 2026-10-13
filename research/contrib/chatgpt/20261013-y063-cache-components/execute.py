"""Y063: factorial cache-clear, departure-quarantine and selective relabel controls."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y062-cache-flush"/"execute.py"
spec=importlib.util.spec_from_file_location("y62_pinned",SOURCE)
assert spec and spec.loader
y62=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y62)

y60=y62.y60
y59=y62.y59
y58=y62.y58
y49=y62.y49
y46=y62.y46
y50=y62.y50
y25=y62.y25
y36=y62.y36

DEV=tuple(range(3940,3948))
HELDOUT=tuple(range(3960,3976))
FAMILIES=((3,9,15),(5,3,7),(7,15,1),(11,13,9))
SWAPS=((2,3),(4,5))
REGIMES=(("steady",None),("onset4",4),("onset6",6))
POLICIES=("matched_sham","full","quorum2")
ARMS=("corrected_keep","corrected_clear_only","corrected_skip_only",
      "corrected_clear_skip","corrected_relabel")

def candidate(seed,family,policy,arm,canonical):
    readings=y59.sample(seed,family,"fixed_rotating_sentinels")
    assert sum(len(v) for v in readings.values())==10
    cached=OrderedDict()
    previous_active=set()
    previous_assignments={}
    history=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        original_neighborhoods=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert len(active)==7 and y25.hall_cardinality(active,original_neighborhoods)==7
        encoded={key:tuple(sorted({y46.coordinate(
            x,seed,episode,family,"late_shock") for x in original_neighborhoods[key]}))
                 for key in active}
        if episode==0:
            phase=readings[0]["0"]
            a=(readings[0]["1"]-phase)%16
            assert a%2==1
            inv=pow(a,-1,16)
            model=None
            first=None
            def decode(v,phase=phase,inv=inv):
                return (inv*(v-phase))%16
        else:
            model=y60.public_decoder(readings,episode)
            first=model["first_detection_episode"]
            def decode(v,model=model,episode=episode):
                return y60.decode_label(v,model,episode,True)
        event=first==episode
        clear=bool(event and arm in ("corrected_clear_only","corrected_clear_skip"))
        quarantine=bool(event and arm in ("corrected_skip_only","corrected_clear_skip"))
        relabel=bool(event and arm=="corrected_relabel")
        if clear:
            cached.clear()
        if relabel:
            assert model and len(model["detected_pair"])==2
            cached=OrderedDict((key,model["detected_pair"].get(value,value))
                               for key,value in cached.items())
        lookup={}
        allowed={}
        for key,choices in encoded.items():
            local={}
            for encoded_cell in choices:
                predicted=decode(encoded_cell)
                assert predicted not in local,"DUPLICATE_PREDICTED_SOURCE_OPTION"
                local[predicted]=encoded_cell
            lookup[key]=local
            allowed[key]=set(local)
        assert y25.hall_cardinality(active,allowed)==7
        preferences={key:cached[key] for key in active
                     if key in cached and cached[key] in allowed[key]}
        minimum={"matched_sham":999,"full":1,"quorum2":2}[policy]
        assignments,calls=y25.match(
            active,allowed,preferences if len(preferences)>=minimum else {})
        assert len(assignments)==7 and len(set(assignments.values()))==7
        true_physical={}
        illegal=0
        for key in active:
            value=lookup[key][assignments[key]]
            physical=y46.physical_coordinate(value,seed,episode,family,"late_shock")
            true_physical[key]=physical
            illegal+=int(physical not in original_neighborhoods[key])
        assert illegal==0 and len(set(true_physical.values()))==7
        reference=canonical["rows"][episode]["physical_assignment"]
        assert set(reference)=={str(k) for k in active}
        wrong=sum(reference[str(key)]!=true_physical[key] for key in active)
        for key in active:
            cached.pop(key,None)
        departures=sorted(previous_active.difference(active))
        writes=skips=0
        for key in departures:
            if quarantine:
                skips+=1
                continue
            cached.pop(key,None)
            cached[key]=previous_assignments[key]
            writes+=1
            while len(cached)>9:
                cached.popitem(last=False)
        assert len(cached)<=9 and len(cached)+7<=16
        assert not set(cached).intersection(active)
        previous_active=set(active)
        previous_assignments=dict(assignments)
        history.append({"episode":episode,"mismatch":int(wrong>0),
                        "wrong_assignments":wrong,"first_detection":first,
                        "public_event_clear":int(clear),"public_event_quarantine":int(quarantine),
                        "public_event_relabel":int(relabel),
                        "retained_occupancy":len(cached),
                        "retained_writes":writes,"quarantined_departures":skips,
                        "match_search_calls":calls,"physically_illegal":illegal})
    first=y60.public_decoder(readings,7)["first_detection_episode"]
    assert first in (None,5,7)
    return {"first_public_detection":first,
            "total_mismatch_episodes":sum(x["mismatch"] for x in history),
            "post_detection_mismatch_episodes":sum(
                x["mismatch"] for x in history if first is not None and x["episode"]>=first),
            "wrong_assignments":sum(x["wrong_assignments"] for x in history),
            "cache_clear_actions":sum(x["public_event_clear"] for x in history),
            "quarantine_actions":sum(x["public_event_quarantine"] for x in history),
            "relabel_actions":sum(x["public_event_relabel"] for x in history),
            "retained_writes":sum(x["retained_writes"] for x in history),
            "matching_calls":sum(x["match_search_calls"] for x in history),
            "public_scalar_reads":10,
            "illegal_physical":sum(x["physically_illegal"] for x in history),
            "by_episode":history}

def run():
    groups={}
    records=[]
    dev_checks=0
    try:
        for pair in SWAPS:
            for regime,onset in REGIMES:
                key=f"{pair[0]}_{pair[1]}:{regime}"
                source={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,source)
                accum={arm:{field:0 for field in (
                    "total_mismatch_episodes","post_detection_mismatch_episodes",
                    "wrong_assignments","cache_clear_actions","quarantine_actions",
                    "relabel_actions","retained_writes","matching_calls",
                    "public_scalar_reads","illegal_physical")}
                    for arm in ARMS}
                detections=0
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            canonical=y50.evaluate(seed,policy,"canonical","continue",family)
                            tested={arm:candidate(seed,family,policy,arm,canonical)
                                    for arm in ARMS}
                            first=tested["corrected_keep"]["first_public_detection"]
                            assert all(row["first_public_detection"]==first for row in tested.values())
                            if seed in DEV:
                                dev_checks+=1
                            else:
                                detections+=int(first is not None)
                                for arm,row in tested.items():
                                    for field in accum[arm]:
                                        accum[arm][field]+=row[field]
                                records.append({"case":key,"family":family,"seed":seed,
                                                "policy":policy,"first_public_detection":first,
                                                "arms":{arm:{k:v for k,v in row.items() if k!="by_episode"}
                                                        for arm,row in tested.items()}})
                assert source["anchor_pair_checks"]>0
                for arm in ARMS:
                    assert accum[arm]["public_scalar_reads"]==4*16*3*10
                    assert accum[arm]["illegal_physical"]==0
                groups[key]={"arms":accum,"detected_trials":detections,
                             "source_anchor_check_count":source["anchor_pair_checks"]}
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert len(records)==2*3*4*16*3
    assert dev_checks==2*3*4*8*3
    steady=all(groups[f"{p[0]}_{p[1]}:steady"]["arms"][a]["total_mismatch_episodes"]==0
               for p in SWAPS for a in ARMS)
    blind=groups["2_3:onset6"]
    no_oracle=(blind["detected_trials"]==0 and
               all(blind["arms"][a][action]==0 for a in ARMS
                   for action in ("cache_clear_actions","quarantine_actions","relabel_actions")) and
               all(blind["arms"][a]["total_mismatch_episodes"]==
                   blind["arms"]["corrected_keep"]["total_mismatch_episodes"] for a in ARMS))
    observed_cases=("2_3:onset4","4_5:onset4","4_5:onset6")
    comparisons=[]
    for key in observed_cases:
        cells=groups[key]["arms"]
        baseline=cells["corrected_keep"]["post_detection_mismatch_episodes"]
        treatments={arm:cells[arm]["post_detection_mismatch_episodes"] for arm in ARMS}
        comparisons.append({"case":key,"baseline_post":baseline,
                            "post_by_treatment":treatments,
                            "clear_only_vs_clear_skip":treatments["corrected_clear_only"]-
                                                       treatments["corrected_clear_skip"],
                            "skip_only_vs_clear_skip":treatments["corrected_skip_only"]-
                                                      treatments["corrected_clear_skip"]})
    primary=next(c for c in comparisons if c["case"]=="4_5:onset4")
    best=any(primary["baseline_post"]>0 and
             primary["post_by_treatment"][arm]<=.8*primary["baseline_post"] and
             all(c["post_by_treatment"][arm]<=c["baseline_post"] for c in comparisons)
             for arm in ("corrected_skip_only","corrected_relabel"))
    distinct=(primary["post_by_treatment"]["corrected_clear_only"]!=
              primary["post_by_treatment"]["corrected_clear_skip"] or
              primary["post_by_treatment"]["corrected_skip_only"]!=
              primary["post_by_treatment"]["corrected_clear_skip"])
    label=("SELECTIVE_CACHE_GAIN" if steady and no_oracle and best else
           "PARTIAL_COMPONENT_ATTRIBUTION" if steady and no_oracle and distinct else
           "NO_GAIN")
    return {"schema":"yggdrasil.y063-factorial-cache-action.v1",
            "parent_head":"53693c35db7253916082e6574218fc6e1b50ca41",
            "classification":label,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "source_families":FAMILIES,"matching_policies":POLICIES,
            "public_scalar_reads_per_trial":10,"active":7,"cache_limit":9,
            "steady_zero_mismatches":steady,"source_invisible_no_oracle_action":no_oracle,
            "factorial_comparisons":comparisons,"development_checks":dev_checks,
            "source_groups":groups,"heldout_records":records,"model_calls":0,
            "claim_limit":"Synthetic publicly detected cache-action component ablation; source physical truth evaluator-only, actual live cache recovery not authorized."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
