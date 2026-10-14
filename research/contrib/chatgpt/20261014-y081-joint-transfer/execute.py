"""Y081: frozen combined new-topology and delayed-onset transfer of address-aware public decoder."""
import importlib.util
import json
from pathlib import Path

p=Path(__file__).resolve().parent.parent/"20261014-y075-blind-geometry-timing"/"execute.py"
spec=importlib.util.spec_from_file_location("y075_frozen",p)
assert spec and spec.loader
y075=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y075)

m=y075.m
HELDOUT=tuple(range(14848,14864))
DEV=tuple(range(14816,14824))
PAIRS=((4,12),(5,10))
FAMILIES=y075.FAMILIES
REGIMES=(("steady",None),("onset2",2),("onset6",6))
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

def public_decoder_any_pinned_public_address(observed,episode):
    b0=observed[0]["0"]
    a=(observed[0]["1"]-b0)%16
    d=(observed[1]["0"]-b0)%16
    assert a%2==1 and observed[1]["1"]==(b0+d+a)%16
    inverse=pow(a,-1,16)
    history={}
    first=None
    for checked_episode in (5,7):
        if checked_episode>episode: break
        for key in sorted(observed[checked_episode],key=int):
            address=int(key)
            if address in (0,1):continue
            now=observed[checked_episode][key]
            inferred=(inverse*(now-(b0+checked_episode*d)))%16
            if inferred!=address:
                assert inferred not in (0,1,address)
                if history and history!={address:inferred,inferred:address}:
                    raise AssertionError("UNQUALIFIED_SECOND_INDEPENDENT_SWAP")
                history={address:inferred,inferred:address}
                if first is None:first=checked_episode
    return {"a":a,"b0":b0,"d":d,"inverse":inverse,
            "detected_pair":history,"first_detection_episode":first}

def new_candidate(seed,family,policy,corrected):
    prior_sampler=m.y64.dual_public_samples
    prior_decoder=m.y61.y60.public_decoder
    try:
        m.y64.dual_public_samples=new_public_samples
        m.y61.y60.public_decoder=public_decoder_any_pinned_public_address
        arm="dual_sentinel_decoder_corrected" if corrected else "dual_sentinel_detect_only"
        return m.candidate(seed,family,policy,arm)
    finally:
        m.y61.y60.public_decoder=prior_decoder
        m.y64.dual_public_samples=prior_sampler

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
        for onset in ("onset2","onset6"):
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
    target=all(by[f"5_10:{onset}"]["safe_recovery"] for onset in ("onset2","onset6"))
    control=all(by[f"4_12:{onset}"]["new_detections"]==192 and
                by[f"4_12:{onset}"]["new_total"]<=by[f"4_12:{onset}"]["old_total"]
                for onset in ("onset2","onset6"))
    visible=any(by[f"5_10:{onset}"]["new_detections"]>0 for onset in ("onset2","onset6"))
    if not steady:
        label="STEADY_SAFETY_FAILURE"
    elif target and control:
        label="JOINT_TOPOLOGY_ONSET_SAFE_TRANSFER"
    elif target:
        label="JOINT_TRANSFER_CONTROL_COST"
    elif visible:
        label="JOINT_TRANSFER_DETECTION_UNSAFE"
    else:
        label="JOINT_TRANSFER_UNDETECTED"
    return {"schema":"yggdrasil.y081-joint-topology-onset-transfer.v1",
            "parent_head":"ace52db062449b9cd664158a43b655b8e8351de2",
            "classification":label,"sealed_heldout_seeds":HELDOUT,
            "development_seeds":DEV,"pairs":PAIRS,"families":FAMILIES,
            "regimes":REGIMES,"new_sampled_addresses":{"early":[0,1],"late":[4,5]},
            "old_sampled_addresses":{"early":[0,1],"late":[2,4]},
            "fixed_public_reads_per_trial":10,"active":7,"retained_limit":9,
            "steady_zero_mismatches_and_detections":steady,
            "comparisons":comparisons,"groups":groups,"complete_heldout_records":records,
            "dev_only_public_decoder_blob":"9f763bb5ae6c7f411ce1e01cab6a705d117300ce",
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Novel onset2/onset6 synthetic fixed read-budget causal transfer; no general cognition or RSI."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
