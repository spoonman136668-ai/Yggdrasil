"""CASP02 source-free negative and evidence/cold-restore integrity tests."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

HERE = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/CAUSAL-AMALGAM'
sys.path.insert(0, str(HERE))
from capsule_memory_dev import digest
from casp02_compositional import CompositionalCapsules
from casp02_trial import run, PROTOCOL


def evidence(i):
    return hashlib.sha256(('CASP02-TEST-' + str(i)).encode()).hexdigest()


class CompositionalTests(unittest.TestCase):
    def test_local_capsules_are_independently_unchanged(self):
        m = CompositionalCapsules()
        for i in range(16):
            action = i % 2
            m.observe(evidence(i), (0, 0), action, action)
        original = tuple(m.predict((0, 0), a) for a in (0, 1))
        for i in range(16, 32):
            action = i % 2
            m.observe(evidence(i), (1, 0), action, 1 - action)
        self.assertEqual(original, tuple(m.predict((0, 0), a) for a in (0, 1)))

    def test_public_unseen_composition_not_oracle_context(self):
        m = CompositionalCapsules()
        for i in range(48):
            cue = ((i // 16) & 1, (i // 32) & 1)
            action = i % 2
            m.observe(evidence(i), cue, action, action ^ cue[0] ^ cue[1])
        self.assertEqual(len(m.local._cells), 3)
        self.assertLess(m.predict((1, 1), 0), 0.1)
        self.assertGreater(m.predict((1, 1), 1), 0.9)

    def test_exact_replay_and_tamper_negative(self):
        m = CompositionalCapsules()
        for i in range(30):
            a = i % 2
            m.observe(evidence(i), (0, 0), a, a)
        raw = m.checkpoint()
        self.assertEqual(raw, CompositionalCapsules.restore(raw, digest(raw)).checkpoint())
        self.assertFalse(m.observe(evidence(0), (0, 0), 0, 0))
        self.assertEqual(raw, m.checkpoint())
        modified = json.loads(raw)
        modified['shared_weights'][0] += 1
        from capsule_memory_dev import canonical
        bad = canonical(modified)
        with self.assertRaisesRegex(ValueError, 'TAMPER'):
            CompositionalCapsules.restore(bad, digest(bad))

    def test_frozen_comparison_against_strong_controls(self):
        result = run(json.loads(PROTOCOL.read_bytes()))
        self.assertEqual(len(result['rows']), 3)
        self.assertFalse(result['scientific_pass'])
        for row in result['rows']:
            self.assertEqual(row['fit_events'], 48)
            self.assertTrue(row['old_A_predictions_identical'])
            self.assertTrue(row['cold_checkpoint_exact'])
            self.assertEqual(row['retention_delta_brier'], 0.0)
            self.assertEqual(row['brier_same_mechanism_held_D']['exact_gf2'], 0)
            self.assertLess(row['brier_same_mechanism_held_D']['capsule02'],
                            row['brier_same_mechanism_held_D']['capsule01'])
            self.assertFalse(row['go'])


if __name__ == '__main__':
    unittest.main()
