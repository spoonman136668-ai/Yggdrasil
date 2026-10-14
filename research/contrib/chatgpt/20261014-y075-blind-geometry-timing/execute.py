"""Y075 preregistered onset-timing falsification of persistent geometry blind spot."""
import importlib.util
import json
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent / "20261014-y074-novel-affine-transfer" / "execute.py"
spec = importlib.util.spec_from_file_location("y074_pinned", PARENT)
assert spec and spec.loader
y074 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y074)

y070 = y074.y073.y072.y071.y070
m = y070.m
DEV = tuple(range(9320, 9328))
HELDOUT = tuple(range(9392, 9408))
FAMILIES = y074.FAMILIES
PAIRS = ((4, 11), (5, 12))
REGIMES = (("steady", None), ("onset1", 1), ("onset4", 4))
POLICIES = y070.POLICIES
ARMS = y070.ARMS

def run():
    groups = {}
    records = []
    development_checks = 0
    try:
        for pair in PAIRS:
            for regime, onset in REGIMES:
                case_key = f"{pair[0]}_{pair[1]}:{regime}"
                integrity = {"anchor_pair_checks": 0}
                m.y58.install_transposition(onset, pair, integrity)
                totals = {arm: {
                    "mismatch_episodes": 0, "pre_detection_mismatch_episodes": 0,
                    "post_detection_mismatch_episodes": 0,
                    "illegal_physical_assignments": 0, "public_reads": 0
                } for arm in ARMS}
                detections = {arm: 0 for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV + HELDOUT:
                        for policy in POLICIES:
                            truth = m.y50.evaluate(
                                seed, policy, "canonical", "continue", family)
                            candidates = {
                                arm: m.candidate(seed, family, policy, arm)
                                for arm in ARMS
                            }
                            if seed in DEV:
                                development_checks += 1
                                continue
                            case = {"seed": seed, "pair": pair,
                                    "regime": regime, "family": family,
                                    "policy": policy, "arms": {}}
                            for arm, trial in candidates.items():
                                first = next(
                                    (r["public_detected_swap_first_episode"]
                                     for r in reversed(trial["rows"])
                                     if r["public_detected_swap_first_episode"] is not None),
                                    None)
                                detections[arm] += int(first is not None)
                                observed = {
                                    "first_detection": first,
                                    "mismatch_episodes": 0,
                                    "pre_detection_mismatch_episodes": 0,
                                    "post_detection_mismatch_episodes": 0,
                                    "illegal_physical_assignments": 0,
                                    "public_reads": trial["public_scalar_reads"]
                                }
                                assert trial["public_scalar_reads"] == 10
                                for reference, row in zip(truth["rows"], trial["rows"]):
                                    assert row["episode"] == reference["episode"]
                                    assert row["candidate_retained_cache_occupancy"] <= 9
                                    assert len(row["physical_assignment_evaluator_only"]) == 7
                                    wrong = sum(
                                        reference["physical_assignment"][k] !=
                                        row["physical_assignment_evaluator_only"][k]
                                        for k in reference["physical_assignment"])
                                    mismatch = int(wrong > 0)
                                    observed["mismatch_episodes"] += mismatch
                                    observed["illegal_physical_assignments"] += row["illegal_physical_assignments"]
                                    if first is not None and row["episode"] >= first:
                                        observed["post_detection_mismatch_episodes"] += mismatch
                                    else:
                                        observed["pre_detection_mismatch_episodes"] += mismatch
                                assert observed["illegal_physical_assignments"] == 0
                                case["arms"][arm] = observed
                                for key in totals[arm]:
                                    totals[arm][key] += observed[key]
                            records.append(case)
                assert all(
                    totals[a]["public_reads"] == 4*16*3*10 and
                    totals[a]["illegal_physical_assignments"] == 0
                    for a in ARMS)
                groups[case_key] = {
                    "totals": totals, "detections": detections,
                    "source_anchor_checks": integrity["anchor_pair_checks"]
                }
                m.y49.restore_environment()
    finally:
        m.y49.restore_environment()
    assert len(records) == 2*3*4*16*3
    assert development_checks == 2*3*4*8*3
    assert all(groups[f"{p[0]}_{p[1]}:steady"]["totals"][a]["mismatch_episodes"] == 0
               for p in PAIRS for a in ARMS)
    comparisons = []
    for pair in PAIRS:
        for regime in ("onset1", "onset4"):
            key = f"{pair[0]}_{pair[1]}:{regime}"
            totals = groups[key]["totals"]
            baseline = totals["dual_sentinel_detect_only"]["post_detection_mismatch_episodes"]
            corrected = totals["dual_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
            original_total = totals["original_rotating_detect_only"]["mismatch_episodes"]
            corrected_total = totals["dual_sentinel_decoder_corrected"]["mismatch_episodes"]
            detected = groups[key]["detections"]["dual_sentinel_decoder_corrected"]
            comparisons.append({
                "case": key, "detections": detected,
                "uncorrected_post": baseline, "corrected_post": corrected,
                "original_total": original_total, "corrected_total": corrected_total,
                "post_gain": None if baseline == 0 else 1-corrected/baseline,
                "strict": baseline > 0 and corrected <= .5*baseline and corrected_total < original_total,
                "partial_safe": baseline > 0 and corrected <= .8*baseline and
                                corrected_total <= original_total
            })
    by_case = {c["case"]: c for c in comparisons}
    positive_control = by_case["4_11:onset1"]
    blind_early = by_case["5_12:onset1"]
    blind_later = by_case["5_12:onset4"]
    if positive_control["detections"] == 0:
        label = "POSITIVE_CONTROL_FAILED"
    elif blind_early["detections"] == 0 and blind_later["detections"] == 0:
        label = "PERSISTENT_SENSOR_BLIND_SPOT"
    elif blind_later["detections"] > 0 and blind_later["partial_safe"]:
        label = "DELAYED_ONSET_SAFE_RECOVERY"
    elif blind_later["detections"] > 0:
        label = "DETECTION_WITHOUT_SAFE_RECOVERY"
    else:
        label = "MIXED_SENSOR_VISIBILITY"
    return {
        "schema": "yggdrasil.y075-sensor-topology-vs-onset.v1",
        "parent_head": "92ff8efb2489cf2e986562d6f51155387dac957e",
        "classification": label, "development_seeds": DEV,
        "sealed_heldout_seeds": HELDOUT, "families": FAMILIES,
        "pairs": PAIRS, "regimes": REGIMES, "comparisons": comparisons,
        "groups": groups, "complete_heldout_records": records,
        "development_checks": development_checks,
        "public_scalar_reads_per_trial": 10, "active": 7, "retained_limit": 9,
        "model_calls": 0, "accepted_ref_mutation": False,
        "claim_limit": "Synthetic bounded matching sensor onset visibility, not RSI or production."
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
