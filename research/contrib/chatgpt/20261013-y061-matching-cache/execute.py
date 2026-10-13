"""Y061: actual seven-active/nine-retained matching with causal public sentinel correction."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y060-decoder-recovery"/"execute.py"
spec=importlib.util.spec_from_file_location("y60_pinned",SOURCE)
assert spec and spec.loader
y60=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y60)

y59=y60.y59
y58=y60.y58
y49=y60.y49
y46=y60.y46
y50=y58.y57.y53.y52.y50
y25=y50.y25
y36=y50.y36

DEV=tuple(range(3360,3368))
HELDOUT=tuple(range(3376,3392))
FAMILIES=((3,1,11),(5,13,3),(7,3,9),(11,7,13))
SWAPS=((2,3),(4,5))
REGIMES=(("steady",None),("onset4",4),("onset6",6))
POLICIES=("matched_sham","full","quorum2")
ARMS=("anchor_only","sentinel_no_correction","sentinel_corrected")

def candidate_match(seed,family,policy,arm):
    """No actual/source truth enters the candidate matching or cache update."""
    instrument=("fixed_two_anchors" if arm=="anchor_only" else "fixed_rotating_sentinels")
    public=y59.sample(seed,family,instrument)
    assert sum(len(v) for v in public.values())==10
    retention=OrderedDict()
    previous_active=set()
    previous_encoded_assignment={}
    history_evaluator_only={}
    rows=[]
    for episode in range(8):
        active=y25.active_keys(seed,episode)
        assert len(active)==7
        source_neighborhoods=y36.neighborhoods(seed,episode,active,"ring_reference")
        assert y25.hall_cardinality(active,source_neighborhoods)==7
        # Source builds task inputs as encoded legal options; physical truth
        # is not forwarded to any candidate inference or cache operation.
        task_inputs={key:tuple(sorted({
                    y46.coordinate(cell,seed,episode,family,"late_shock")
                    for cell in source_neighborhoods[key]})) for key in active}
        assert y25.hall_cardinality(active,{key:set(v) for key,v in task_inputs.items()})==7
        if episode==0:
            b0=public[0]["0"]
            a=(public[0]["1"]-b0)%16
            assert a%2==1
            inv=pow(a,-1,16)
            def decode(observed,b0=b0,inv=inv):
                return (inv*(observed-b0))%16
            detected=None
        else:
            model=y60.public_decoder(public,episode)
            detected=model["first_detection_episode"]
            do_correct=arm=="sentinel_corrected"
            def decode(observed,model=model,episode=episode,do_correct=do_correct):
                return y60.decode_label(observed,model,episode,do_correct)
        # One-to-one public decoder maps each candidate's actually
        # presented encoded options to a coordinate chosen by matching.
        lookup={}
        decoded_neighborhoods={}
        for key,encoded_options in task_inputs.items():
            own={}
            for encoded in encoded_options:
                physical_estimate=decode(encoded)
                assert physical_estimate not in own,"NONBIJECTIVE_CANDIDATE_INPUT"
                own[physical_estimate]=encoded
            lookup[key]=own
            decoded_neighborhoods[key]=set(own)
        assert y25.hall_cardinality(active,decoded_neighborhoods)==7
        legal={key:retention[key] for key in active
               if key in retention and retention[key] in decoded_neighborhoods[key]}
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=threshold else {}
        chosen,calls=y25.match(active,decoded_neighborhoods,preferred)
        assert len(chosen)==7 and len(set(chosen.values()))==7
        # This is a separate EVALUATOR-ONLY physical-truth scoring step.
        # The following actual values are never used for retention/preference.
        actual={}
        physically_illegal=0
        for key in active:
            chosen_encoded=lookup[key][chosen[key]]
            physically_correct=y46.physical_coordinate(
                chosen_encoded,seed,episode,family,"late_shock")
            actual[key]=physically_correct
            physically_illegal+=int(physically_correct not in source_neighborhoods[key])
        assert physically_illegal==0,"ILLEGAL_PHYSICAL_MATCH"
        assert len(set(actual.values()))==7
        churn=sum(actual[key]!=history_evaluator_only[key]
                  for key in active if key in history_evaluator_only)
        history_evaluator_only.update(actual)
        for key in active:
            retention.pop(key,None)
        departures=sorted(previous_active.difference(active))
        writes=0
        for key in departures:
            retention.pop(key,None)
            retention[key]=previous_encoded_assignment[key]
            writes+=1
            while len(retention)>9:retention.popitem(last=False)
        assert len(retention)<=9 and len(retention)+7<=16
        assert not set(retention).intersection(active)
        previous_active=set(active)
        previous_encoded_assignment=dict(chosen)
        rows.append({
            "episode":episode,
            "physical_assignment_evaluator_only":{str(k):actual[k] for k in sorted(active)},
            "candidate_retained_cache_occupancy":len(retention),
            "candidate_retained_writes":writes,
            "matching_search_calls":calls,
            "physical_churn_evaluator_only":churn,
            "illegal_physical_assignments":physically_illegal,
            "public_detected_swap_first_episode":detected,
            "matched":7})
    return {"arm":arm,"policy":policy,"public_scalar_reads":10,"rows":rows}

def run():
    aggregate={}
    records=[]
    dev_checks=0
    try:
        for pair in SWAPS:
            for name,onset in REGIMES:
                key=f"{pair[0]}_{pair[1]}:{name}"
                checks={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,checks)
                totals={arm:{"mismatch_episodes":0,"post_detection_mismatch_episodes":0,
                             "pre_detection_mismatch_episodes":0,
                             "wrong_individual_assignments":0,"illegal_physical_assignments":0,
                             "candidate_retained_writes":0,"candidate_cache_occupancy_total":0,
                             "matching_search_calls":0,"physical_churn":0,
                             "public_scalar_reads":0}
                        for arm in ARMS}
                detections=0
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            reference=y50.evaluate(seed,policy,"canonical","continue",family)
                            assert len(reference["rows"])==8
                            candidates={arm:candidate_match(seed,family,policy,arm)
                                        for arm in ARMS}
                            first=candidates["sentinel_corrected"]["rows"][-1][
                                "public_detected_swap_first_episode"]
                            assert first in (None,5,7)
                            if seed in HELDOUT:
                                detections+=int(first is not None)
                            row={}
                            for arm in ARMS:
                                trial=candidates[arm]
                                assert trial["public_scalar_reads"]==10
                                mismatches=0
                                after=before=wrong=illegal=writes=occupancy=calls=churn=0
                                for a,b in zip(reference["rows"],trial["rows"]):
                                    assert a["episode"]==b["episode"]
                                    assert b["matched"]==7
                                    assert b["candidate_retained_cache_occupancy"]<=9
                                    expected=a["physical_assignment"]
                                    actual=b["physical_assignment_evaluator_only"]
                                    errors=sum(expected[k]!=actual[k] for k in expected)
                                    changed=int(bool(errors))
                                    mismatches+=changed
                                    wrong+=errors
                                    illegal+=b["illegal_physical_assignments"]
                                    writes+=b["candidate_retained_writes"]
                                    occupancy+=b["candidate_retained_cache_occupancy"]
                                    calls+=b["matching_search_calls"]
                                    churn+=b["physical_churn_evaluator_only"]
                                    if first is not None and a["episode"]>=first:after+=changed
                                    else:before+=changed
                                if seed in HELDOUT:
                                    total=totals[arm]
                                    for name2,value in (
                                        ("mismatch_episodes",mismatches),
                                        ("post_detection_mismatch_episodes",after),
                                        ("pre_detection_mismatch_episodes",before),
                                        ("wrong_individual_assignments",wrong),
                                        ("illegal_physical_assignments",illegal),
                                        ("candidate_retained_writes",writes),
                                        ("candidate_cache_occupancy_total",occupancy),
                                        ("matching_search_calls",calls),
                                        ("physical_churn",churn),
                                        ("public_scalar_reads",10)):
                                        total[name2]+=value
                                row[arm]={"mismatch_episodes":mismatches,
                                          "post_detection_mismatches":after,
                                          "pre_detection_mismatches":before,
                                          "wrong_individual_assignments":wrong,
                                          "candidate_retained_writes":writes,
                                          "candidate_cache_occupancy_total":occupancy,
                                          "physical_churn":churn,
                                          "matching_search_calls":calls}
                            if seed in HELDOUT:
                                records.append({"source_case":key,"family":family,
                                                "seed":seed,"policy":policy,
                                                "first_public_detection":first,
                                                "paired_controller_results":row})
                            else:
                                dev_checks+=1
                assert checks["anchor_pair_checks"]>0
                assert all(t["public_scalar_reads"]==4*16*3*10 for t in totals.values())
                assert all(t["illegal_physical_assignments"]==0 for t in totals.values())
                aggregate[key]={"total":totals,"detected_controller_trials":detections,
                                "anchor_witness_checks":checks["anchor_pair_checks"]}
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert dev_checks==2*3*4*8*3
    assert len(records)==2*3*4*16*3
    detectable=("2_3:onset4","4_5:onset4","4_5:onset6")
    successes=[]
    for key in detectable:
        trial=aggregate[key]
        control=trial["total"]["sentinel_no_correction"]["post_detection_mismatch_episodes"]
        treated=trial["total"]["sentinel_corrected"]["post_detection_mismatch_episodes"]
        successes.append({"case":key,"detectable":trial["detected_controller_trials"]==4*16*3,
                          "control_post":control,"corrected_post":treated,
                          "reduction":(1-treated/control if control else None),
                          "strict":trial["detected_controller_trials"]==4*16*3 and control>0
                                   and treated<=0.5*control,
                          "partial":trial["detected_controller_trials"]==4*16*3 and control>0
                                   and treated<=0.8*control})
    steady=all(aggregate[f"{p[0]}_{p[1]}:steady"]["total"][arm]["mismatch_episodes"]==0
               for p in SWAPS for arm in ARMS)
    blind=aggregate["2_3:onset6"]
    no_speculative=(blind["detected_controller_trials"]==0 and
                    blind["total"]["sentinel_no_correction"]["mismatch_episodes"]==
                    blind["total"]["sentinel_corrected"]["mismatch_episodes"])
    if steady and no_speculative and all(s["strict"] for s in successes):
        label="MATCHING_RECOVERY"
    elif steady and no_speculative and any(s["partial"] for s in successes):
        label="PARTIAL_MATCHING_GAIN"
    else: label="NO_GAIN"
    return {"schema":"yggdrasil.y061-public-sentinel-matching-cache.v1",
            "parent_head":"5aee4b1e1461679baf1e297a0c5cc23514ac6aa7",
            "classification":label,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"matching_policies":POLICIES,
            "per_trial_public_scalar_reads":10,"active":7,"cache_limit":9,
            "steady_zero_mismatches":steady,"undetected_case_no_correction":no_speculative,
            "precommitted_detectable_case_gates":successes,
            "development_checks":dev_checks,
            "aggregate_by_case":aggregate,"heldout_records":records,
            "candidate_uses_source_truth_to_match":False,
            "new_production_runtime_authority":False,"model_calls":0,
            "claim_limit":"Synthetic source-labeled matching-cache integration and evaluator-only physical scoring, not production controller repair or external-world independent qualification."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
