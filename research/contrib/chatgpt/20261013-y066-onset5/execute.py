"""Y066 prospective new-onset perturbation of Y065 fixed dual-sentinel matching."""
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261013-y065-dual-matching"/"execute.py"
spec=importlib.util.spec_from_file_location("y65_pinned",p)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DEV=tuple(range(5896,5904))
HELDOUT=tuple(range(5920,5936))
FAMILIES=((3,7,5),(5,15,9),(7,1,13),(11,5,3))
REGIMES=(("steady",None),("onset4",4),("onset5",5),("onset6",6),("onset7",7))
def run():
    old=(m.DEV,m.HELDOUT,m.FAMILIES,m.REGIMES)
    try:
        m.DEV=DEV;m.HELDOUT=HELDOUT;m.FAMILIES=FAMILIES
        # Run the unchanged Y065 original four-case study on this NEW
        # cohort, then the prospectively frozen fifth onset-5 case below.
        m.REGIMES=(("steady",None),("onset4",4),("onset6",6),("onset7",7))
        result=m.run()
        extra={}
        extra_records=[]
        for pair in m.PAIRS:
            integrity={"anchor_pair_checks":0}
            m.y58.install_transposition(5,pair,integrity)
            key=f"{pair[0]}_{pair[1]}:onset5"
            totals={arm:{"mismatch_episodes":0,"post_detection_mismatch_episodes":0,
                         "illegal_physical_assignments":0,"public_reads":0} for arm in m.ARMS}
            detections={arm:0 for arm in m.ARMS}
            for family in FAMILIES:
                for seed in DEV+HELDOUT:
                    for policy in m.POLICIES:
                        canonical=m.y50.evaluate(seed,policy,"canonical","continue",family)
                        candidate={arm:m.candidate(seed,family,policy,arm) for arm in m.ARMS}
                        if seed in DEV: continue
                        row={"case":key,"seed":seed,"family":family,"policy":policy,"arms":{}}
                        for arm,trial in candidate.items():
                            first=next((r["public_detected_swap_first_episode"] for r in reversed(
                                trial["rows"]) if r["public_detected_swap_first_episode"] is not None),None)
                            detections[arm]+=int(first is not None)
                            wrong=post=illegal=0
                            for truth,guess in zip(canonical["rows"],trial["rows"]):
                                error=sum(truth["physical_assignment"][k]!=
                                          guess["physical_assignment_evaluator_only"][k]
                                          for k in truth["physical_assignment"])
                                wrong+=int(error>0)
                                if first is not None and truth["episode"]>=first:
                                    post+=int(error>0)
                                illegal+=guess["illegal_physical_assignments"]
                                assert guess["candidate_retained_cache_occupancy"]<=9
                            assert illegal==0
                            vals=totals[arm]
                            vals["mismatch_episodes"]+=wrong
                            vals["post_detection_mismatch_episodes"]+=post
                            vals["public_reads"]+=10
                            row["arms"][arm]={"mismatch_episodes":wrong,
                                               "post_detection_mismatch_episodes":post,
                                               "first_public_detection":first}
                        extra_records.append(row)
            assert len(extra_records)==(1 if pair==m.PAIRS[0] else 2)*4*16*3
            assert all(v["public_reads"]==4*16*3*10 for v in totals.values())
            extra[key]={"arms":totals,"detections":detections,
                        "source_anchor_checks":integrity["anchor_pair_checks"]}
            m.y49.restore_environment()
    finally:
        m.DEV,m.HELDOUT,m.FAMILIES,m.REGIMES=old
        m.y49.restore_environment()
    assert result["development_seeds"]==DEV
    assert result["sealed_heldout_seeds"]==HELDOUT
    assert len(result["heldout_records"])==2*4*4*16*3
    comparisons=[]
    for source in ("2_3:onset5","4_5:onset5"):
        a=extra[source]
        ref=a["arms"]["dual_sentinel_detect_only"]["post_detection_mismatch_episodes"]
        corrected=a["arms"]["dual_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
        first=a["arms"]["original_rotating_detect_only"]["mismatch_episodes"]
        second=a["arms"]["dual_sentinel_decoder_corrected"]["mismatch_episodes"]
        comparisons.append({"case":source,"uncorrected_post":ref,"corrected_post":corrected,
                            "original_total":first,"corrected_total":second,
                            "gain":1-corrected/ref if ref else None,
                            "strict":ref>0 and corrected<=ref*.5 and second<first,
                            "partial":ref>0 and corrected<=ref*.8})
    safe=result["steady_zero_mismatches"] and all(
        v["arms"][arm]["illegal_physical_assignments"]==0 and
        v["arms"][arm]["public_reads"]==4*16*3*10
        for v in extra.values() for arm in m.ARMS)
    if safe and all(x["strict"] for x in comparisons):label="TIMING_ROBUST_RECOVERY"
    elif safe and any(x["partial"] for x in comparisons):label="PARTIAL_TIMING_GAIN"
    else:label="NO_GAIN"
    return {"schema":"yggdrasil.y066-dual-new-onset5-matching.v1",
            "parent_head":"343621953c382f450e5603abaac7bf51b92ae09e",
            "classification":label,"development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"new_onset5_comparisons":comparisons,
            "matching_and_sensing_safe":safe,"new_onset5_groups":extra,
            "new_onset5_records":extra_records,
            "original_complete_data":result,
            "model_calls":0,"claim_limit":"Synthetic bounded matching source onset shift; not independently admitted FSA recovery."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
