"""Y076 frozen sensor address reallocation under unchanged ten-read budget.

Preregistered paired arms within one first-use experiment: original rotating,
unchanged dual-sentinel, and alternative dual-sentinel using addresses (4,5).
The true transposition is evaluator-only; the sampling plan is identical for
both experimental swap pairs and does not inspect trial truth.
"""
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
DEV = tuple(range(9536, 9544))
HELDOUT = tuple(range(9568, 9584))
PAIRS = ((4, 11), (5, 12))
FAMILIES = y074.FAMILIES
REGIMES = (("steady", None), ("onset1", 1))
POLICIES = ("matched_sham", "full", "quorum2")
ARMS = ("original_rotating_detect_only",
        "dual_sentinel_detect_only", "dual_sentinel_decoder_corrected",
        "new_sentinel_detect_only", "new_sentinel_decoder_corrected")

def new_public_samples(seed, family):
    observations = {}
    for episode in (0, 1, 3, 5, 7):
        addresses = (4, 5) if episode in (5, 7) else (0, 1)
        observations[episode] = {
            str(cell): m.y64.y46.coordinate(cell, seed, episode, family, "late_shock")
            for cell in addresses
        }
    assert sum(len(v) for v in observations.values()) == 10
    return observations

def candidate(seed, family, policy, arm):
    if not arm.startswith("new_"):
        return m.candidate(seed, family, policy, arm)
    original = m.y64.dual_public_samples
    try:
        m.y64.dual_public_samples = new_public_samples
        underlying = ("dual_sentinel_decoder_corrected" if arm.endswith("decoder_corrected")
                      else "dual_sentinel_detect_only")
        return m.candidate(seed, family, policy, underlying)
    finally:
        m.y64.dual_public_samples = original

