"""Y076: prospective fixed-read-budget sensor coverage repair, archive all controls."""
import importlib.util
import json
from pathlib import Path

p=Path(__file__).resolve().parent.parent/"20261014-y075-blind-geometry-timing"/"execute.py"
spec=importlib.util.spec_from_file_location("y075_frozen",p)
assert spec and spec.loader
y075=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y075)

m=y075.m
HELDOUT=tuple(range(9472,9488))
DEV=tuple(range(9440,9448))
PAIRS=((4,11),(5,12))
FAMILIES=y075.FAMILIES
REGIMES=(("steady",None),("onset1",1),("onset4",4))
POLICIES=y075.POLICIES
ARMS=("original_detect_only","old_dual_detect_only","old_dual_corrected",
      "new_dual_detect_only","new_dual_corrected")

def new_public_samples(seed,family):
    readings={}
    for episode in m.y64.PROBES:
        addresses=(4,5) if episode in (5,7) else (0,1)
        readings[episode]={str(address):m.y64.y46.coordinate(
            address,seed,episode,family,"late_shock") for address in addresses}
    assert sum(len(r) for r in readings.values())==10
    return readings

def new_candidate(seed,family,policy,corrected):
    prior=m.y64.dual_public_samples
    try:
        m.y64.dual_public_samples=new_public_samples
        arm="dual_sentinel_decoder_corrected" if corrected else "dual_sentinel_detect_only"
        return m.candidate(seed,family,policy,arm)
    finally:
        m.y64.dual_public_samples=prior

