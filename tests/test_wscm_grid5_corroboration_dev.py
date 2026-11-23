"""Source-free DEV regression: corroboration does not authorize planning."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

from test_native_grid5_evidence_dev import receipt
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence

_P = (Path(__file__).resolve().parents[1] / 'research' / 'contrib' / 'chatgpt'
      / 'WSCM-GRID5-ROLE-DEV-01' / 'evidence_gate_dev.py')
_SPEC = importlib.util.spec_from_file_location('evidence_gate_dev', _P)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
readout = _MOD.corroborated_delta_forecast


def observe(seq):
    m = NativeGrid5Evidence()
    for step, action, before, after in seq:
        m = m.observe_public_receipt(*receipt(step, act=action,
                                             before=before, after=after))
    return m


PREFIX = ((0, 0, (0, 0), (1, 0)),
          (1, 1, (1, 0), (1, 1)),
          (2, 0, (1, 1), (2, 1)))


class CorroborationDev(unittest.TestCase):
    def test_one_support_remains_abstention(self):
        m = observe(PREFIX)
        self.assertEqual(m.public_learned_delta_forecast(
            [5, 5], 0, episode_id='a'*64)['status'], 'HYPOTHESIS')
        self.assertEqual(readout(m, [5, 5], 0, episode_id='a'*64)['status'], 'ABSTAIN')

    def test_distinct_state_corroboration_is_still_only_hypothesis(self):
        m = observe(PREFIX + ((3, 1, (2, 1), (2, 2)),
                              (4, 0, (2, 2), (3, 2))))
        plan_before = m.public_plan([5, 5], episode_id='a'*64)
        got = readout(m, [5, 5], 0, episode_id='a'*64)
        self.assertEqual(got['status'], 'HYPOTHESIS')
        self.assertEqual(got['predicted_next_state'], [6, 5])
        self.assertEqual(got['distinct_predecessor_states'], 2)
        self.assertFalse(got['planner_authorized'])
        self.assertFalse(got['scientific_gain_verified'])
        self.assertEqual(m.public_plan([5, 5], episode_id='a'*64), plan_before)
        self.assertEqual(m.checkpoint(), NativeGrid5Evidence.restore(
            m.checkpoint(), hashlib.sha256(m.checkpoint()).hexdigest()).checkpoint())
        restored = NativeGrid5Evidence.restore(
            m.checkpoint(), hashlib.sha256(m.checkpoint()).hexdigest())
        self.assertEqual(readout(restored, [5, 5], 0, episode_id='a'*64), got)

    def test_repeated_same_state_cannot_count_as_independent(self):
        m = observe(PREFIX + ((3, 1, (2, 1), (1, 1)),
                              (4, 0, (1, 1), (2, 1))))
        self.assertEqual(readout(m, [5, 5], 0, episode_id='a'*64)['status'], 'ABSTAIN')

    def test_conflicting_second_state_rejects(self):
        m = observe(PREFIX + ((3, 1, (2, 1), (2, 2)),
                              (4, 0, (2, 2), (2, 3))))
        got = readout(m, [5, 5], 0, episode_id='a'*64)
        self.assertEqual(got['status'], 'CONTRADICTION')
        self.assertIsNone(got['predicted_next_state'])

    def test_seen_query_and_cross_episode_not_transfer(self):
        m = observe(PREFIX + ((3, 1, (2, 1), (2, 2)),
                              (4, 0, (2, 2), (3, 2))))
        self.assertEqual(readout(m, [1, 1], 0, episode_id='a'*64)['status'], 'ABSTAIN')
        self.assertEqual(readout(m, [5, 5], 0, episode_id='b'*64)['status'], 'ABSTAIN')

    def test_input_validation_retained(self):
        m = observe(PREFIX)
        for action in (True, -1, 5, '0'):
            with self.assertRaises(ValueError):
                readout(m, [5, 5], action, episode_id='a'*64)
        with self.assertRaises(ValueError):
            readout(m, [5, 5], 0, episode_id=None)
        with self.assertRaises(TypeError):
            readout(object(), [5, 5], 0, episode_id='a'*64)


if __name__ == '__main__':
    unittest.main()
