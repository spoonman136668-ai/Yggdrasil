"""Cross-readout source-free WSCM safety controls; no original world steps."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

from test_native_grid5_evidence_dev import receipt
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence

_ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, _ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

GUARD = load('wscm_guard01_cross', 'research/contrib/chatgpt/WSCM-EPISTEMIC-GUARD-01/guard.py')
CORROBORATE = load('wscm_corroborate01_cross', 'research/contrib/chatgpt/WSCM-GRID5-ROLE-DEV-01/evidence_gate_dev.py')
EP = 'a' * 64
PREFIX = ((0, 0, (0, 0), (1, 0)),
          (1, 1, (1, 0), (1, 1)),
          (2, 0, (1, 1), (2, 1)))


def observed(rows):
    m = NativeGrid5Evidence()
    for step, action, before, after in rows:
        m = m.observe_public_receipt(*receipt(step, act=action, before=before, after=after))
    return m


class CrossReadoutGuardTests(unittest.TestCase):
    def test_one_evidence_cannot_authorize(self):
        m = observed(((0, 0, (0, 0), (1, 0)),))
        role = m.public_role_forecast([1, 0], 0, episode_id=EP)
        self.assertEqual(role['status'], 'ENTAILED')
        self.assertEqual(role['predicted_next_state'], [2, 0])
        self.assertEqual(CORROBORATE.corroborated_delta_forecast(m, [1, 0], 0, episode_id=EP)['status'], 'ABSTAIN')
        guarded = GUARD.unfamiliar_family_readout(m, [1, 0], 0, episode_id=EP)
        self.assertFalse(guarded['action_admissible'])
        self.assertIsNone(guarded['actionable_next_state'])

    def test_corrob_two_different_predecessors_remains_nonactionable(self):
        m = observed(PREFIX + ((3, 1, (2, 1), (2, 2)), (4, 0, (2, 2), (3, 2))))
        before = m.checkpoint()
        plan = m.public_plan([5, 5], episode_id=EP)
        q = CORROBORATE.corroborated_delta_forecast(m, [5, 5], 0, episode_id=EP)
        self.assertEqual(q['status'], 'HYPOTHESIS')
        self.assertEqual(q['predicted_next_state'], [6, 5])
        self.assertFalse(q['planner_authorized'])
        g = GUARD.unfamiliar_family_readout(m, [5, 5], 0, episode_id=EP)
        self.assertEqual(g['delta_family_status'], 'HYPOTHESIS')
        self.assertEqual(g['status'], 'ABSTAIN_UNVERIFIED_FAMILY')
        self.assertIsNone(g['actionable_next_state'])
        self.assertEqual(m.checkpoint(), before)
        self.assertEqual(m.public_plan([5, 5], episode_id=EP), plan)

    def test_conflicting_observation_fails_closed(self):
        m = observed(PREFIX + ((3, 1, (2, 1), (2, 2)), (4, 0, (2, 2), (2, 3))))
        c = CORROBORATE.corroborated_delta_forecast(m, [5, 5], 0, episode_id=EP)
        g = GUARD.unfamiliar_family_readout(m, [5, 5], 0, episode_id=EP)
        self.assertEqual(c['status'], 'CONTRADICTION')
        self.assertEqual(g['delta_family_status'], 'CONTRADICTION')
        self.assertFalse(g['action_admissible'])

    def test_restore_has_identical_guard_and_corroboration(self):
        m = observed(PREFIX + ((3, 1, (2, 1), (2, 2)), (4, 0, (2, 2), (3, 2))))
        raw = m.checkpoint()
        cold = NativeGrid5Evidence.restore(raw, hashlib.sha256(raw).hexdigest())
        self.assertEqual(GUARD.unfamiliar_family_readout(m, [5, 5], 0, episode_id=EP),
                         GUARD.unfamiliar_family_readout(cold, [5, 5], 0, episode_id=EP))
        self.assertEqual(CORROBORATE.corroborated_delta_forecast(m, [5, 5], 0, episode_id=EP),
                         CORROBORATE.corroborated_delta_forecast(cold, [5, 5], 0, episode_id=EP))

    def test_invalid_action_episode_rejected(self):
        m = observed(PREFIX)
        for callback in (GUARD.unfamiliar_family_readout, CORROBORATE.corroborated_delta_forecast):
            with self.assertRaises(ValueError):
                callback(m, [5, 5], 5, episode_id=EP)
            with self.assertRaises(ValueError):
                callback(m, [5, 5], 0, episode_id=None)


if __name__ == '__main__':
    unittest.main()
