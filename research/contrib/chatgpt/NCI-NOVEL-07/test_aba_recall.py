"""NCI07 tests use fabricated hand-typed engineering tuples, not trial seeds."""
from __future__ import annotations
import unittest
from aba_recall import (BoundedCausalRecall, ExactGridSwitchBayes,
                        EpisodicTwoWindowControl, WindowBetaControl)
from protocol_guard import AuditError, assert_paired_evidence


def row(action, outcome):
    return {"observation": 7, "action": action, "outcome": outcome}


# Repetitions are explicitly authored toy witnesses, not a scored source world.
A = [row(0, 1), row(1, 0)] * 12
B = [row(0, 0), row(1, 1)] * 12


class RecallEngineeringTests(unittest.TestCase):
    def test_unmarked_switch_and_cold_return(self):
        m = BoundedCausalRecall()
        for witness in A:
            m.observe(witness)
        old = [m.retained_predict(0, arm) for arm in (0, 1)]
        self.assertEqual(len(m.slots), 1)
        for witness in B:
            m.observe(witness)
        self.assertEqual(len(m.slots), 2)
        self.assertEqual(m.active, 1)
        self.assertGreater(m.transitions, 0)
        cold = BoundedCausalRecall.restore(m.snapshot())
        self.assertEqual([cold.retained_predict(0,a) for a in (0,1)], old)
        for witness in A:
            cold.observe(witness)
        self.assertEqual(cold.active, 0)
        self.assertGreaterEqual(cold.transitions, 2)
        self.assertEqual(len(cold.slots), 2)
        self.assertGreater(cold.predict(0, 7), cold.predict(1, 7))

    def test_source_leakage_rejected(self):
        for name in ('source', 'phase', 'source_id', 'reset', 'counterfactual'):
            with self.subTest(name=name), self.assertRaises(AuditError):
                BoundedCausalRecall().observe(dict(row(0, 1), **{name: 'A'}))

    def test_no_change_no_false_context(self):
        m = BoundedCausalRecall()
        for witness in A + A:
            m.observe(witness)
        self.assertEqual(len(m.slots), 1)
        self.assertEqual(m.transitions, 0)

    def test_cold_tamper_rejected(self):
        m = BoundedCausalRecall()
        m.observe(row(0, 1))
        corrupted = bytearray(m.snapshot())
        corrupted[-65] ^= 1
        with self.assertRaises(AuditError):
            BoundedCausalRecall.restore(bytes(corrupted))

    def test_empty_or_false_cold_snapshot_rejected(self):
        for bad in (b'', 'wrong', b'NCI07A1:{}:bad'):
            with self.subTest(bad=bad), self.assertRaises(AuditError):
                BoundedCausalRecall.restore(bad)

    def test_matched_public_tapes_controls(self):
        controls = {
            'candidate': BoundedCausalRecall(),
            'bayes': ExactGridSwitchBayes(),
            'window': WindowBetaControl(window=8),
            'full_history': WindowBetaControl(),
            'episodic': EpisodicTwoWindowControl(),
        }
        tape = A + B + A
        local = {name: [] for name in controls}
        for witness in tape:
            for name, model in controls.items():
                forecasts = [model.predict(i, witness['observation']) for i in (0,1)]
                self.assertTrue(all(0.0 <= x <= 1.0 for x in forecasts))
                self.assertIn(model.choose(witness['observation']), (None, 0, 1))
                model.observe(dict(witness))
                local[name].append(dict(witness))
        report = assert_paired_evidence(local, tuple(controls), max_witnesses=72)
        self.assertEqual(report['witnesses_per_arm'], 72)
        self.assertFalse(report['scientific_gain_verified'])
        self.assertEqual(controls['candidate'].active, 0)

    def test_bayes_is_normalized_and_public_only(self):
        b = ExactGridSwitchBayes()
        for x in A+B:
            b.observe(x)
            self.assertAlmostEqual(sum(b.posterior), 1.0)
        with self.assertRaises(AuditError):
            b.observe(dict(row(0, 1), phase='B'))

    def test_controls_not_untrained(self):
        for klass in (ExactGridSwitchBayes, EpisodicTwoWindowControl, WindowBetaControl):
            ctl = klass()
            before = ctl.predict(0, 7)
            for witness in A:
                ctl.observe(witness)
            self.assertNotEqual(before, ctl.predict(0, 7))

    def test_invalid_observations(self):
        m = BoundedCausalRecall()
        for bad in (True, 1.0, -1, 256, None):
            with self.subTest(bad=bad), self.assertRaises(AuditError):
                m.predict(0, bad)

    def test_checkpoint_cannot_claim_cryptographic_source_authentication(self):
        m = BoundedCausalRecall()
        data = m.snapshot()
        self.assertTrue(data.startswith(b'NCI07A1:'))
        self.assertEqual(m.snapshot(), BoundedCausalRecall.restore(data).snapshot())


if __name__ == '__main__':
    unittest.main()
