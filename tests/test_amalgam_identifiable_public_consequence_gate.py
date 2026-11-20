"""Gate26 source-free preregistered hard-disagreement retention gate tests.

Preserves Gate25 negative tests unchanged. A full regression will continue
to fail Gate25, which is deliberately NOT disabled or retroactively repaired.
"""
from hashlib import sha256
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import unittest

ROOT = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/CAUSAL-AMALGAM")
SPEC = spec_from_file_location(
    "gate26_identifiability", ROOT / "identifiable_public_consequence_gate.py")
GATE = module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class IdentifiablePublicConsequenceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = GATE.audit()

    def test_primary_frozen_64_public_consequences_and_equal_data_controls(self):
        primary = self.result["primary"]
        expected = {"gated": 60, "static_old": 56, "static_new": 56,
                    "symbolic": 62, "last_public_label": 62}
        self.assertEqual(
            {k: v["correct"] for k, v in primary["scores"].items()}, expected)
        self.assertEqual([phase["gated"]["correct"]
                          for phase in primary["phase_scores"]],
                         [16, 30, 14])
        self.assertGreater(
            primary["scores"]["symbolic"]["correct"],
            primary["scores"]["gated"]["correct"])
        self.assertGreater(
            primary["scores"]["last_public_label"]["correct"],
            primary["scores"]["gated"]["correct"])
        self.assertEqual(primary["training_public_events_per_expert"], 16)
        self.assertEqual(primary["evaluated_public_events"], 64)

    def test_exact_discriminating_witnesses_not_calibration_preferences(self):
        gate = GATE.IdentifiablePublicConsequenceGate(
            GATE.PRIOR._fit_expert("or"), GATE.PRIOR._fit_expert("xor"))
        decisive_indices = []
        for index, (_, identifier, views, y) in enumerate(GATE._fixture()):
            old_p, new_p = gate.pair_probabilities(views)
            before = (gate.active, gate.votes)
            if int(old_p > 0.5) == int(new_p > 0.5):
                self.assertNotEqual(GATE.PRIOR.PRIOR._public_pair(views), (1, 1))
            else:
                self.assertEqual(GATE.PRIOR.PRIOR._public_pair(views), (1, 1))
                decisive_indices.append(index)
            self.assertEqual(gate.predict(views), gate.predict(views))
            gate.observe(identifier, views, y)
            if index not in decisive_indices:
                self.assertEqual((gate.active, gate.votes), before)
        self.assertEqual(decisive_indices, list(range(3, 64, 4)))
        self.assertEqual(gate.discriminating, 16)
        self.assertEqual(gate.abstentions, 48)

    def test_frozen_switch_points_and_reverted_old_readout(self):
        c = self.result["primary"]["custody"]
        self.assertEqual(c["switch_after_zero_based_event_indices"], (23, 55))
        self.assertEqual(c["active"], "old")
        self.assertEqual(c["pending_votes"], 0)
        self.assertEqual(c["observed_event_count"], 64)
        self.assertEqual(c["discriminating_events"], 16)
        self.assertEqual(c["abstaining_events"], 48)

    def test_no_change_and_one_outlier_do_not_switch(self):
        clean = self.result["no_change_negative"]
        one = self.result["single_noise_negative"]
        self.assertEqual(clean["scores"]["gated"]["correct"], 64)
        self.assertEqual(one["scores"]["gated"]["correct"], 63)
        for run in (clean, one):
            self.assertEqual(
                run["custody"]["switch_after_zero_based_event_indices"], ())
            self.assertEqual(run["custody"]["active"], "old")

    def test_two_ambiguous_noise_events_force_false_switch(self):
        noise = self.result["double_noise_identifiability_limit"]
        self.assertEqual(noise["scores"]["gated"]["correct"], 60)
        self.assertEqual(
            noise["custody"]["switch_after_zero_based_event_indices"],
            (35, 43))
        self.assertEqual(noise["custody"]["active"], "old")
        self.assertFalse(noise["scientific_pass"])
        # Two identical public interventions cannot certify if the latent
        # cause is a true phase shift or adversarial/sensor noise.
        self.assertLess(noise["scores"]["gated"]["correct"], 64)

    def test_public_opaque_event_ids_never_encode_law_or_phase(self):
        rows = GATE._fixture()
        self.assertEqual(len(rows), 64)
        self.assertEqual(len({identifier for _, identifier, _, _ in rows}), 64)
        for index, (phase, identifier, views, y) in enumerate(rows):
            self.assertEqual(
                identifier, sha256(f"gate25-event/{index}".encode()).hexdigest())
            self.assertNotIn("xor", identifier)
            self.assertNotIn("or", identifier)
            self.assertNotIn(str(phase) + "/", identifier)
            self.assertEqual(views[0][0], 1)
            self.assertIn(y, (0, 1))

    def test_idempotent_conflicting_source_and_64_event_cap(self):
        gate = GATE.IdentifiablePublicConsequenceGate(
            GATE.PRIOR._fit_expert("or"), GATE.PRIOR._fit_expert("xor"))
        first = GATE._fixture()[0]
        _, identifier, views, y = first
        self.assertTrue(gate.observe(identifier, views, y))
        snapshot = gate.custody()
        self.assertFalse(gate.observe(identifier, views, y))
        self.assertEqual(gate.custody(), snapshot)
        with self.assertRaisesRegex(ValueError, "GATE26_CONFLICTING_REPLAY"):
            gate.observe(identifier, views, 1 - y)
        self.assertEqual(gate.custody(), snapshot)
        for _, ident, current_views, label in GATE._fixture()[1:]:
            gate.observe(ident, current_views, label)
        with self.assertRaisesRegex(ValueError, "GATE26_MAX_EVENTS"):
            gate.observe(GATE.PRIOR._event_id(64), ((1, 0), (1, 0)), 0)
        self.assertEqual(gate.custody()["observed_event_count"], 64)

    def test_source_free_cold_replay_and_existing_weights_unchanged(self):
        for key in ("primary", "no_change_negative",
                    "single_noise_negative", "double_noise_identifiability_limit"):
            receipt = self.result[key]
            self.assertTrue(receipt["predictions_before_outcomes"])
            self.assertTrue(receipt["cold_replay_exact"])
            self.assertTrue(receipt["old_model_weights_unchanged"])
            self.assertTrue(receipt["new_model_weights_unchanged"])
            self.assertEqual(receipt["canonical_checkpoint_mutations"], 0)
            self.assertEqual(receipt["original_source_actions"], 0)
            self.assertEqual(receipt["deployment"], "NONE")
            self.assertFalse(receipt["scientific_pass"])
            self.assertEqual(len(receipt["source_free_ledger_sha256"]), 64)

    def test_negative_inputs_and_single_new_classification_contract(self):
        with self.assertRaisesRegex(ValueError, "GATE26_CORRUPTION_INDICES"):
            GATE._fixture(corrupted=[31])
        for corrupted in ((31, 31), (30,), (35, 64)):
            with self.subTest(corrupted=corrupted):
                with self.assertRaisesRegex(ValueError, "GATE26_CORRUPTION_SCOPE"):
                    GATE._fixture(corrupted=corrupted)
        gate = GATE.IdentifiablePublicConsequenceGate(
            GATE.PRIOR._fit_expert("or"), GATE.PRIOR._fit_expert("xor"))
        with self.assertRaisesRegex(ValueError, "GATE25_PUBLIC_OUTCOME"):
            gate.observe(GATE.PRIOR._event_id(0), ((1, 1), (1, 1)), "0")
        with self.assertRaisesRegex(ValueError, "GATE24_PUBLIC_PAIR"):
            gate.observe(GATE.PRIOR._event_id(0), ((1, 1), (0, 1)), 0)
        self.assertEqual(gate.custody()["observed_event_count"], 0)

    def test_preserve_failed_gate25_and_no_new_scientific_admission(self):
        self.assertTrue(self.result["gate25_unchanged"])
        self.assertFalse(self.result["owner_model_integrated"])
        self.assertFalse(self.result["scientific_pass"])
        self.assertEqual(GATE.VOTES, 2)
        self.assertEqual(GATE.DISCRIMINATOR, 0.5)
        self.assertEqual(GATE.SCHEMA,
                         "yggdrasil.amalgam.identifiable-consequence-gate-dev.v1")


if __name__ == "__main__":
    unittest.main()