def run():
    groups={}
    records=[]
    development_checks=0
    try:
        for pair in PAIRS:
            for regime,onset in REGIMES:
                key=f"{pair[0]}_{pair[1]}:{regime}"
                integrity={"anchor_pair_checks":0}
                m.y58.install_transposition(onset,pair,integrity)
                totals={arm:{"mismatch_episodes":0,"pre_detection_mismatch_episodes":0,
                             "post_detection_mismatch_episodes":0,"illegal_physical_assignments":0,
                             "public_reads":0} for arm in ARMS}
                detections={arm:0 for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        for policy in POLICIES:
                            truth=m.y50.evaluate(seed,policy,"canonical","continue",family)
                            trials={
                                "original_detect_only":m.candidate(seed,family,policy,"original_rotating_detect_only"),
                                "old_dual_detect_only":m.candidate(seed,family,policy,"dual_sentinel_detect_only"),
                                "old_dual_corrected":m.candidate(seed,family,policy,"dual_sentinel_decoder_corrected"),
                                "new_dual_detect_only":new_candidate(seed,family,policy,False),
                                "new_dual_corrected":new_candidate(seed,family,policy,True)
                            }
                            if seed in DEV:
                                development_checks+=1
                                continue
                            case={"seed":seed,"pair":pair,"regime":regime,
                                  "family":family,"policy":policy,"arms":{}}
                            for arm,trial in trials.items():
                                assert trial["public_scalar_reads"]==10
                                first=next((r["public_detected_swap_first_episode"]
                                            for r in reversed(trial["rows"])
                                            if r["public_detected_swap_first_episode"] is not None),None)
                                detections[arm]+=int(first is not None)
                                obs={"first_detection":first,"mismatch_episodes":0,
                                     "pre_detection_mismatch_episodes":0,
                                     "post_detection_mismatch_episodes":0,
                                     "illegal_physical_assignments":0,
                                     "public_reads":10}
                                for ref,r in zip(truth["rows"],trial["rows"]):
                                    assert ref["episode"]==r["episode"]
                                    assert len(r["physical_assignment_evaluator_only"])==7
                                    assert r["candidate_retained_cache_occupancy"]<=9
                                    errors=sum(ref["physical_assignment"][k]!=
                                               r["physical_assignment_evaluator_only"][k]
                                               for k in ref["physical_assignment"])
                                    bad=int(errors>0)
                                    obs["mismatch_episodes"]+=bad
                                    obs["illegal_physical_assignments"]+=r["illegal_physical_assignments"]
                                    if first is not None and r["episode"]>=first:
                                        obs["post_detection_mismatch_episodes"]+=bad
                                    else:
                                        obs["pre_detection_mismatch_episodes"]+=bad
                                assert obs["illegal_physical_assignments"]==0
                                case["arms"][arm]=obs
                                for field in totals[arm]:
                                    totals[arm][field]+=obs[field]
                            records.append(case)
                assert all(v["public_reads"]==4*16*3*10 and
                           v["illegal_physical_assignments"]==0 for v in totals.values())
                groups[key]={"totals":totals,"detections":detections,
                             "anchor_checks":integrity["anchor_pair_checks"]}
                m.y49.restore_environment()
    finally:
        m.y49.restore_environment()
    assert len(records)==2*3*4*16*3
    assert development_checks==2*3*4*8*3
    steady=all(groups[f"{a}_{b}:steady"]["totals"][arm]["mismatch_episodes"]==0 and
               groups[f"{a}_{b}:steady"]["detections"][arm]==0
               for a,b in PAIRS for arm in ARMS)
    comparisons=[]
    for a,b in PAIRS:
        for onset in ("onset1","onset4"):
            key=f"{a}_{b}:{onset}"
            group=groups[key]
            old_det=group["detections"]["old_dual_corrected"]
            new_det=group["detections"]["new_dual_corrected"]
            old_total=group["totals"]["old_dual_corrected"]["mismatch_episodes"]
            corrected_total=group["totals"]["new_dual_corrected"]["mismatch_episodes"]
            new_post_base=group["totals"]["new_dual_detect_only"]["post_detection_mismatch_episodes"]
            new_post_corrected=group["totals"]["new_dual_corrected"]["post_detection_mismatch_episodes"]
            safe=(new_det==192 and new_post_base>0 and
                  new_post_corrected<=.8*new_post_base and corrected_total<old_total)
            comparisons.append({"case":key,"old_detections":old_det,"new_detections":new_det,
                                "old_total":old_total,"new_total":corrected_total,
                                "new_uncorrected_post":new_post_base,
                                "new_corrected_post":new_post_corrected,
                                "post_gain":None if new_post_base==0 else 1-new_post_corrected/new_post_base,
                                "safe_recovery":safe})
    by={c["case"]:c for c in comparisons}
    target=all(by[f"5_12:{onset}"]["safe_recovery"] for onset in ("onset1","onset4"))
    control=all(by[f"4_11:{onset}"]["new_detections"]==192 and
                by[f"4_11:{onset}"]["new_total"]<=by[f"4_11:{onset}"]["old_total"]
                for onset in ("onset1","onset4"))
    visible=any(by[f"5_12:{onset}"]["new_detections"]>0 for onset in ("onset1","onset4"))
    if not steady:
        label="STEADY_SAFETY_FAILURE"
    elif target and control:
        label="DUAL_PAIR_SAFE_RECOVERY"
    elif target:
        label="TARGET_RECOVERY_WITH_CONTROL_COST"
    elif visible:
        label="DETECTION_WITHOUT_BOTH_ONSET_RECOVERY"
    else:
        label="TARGET_STILL_BLIND"
    return {"schema":"yggdrasil.y076-fixed-read-sentinel-coverage.v1",
            "parent_head":"5e20c3ef2d0eded5435599a2a826664e08d4b9e9",
            "classification":label,"sealed_heldout_seeds":HELDOUT,
            "development_seeds":DEV,"pairs":PAIRS,"families":FAMILIES,
            "regimes":REGIMES,"new_sampled_addresses":{"early":[0,1],"late":[4,5]},
            "old_sampled_addresses":{"early":[0,1],"late":[2,4]},
            "fixed_public_reads_per_trial":10,"active":7,"retained_limit":9,
            "steady_zero_mismatches_and_detections":steady,
            "comparisons":comparisons,"groups":groups,"complete_heldout_records":records,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Fixed read-budget targeted synthetic geometry sensing; old pair2 sensing tradeoff untested; not RSI."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
