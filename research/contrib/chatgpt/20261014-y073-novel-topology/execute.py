"""Y073: prospective fresh unseen cross-gap shock-site transfer."""
import importlib.util
import json
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent / "20261013-y072-cross-pairs" / "execute.py"
spec = importlib.util.spec_from_file_location("y072_pinned", PARENT)
assert spec and spec.loader
y072 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y072)

DEV = tuple(range(9064,9072))
HELDOUT = tuple(range(9104,9120))
PAIRS = ((4,11),(5,12))
FAMILIES = y072.FAMILIES

def run():
    y070 = y072.y071.y070
    original = (y070.DEV,y070.HELDOUT,y070.PAIRS,y070.FAMILIES)
    try:
        y070.DEV,y070.HELDOUT = DEV,HELDOUT
        y070.PAIRS,y070.FAMILIES = PAIRS,FAMILIES
        result = y070.run()
    finally:
        y070.DEV,y070.HELDOUT,y070.PAIRS,y070.FAMILIES = original
        y070.m.y49.restore_environment()
    assert tuple(result["sealed_heldout_seeds"])==HELDOUT
    assert tuple(tuple(p) for p in result["pairs"])==PAIRS
    assert tuple(tuple(f) for f in result["families"])==FAMILIES
    assert len(result["complete_heldout_records"])==2*2*4*16*3
    assert result["steady_zero_mismatches"]
    assert all(0 not in p and 1 not in p for p in PAIRS)
    assert all(arm["illegal_physical_assignments"]==0 and
               arm["public_reads"]==4*16*3*10
               for group in result["groups"].values()
               for arm in group["totals"].values())
    comparisons=result["comparisons"]
    assert len(comparisons)==2
    if all(x["strict"] for x in comparisons):
        label="TOPOLOGY_TRANSFER"
    elif any(x["partial"] for x in comparisons):
        label="PARTIAL_TOPOLOGY_TRANSFER"
    elif all(x["uncorrected_post"]==0 for x in comparisons):
        label="NO_POSTDETECTION_OPPORTUNITY"
    else:
        label="NO_GAIN"
    return {"schema":"yggdrasil.y073-fresh-cross-gap-topology.v1",
            "parent_head":"6a2bafd89b4500ac700d04415f41e2552f87014c",
            "classification":label,"development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "pairs":PAIRS,"families":FAMILIES,"comparisons":comparisons,
            "original_y070_unchanged_trial_evidence":result,
            "model_calls":0,"accepted_ref_mutation":False,
            "claim_limit":"Frozen synthetic early sensor and decoder transfer across two new swap sites; not RSI."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
