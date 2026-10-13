"""Y059: fixed-cost rotating landmark observability of anchor-invisible coordinate swaps."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y058-anchor-blind"/"execute.py"
spec=importlib.util.spec_from_file_location("y58_pinned",SOURCE)
assert spec and spec.loader
y58=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y58)
y46=y58.y46
y49=y58.y49

DEV=tuple(range(2944,2952))
HELDOUT=tuple(range(2952,2968))
FAMILIES=((3,13,7),(5,7,11),(7,3,5),(11,5,9))
PAIRS=((2,3),(4,5))
CASES=(("steady",None),("onset4",4),("onset6",6))
PROBES=(0,1,3,5,7)
ARMS=("fixed_two_anchors","fixed_rotating_sentinels")

def sample(seed,family,arm):
    out={}
    for episode in PROBES:
        if arm=="fixed_rotating_sentinels" and episode==5:
            cells=(0,2)
        elif arm=="fixed_rotating_sentinels" and episode==7:
            cells=(0,4)
        else:
            cells=(0,1)
        # Instrument samples only the precommitted public physical landmark
        # addresses; no generator-shock metadata passes to detector.
        sampled={}
        for cell in cells:
            value=y46.coordinate(cell,seed,episode,family,"late_shock")
            if cell in (0,1):
                # Source-integrity witness only; native coordinate is NOT
                # supplied to the candidate's independent detector.
                assert value==y58.ORIGINAL[0](cell,seed,episode,family,"steady")
            sampled[str(cell)]=value
        out[episode]=sampled
    assert sum(len(x) for x in out.values())==10
    return out

def detector(observed):
    """Only 0/1 baseline and selected current observations, no swap/onset."""
    b0=observed[0]["0"]
    a=(observed[0]["1"]-b0)%16
    d=(observed[1]["0"]-b0)%16
    assert a%2==1
    assert observed[1]["1"]==(b0+d+a)%16
    residuals=[]
    for episode in PROBES:
        for address,value in observed[episode].items():
            cell=int(address)
            expectation=(b0+episode*d+cell*a)%16
            delta=(value-expectation)%16
            residuals.append({"episode":episode,"public_cell":cell,
                              "observed":value,"expected":expectation,
                              "residual_mod16":delta})
    return {"detected":any(x["residual_mod16"]!=0 for x in residuals),
            "reads":len(residuals),"per_landmark":residuals}

def run():
    records=[]
    dev_structural=0
    counts={}
    try:
        for pair in PAIRS:
            for name,onset in CASES:
                checks={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,checks)
                key=f"{pair[0]}_{pair[1]}:{name}"
                acc={arm:{"detected":0,"trials":0,"reads":0} for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        arm_results={}
                        for arm in ARMS:
                            obs=sample(seed,family,arm)
                            decision=detector(obs)
                            assert decision["reads"]==10
                            arm_results[arm]=decision
                            if seed in HELDOUT:
                                acc[arm]["trials"]+=1
                                acc[arm]["detected"]+=int(decision["detected"])
                                acc[arm]["reads"]+=decision["reads"]
                        if seed in DEV:
                            # The dev-only check verifies the entire
                            # instrument route before first sealed use.
                            dev_structural+=int(
                                all(arm_results[x]["reads"]==10 for x in ARMS))
                        else:
                            records.append({"swap":pair,"regime":name,
                                            "family":family,"seed":seed,
                                            "readout":arm_results})
                counts[key]={"swap":pair,"regime":name,
                             "matched_detector_outcomes":acc,
                             "public_anchor_invariance_checks":checks["anchor_pair_checks"]}
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert len(records)==2*3*4*16
    assert dev_structural==2*3*4*8
    assert all(v["matched_detector_outcomes"][arm]["reads"]==4*16*10
               for v in counts.values() for arm in ARMS)
    steady_ok=all(
        counts[f"{pair[0]}_{pair[1]}:steady"]["matched_detector_outcomes"][arm]["detected"]==0
        for pair in PAIRS for arm in ARMS)
    anchors_blind=all(
        v["matched_detector_outcomes"]["fixed_two_anchors"]["detected"]==0
        for v in counts.values())
    required=(("2_3:onset4"),("4_5:onset4"),("4_5:onset6"))
    covered=sum(counts[key]["matched_detector_outcomes"][
        "fixed_rotating_sentinels"]["detected"]==4*16 for key in required)
    expected_miss=counts["2_3:onset6"]["matched_detector_outcomes"][
        "fixed_rotating_sentinels"]["detected"]==0
    if steady_ok and anchors_blind and covered==3 and expected_miss:
        label="SENSOR_REALLOCATION_GAIN"
    elif steady_ok and anchors_blind and covered>0:
        label="PARTIAL_GAIN"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y059-rotating-landmark-detection.v1",
            "parent_head":"c0c4c1b734053d983cf36a198c15d2c4ff210226",
            "classification":label,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"source_swap_pairs":PAIRS,
            "onset_regimes":[s for s,_ in CASES],
            "observations_per_trial":10,
            "frozen_expected_detection_case_count":3,
            "fully_detected_expected_cases":covered,
            "expected_unseen_onset6_swap2_3_confirmed":expected_miss,
            "fixed_anchor_zero":anchors_blind,
            "steady_false_alarms_zero":steady_ok,
            "source_structural_development_checks":dev_structural,
            "results_by_swap_onset":counts,
            "all_heldout_sensor_records":records,
            "new_controller_actuation":False,
            "model_calls":0,
            "claim_limit":"Fixed non-oracle sentinel landmark observation using same numerical reading count but different physically sampled cells; DETECTION ONLY, no matching repair or biological cognition."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
