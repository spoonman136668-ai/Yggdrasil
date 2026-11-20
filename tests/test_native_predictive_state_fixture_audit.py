"""CAP04 fixture audit: independent deterministic replay and tamper controls.

No registered DEV/pilot/primary seeds or scientific result can be admitted.
"""
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/YGG-CAP04"
spec = importlib.util.spec_from_file_location("cap04_fixture_audit", HERE / "fixture_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FixtureAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = audit.build_fixture_receipt("engineering-history-01")
        cls.parsed = json.loads(cls.raw.decode("ascii"))

    def test_source_replay_metric_clocks_and_fixed_windows(self):
        result = audit.audit_fixture_receipt(self.raw)
        self.assertEqual(result["classification"], "ENGINEERING_FIXTURE_ONLY")
        self.assertEqual(result["rows_verified"], 96)
        self.assertEqual(result["matched_controls"], 6)
        self.assertEqual(result["receipt_sha256"], digest(self.raw))
        self.assertEqual(set(self.parsed["phase_means"]), {"novel", "cold_return", "pooled"})
        self.assertEqual(len(self.parsed["rows"]), 96)
        self.assertEqual(len(self.parsed["rows"][0]["pre_transition"]), 7)
        for scores in self.parsed["phase_means"].values():
            self.assertTrue(all(0 <= x <= 1 for x in scores.values()))

    def mutate(self, fn):
        data = json.loads(self.raw)
        fn(data)
        with self.assertRaisesRegex(ValueError, "AUDIT_REJECTED"):
            audit.audit_fixture_receipt(canonical(data))

    def test_hidden_label_future_outcome_and_order_tampering_rejected(self):
        self.mutate(lambda x: x["rows"][3]["outcome"].update({"y": 1 - x["rows"][3]["outcome"]["y"]}))
        self.mutate(lambda x: x["rows"][4].update({"id": x["rows"][5]["id"]}))
        self.mutate(lambda x: x["rows"][4].update({"t": 8}))
        self.mutate(lambda x: x["rows"][4].update({"private_phase": "B"}))
        # Choose a known asymmetric action: reversing (0,0) or (1,1)
        # would be a no-op and would not test receipt tampering.
        self.assertNotEqual(self.parsed["rows"][2]["action"][0],
                            self.parsed["rows"][2]["action"][1])
        self.mutate(lambda x: x["rows"][2]["action"].reverse())

    def test_forecast_and_brier_forgery_rejected(self):
        arm = "predictive_state_split"
        self.mutate(lambda x: x["rows"][23]["pre_transition"].update(
            {arm: 0.9 if x["rows"][23]["pre_transition"][arm] < 0.5 else 0.1}))
        self.mutate(lambda x: x["rows"][23]["pre_reward"].update(
            {arm: 0.9 if x["rows"][23]["pre_reward"][arm] < 0.5 else 0.1}))
        self.mutate(lambda x: x["phase_means"]["pooled"].update(
            {arm: x["phase_means"]["pooled"][arm] + .01}))
        self.mutate(lambda x: x["rows"][18]["pre_state_sha256"].__setitem__(0, "0" * 64))

    def test_registered_first_use_refused(self):
        for source_id in (99917, 99931, 100017, 100031, 100117, 100131, 100151):
            with self.subTest(source_id=source_id), self.assertRaisesRegex(
                    ValueError, "FIRST_USE_FORBIDDEN"):
                audit.build_fixture_receipt(str(source_id))
        self.mutate(lambda x: x.update({"fixture_id": "99917"}))
        self.mutate(lambda x: x.update({"evidence_class": "SCIENTIFIC_PASS"}))

    def test_reproducible_history_measurement_never_claims_science(self):
        diagnostic = audit.engineering_diagnostic(
            "engineering-history-01", raw=self.raw)
        self.assertEqual(diagnostic["evidence_class"], "ENGINEERING_FIXTURE_ONLY")
        self.assertIs(diagnostic["scientific_pass"], False)
        self.assertEqual(diagnostic["registered_source_actions"], 0)
        self.assertEqual(diagnostic["rows"], 96)
        self.assertEqual(diagnostic["observed_previous_current_pairs"], 16)
        self.assertEqual(diagnostic["receipt_sha256"], digest(self.raw))
        for phase in ("novel", "cold_return", "pooled"):
            arm_scores = self.parsed["phase_means"][phase]
            value = diagnostic["phases"][phase]
            self.assertAlmostEqual(value["candidate_brier"],
                                   arm_scores["predictive_state_split"],
                                   places=8)
            best = min(arm_scores[name] for name in audit.ARMS)
            self.assertAlmostEqual(value["best_control_brier"], best,
                                   places=8)
            self.assertAlmostEqual(value["candidate_minus_best"],
                                   arm_scores["predictive_state_split"] - best,
                                   places=8)
        self.assertGreaterEqual(
            diagnostic["potentially_history_distinguishing_public_cells"], 1)
        with self.assertRaisesRegex(ValueError, "DIAGNOSTIC_SOURCE"):
            audit.engineering_diagnostic("engineering-history-02", raw=self.raw)

    def test_two_source_disjoint_fixture_replay(self):
        second = audit.build_fixture_receipt("engineering-history-02")
        output = audit.audit_fixture_receipt(second)
        self.assertEqual(output["rows_verified"], 96)
        self.assertNotEqual(output["receipt_sha256"], digest(self.raw))


if __name__ == "__main__":
    unittest.main()