def run():
    groups = {}
    records = []
    dev_structural_checks = 0
    original_sampler = m.y64.dual_public_samples
    try:
        for pair in PAIRS:
            for name, onset in REGIMES:
                integrity = {"anchor_pair_checks": 0}
                m.y58.install_transposition(onset, pair, integrity)
                key = f"{pair[0]}_{pair[1]}:{name}"
                totals = {arm: {"mismatch_episodes": 0, "pre_detection_mismatch_episodes": 0,
                                "post_detection_mismatch_episodes": 0, "wrong_assignments": 0,
                                "illegal_physical_assignments": 0, "matching_search_calls": 0,
                                "candidate_retained_writes": 0, "public_reads": 0}
                          for arm in ARMS}
                detections = {arm: 0 for arm in ARMS}
                for family in FAMILIES:
                    for seed in DEV + HELDOUT:
                        for policy in POLICIES:
                            truth = m.y50.evaluate(seed, policy, "canonical", "continue", family)
                            trials = {arm: candidate(seed, family, policy, arm) for arm in ARMS}
                            if seed in DEV:
                                dev_structural_checks += 1
                                continue
                            row = {"seed": seed, "pair": pair, "regime": name, "family": family,
                                   "policy": policy, "arms": {}}
                            for arm, trial in trials.items():
                                first = next((r["public_detected_swap_first_episode"]
                                              for r in reversed(trial["rows"])
                                              if r["public_detected_swap_first_episode"] is not None), None)
                                detections[arm] += int(first is not None)
                                observed = {"first_detection": first,
                                            "mismatch_episodes": 0,
                                            "pre_detection_mismatch_episodes": 0,
                                            "post_detection_mismatch_episodes": 0,
                                            "wrong_assignments": 0,
                                            "illegal_physical_assignments": 0,
                                            "matching_search_calls": 0,
                                            "candidate_retained_writes": 0}
                                for canonical, predicted in zip(truth["rows"], trial["rows"]):
                                    assert canonical["episode"] == predicted["episode"]
                                    wrong = sum(canonical["physical_assignment"][k] !=
                                                predicted["physical_assignment_evaluator_only"][k]
                                                for k in canonical["physical_assignment"])
                                    mismatch = int(wrong > 0)
                                    observed["mismatch_episodes"] += mismatch
                                    observed["wrong_assignments"] += wrong
                                    observed["illegal_physical_assignments"] += predicted["illegal_physical_assignments"]
                                    observed["matching_search_calls"] += predicted["matching_search_calls"]
                                    observed["candidate_retained_writes"] += predicted["candidate_retained_writes"]
                                    assert predicted["candidate_retained_cache_occupancy"] <= 9
                                    assert len(predicted["physical_assignment_evaluator_only"]) == 7
                                    if first is not None and predicted["episode"] >= first:
                                        observed["post_detection_mismatch_episodes"] += mismatch
                                    else:
                                        observed["pre_detection_mismatch_episodes"] += mismatch
                                assert observed["illegal_physical_assignments"] == 0
                                row["arms"][arm] = observed
                                for field in totals[arm]:
                                    totals[arm][field] += 10 if field == "public_reads" else observed[field]
                            records.append(row)
                assert all(v["public_reads"] == 4*16*3*10 and
                           v["illegal_physical_assignments"] == 0 for v in totals.values())
                groups[key] = {"totals": totals, "detections": detections,
                               "source_anchor_checks": integrity["anchor_pair_checks"]}
                m.y49.restore_environment()
    finally:
        m.y64.dual_public_samples = original_sampler
        m.y49.restore_environment()
    assert len(records) == 2*2*4*16*3
    assert dev_structural_checks == 2*2*4*8*3
    assert all(groups[f"{a}_{b}:steady"]["totals"][arm]["mismatch_episodes"] == 0
               for a, b in PAIRS for arm in ARMS)
    comparisons = []
    for a, b in PAIRS:
        result = groups[f"{a}_{b}:onset1"]
        t, d = result["totals"], result["detections"]
        old_corrected = t["dual_sentinel_decoder_corrected"]["mismatch_episodes"]
        new_uncorrected = t["new_sentinel_detect_only"]["post_detection_mismatch_episodes"]
        new_corrected = t["new_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
        new_total = t["new_sentinel_decoder_corrected"]["mismatch_episodes"]
        original_total = t["original_rotating_detect_only"]["mismatch_episodes"]
        post_gain = None if new_uncorrected == 0 else 1 - new_corrected / new_uncorrected
        comparisons.append({
            "pair": (a, b),
            "old_detected": d["dual_sentinel_detect_only"],
            "new_detected": d["new_sentinel_detect_only"],
            "uncorrected_post": new_uncorrected, "corrected_post": new_corrected,
            "post_gain": post_gain, "old_total": old_corrected,
            "new_total": new_total, "original_total": original_total,
            "correction_safe": new_uncorrected > 0 and new_corrected <= .8*new_uncorrected
                               and new_total < original_total
        })
    p411, p512 = comparisons
    rescued = p512["old_detected"] == 0 and p512["new_detected"] == 192
    corrected = rescued and p512["correction_safe"]
    retained_411 = p411["new_total"] <= p411["old_total"]
    if corrected and retained_411:
        classification = "BLINDSPOT_DETECTED_AND_CORRECTED_WITHOUT_REGRESSION"
    elif corrected:
        classification = "BLINDSPOT_CORRECTED_WITH_PAIR411_TRADEOFF"
    elif rescued:
        classification = "DETECTION_RESTORED_BUT_CORRECTION_UNPROVEN"
    elif p512["new_detected"] > p512["old_detected"]:
        classification = "PARTIAL_DETECTION_GAIN"
    else:
        classification = "NO_SENSOR_COVERAGE_GAIN"
    return {"schema": "yggdrasil.y076-sensor-address-budget-reallocation.v1",
            "parent_head": "5e20c3ef2d0eded5435599a2a826664e08d4b9e9",
            "classification": classification, "development_seeds": DEV,
            "sealed_heldout_seeds": HELDOUT, "pairs": PAIRS, "families": FAMILIES,
            "regimes": [r for r, _ in REGIMES], "policies": POLICIES,
            "new_late_sensor_addresses": (4, 5), "legacy_late_sensor_addresses": (2, 4),
            "per_trial_public_scalar_reads": 10, "active": 7, "retained_limit": 9,
            "comparisons": comparisons, "groups": groups, "complete_heldout_records": records,
            "development_structural_checks": dev_structural_checks, "model_calls": 0,
            "accepted_ref_mutation": False,
            "claim_limit": "Synthetic no-oracle ten-read sensor reallocation and fixed causal decoder, not RSI."}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
