"""Y060: public-sentinel-triggered causal decoding of one unknown synthetic cell swap."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y059-rotating-probes"/"execute.py"
spec=importlib.util.spec_from_file_location("y59_source",SOURCE)
assert spec and spec.loader
y59=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y59)

y58=y59.y58
y49=y59.y49
y46=y59.y46
DEV=tuple(range(3136,3144))
HELDOUT=tuple(range(3144,3160))
FAMILIES=((3,3,7),(5,9,13),(7,11,1),(11,15,5))
PAIRS=((2,3),(4,5))
CASES=(("steady",None),("onset4",4),("onset6",6))
ARMS=("anchor_only_decode","rotating_detect_only","rotating_causal_decoder_correction")

def public_decoder(observed,episode):
    # Observe only precommitted PUBLIC scalars. Source truth is never used
    # to build the decoder correction.
    b0=observed[0]["0"]
    a=(observed[0]["1"]-b0)%16
    d=(observed[1]["0"]-b0)%16
    assert a%2==1
    assert observed[1]["1"]==(b0+d+a)%16
    inverse=pow(a,-1,16)
    history={}
    first_detection=None
    for probed_episode in (5,7):
        if probed_episode>episode:
            break
        address=2 if probed_episode==5 else 4
        if str(address) not in observed[probed_episode]:
            # The matched anchor-only control has no sentinel capability.
            # This branch is determined by public sensor identity, not truth.
            continue
        now=observed[probed_episode][str(address)]
        inferred_physical=(inverse*(now-(b0+probed_episode*d)))%16
        if inferred_physical != address:
            assert inferred_physical not in (0,1,address)
            # One bounded one-swap correction. An unrelated second swap
            # would be an explicitly unsupported event and fails closed.
            if history and set(history)!={address,inferred_physical}:
                raise AssertionError("UNQUALIFIED_SECOND_INDEPENDENT_SWAP")
            history={address:inferred_physical,inferred_physical:address}
            if first_detection is None:
                first_detection=probed_episode
    return {"a":a,"b0":b0,"d":d,"inverse":inverse,
            "detected_pair":history,"first_detection_episode":first_detection}

def decode_label(encoded,model,episode,corrected):
    presumed=(model["inverse"]*(encoded-(model["b0"]+episode*model["d"])))%16
    return model["detected_pair"].get(presumed,presumed) if corrected else presumed

def one_instance(seed,family,source_pair,onset):
    # Simulator configuration and labeled test vectors are EVALUATOR-ONLY.
    # Candidate receives only encoded value + the precommitted public sensors.
    native_reads=y59.sample(seed,family,"fixed_two_anchors")
    rotated_reads=y59.sample(seed,family,"fixed_rotating_sentinels")
    assert sum(len(x) for x in native_reads.values())==10
    assert sum(len(x) for x in rotated_reads.values())==10
    errors={arm:0 for arm in ARMS}
    post_errors={arm:0 for arm in ARMS}
    records=[]
    action_first=None
    previous_pair={}
    for episode in range(8):
        native_model=public_decoder(native_reads,episode) if episode>=1 else None
        rotating_model=public_decoder(rotated_reads,episode) if episode>=1 else None
        if rotating_model and rotating_model["first_detection_episode"] is not None:
            action_first=rotating_model["first_detection_episode"]
        if previous_pair:
            assert rotating_model["detected_pair"]==previous_pair,"CORRECTION_FORGOTTEN"
        if rotating_model and rotating_model["detected_pair"]:
            previous_pair=dict(rotating_model["detected_pair"])
        diffs={arm:0 for arm in ARMS}
        for actual_cell in range(16):
            incoming_encoded=y46.coordinate(actual_cell,seed,episode,family,"late_shock")
            if episode==0:
                # Initial calibration b0/a is already available at episode0;
                # d is not yet learned, but phase step0 needs no d.
                b0=rotated_reads[0]["0"]
                a=(rotated_reads[0]["1"]-b0)%16
                expected=(pow(a,-1,16)*(incoming_encoded-b0))%16
                decoded={arm:expected for arm in ARMS}
            else:
                decoded={
                    "anchor_only_decode":decode_label(incoming_encoded,native_model,episode,False),
                    "rotating_detect_only":decode_label(incoming_encoded,rotating_model,episode,False),
                    "rotating_causal_decoder_correction":decode_label(incoming_encoded,rotating_model,episode,True)}
            for arm in ARMS:
                diffs[arm]+=int(decoded[arm]!=actual_cell)
        for arm in ARMS:
            errors[arm]+=diffs[arm]
            if action_first is not None and episode>=action_first:
                post_errors[arm]+=diffs[arm]
        records.append({"episode":episode,"errors_by_decoder":diffs,
                        "detected_swap_public":dict(previous_pair),
                        "has_public_calibration":episode>=1,
                        "has_caused_correction":bool(previous_pair)})
    return {"source_pair_evaluator_only":source_pair,"source_onset_evaluator_only":onset,
            "errors":errors,"post_detection_errors":post_errors,
            "first_causal_detection":action_first,
            "observations_per_trial":10,
            "episodes":records}

def run():
    groups={}
    records=[]
    structural_checks=0
    try:
        for pair in PAIRS:
            for name,onset in CASES:
                key=f"{pair[0]}_{pair[1]}:{name}"
                checks={"anchor_pair_checks":0}
                y58.install_transposition(onset,pair,checks)
                acc={"cases":0,"first_detection":{},"errors":{a:0 for a in ARMS},
                     "post_detection_errors":{a:0 for a in ARMS},
                     "detected":0,"source_anchor_checks":0}
                for family in FAMILIES:
                    for seed in DEV+HELDOUT:
                        item=one_instance(seed,family,pair,onset)
                        assert item["observations_per_trial"]==10
                        if seed in DEV:
                            structural_checks+=1
                        else:
                            acc["cases"]+=1
                            detection=item["first_causal_detection"]
                            acc["detected"]+=int(detection is not None)
                            if detection is not None:
                                acc["first_detection"][str(detection)]=acc["first_detection"].get(str(detection),0)+1
                            for arm in ARMS:
                                acc["errors"][arm]+=item["errors"][arm]
                                acc["post_detection_errors"][arm]+=item["post_detection_errors"][arm]
                            records.append({"case":key,"family":family,"seed":seed,**item})
                acc["source_anchor_checks"]=checks["anchor_pair_checks"]
                assert acc["cases"]==4*16
                groups[key]=acc
                y49.restore_environment()
    finally:
        y49.restore_environment()
    assert structural_checks==2*3*4*8
    steady_ok=all(groups[f"{p[0]}_{p[1]}:steady"]["errors"][a]==0
                  for p in PAIRS for a in ARMS)
    expected_detect=("2_3:onset4","4_5:onset4","4_5:onset6")
    valid=[]
    for key in expected_detect:
        cell=groups[key]
        baseline=cell["post_detection_errors"]["rotating_detect_only"]
        corrected=cell["post_detection_errors"]["rotating_causal_decoder_correction"]
        valid.append(cell["detected"]==64 and baseline>0 and corrected<=0.10*baseline)
    miss=groups["2_3:onset6"]
    miss_ok=(miss["detected"]==0 and
             miss["errors"]["rotating_causal_decoder_correction"]==
             miss["errors"]["rotating_detect_only"])
    if steady_ok and miss_ok and all(valid):
        label="CAUSAL_DECODER_RECOVERY"
    elif steady_ok and any(valid):
        label="PARTIAL_DECODER_RECOVERY"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y060-public-sentinel-causal-decoder.v1",
            "parent_head":"05f367ddfa06dca232ec66282e18889968e18a9e",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"families":FAMILIES,
            "steadies_no_false_corrections":steady_ok,
            "known_timing_blindspot_preserved":miss_ok,
            "detectable_recovery_gates":dict(zip(expected_detect,valid)),
            "development_structural_checks":structural_checks,
            "per_trial_public_scalar_reads":10,
            "results_by_condition":groups,"heldout_records":records,
            "new_matching_controller_or_cache_actuation":False,
            "model_calls":0,
            "claim_limit":"Synthetic one-transposition coordinate-label decoder repair after public sentinel readings, NOT cache matching recovery, independent physical source or autonomous cognition."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
