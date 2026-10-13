"""Y062: public-sentinel event-conditioned retention reset in real 7/9 matching."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y061-matching-cache"/"execute.py"
spec=importlib.util.spec_from_file_location("y61_pinned",SOURCE)
assert spec and spec.loader
y61=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y61)

y60=y61.y60
y59=y61.y59
y58=y61.y58
y49=y61.y49
y46=y61.y46
y50=y61.y50
y25=y61.y25
y36=y61.y36

DEV=tuple(range(3632,3640))
HELDOUT=tuple(range(3648,3664))
FAMILIES=((3,11,1),(5,5,15),(7,9,11),(11,3,7))
SWAPS=((2,3),(4,5))
REGIMES=(("steady",None),("onset4",4),("onset6",6))
POLICIES=("matched_sham","full","quorum2")
ARMS=("sentinel_no_correction_keep","sentinel_corrected_keep",
      "sentinel_corrected_event_flush","sentinel_no_correction_event_flush")

def candidate_match(seed,family,policy,arm,canonical):
    """Candidate does not ingest the simulator's true physical assignments."""
    do_correct=arm.startswith("sentinel_corrected")
    flush_on_detection=arm.endswith("event_flush")
    public=y59.sample(seed,family,"fixed_rotating_sentinels")
    assert sum(len(v) for v in public.values())==10
    cached=OrderedDict()
    previous_active=set()
    previous_decoded_assignments={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        physical_source_neighborhoods=y36.neighborhoods(
            seed,episode,active,"ring_reference")
        assert len(active)==7 and y25.hall_cardinality(active,physical_source_neighborhoods)==7
        encoded_task_options={key:tuple(sorted({
            y46.coordinate(cell,seed,episode,family,"late_shock")
            for cell in physical_source_neighborhoods[key]})) for key in active}
        if episode==0:
            b0=public[0]["0"]
            a=(public[0]["1"]-b0)%16
            assert a%2==1
            inverse=pow(a,-1,16)
            first_detection=None
            def decode(observed,b0=b0,inverse=inverse):
                return (inverse*(observed-b0))%16
        else:
            model=y60.public_decoder(public,episode)
            first_detection=model["first_detection_episode"]
            def decode(observed,model=model,episode=episode,corrected=do_correct):
                return y60.decode_label(observed,model,episode,corrected)

        # Actual public correction was observed in THIS episode, not a
        # future timestamp or evaluator-known source-onset signal.
        flush=(flush_on_detection and first_detection==episode)
        if flush: cached.clear()
        lookup={}
        allowed={}
        for key,opts in encoded_task_options.items():
            mapped={}
            for encoded in opts:
                estimated=decode(encoded)
                assert estimated not in mapped,"DECODED_BIJECTION_FAILED"
                mapped[estimated]=encoded
            lookup[key]=mapped
            allowed[key]=set(mapped)
        assert y25.hall_cardinality(active,allowed)==7
        valid_preferences={key:cached[key] for key in active
                           if key in cached and cached[key] in allowed[key]}
        quorum={"matched_sham":999,"full":1,"quorum2":2}[policy]
        assigned,search_calls=y25.match(
            active,allowed,valid_preferences if len(valid_preferences)>=quorum else {})
        assert len(assigned)==7 and len(set(assigned.values()))==7

        # EVALUATOR-ONLY physical grounding occurs AFTER chosen decoded
        # options have been matched; never fed to candidate cache or matcher.
        actual={}
        illegal=0
        for key in active:
            chosen_encoded=lookup[key][assigned[key]]
            real=y46.physical_coordinate(chosen_encoded,seed,episode,family,"late_shock")
            actual[key]=real
            illegal+=int(real not in physical_source_neighborhoods[key])
        assert len(set(actual.values()))==7 and illegal==0
        ref=canonical["rows"][episode]["physical_assignment"]
        assert set(ref)=={str(k) for k in active}
        disagreement=sum(ref[str(k)]!=actual[k] for k in active)
        for key in active:cached.pop(key,None)
        departures=sorted(previous_active.difference(active))
        writes=skipped=0
        for key in departures:
            if flush:
                skipped+=1
                continue
            cached.pop(key,None)
            cached[key]=previous_decoded_assignments[key]
            writes+=1
            while len(cached)>9:cached.popitem(last=False)
        assert len(cached)<=9 and len(cached)+7<=16
        assert not set(cached).intersection(active)
        previous_active=set(active)
        previous_decoded_assignments=dict(assigned)
        rows.append({
            "episode":episode,
            "mismatch":int(disagreement>0),
            "wrong_assignments":disagreement,
            "first_detected_public_episode":first_detection,
            "cache_flush":bool(flush),
            "skipped_departure_writes":skipped,
            "retained_writes":writes,
            "cache_occupancy":len(cached),
            "search_calls":search_calls,
            "physical_illegal":illegal})
    first=y60.public_decoder(public,7)["first_detection_episode"]
    assert first in (None,5,7)
    return {"arm":arm,"first_public_detection":first,
            "scalar_reads":10,"rows":rows,
            "total_mismatches":sum(r["mismatch"] for r in rows),
            "post_detection_mismatches":sum(
                r["mismatch"] for r in rows if first is not None and r["episode"]>=first),
            "wrong_assignments":sum(r["wrong_assignments"] for r in rows),
            "cache_flushes":sum(r["cache_flush"] for r in rows),
            "retained_writes":sum(r["retained_writes"] for r in rows),
            "skipped_departures":sum(r["skipped_departure_writes"] for r in rows),
            "search_calls":sum(r["search_calls"] for r in rows),
            "physical_illegal":sum(r["physical_illegal"] for r in rows)}

def run():
    groups={}
    records=[]
    development_checks=0
    try:
        for pair in SWAPS:
            for regime,onset in REGIMES:
                case=f"{pair[0]}_{pair[1]}:{regime}"
                checks={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,checks)
                totals={arm:{"mismatch_episodes":0,"post_detection_mismatch_episodes":0,
                             "wrong_individual_assignments":0,
                             "cache_flushes":0,"skipped_departures":0,
                             "retained_writes":0,"search_calls":0,
                             "public_reads":0,"physical_illegal":0}
                        for arm in ARMS}
                detections=0
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            reference=y50.evaluate(seed,policy,"canonical","continue",family)
                            arms={arm:candidate_match(seed,family,policy,arm,reference) for arm in ARMS}
                            first=arms[ARMS[0]]["first_public_detection"]
                            assert all(a["first_public_detection"]==first for a in arms.values())
                            if seed in DEV:
                                development_checks+=1
                            else:
                                detections+=int(first is not None)
                                for arm,result in arms.items():
                                    agg=totals[arm]
                                    for key,new in (
                                        ("mismatch_episodes",result["total_mismatches"]),
                                        ("post_detection_mismatch_episodes",result["post_detection_mismatches"]),
                                        ("wrong_individual_assignments",result["wrong_assignments"]),
                                        ("cache_flushes",result["cache_flushes"]),
                                        ("skipped_departures",result["skipped_departures"]),
                                        ("retained_writes",result["retained_writes"]),
                                        ("search_calls",result["search_calls"]),
                                        ("public_reads",result["scalar_reads"]),
                                        ("physical_illegal",result["physical_illegal"])):
                                        agg[key]+=new
                                records.append({"case":case,"family":family,"seed":seed,
                                                "policy":policy,"public_detection":first,
                                                "candidate_results":{arm:{
                                                    k:v for k,v in result.items() if k!="rows"}
                                                    for arm,result in arms.items()}})
                assert checks["anchor_pair_checks"]>0
                assert all(v["public_reads"]==4*16*3*10 for v in totals.values())
                assert all(v["physical_illegal"]==0 for v in totals.values())
                groups[case]={"public_detection_trials":detections,
                              "source_anchor_checks":checks["anchor_pair_checks"],
                              "arms":totals}
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert development_checks==2*3*4*8*3
    assert len(records)==2*3*4*16*3
    steady=all(groups[f"{p[0]}_{p[1]}:steady"]["arms"][arm]["mismatch_episodes"]==0
               for p in SWAPS for arm in ARMS)
    blind=groups["2_3:onset6"]
    no_false_action=(blind["public_detection_trials"]==0 and
                     all(blind["arms"][arm]["cache_flushes"]==0 for arm in ARMS))
    keys=("2_3:onset4","4_5:onset4","4_5:onset6")
    comparisons=[]
    for key in keys:
        agg=groups[key]["arms"]
        old=agg["sentinel_corrected_keep"]["post_detection_mismatch_episodes"]
        flush=agg["sentinel_corrected_event_flush"]["post_detection_mismatch_episodes"]
        sham=agg["sentinel_no_correction_event_flush"]["post_detection_mismatch_episodes"]
        comparisons.append({"case":key,"corrected_keep_post":old,
                            "corrected_flush_post":flush,"sham_flush_post":sham,
                            "absolute_reduction":old-flush,
                            "ratio":(1-flush/old) if old else None})
    primary=next(r for r in comparisons if r["case"]=="4_5:onset4")
    no_harm=all(r["corrected_flush_post"]<=r["corrected_keep_post"] for r in comparisons)
    strict=(steady and no_false_action and no_harm and
            primary["corrected_keep_post"]>0 and
            primary["corrected_flush_post"]<=.5*primary["corrected_keep_post"] and
            primary["sham_flush_post"]>0 and
            primary["corrected_flush_post"]<=.5*primary["sham_flush_post"])
    partial=(steady and no_false_action and
             primary["corrected_flush_post"]<primary["corrected_keep_post"])
    label="CACHE_INVALIDATION_GAIN" if strict else (
        "PARTIAL_FLUSH_GAIN" if partial else "NO_GAIN")
    return {"schema":"yggdrasil.y062-public-cache-flush.v1",
            "parent_head":"f9559aeef0cb9daa33cae31bc620af2c796dac4c",
            "classification":label,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"policies":POLICIES,
            "per_trial_public_scalar_reads":10,"active":7,"retained_limit":9,
            "steady_no_mismatches":steady,
            "blind_no_oracle_flush":no_false_action,
            "precommitted_cache_intervention_comparisons":comparisons,
            "development_structural_checks":development_checks,
            "source_groups":groups,"heldout_records":records,
            "model_calls":0,
            "claim_limit":"Synthetic source-anchored candidate cache flush comparison; pure cache effect not identified beyond included sham, no physical-world or production controller repair."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
