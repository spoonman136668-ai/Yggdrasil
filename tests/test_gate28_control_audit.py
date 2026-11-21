"""Independent Gate28 score audit must reject evidence substitution."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import control_audit as a


def cases():
    out = []
    for i, cohort in enumerate(a.COHORTS):
        scores = {}
        for arm in a.ARMS:
            full = arm == a.REFERENCE
            held = 0.28 if cohort == "independent_noise" else (
                0.18 if full else 0.2)
            full_brier = 0.28 if cohort == "independent_noise" else 0.18
            scores[arm] = {
                "equal_action_held_brier": held,
                "prequential_brier": 0.23,
                "selected_held_reward": 15,
                "cpu_ms_accumulated": 9.3,
                "checkpoint_bytes": 24000 if full else 2300,
                "peak_rule_work": 11424 if full else 2400,
                "delta_brier_vs_full": round(full_brier - held, 9)}
        out.append({
            "status": "G28_EQUAL_EXPOSURE_CONTROL_DIAGNOSTIC_ONLY",
            "scientific_primary_scored": False, "original_world_first_use": False,
            "independent_reproduction": False,
            "full_reference_is_unconstrained": True,
            "strongest_matched_control_adequacy": "UNVERIFIED",
            "seed": 900071 + i, "cohort": cohort, "models": list(a.ARMS),
            "phases": {
                "A": {"public_exposures": 96,
                      "public_exposure_sha256": "a" * 64},
                "B": {"public_exposures": 64,
                      "public_exposure_sha256": "b" * 64,
                      "scores": copy.deepcopy(scores)},
                "R": {"public_exposures": 64,
                      "public_exposure_sha256": "c" * 64,
                      "scores": copy.deepcopy(scores)}}})
    return out


class TestGate28IndependentAudit(unittest.TestCase):
    def test_diagnostic_only_with_noise_negative_alert(self):
        got = a.audit(cases())
        self.assertEqual(got["seed_count"], 3)
        self.assertEqual(got["noise_diagnostic_flag"],
                         "WARNING_EXCEEDS_0_02")
        self.assertEqual(len(got["diagnostic_noise_threshold_exceeders"]), 7)
        self.assertEqual(got["classification"],
                         "NO_SCIENTIFIC_FIRST_USE_OR_PROMOTION")
        self.assertEqual(got["stationary_spurious_rewire_fraction"],
                         "NOT_REPORTED_BY_RUNNER")
        self.assertFalse(got["scientific_gain_verified"])

    def test_primary_seed_and_flags_fail_closed(self):
        for field, value in [
                ("seed", 501000), ("seed", True),
                ("scientific_primary_scored", True),
                ("original_world_first_use", True),
                ("independent_reproduction", True),
                ("strongest_matched_control_adequacy", "PASS")]:
            rows = cases()
            rows[0][field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(ValueError,
                                            "G28_AUDIT_FAIL_CLOSED"):
                    a.audit(rows)

    def test_forged_data_cannot_pass(self):
        modifications = [
            lambda x: x.pop("B"),
            lambda x: x["B"].update(public_exposures=65),
            lambda x: x["B"].update(public_exposure_sha256="x" * 64),
            lambda x: x["R"]["scores"]["fixed"].update(
                equal_action_held_brier=2),
            lambda x: x["R"]["scores"]["fixed"].update(
                peak_rule_work=8193),
            lambda x: x["R"]["scores"]["full_reference_reward"].update(
                checkpoint_bytes=8000),
            lambda x: x["R"]["scores"]["fixed"].update(
                delta_brier_vs_full=0.9),
        ]
        for mutation in modifications:
            rows = cases()
            mutation(rows[0]["phases"])
            with self.subTest(mutation=str(mutation)):
                with self.assertRaisesRegex(ValueError,
                                            "G28_AUDIT_FAIL_CLOSED"):
                    a.audit(rows)

    def test_duplicate_cohort_and_seed_refused(self):
        rows = cases()
        rows[1]["cohort"] = rows[0]["cohort"]
        with self.assertRaisesRegex(ValueError, "COHORT_DUPLICATION"):
            a.audit(rows)
        rows = cases()
        rows[1]["seed"] = rows[0]["seed"]
        with self.assertRaisesRegex(ValueError, "REUSED_WORLD_SEED"):
            a.audit(rows)

    def test_small_sample_cannot_claim_significance(self):
        z = a.audit(cases())
        self.assertEqual(z["paired_confidence_interval"],
                         "NOT_ESTIMABLE_FROM_ONE_SHIFTED_WORLD")
        self.assertEqual(z["matched_control_adequacy"], "UNVERIFIED")
        self.assertEqual(z["per_arm_forced_exposure_hash_parity"],
                         "NOT_PROVEN_BY_THIS_AUDIT")
