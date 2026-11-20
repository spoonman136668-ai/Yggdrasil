"""Gate25 preregistered source-free A→B→A retention gate and controls.

Tests existing trained-shadow interfaces only; no owner model or original source.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from hashlib import sha256
import unittest

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/CAUSAL-AMALGAM")
SPEC = spec_from_file_location("gate25_public_consequence", HERE /
                               "public_consequence_retention_gate.py")
GATE = module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class PublicConsequenceRetentionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = GATE.audit()

    def test_fixed_a_b_a_public_tape_and_opaque_identifiers(self):
        tape = GATE._tape()
        self.assertEqual(len(tape), 64)
        self.assertEqual([sum(p == phase for p, *_ in tape)
                          for phase in (0, 1, 2)], [16, 32, 16])
        for i, (phase, identifier, views, y) in enumerate(tape):
            self.assertEqual(
                identifier, sha256(f"gate25-event/{i}".encode()).hexdigest())
            self.assertEqual(views[0][0], views[1][0])
            self.assertEqual(views[0][0], 1)
            a, b = GATE.PRIOR._public_pair(views)
            self.assertEqual(y, (a ^ b) if phase == 1 else (a | b))
            self.assertNotIn("xor", identifier)
            self.assertNotIn("or", identifier)
        self.assertEqual({v[0][1:] + v[1][1:] for _, _, v, _ in tape},
                         set(GATE.PRIOR.PAIRS))

    def test_primary_frozen_accuracy_and_explicit_stronger_controls(self):
        p = self.audit["primary"]
        self.assertEqual(p["scores"]["gated"]["correct"], 60)
        self.assertEqual(p["scores"]["static_old"]["correct"], 56)
        self.assertEqual(p["scores"]["static_new"]["correct"], 56)
        self.assertEqual(p["scores"]["symbolic"]["correct"], 62)
        self.assertEqual(p["scores"]["last_public_label"]["correct"], 62)
        self.assertEqual(
            [s["gated"]["correct"] for s in p["phase_scores"]],
            [16, 30, 14])
        self.assertEqual(
            [s["static_old"]["correct"] for s in p["phase_scores"]],
            [16, 24, 16])
        self.assertEqual(
            [s["static_new"]["correct"] for s in p["phase_scores"]],
            [12, 32, 12])
        self.assertEqual(
            [s["symbolic"]["correct"] for s in p["phase_scores"]],
            [16, 31, 15])
        self.assertEqual(
            [s["last_public_label"]["correct"] for s in p["phase_scores"]],
            [16, 31, 15])
        self.assertGreater(
            p["scores"]["gated"]["brier"],
            p["scores"]["symbolic"]["brier"])

    def test_no_label_or_public_regime_gating_shortcut(self):
        p = self.audit["primary"]
        self.assertEqual(p["custody"]["switch_after_zero_based_event_indices"],
                         (23, 55))
        self.assertEqual(p["custody"]["active"], "old")
        self.assertEqual(
            [r["active"] for r in p["phase_custody"]],
            ["old", "new", "old"])
        self.assertEqual(
            [r["observed_event_count"] for r in p["phase_custody"]],
            [16, 48, 64])
        self.assertTrue(p["predictions_before_outcomes"])

    def test_no_change_negative_never_switches(self):
        n = self.audit["no_change_negative"]
        self.assertEqual(n["scores"]["gated"]["correct"], 64)
        self.assertEqual(n["scores"]["static_old"]["correct"], 64)
        self.assertEqual(n["custody"]["switch_after_zero_based_event_indices"],
                         ())
        self.assertEqual(n["custody"]["active"], "old")
        self.assertEqual(n["test_events"], 64)

    def test_single_noisy_contradiction_does_not_flip(self):
        n = self.audit["single_contradiction_negative"]
        self.assertEqual(n["scores"]["gated"]["correct"], 63)
        self.assertEqual(n["custody"]["switch_after_zero_based_event_indices"],
                         ())
        self.assertEqual(n["custody"]["active"], "old")
        with self.assertRaisesRegex(ValueError,
                                     "GATE25_BAD_OUTCOME_POSITION"):
            GATE._tape(("or", "or", "or"), lone_bad_at=30)

    def test_uninformative_pairs_never_vote_and_two_decisive_do(self):
        gate = GATE.PublicConsequenceGate(
            GATE._fit_expert("or"), GATE._fit_expert("xor"))
        # XOR/OR differ only at pair 11. The first 3 pairs are not evidence.
        for i, (phase, identifier, views, y) in enumerate(GATE._tape()):
            if i == 19:
                self.assertEqual(gate.active, "old")
                self.assertEqual(gate.votes, 0)
            if i == 23:
                self.assertEqual(gate.active, "old")
                self.assertEqual(gate.votes, 1)
            if i == 51:
                self.assertEqual(gate.active, "new")
                self.assertEqual(gate.votes, 0)
            if i == 55:
                self.assertEqual(gate.active, "new")
                self.assertEqual(gate.votes, 1)
            gate.observe(identifier, views, y)
        self.assertEqual(tuple(gate.switches), (23, 55))

    def test_duplicate_idempotence_and_conflicting_replay_rejected(self):
        gate = GATE.PublicConsequenceGate(
            GATE._fit_expert("or"), GATE._fit_expert("xor"))
        _, identifier, views, y = GATE._tape()[0]
        before = gate.predict(views)
        self.assertEqual(before, gate.predict(views))
        self.assertTrue(gate.observe(identifier, views, y))
        custody = gate.custody()
        self.assertFalse(gate.observe(identifier, views, y))
        self.assertEqual(gate.custody(), custody)
        with self.assertRaisesRegex(ValueError,
                                    "GATE25_CONFLICTING_REPLAY"):
            gate.observe(identifier, views, 1-y)
        self.assertEqual(gate.custody(), custody)
        with self.assertRaisesRegex(ValueError, "GATE25_EVENT_ID"):
            gate.observe("gate25/or/0/0/0", views, y)

    def test_no_privileged_fields_and_bounded_cold_replay(self):
        p = self.audit["primary"]
        self.assertTrue(p["old_weights_unchanged"])
        self.assertTrue(p["new_weights_unchanged"])
        self.assertTrue(p["replay_equal"])
        self.assertEqual(len(p["custody"]["public_ledger_sha256"]), 64)
        gate = GATE.PublicConsequenceGate(
            GATE._fit_expert("or"), GATE._fit_expert("xor"))
        for _, identifier, views, y in GATE._tape():
            gate.observe(identifier, views, y)
        with self.assertRaisesRegex(ValueError, "GATE25_MAX_EVENTS"):
            gate.observe(GATE._event_id(64),
                         ((1, 0), (1, 0)), 0)
        with self.assertRaisesRegex(ValueError, "GATE24_PUBLIC_PAIR"):
            gate.observe(GATE._event_id(65),
                         ((1, 0), (0, 0)), 0)
        with self.assertRaisesRegex(ValueError, "GATE25_PUBLIC_OUTCOME"):
            gate.observe(GATE._event_id(65),
                         ((1, 0), (1, 0)), "0")
        self.assertEqual(gate.custody(), p["custody"])

    def test_one_source_free_workflow_cannot_claim_scientific_acceptance(self):
        self.assertEqual(self.audit["schema"], GATE.SCHEMA)
        self.assertFalse(self.audit["owner_model_integrated"])
        self.assertFalse(self.audit["scientific_pass"])
        for run in (self.audit["primary"],
                    self.audit["no_change_negative"],
                    self.audit["single_contradiction_negative"]):
            self.assertEqual(run["train_rows_per_expert"], 16)
            self.assertTrue(run["replay_equal"])
            self.assertEqual(run["original_world_source_actions"], 0)
            self.assertEqual(run["canonical_checkpoint_updates"], 0)
            self.assertEqual(run["deployment"], "NONE")
            self.assertFalse(run["scientific_pass"])


if __name__ == "__main__":
    unittest.main()
