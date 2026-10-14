"""Y077: fixed-read public address-aware decoder, independent sealed source."""
import importlib.util
import json
from pathlib import Path

p=Path(__file__).resolve().parent.parent/"20261014-y076-sentinel-coverage"/"execute.py"
spec=importlib.util.spec_from_file_location("y076_frozen",p)
assert spec and spec.loader
y076=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y076)
m=y076.m

DEV=tuple(range(9520,9528))
HELDOUT=tuple(range(9568,9584))

def public_decoder(readings,episode):
    b0=readings[0]["0"]
    a=(readings[0]["1"]-b0)%16
    d=(readings[1]["0"]-b0)%16
    assert a%2==1 and readings[1]["1"]==(b0+d+a)%16
    inv=pow(a,-1,16)
    first=None
    mapping={}
    for at in (5,7):
        if at>episode:break
        for label in sorted(readings[at],key=int):
            address=int(label)
            if address in (0,1):continue
            physical=(inv*(readings[at][label]-(b0+at*d)))%16
            if physical!=address:
                assert physical not in (0,1,address)
                swap={address:physical,physical:address}
                if mapping and mapping!=swap:
                    raise AssertionError("UNQUALIFIED_SECOND_INDEPENDENT_SWAP")
                mapping=swap
                if first is None:first=at
    return {"a":a,"b0":b0,"d":d,"inverse":inv,
            "detected_pair":mapping,"first_detection_episode":first}

def run():
    dev,heldout=y076.DEV,y076.HELDOUT
    original_candidate=y076.new_candidate
    counts={"new_arms":0,"decoder":0}
    def corrected_new_candidate(seed,family,policy,corrected):
        saved=m.y61.y60.public_decoder
        def observed_decoder(readings,episode):
            counts["decoder"]+=1
            return public_decoder(readings,episode)
        try:
            m.y61.y60.public_decoder=observed_decoder
            output=original_candidate(seed,family,policy,corrected)
        finally:
            m.y61.y60.public_decoder=saved
        counts["new_arms"]+=1
        return output
    try:
        y076.DEV,y076.HELDOUT=DEV,HELDOUT
        y076.new_candidate=corrected_new_candidate
        result=y076.run()
    finally:
        y076.DEV,y076.HELDOUT=dev,heldout
        y076.new_candidate=original_candidate
        m.y49.restore_environment()
    assert result["sealed_heldout_seeds"]==HELDOUT
    assert len(result["complete_heldout_records"])==1152
    assert counts["new_arms"]==2*3*4*24*3*2
    assert counts["decoder"]>0
    comparisons={r["case"]:r for r in result["comparisons"]}
    target=all(comparisons[f"5_12:{at}"]["safe_recovery"] for at in ("onset1","onset4"))
    control=all(comparisons[f"4_11:{at}"]["new_detections"]==192 and
                comparisons[f"4_11:{at}"]["new_total"]<=comparisons[f"4_11:{at}"]["old_total"]
                for at in ("onset1","onset4"))
    visible=any(comparisons[f"5_12:{at}"]["new_detections"]>0 for at in ("onset1","onset4"))
    if not result["steady_zero_mismatches_and_detections"]:
        label="STEADY_SAFETY_FAILURE"
    elif target and control:
        label="DUAL_TOPOLOGY_SAFE_RECOVERY"
    elif target:
        label="TARGET_RECOVERY_WITH_CONTROL_COST"
    elif visible:
        label="TARGET_DETECTED_PARTIAL_OR_UNSAFE"
    else:
        label="TARGET_UNDETECTED"
    return {"schema":"yggdrasil.y077-frozen-public-decoder.v1",
            "parent_head":"44c1f6f81066b219ff209fbd8aed318d795915ed",
            "classification":label,"development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "new_decoder_invocations":counts,"comparisons":result["comparisons"],
            "groups":result["groups"],"paired_trials":result["complete_heldout_records"],
            "steady_zero_mismatches_and_detections":result["steady_zero_mismatches_and_detections"],
            "fixed_public_reads_per_trial":10,"active":7,"retained_limit":9,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Synthetic bounded prospective public decoder qualification; not broad intelligence or RSI."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
