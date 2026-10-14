"""Y074: prospective transfer of unchanged early-shock decoder to new affine backgrounds."""
import importlib.util
import json
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent / "20261014-y073-novel-topology" / "execute.py"
spec = importlib.util.spec_from_file_location("y073_frozen", PARENT)
assert spec and spec.loader
y073 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y073)

DEV = tuple(range(9184, 9192))
HELDOUT = tuple(range(9248, 9264))
PAIRS = ((4, 11), (5, 12))
FAMILIES = ((3, 5, 9), (7, 13, 3), (11, 7, 5), (15, 11, 13))

def run():
    y070 = y073.y072.y071.y070
    original = (y070.DEV, y070.HELDOUT, y070.PAIRS, y070.FAMILIES)
    try:
        y070.DEV, y070.HELDOUT, y070.PAIRS, y070.FAMILIES = DEV, HELDOUT, PAIRS, FAMILIES
        result = y070.run()
    finally:
        y070.DEV, y070.HELDOUT, y070.PAIRS, y070.FAMILIES = original
        y070.m.y49.restore_environment()
    assert tuple(result["sealed_heldout_seeds"]) == HELDOUT
    assert tuple(tuple(p) for p in result["pairs"]) == PAIRS
    assert tuple(tuple(f) for f in result["families"]) == FAMILIES
    assert len(result["complete_heldout_records"]) == 768
    assert result["steady_zero_mismatches"]
    assert all(arm["illegal_physical_assignments"] == 0 and
               arm["public_reads"] == 4*16*3*10
               for group in result["groups"].values()
               for arm in group["totals"].values())
    comparisons = result["comparisons"]
    assert len(comparisons) == 2
    p411, p512 = comparisons
    assert p411["case"] == "4_11:onset1" and p512["case"] == "5_12:onset1"
    if p411["partial"] and p512["partial"]:
        label = "BOTH_PAIRS_NEW_FAMILY_RECOVERY"
    elif p411["partial"] and p512["uncorrected_post"] == 0:
        label = "PAIR411_RECOVERY_PAIR512_NO_OPPORTUNITY"
    elif p411["partial"]:
        label = "PAIR411_ONLY_NEW_FAMILY_RECOVERY"
    elif p512["partial"]:
        label = "PAIR512_ONLY_NEW_FAMILY_RECOVERY"
    elif all(x["uncorrected_post"] == 0 for x in comparisons):
        label = "BOTH_NO_POSTDETECTION_OPPORTUNITY"
    else:
        label = "NO_DEMONSTRATED_NEW_FAMILY_RECOVERY"
    return {"schema": "yggdrasil.y074-fresh-affine-family-transfer.v1",
            "parent_head": "073f44b4a8f2ae61fd73c8f13f04ea280fde6121",
            "classification": label, "development_seeds": DEV,
            "sealed_heldout_seeds": HELDOUT, "pairs": PAIRS,
            "families": FAMILIES, "comparisons": comparisons,
            "original_y070_unchanged_trial_evidence": result,
            "model_calls": 0, "accepted_ref_mutation": False,
            "claim_limit": "Synthetic Y070 decoder transfer to new affine backgrounds; not RSI."}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
