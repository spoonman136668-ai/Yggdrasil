"""Y065: new-source dual-sentinel matching-cache recovery versus original sensing."""
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261013-y064-dual-sentinel"/"execute.py"
spec=importlib.util.spec_from_file_location("y64_custody",p)
assert spec and spec.loader
y64=importlib.util.module_from_spec(spec);spec.loader.exec_module(y64)
y61=y64.y63.y62.y61
y58=y64.y58
y49=y64.y49
y59=y64.y59
y50=y61.y50

DEV=tuple(range(5600,5608))
HELDOUT=tuple(range(5632,5648))
FAMILIES=((3,15,5),(5,1,11),(7,5,7),(11,11,3))
PAIRS=((2,3),(4,5))
REGIMES=(("steady",None),("onset4",4),("onset6",6),("onset7",7))
POLICIES=("matched_sham","full","quorum2")
ARMS=("original_rotating_detect_only","dual_sentinel_detect_only","dual_sentinel_decoder_corrected")

def candidate(seed,family,policy,arm):
    original_sample=y59.sample
    if arm.startswith("dual_"):
        def sample(seed_,family_,instrument):
            if instrument=="fixed_rotating_sentinels":
                return y64.dual_public_samples(seed_,family_)
            return original_sample(seed_,family_,instrument)
        y59.sample=sample
    try:
        y61.y59.sample=y59.sample
        base_arm="sentinel_corrected" if arm.endswith("decoder_corrected") else "sentinel_no_correction"
        result=y61.candidate_match(seed,family,policy,base_arm)
    finally:
        y59.sample=original_sample
        y61.y59.sample=original_sample
    assert result["public_scalar_reads"]==10
    return result

def run():
    groups={}
    records=[]
    development_checks=0
    try:
        for pair in PAIRS:
            for regime,onset in REGIMES:
                key=f"{pair[0]}_{pair[1]}:{regime}"
                integrity={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,integrity)
                totals={arm:{"mismatch_episodes":0,"post_detection_mismatch_episodes":0,
                             "pre_detection_mismatch_episodes":0,
                             "illegal_physical_assignments":0,
                             "wrong_individual_assignments":0,
                             "matching_search_calls":0,
                             "candidate_retained_writes":0,
                             "public_reads":0} for arm in ARMS}
                detections={arm:0 for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            canonical=y50.evaluate(seed,policy,"canonical","continue",family)
                            experiments={arm:candidate(seed,family,policy,arm) for arm in ARMS}
                            firsts={arm:next(
                                (r["public_detected_swap_first_episode"] for r in reversed(
                                    trial["rows"]) if r["public_detected_swap_first_episode"] is not None),None)
                                for arm,trial in experiments.items()}
                            if seed in DEV:
                                development_checks+=1
                                continue
                            row={"case":key,"seed":seed,"family":family,"policy":policy,
                                 "first_public_detection":firsts,"arms":{}}
                            for arm,trial in experiments.items():
                                first=firsts[arm]
                                detections[arm]+=int(first is not None)
                                summary={"mismatch_episodes":0,"post_detection_mismatch_episodes":0,
                                         "pre_detection_mismatch_episodes":0,
                                         "illegal_physical_assignments":0,
                                         "wrong_individual_assignments":0,
                                         "matching_search_calls":0,"candidate_retained_writes":0}
                                for truth,observed in zip(canonical["rows"],trial["rows"]):
                                    assert truth["episode"]==observed["episode"]
                                    errors=sum(truth["physical_assignment"][k]!=
                                               observed["physical_assignment_evaluator_only"][k]
                                               for k in truth["physical_assignment"])
                                    changed=int(errors>0)
                                    summary["mismatch_episodes"]+=changed
                                    summary["wrong_individual_assignments"]+=errors
                                    summary["illegal_physical_assignments"]+=observed["illegal_physical_assignments"]
                                    summary["matching_search_calls"]+=observed["matching_search_calls"]
                                    summary["candidate_retained_writes"]+=observed["candidate_retained_writes"]
                                    assert observed["candidate_retained_cache_occupancy"]<=9
                                    if first is not None and observed["episode"]>=first:
                                        summary["post_detection_mismatch_episodes"]+=changed
                                    else:summary["pre_detection_mismatch_episodes"]+=changed
                                assert summary["illegal_physical_assignments"]==0
                                row["arms"][arm]=summary
                                for field,value in summary.items():totals[arm][field]+=value
                                totals[arm]["public_reads"]+=10
                            records.append(row)
                assert all(t["public_reads"]==4*16*3*10 and
                           t["illegal_physical_assignments"]==0 for t in totals.values())
                groups[key]={"arms":totals,"detections":detections,
                             "source_anchor_checks":integrity["anchor_pair_checks"]}
                y49.restore_environment()
    finally:y49.restore_environment()
    assert len(records)==2*4*4*16*3
    assert development_checks==2*4*4*8*3
    cases=[f"{a}_{b}:onset{x}" for a,b in PAIRS for x in (4,6,7)]
    comparisons=[]
    for key in cases:
        group=groups[key]
        baseline=group["arms"]["dual_sentinel_detect_only"]["post_detection_mismatch_episodes"]
        fixed=group["arms"]["dual_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
        comparisons.append({"case":key,"dual_detected":group["detections"]["dual_sentinel_decoder_corrected"]==192,
                            "no_correction_post":baseline,"corrected_post":fixed,
                            "reduction":1-fixed/baseline if baseline else None,
                            "strict":baseline>0 and fixed<=.5*baseline,
                            "partial":baseline>0 and fixed<=.8*baseline})
    steady=all(groups[f"{a}_{b}:steady"]["arms"][arm]["mismatch_episodes"]==0
               for a,b in PAIRS for arm in ARMS)
    blindbetter=all(
        groups[key]["arms"]["dual_sentinel_decoder_corrected"]["mismatch_episodes"]<
        groups[key]["arms"]["original_rotating_detect_only"]["mismatch_episodes"]
        for key in ("2_3:onset6","2_3:onset7"))
    if steady and blindbetter and all(x["strict"] and x["dual_detected"] for x in comparisons):
        label="DUAL_MATCHING_RECOVERY"
    elif steady and sum(x["partial"] and x["dual_detected"] for x in comparisons)>=4:
        label="PARTIAL_MATCHING_RECOVERY"
    else:label="NO_GAIN"
    return {"schema":"yggdrasil.y065-dual-sentinel-real-matching.v1",
            "parent_head":"d7584fc44e120d55e5dcbe147decc603c8bd8230",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "per_trial_public_scalar_reads":10,"active":7,"retained_limit":9,
            "steady_zero_mismatches":steady,"blind_case_improvement":blindbetter,
            "comparisons":comparisons,"groups":groups,
            "heldout_records":records,"model_calls":0,
            "claim_limit":"Synthetic causal physical-label matching, public dual-sentinel hardware assumption and candidate-owned cache; no production authority."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
