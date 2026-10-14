"""Y070: preregistered earliest onset 1 detection latency and causal correction."""
import importlib.util
import json
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y069-onset2"/"execute.py"
spec=importlib.util.spec_from_file_location("y069_pinned",PARENT)
assert spec and spec.loader
m69=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m69)
m=m69.m

DEV=tuple(range(8224,8232))
HELDOUT=tuple(range(8256,8272))
FAMILIES=((3,1,9),(5,13,7),(7,11,5),(11,3,15))
REGIMES=(("steady",None),("onset1",1))
PAIRS=((2,3),(4,5))
POLICIES=("matched_sham","full","quorum2")
ARMS=m.ARMS

def run():
    groups={}
    records=[]
    development_checks=0
    try:
        for pair in PAIRS:
            for label,onset in REGIMES:
                key=f"{pair[0]}_{pair[1]}:{label}"
                integrity={"anchor_pair_checks":0}
                m.y58.install_transposition(onset,pair,integrity)
                totals={arm:{"mismatch_episodes":0,"pre_detection_mismatch_episodes":0,
                             "post_detection_mismatch_episodes":0,"wrong_assignments":0,
                             "matching_search_calls":0,"candidate_retained_writes":0,
                             "illegal_physical_assignments":0,"public_reads":0} for arm in ARMS}
                detections={arm:0 for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            truth=m.y50.evaluate(seed,policy,"canonical","continue",family)
                            experiments={arm:m.candidate(seed,family,policy,arm) for arm in ARMS}
                            if seed in DEV:
                                development_checks+=1
                                continue
                            case={"seed":seed,"pair":pair,"regime":label,
                                  "family":family,"policy":policy,"arms":{}}
                            for arm,candidate in experiments.items():
                                first=next((row["public_detected_swap_first_episode"]
                                            for row in reversed(candidate["rows"])
                                            if row["public_detected_swap_first_episode"] is not None),None)
                                detections[arm]+=int(first is not None)
                                observed={"first_detection":first,
                                          "mismatch_episodes":0,
                                          "pre_detection_mismatch_episodes":0,
                                          "post_detection_mismatch_episodes":0,
                                          "wrong_assignments":0,
                                          "matching_search_calls":0,
                                          "candidate_retained_writes":0,
                                          "illegal_physical_assignments":0}
                                for reference,row in zip(truth["rows"],candidate["rows"]):
                                    assert reference["episode"]==row["episode"]
                                    wrong=sum(reference["physical_assignment"][k]!=
                                              row["physical_assignment_evaluator_only"][k]
                                              for k in reference["physical_assignment"])
                                    mismatch=int(wrong>0)
                                    observed["mismatch_episodes"]+=mismatch
                                    observed["wrong_assignments"]+=wrong
                                    observed["matching_search_calls"]+=row["matching_search_calls"]
                                    observed["candidate_retained_writes"]+=row["candidate_retained_writes"]
                                    observed["illegal_physical_assignments"]+=row["illegal_physical_assignments"]
                                    assert row["candidate_retained_cache_occupancy"]<=9
                                    assert len(row["physical_assignment_evaluator_only"])==7
                                    if first is not None and row["episode"]>=first:
                                        observed["post_detection_mismatch_episodes"]+=mismatch
                                    else:
                                        observed["pre_detection_mismatch_episodes"]+=mismatch
                                assert observed["illegal_physical_assignments"]==0
                                case["arms"][arm]=observed
                                for field in totals[arm]:
                                    totals[arm][field]+=10 if field=="public_reads" else observed[field]
                            records.append(case)
                assert all(v["public_reads"]==4*16*3*10 and
                           v["illegal_physical_assignments"]==0 for v in totals.values())
                groups[key]={"totals":totals,"detections":detections,
                             "source_anchor_checks":integrity["anchor_pair_checks"]}
                m.y49.restore_environment()
    finally:
        m.y49.restore_environment()
    assert len(records)==2*2*4*16*3
    assert development_checks==2*2*4*8*3
    comparisons=[]
    for a,b in PAIRS:
        name=f"{a}_{b}:onset1"
        result=groups[name]
        baseline=result["totals"]["dual_sentinel_detect_only"]["post_detection_mismatch_episodes"]
        corrected=result["totals"]["dual_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
        original_total=result["totals"]["original_rotating_detect_only"]["mismatch_episodes"]
        corrected_total=result["totals"]["dual_sentinel_decoder_corrected"]["mismatch_episodes"]
        comparisons.append({"case":name,"uncorrected_post":baseline,
                            "corrected_post":corrected,"original_total":original_total,
                            "corrected_total":corrected_total,
                            "post_gain":None if baseline==0 else 1-corrected/baseline,
                            "strict":baseline>0 and corrected<=.5*baseline and
                                     corrected_total<original_total,
                            "partial":baseline>0 and corrected<=.8*baseline})
    steady=all(groups[f"{a}_{b}:steady"]["totals"][arm]["mismatch_episodes"]==0
               for a,b in PAIRS for arm in ARMS)
    if steady and all(r["strict"] for r in comparisons):
        label="EARLY_CAUSAL_GAIN"
    elif steady and any(r["partial"] for r in comparisons):
        label="PARTIAL_EARLY_GAIN"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y070-onset1-causal-timing.v1",
            "parent_head":"c9b32aa0e0fb54277666661f8299ee33d61691d1",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "pairs":PAIRS,"regimes":REGIMES,"per_trial_public_scalar_reads":10,
            "active":7,"retained_limit":9,"steady_zero_mismatches":steady,
            "comparisons":comparisons,"groups":groups,
            "complete_heldout_records":records,"development_checks":development_checks,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Synthetic real bounded matching under early-coordinate shock; sensor delay not prevented."}

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
