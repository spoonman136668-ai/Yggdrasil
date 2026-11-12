"""SELFTEST-only evidence-gated readout checks; no heldout-based fitting."""
import unittest
from dataclasses import replace

from source import build_world, Observation
from direct_writer import DirectWeightWriter
from evidence_selected_readout import (EvidenceSelectedReadout, select_readout,
                                      REPLAY_WRITES, run_selftest_selection)


class EvidenceSelectedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = build_world("SELFTEST", 9001, "identity")

    def train(self):
        m = EvidenceSelectedReadout()
        for row in self.world.phase_a:
            m.observe(row)
        m.seal_a()
        for row in self.world.phase_b:
            m.observe(row)
        m.finalize_b()
        return m

    def test_learned_gate_uses_only_observed_labels(self):
        m = self.train()
        self.assertIn(m.mode, ("slot", "unordered"))
        self.assertEqual(m.actions, 42)
        self.assertEqual(m.replay_writes, REPLAY_WRITES)
        self.assertEqual(m.selector_predictions, 12)
        self.assertEqual(m.selection["validation_examples"], 6)
        self.assertEqual(sum(m.selection["counts"]["slot"].values()), 6)
        self.assertEqual(sum(m.selection["counts"]["unordered"].values()), 6)

    def test_phase_a_is_identical_to_original_readout(self):
        a, b = EvidenceSelectedReadout(), DirectWeightWriter()
        for row in self.world.phase_a:
            a.observe(row)
            b.observe(row)
        for row in self.world.heldout_a[:12]:
            self.assertEqual(a.predict(row.before, row.acoustic_bits),
                             b.predict(row.before, row.acoustic_bits))
        self.assertEqual(a.actions, b.actions)

    def test_safe_gate_rejects_false_confidence(self):
        validation = [{"slot": "abstain", "unordered": "correct"} for _ in range(5)]
        validation.append({"slot": "correct", "unordered": "wrong"})
        mode, receipt = select_readout(validation)
        self.assertEqual(mode, "slot")
        self.assertEqual(receipt["counts"]["unordered"]["wrong"], 1)

    def test_safe_gate_requires_independent_advantage(self):
        rows = [{"slot": "abstain", "unordered": "correct"},
                {"slot": "abstain", "unordered": "abstain"}] * 3
        mode, receipt = select_readout(rows)
        self.assertEqual(mode, "unordered")
        self.assertEqual(receipt["gain"], 3)
        rows[0] = {"slot": "correct", "unordered": "correct"}
        rows[2] = {"slot": "correct", "unordered": "correct"}
        mode, _ = select_readout(rows)
        self.assertEqual(mode, "slot")
        with self.assertRaises(ValueError):
            select_readout(rows[:5])

    def test_snapshot_cold_restore_and_negative_tamper(self):
        m = self.train()
        snap = m.snapshot()
        restored = EvidenceSelectedReadout.restore(snap)
        self.assertEqual(restored.snapshot(), snap)
        for row in self.world.heldout_b[:10]:
            self.assertEqual(m.predict(row.before, row.acoustic_bits),
                             restored.predict(row.before, row.acoustic_bits))
        with self.assertRaises(ValueError):
            EvidenceSelectedReadout.restore(snap + " ")
        with self.assertRaises(ValueError):
            EvidenceSelectedReadout.restore(snap[:-1] + "x")

    def test_phase_caps_do_not_expose_more_actions(self):
        m = EvidenceSelectedReadout()
        with self.assertRaises(ValueError):
            m.seal_a()
        for row in self.world.phase_a:
            m.observe(row)
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_a[0])
        m.seal_a()
        with self.assertRaises(ValueError):
            m.finalize_b()
        for row in self.world.phase_b:
            m.observe(row)
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_b[0])
        m.finalize_b()
        with self.assertRaises(ValueError):
            m.observe(self.world.phase_b[0])

    def test_selftest_receipts_and_registered_cohort_guard(self):
        r = run_selftest_selection(self.world)
        self.assertEqual(r["unique_environment_actions"], 42)
        self.assertEqual(r["replay_writes"], 246)
        self.assertTrue(r["cold_restore_parity"])
        self.assertEqual(r["gradient_steps"], 0)
        self.assertEqual(r["phase_a"]["total"], 60)
        self.assertEqual(r["phase_b"]["total"], 90)
        with self.assertRaises(PermissionError):
            run_selftest_selection(replace(self.world, cohort="PRIMARY"))


if __name__ == "__main__":
    unittest.main()
