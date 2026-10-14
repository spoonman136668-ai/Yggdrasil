"""Y072: frozen cross-gap shock-site transfer of earliest-onset causal decoder."""
import importlib.util
import json
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y071-unseen-swap"/"execute.py"
spec=importlib.util.spec_from_file_location("y071_pinned",PARENT)
assert spec and spec.loader
y071=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y071)

DEV=tuple(range(8880,8888))
HELDOUT=tuple(range(8928,8944))
PAIRS=((2,6),(3,9))
FAMILIES=y071.FAMILIES

def run():
    y070=y071.y070
    old=(y070.DEV,y070.HELDOUT,y070.PAIRS,y070.FAMILIES)
    try:
        y070.DEV,y070.HELDOUT=DEV,HELDOUT
        y070.PAIRS,y070.FAMILIES=PAIRS,FAMILIES
        result=y070.run()
    finally:
        y070.DEV,y070.HELDOUT,y070.PAIRS,y070.FAMILIES=old
        y070.m.y49.restore_environment()
    assert result["sealed_heldout_seeds"]==HELDOUT
    assert result["pairs"]==PAIRS and result["families"]==FAMILIES
    assert len(result["complete_heldout_records"])==768
    assert result["steady_zero_mismatches"]
    for (a,b) in PAIRS:
        assert a not in (0,1) and b not in (0,1)
    assert all(arm["illegal_physical_assignments"]==0 and
               arm["public_reads"]==4*16*3*10
               for group in result["groups"].values()
               for arm in group["totals"].values())
    cases=result["comparisons"]
    assert len(cases)==2
    if all(c["strict"] for c in cases):
        label="CROSS_PAIR_RECOVERY"
    elif any(c["partial"] for c in cases):
        label="PARTIAL_CROSS_PAIR_RECOVERY"
    elif all(c["uncorrected_post"]==0 for c in cases):
        label="POST_DETECTION_ZERO_ERROR"
    else:
        label="CROSS_PAIR_NO_GAIN"
    return {"schema":"yggdrasil.y072-cross-gap-pairs.v1",
            "parent_head":"c53d1d3000ec69846f4e06706e899e5b0a5a9514",
            "classification":label,"development_seeds":DEV,
            "sealed_heldout_seeds":HELDOUT,"cross_gap_swap_pairs":PAIRS,
            "source_affine_families":FAMILIES,
            "early_post_detection_comparisons":cases,
            "original_y070_unchanged_trial_evidence":result,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Synthetic Y070 early onset bounded-matching correction transfer to new cross-gap cell pairs."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
