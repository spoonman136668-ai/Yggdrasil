"""Native Grid5 evidence integration for opt-in conditional hypothesis, DEV ONLY.

No original-world episode or hidden role mapping is used; all emitted receipts
are local source-free fixtures. Native ingestion proves input continuity.
"""
import hashlib
import importlib.util
from pathlib import Path
import unittest

from test_native_grid5_evidence_dev import receipt
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence

_SOURCE = (Path(__file__).resolve().parents[1] / 'research' / 'contrib'
           / 'chatgpt' / 'WSCM-GRID5-ROLE-DEV-01' / 'conditional_rule_dev.py')
_SPEC = importlib.util.spec_from_file_location('wscm_conditional', _SOURCE)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
forecast = _MOD.conditional_delta_forecast


def admitted_sequence():
    """Actual native public-receipt path, using only Manhattan-legal moves."""
    model = NativeGrid5Evidence()
    current = (0, 0)
    step = 0
    # Both branches of x-parity have two different witnessed predecessors.
    samples = (((2, 2), (3, 2)), ((3, 2), (2, 2)),
               ((4, 2), (5, 2)), ((5, 2), (4, 2)))
    for target, observed in samples:
        while current != target:
            if current[0] != target[0]:
                next_state = (current[0] + (1 if current[0] < target[0] else -1), current[1])
            else:
                next_state = (current[0], current[1] + (1 if current[1] < target[1] else -1))
            model = model.observe_public_receipt(*receipt(
                step, act=1, before=current, after=next_state))
            current = next_state
            step += 1
        model = model.observe_public_receipt(*receipt(
            step, act=0, before=current, after=observed))
        current = observed
        step += 1
    return model, current, step


class ConditionalNativeDev(unittest.TestCase):
    def test_native_receipt_admission_and_cold_noninterference(self):
        model, _, _ = admitted_sequence()
        status = forecast(model, [6, 2], 0, episode_id='a' * 64)
        self.assertEqual((status['status'], status['predicted_next_state']),
                         ('HYPOTHESIS', [7, 2]))
        self.assertFalse(status['planner_authorized'])
        self.assertFalse(status['scientific_gain_verified'])
        self.assertIsNone(model.public_forecast([6, 2], 0, episode_id='a'*64))
        self.assertEqual(model.public_learned_delta_forecast(
            [6, 2], 0, episode_id='a'*64)['status'], 'CONTRADICTION')
        original_plan = model.public_plan([6, 2], episode_id='a'*64)
        saved = model.checkpoint()
        cold = NativeGrid5Evidence.restore(saved, hashlib.sha256(saved).hexdigest())
        self.assertEqual(cold.checkpoint(), saved)
        self.assertEqual(forecast(cold, [6, 2], 0, episode_id='a'*64), status)
        self.assertEqual(model.public_plan([6, 2], episode_id='a'*64), original_plan)

    def test_actual_native_conflict_causes_refusal(self):
        model, current, step = admitted_sequence()
        while current != (2, 2):
            nxt = (current[0] - 1, current[1])
            model = model.observe_public_receipt(*receipt(
                step, act=1, before=current, after=nxt))
            current = nxt
            step += 1
        model = model.observe_public_receipt(*receipt(
            step, act=0, before=current, after=(2, 3)))
        got = forecast(model, [6, 2], 0, episode_id='a'*64)
        self.assertEqual((got['status'], got['reason']),
                         ('CONTRADICTION', 'SAME_STATE_CONFLICT'))

    def test_original_episode_boundary_and_input_guard(self):
        model, _, _ = admitted_sequence()
        self.assertEqual(forecast(model, [6, 2], 0, episode_id='b'*64)['status'],
                         'ABSTAIN')
        self.assertEqual(forecast(model, [2, 2], 0, episode_id='a'*64)['status'],
                         'ABSTAIN')
        with self.assertRaises(TypeError):
            forecast(object(), [6, 2], 0, episode_id='a'*64)
        with self.assertRaises(ValueError):
            forecast(model, [6, 2], True, episode_id='a'*64)


if __name__ == '__main__':
    unittest.main()

