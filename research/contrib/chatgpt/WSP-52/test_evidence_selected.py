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


    def test_six_condition_fixture_receipts_no_threshold_tuning(self):
        """Report every pre-existing fixture condition, including negative outcomes.

        Nothing in this test chooses parameter settings after reading a score.
        The source worlds are SELFTEST and must not be treated as a valid PRIMARY.
        """
        import json
        from direct_writer import DirectWeightWriter
        from order_invariant_ablation import OrderInvariantReadout
        from fixture_harness import learn_observations, score_observations
        rows = []
        for seed in (9001, 9002):
            for encoding in ("identity", "permuted", "rotated"):
                world = build_world("SELFTEST", seed, encoding)
                selected = run_selftest_selection(world)
                fixed = {}
                for label, cls in (("slot", DirectWeightWriter),
                                   ("explicit_invariant", OrderInvariantReadout)):
                    model = cls()
                    learn_observations(model, world.phase_a)
                    a = score_observations(model, world.heldout_a)
                    learn_observations(model, world.phase_b)
                    b = score_observations(model, world.heldout_b)
                    retention = score_observations(model, world.heldout_a)
                    fixed[label] = {
                        "a_correct": a.correct, "b_correct": b.correct,
                        "b_wrong_confident": b.wrong_confident,
                        "retained_a_correct": retention.correct,
                        "retained_a_wrong_confident": retention.wrong_confident,
                    }
                self.assertEqual(selected["unique_environment_actions"], 42)
                self.assertEqual(selected["replay_writes"], 246)
                rows.append({
                    "seed": seed, "encoding": encoding, "selected": selected["selected"],
                    "selected_a_correct": selected["phase_a"]["correct"],
                    "selected_b_correct": selected["phase_b"]["correct"],
                    "selected_b_wrong_confident": selected["phase_b"]["wrong_confident"],
                    "selected_retained_a_correct": selected["retained_a"]["correct"],
                    "selected_retained_a_wrong_confident": selected["retained_a"]["wrong_confident"],
                    "gain": selected["selector"]["gain"],
                    "loss": selected["selector"]["loss"], "baseline": fixed,
                    "capacity_bits": selected["total_persistent_bits"],
                })
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(r["selected_b_correct"] + r["selected_b_wrong_confident"]
                             for r in rows) <= 540, True)
        # Fixture data is emitted into repository CI logs, NOT to an external library.
        print("WSP52_EVIDENCE_SELECTION_SELFTEST " + json.dumps(
            rows, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
