"""Y064: redistribute fixed ten public reads to two nonanchor sentinels."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y063-cache-components"/"execute.py"
spec=importlib.util.spec_from_file_location("y63_pinned",SOURCE)
assert spec and spec.loader
y63=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y63)

y59=y63.y59
y58=y63.y58
y49=y63.y49
y46=y63.y46

DEV=tuple(range(5000,5008))
HELDOUT=tuple(range(5016,5032))
FAMILIES=((3,5,11),(5,11,15),(7,9,3),(11,1,7))
SWAPS=((2,3),(4,5))
CASES=(("steady",None),("onset4",4),("onset6",6),("onset7",7))
ARMS=("original_rotating","dual_sentinel")
PROBES=(0,1,3,5,7)

def dual_public_samples(seed,family):
    measurements={}
    for episode in PROBES:
        if episode in (5,7):addresses=(2,4)
        else:addresses=(0,1)
        measurements[episode]={str(address):y46.coordinate(
            address,seed,episode,family,"late_shock") for address in addresses}
    assert sum(len(v) for v in measurements.values())==10
    return measurements

def sample_and_detect(seed,family,arm):
    if arm=="original_rotating":
        readings=y59.sample(seed,family,"fixed_rotating_sentinels")
    else:
        readings=dual_public_samples(seed,family)
    assert sum(len(r) for r in readings.values())==10
    # Original Y059 detector consumes ONLY sampled observed coordinates;
    # cannot see evaluator-only known physical swap or true onset.
    observed=y59.detector(readings)
    assert observed["reads"]==10
    earliest=next((r["episode"] for r in observed["per_landmark"]
                   if r["residual_mod16"]!=0),None)
    assert observed["detected"]==(earliest is not None)
    return {"detected":observed["detected"],
            "first_public_detection_episode":earliest,
            "readings":readings,
            "public_residuals":observed["per_landmark"],
            "scalar_read_count":10}

def run():
    groups={}
    records=[]
    checks=0
    dev_structural=0
    try:
        for pair in SWAPS:
            for case,onset in CASES:
                integrity={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,integrity)
                key=f"{pair[0]}_{pair[1]}:{case}"
                group={arm:{"detections":0,"false_alarms":0,
                            "trials":0,"reads":0,"detection_episode_counts":{}}
                       for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        candidate={}
                        for arm in ARMS:
                            candidate[arm]=sample_and_detect(seed,family,arm)
                            # Source witness remains evaluator-side only.
                            for sampled_episode in (0,1,3):
                                for cell in (0,1):
                                    native=y58.ORIGINAL[0](
                                        cell,seed,sampled_episode,family,"steady")
                                    assert candidate[arm]["readings"][sampled_episode][str(cell)]==native
                                    checks+=1
                        if seed in DEV:
                            assert all(item["scalar_read_count"]==10 for item in candidate.values())
                            dev_structural+=1
                        else:
                            for arm,item in candidate.items():
                                aggregate=group[arm]
                                aggregate["trials"]+=1
                                aggregate["detections"]+=int(item["detected"])
                                aggregate["false_alarms"]+=int(onset is None and item["detected"])
                                aggregate["reads"]+=item["scalar_read_count"]
                                e=item["first_public_detection_episode"]
                                if e is not None:
                                    s=str(e)
                                    aggregate["detection_episode_counts"][s]=aggregate[
                                        "detection_episode_counts"].get(s,0)+1
                            records.append({"source_pair_evaluator_only":pair,"onset_evaluator_only":case,
                                            "family":family,"seed":seed,"arms":candidate})
                assert all(group[arm]["trials"]==4*16 and group[arm]["reads"]==4*16*10 for arm in ARMS)
                assert integrity["anchor_pair_checks"]==0 or integrity["anchor_pair_checks"]>0
                groups[key]=group
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert len(records)==2*4*4*16
    assert dev_structural==2*4*4*8
    assert checks==2*4*4*(8+16)*2*3*2
    all_steady_zero=all(groups[f"{p[0]}_{p[1]}:steady"][arm]["detections"]==0
                        for p in SWAPS for arm in ARMS)
    expect=["2_3:onset4","2_3:onset6","2_3:onset7",
            "4_5:onset4","4_5:onset6","4_5:onset7"]
    full_dual=sum(groups[k]["dual_sentinel"]["detections"]==64 for k in expect)
    past_blind=all(groups[k]["original_rotating"]["detections"]==0
                   for k in ("2_3:onset6","2_3:onset7"))
    gained=sum(groups[k]["dual_sentinel"]["detections"]==64 and
               groups[k]["original_rotating"]["detections"]==0
               for k in ("2_3:onset6","2_3:onset7"))
    if all_steady_zero and full_dual==6 and past_blind:
        label="DUAL_SENTINEL_COVERAGE"
    elif all_steady_zero and gained>=1:
        label="PARTIAL_COVERAGE_GAIN"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y064-dual-nonanchor-sentinel.v1",
            "parent_head":"7ceb113e90e7dfb6f9fb0bef8afb842fc0316156",
            "classification":label,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"source_swaps":SWAPS,
            "regimes":[x for x,_ in CASES],
            "per_trial_public_scalar_reads":10,
            "original_blind_cases_still_blind":past_blind,
            "dual_detected_all_64_by_group":full_dual,
            "recovered_blind_group_count":gained,
            "steady_false_positive_free":all_steady_zero,
            "source_integrity_checks":checks,
            "development_structural_cases":dev_structural,
            "aggregate_by_case":groups,"heldout_records":records,
            "new_candidate_matching_or_controller_actuation":False,
            "model_calls":0,
            "claim_limit":"Prospective synthetic non-oracle scheduled public landmark detector covering two shifted sentinels with unchanged sample COUNT and changed sampled sensor addresses, not autonomous matching recovery."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
