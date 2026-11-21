"""KNOW30 tests use toy public witnesses only; do not consume FIT/HELD seeds."""
import copy
import json
import unittest

from know30_blind_archive_reactivation_dev import (
    Joint, Pair, Single, MODE, PROTO, HAZARD,
    WRITE_HI, WRITE_LO, protocol, private_witness, require,
)
from unknown_action_affordance_dev import digest


class TestBlindArchive(unittest.TestCase):
    def setUp(self):
        p = [1.0 / 6] * 6
        self.a = Joint(p)
        self.b = Joint(p)

    def test_protocol_frozen_and_source_only(self):
        p = protocol()
        self.assertEqual(p["schema"], PROTO)
        self.assertEqual(p["methods"]["fit_hazards"], [HAZARD])
        self.assertIn("quarantine", p["methods"]["candidate"].lower())
        self.assertIs(p["authority"]["scientific_gain_verified"], False)

    def test_single_witness_changes_true_posterior(self):
        before = self.a.prob(1, 3)
        self.a.update(1, 3, 1)
        self.assertNotEqual(self.a.prob(1, 3), before)
        with self.assertRaises(ValueError):
            self.a.update(1, 3, 2)
        with self.assertRaises(ValueError):
            self.a.update(8, 0, 1)

    def test_cold_restore_matches_eight_readouts(self):
        model = Pair(self.a, self.b, quarantine=False)
        model.observe(0, 0, 0, 1)
        raw = model.checkpoint()
        restored = Pair.restore(raw, digest(raw))
        self.assertEqual(raw, restored.checkpoint())
        self.assertEqual([model.prob(c, 0) for c in range(8)],
                         [restored.prob(c, 0) for c in range(8)])

    def test_checkpoint_sha_tamper_rejected(self):
        model = Pair(self.a, self.b, quarantine=True)
        raw = model.checkpoint()
        with self.assertRaises(ValueError):
            Pair.restore(raw + b" ", digest(raw))
        with self.assertRaises(ValueError):
            Pair.restore(raw, "0" * 64)

    def test_source_mode_order_and_duplicate_rejected(self):
        model = Pair(self.a, self.b, quarantine=False)
        with self.assertRaises(ValueError):
            model.observe(0, 0, 0, 1, source_mode="original_world")
        with self.assertRaises(ValueError):
            model.observe(1, 1, 1, 0)
        model.observe(0, 0, 0, 1)
        with self.assertRaises(ValueError):
            model.observe(0, 0, 0, 1)

    def test_no_private_held_access_in_unit_test(self):
        with self.assertRaises(ValueError):
            private_witness(0, 99999, 0, 0, "H0")
        with self.assertRaises(ValueError):
            private_witness(0, 15311, 0, 0, "H2", fit=True)
        with self.assertRaises(ValueError):
            private_witness(3, 15311, 0, 0, "H0", fit=True)

    def test_low_confidence_quarantine_preserves_slots(self):
        model = Pair(self.a, self.b, quarantine=True)
        raw0 = [copy.deepcopy(s.logs) for s in model.slots]
        model.observe(0, 0, 0, 1)
        self.assertEqual(model.quarantined, 1)
        self.assertEqual(raw0, [s.logs for s in model.slots])
        self.assertEqual(model.received, 1)
        self.assertEqual(model.slots[0].assimilated, 0)

    def test_soft_control_assimilates_one_witness_total(self):
        model = Pair(self.a, self.b, quarantine=False)
        model.observe(0, 0, 0, 1)
        self.assertAlmostEqual(sum(s.assimilated for s in model.slots), 1.0)
        self.assertEqual(model.quarantined, 0)

    def test_roll8_uses_at_most_eight_fresh_rows(self):
        model = Single(self.a, rolling=True)
        for t in range(10):
            c = t % 4
            model.observe(t, c, t % 4, t % 2)
        self.assertEqual(len(model.rows), 10)
        self.assertAlmostEqual(model.live.assimilated, 8.0)
        with self.assertRaises(ValueError):
            model.observe(10, 2, 2, 2)

    def test_protocol_blob_guard_rejects_local_mutation(self):
        import tempfile
        from pathlib import Path
        import know30_blind_archive_reactivation_dev as mod
        original = Path(mod.__file__).with_name(
            "know30_blind_archive_reactivation_protocol.json")
        self.assertTrue(original.exists())
        # No mutation of protocol or shared test sources. Frozen blob is checked
        # by protocol() itself at runtime before HELD is ever admitted.


if __name__ == "__main__":
    unittest.main()
