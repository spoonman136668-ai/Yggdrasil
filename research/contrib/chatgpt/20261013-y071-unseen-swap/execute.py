"""Y071 fresh-source transposition transfer of Y070 bounded sensor/decoder."""
import importlib.util
import json
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent / "20261013-y070-onset1" / "execute.py"
spec = importlib.util.spec_from_file_location("yggdrasil_y070_pinned", PARENT)
assert spec and spec.loader
y070 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y070)

DEV = tuple(range(8500, 8508))
HELDOUT = tuple(range(8576, 8592))
PAIRS = ((6, 7), (8, 9))
FAMILIES = ((3, 3, 11), (5, 9, 13), (9, 5, 7), (13, 11, 3))

def run():
    old = (y070.DEV, y070.HELDOUT, y070.PAIRS, y070.FAMILIES)
    try:
        y070.DEV, y070.HELDOUT = DEV, HELDOUT
        y070.PAIRS, y070.FAMILIES = PAIRS, FAMILIES
        original = y070.run()
    finally:
        y070.DEV, y070.HELDOUT, y070.PAIRS, y070.FAMILIES = old
        y070.m.y49.restore_environment()
    assert original["sealed_heldout_seeds"] == HELDOUT
    assert original["families"] == FAMILIES and original["pairs"] == PAIRS
    assert len(original["complete_heldout_records"]) == 2 * 2 * 4 * 16 * 3
    assert original["steady_zero_mismatches"]
    assert all(p[0] not in (0,1) and p[1] not in (0,1) for p in PAIRS)
    assert all(all(row["illegal_physical_assignments"] == 0 and
                       row["public_reads"] == 4 * len(HELDOUT) * 3 * 10
                       for row in group["totals"].values())
               for group in original["groups"].values())
    outcome = original["comparisons"]
    assert len(outcome) == 2
    if all(c["strict"] for c in outcome):
        label = "SHOCK_TOPOLOGY_TRANSFER"
    elif any(c["partial"] for c in outcome):
        label = "PARTIAL_TOPOLOGY_TRANSFER"
    else:
        label = "NO_TOPOLOGY_TRANSFER"
    return {"schema": "yggdrasil.y071-unseen-early-transposition.v1",
            "parent_head": "5797a257a75fe139313e8486cd1a1ae79c44b148",
            "classification": label, "development_seeds": DEV,
            "sealed_heldout_seeds": HELDOUT, "new_swap_pairs": PAIRS,
            "new_affine_source_families": FAMILIES,
            "strict_comparisons": outcome, "original_y070_unmodified_results": original,
            "model_calls": 0, "accepted_ref_mutation": False,
            "claim_limit": "Synthetic earliest coordinate shock topology transfer with unmodified bounded public sensor and matching policies."}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
