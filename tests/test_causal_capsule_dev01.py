"""Source-free, exact replay and negative controls for CASP-01."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/CAUSAL-AMALGAM'
sys.path.insert(0, str(ROOT))
from capsule_memory_dev import CapsuleMemory, digest
from capsule_dev01_trial import run_trial


def eid(i):
    return hashlib.sha256(('CASP01-TEST-' + str(i)).encode()).hexdigest()


class CapsuleDevelopmentTests(unittest.TestCase):
    def test_evidence_idempotent_conflict_and_custody(self):
        m = CapsuleMemory(max_capsules=2, max_events=2)
        self.assertTrue(m.observe(eid(1), (0, 0), 0, 0))
        baseline = m.checkpoint()
        self.assertFalse(m.observe(eid(1), (0, 0), 0, 0))
        self.assertEqual(baseline, m.checkpoint())
        with self.assertRaisesRegex(ValueError, 'CONFLICTING_REPLAY'):
            m.observe(eid(1), (0, 0), 0, 1)
        self.assertEqual(baseline, m.checkpoint())
        m.observe(eid(2), (1, 0), 0, 1)
        full = m.checkpoint()
        with self.assertRaisesRegex(ValueError, 'EVENT_CAPACITY'):
            m.observe(eid(3), (1, 1), 0, 1)
        self.assertEqual(full, m.checkpoint())

    def test_unseen_abstain_and_locality(self):
        m = CapsuleMemory(max_capsules=2)
        self.assertEqual(m.predict((1, 1), 0), 1 / 2)
        for i in range(24):
            a = i % 2
            m.observe(eid(i), (0, 0), a, a)
        old = tuple(m.predict((0, 0), a) for a in (0, 1))
        for i in range(24, 48):
            a = i % 2
            m.observe(eid(i), (1, 0), a, 1 - a)
        self.assertEqual(old, tuple(m.predict((0, 0), a) for a in (0, 1)))
        self.assertEqual(m.info()['capsules'], 2)
        full = m.checkpoint()
        with self.assertRaisesRegex(ValueError, 'CAPSULE_CAPACITY'):
            m.observe(eid(99), (0, 1), 0, 0)
        self.assertEqual(full, m.checkpoint())

    def test_exact_cold_restore_and_reject_tamper(self):
        m = CapsuleMemory()
        for i in range(16):
            a = i % 2
            m.observe(eid(i), (0, 0), a, a)
        before = m.checkpoint()
        cold = CapsuleMemory.restore(before, digest(before))
        self.assertEqual(before, cold.checkpoint())
        with self.assertRaisesRegex(ValueError, 'CHECKPOINT_PIN'):
            CapsuleMemory.restore(before + b' ', digest(before))
        doc = json.loads(before)
        doc['cells'][0][-1] += 1
        raw = json.dumps(doc, sort_keys=True, separators=(',', ':')).encode()
        with self.assertRaisesRegex(ValueError, 'TAMPERED'):
            CapsuleMemory.restore(raw, digest(raw))

    def test_bounded_local_action_exception_preserves_other_capsule(self):
        m = CapsuleMemory(max_repairs=1)
        for i in range(32):
            a = i % 2
            m.observe(eid(i), (0, 0), a, a)
        for i in range(32, 48):
            a = i % 2
            m.observe(eid(i), (1, 0), a, 1 - a)
        a_prior = tuple(m.predict((1, 0), x) for x in (0, 1))
        unaffected_action = m.predict((0, 0), 0)
        for i in range(48, 51):
            m.observe(eid(i), (0, 0), 1, 0)
        self.assertEqual(m.info()['repairs'], 1)
        self.assertEqual(a_prior, tuple(m.predict((1, 0), x) for x in (0, 1)))
        self.assertEqual(unaffected_action, m.predict((0, 0), 0))
        self.assertEqual(m.checkpoint(), CapsuleMemory.restore(m.checkpoint(), digest(m.checkpoint())).checkpoint())

    def test_frozen_three_seed_run_and_controls(self):
        plan = json.loads((ROOT / 'capsule_dev01_protocol.json').read_text())
        r = run_trial(plan)
        self.assertEqual(len(r['rows']), 3)
        self.assertEqual({x['seed'] for x in r['rows']}, set(plan['seeds']))
        self.assertFalse(r['protected_source_used'])
        self.assertFalse(r['scientific_pass'])
        for row in r['rows']:
            self.assertTrue(row['cold_restart_exact'])
            self.assertTrue(row['A_prediction_exact_retained'])
            self.assertEqual(row['training_actions'], 48)
            self.assertEqual(row['events'], 48)
            self.assertEqual(row['capsules'], 3)
            self.assertEqual(row['repairs'], 0)
            self.assertEqual(row['A_return_delta_brier'], 0)
            self.assertIn('context_rule_bayes', row['scores']['held_D'])


if __name__ == '__main__':
    unittest.main()
