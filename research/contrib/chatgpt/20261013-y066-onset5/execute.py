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
        m.DEV=DEV;m.HELDOUT=HELDOUT;m.FAMILIES=FAMILIES;m.REGIMES=REGIMES
        result=m.run()
    finally:m.DEV,m.HELDOUT,m.FAMILIES,m.REGIMES=old
    assert result["development_seeds"]==DEV
    assert result["sealed_heldout_seeds"]==HELDOUT
    assert len(result["heldout_records"])==2*5*4*16*3
    comparisons=[]
    for source in ("2_3:onset5","4_5:onset5"):
        a=result["groups"][source]
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
        for v in result["groups"].values() for arm in m.ARMS)
    if safe and all(x["strict"] for x in comparisons):label="TIMING_ROBUST_RECOVERY"
    elif safe and any(x["partial"] for x in comparisons):label="PARTIAL_TIMING_GAIN"
    else:label="NO_GAIN"
    return {"schema":"yggdrasil.y066-dual-new-onset5-matching.v1",
            "parent_head":"343621953c382f450e5603abaac7bf51b92ae09e",
            "classification":label,"development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "families":FAMILIES,"new_onset5_comparisons":comparisons,
            "matching_and_sensing_safe":safe,"original_complete_data":result,
            "model_calls":0,"claim_limit":"Synthetic bounded matching source onset shift; not independently admitted FSA recovery."}
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))
