"""Y040: first-use affine-coordinate-family transfer, no policy retuning."""
import importlib.util
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "20261013-y039-moving-frame" / "execute.py"
spec = importlib.util.spec_from_file_location("y039_pinned", SOURCE)
assert spec and spec.loader
y39 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y39)

DEV = tuple(range(632, 640))
HELDOUT = tuple(range(640, 656))
FAMILIES = ((1, 3, 5), (3, 5, 7), (7, 7, 9), (11, 9, 11))
POLICIES = y39.POLICIES
MODES = y39.MODES


def run():
    records = []
    mismatches = {m: 0 for m in MODES if m != "reference_numeric"}
    churn = {p: {m: 0 for m in MODES} for p in POLICIES}
    origins = y39.encode, y39.decode
    try:
        for multiplier, seed_step, time_step in FAMILIES:
            inverse = pow(multiplier, -1, 16)

            def enc(cell, seed, episode):
                return (multiplier * cell + seed_step * seed + time_step * episode) % 16

            def dec(cell, seed, episode):
                return (inverse * (cell - seed_step * seed - time_step * episode)) % 16

            y39.encode, y39.decode = enc, dec
            assert all(dec(enc(c, 640, e), 640, e) == c for e in range(8) for c in range(16))
            for seed in DEV + HELDOUT:
                for policy in POLICIES:
                    arms = {mode: y39.evaluate(seed, mode, policy) for mode in MODES}
                    ref = arms["reference_numeric"]
                    for mode, arm in arms.items():
                        assert ref["cache_writes"] == arm["cache_writes"]
                        for a, b in zip(ref["rows"], arm["rows"]):
                            assert a["cache_writes"] == b["cache_writes"]
                            assert a["matched"] == b["matched"] == 7
                            assert len(a["cache_keys"]) == len(b["cache_keys"])
                            if (seed in HELDOUT and mode != "reference_numeric" and
                                    a["physical_assignment"] != b["physical_assignment"]):
                                mismatches[mode] += 1
                        if seed in HELDOUT:
                            churn[policy][mode] += arm["physical_churn"]
                    records.append({"family": [multiplier, seed_step, time_step],
                                    "seed": seed,
                                    "cohort": "development" if seed in DEV else "heldout",
                                    "policy": policy,
                                    "churn": {m: a["physical_churn"] for m, a in arms.items()}})
    finally:
        y39.encode, y39.decode = origins

    raw_differs = any(churn[p]["moving_raw_numeric"] != churn[p]["reference_numeric"]
                      for p in POLICIES)
    if mismatches["moving_coordinate_aware"] == 0 and mismatches["moving_raw_numeric"] > 0 and raw_differs:
        classification = "AFFINE_FAMILY_TRANSFER"
    elif mismatches["moving_coordinate_aware"] < mismatches["moving_raw_numeric"]:
        classification = "PARTIAL_TRANSFER"
    else:
        classification = "NO_TRANSFER"
    return {"schema": "yggdrasil.y040-affine-frame-transfer.v1",
            "parent_head": "b368758c9f772046f2e67eed628dc3d5e4c6ae4d",
            "classification": classification,
            "development_seeds": DEV,
            "sealed_heldout_seeds": HELDOUT,
            "coordinate_families": FAMILIES,
            "heldout_assignment_mismatches": mismatches,
            "heldout_churn": churn,
            "all_records": records,
            "model_calls": 0,
            "claim_limit": "Synthetic coordinate metadata access under four new bijection families, not learned or metadata-free cognition"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
