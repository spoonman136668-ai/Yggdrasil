"""Source-free native-witness version-space DEV qualification; no env.step."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

from test_native_grid5_evidence_dev import receipt
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence

_SOURCE = (Path(__file__).resolve().parents[1] / 'research' / 'contrib'
           / 'chatgpt' / 'WSCM-GRID5-ROLE-DEV-01' / 'native_version_space_dev.py')
_SPEC = importlib.util.spec_from_file_location('native_version_space_dev', _SOURCE)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
propose = _MOD.propose_public_version_space_probe
EPISODE = 'a' * 64


def observed(sequence):
    model = NativeGrid5Evidence()
    for step, action, before, after in sequence:
        model = model.observe_public_receipt(
            *receipt(step, act=action, before=before, after=after))
    return model


PATH = (
    (0, 1, (0, 0), (1, 0)),
    (1, 1, (1, 0), (2, 0)),
    (2, 1, (2, 0), (2, 1)),
    (3, 1, (2, 1), (2, 2)),
    (4, 0, (2, 2), (3, 2)),
)
ODD_QUERY = {'id': 'odd', 'state': [3, 3], 'action': 0,
             'travel_charge': 1, 'intervention_charge': 1}
EVEN_QUERY = {'id': 'even', 'state': [4, 3], 'action': 0,
              'travel_charge': 0, 'intervention_charge': 1}


def call(model, candidates=None, *, episode=EPISODE, budget=10, action=0):
    return propose(model, [ODD_QUERY, EVEN_QUERY] if candidates is None else candidates,
                   action, episode_id=episode, remaining_charge_units=budget)


class PublicWitnessVersionSpaceDev(unittest.TestCase):
    def test_single_interior_witness_proposes_discriminating_odd_parity(self):
        m = observed(PATH)
        before = m.checkpoint()
        plan = m.public_plan([3, 3], episode_id=EPISODE)
        got = call(m)
        self.assertEqual((got['status'], got['candidate_id']),
                         ('PROPOSAL_ONLY', 'odd'))
        self.assertEqual(got['compatible_hypotheses'], 5)
        self.assertEqual(got['disagreeing_pairs'], 10)
        self.assertEqual(got['charged_units_if_executed'], 2)
        self.assertTrue(got['candidate_laws_derived_from_public_witnesses'])
        self.assertFalse(got['true_law_oracle_supplied'])
        self.assertFalse(got['action_authorized'])
        self.assertFalse(got['scientific_gain_verified'])
        self.assertEqual(before, m.checkpoint())
        self.assertEqual(plan, m.public_plan([3, 3], episode_id=EPISODE))
        # No new unseen-role forecast is fed into the original planner.
        self.assertIsNone(m.public_forecast([3, 3], 0, episode_id=EPISODE))

    def test_known_parity_has_no_discriminating_proposal(self):
        got = call(observed(PATH), [EVEN_QUERY])
        self.assertEqual(got['status'], 'ABSTAIN')
        self.assertIsNone(got['candidate_id'])

    def test_budget_rejects_action(self):
        got = call(observed(PATH), budget=1)
        self.assertEqual(got['status'], 'BUDGET_EXHAUSTED')
        self.assertIsNone(got['candidate_id'])
        self.assertFalse(got['action_authorized'])

    def test_later_odd_witness_removes_unresolved_version_space(self):
        m = observed(PATH + (
            (5, 1, (3, 2), (3, 3)),
            (6, 0, (3, 3), (2, 3)),
        ))
        got = call(m)
        self.assertEqual((got['status'], got['compatible_hypotheses']),
                         ('ABSTAIN', 1))

    def test_same_branch_conflict_rejected(self):
        m = observed(PATH + (
            (5, 1, (3, 2), (2, 2)),
            (6, 0, (2, 2), (2, 3)),
        ))
        got = call(m)
        self.assertEqual(got['status'], 'CONTRADICTION')
        self.assertIsNone(got['candidate_id'])

    def test_no_witness_or_clipped_witness_abstains(self):
        self.assertEqual(call(NativeGrid5Evidence())['reason'], 'NO_WITNESSES')
        m = observed(((0, 0, (0, 0), (0, 0)),))
        self.assertEqual(call(m)['reason'], 'NO_INTERIOR_SUPPORT')

    def test_cross_episode_does_not_reuse_other_law(self):
        got = call(observed(PATH), episode='b'*64)
        self.assertEqual(got['reason'], 'NO_WITNESSES')

    def test_seen_or_boundary_query_is_not_a_new_probe(self):
        witnessed = dict(ODD_QUERY, id='witness', state=[2, 2])
        got = call(observed(PATH), [witnessed])
        self.assertEqual(got['reason'], 'NO_SUPPORTED_QUERY')
        boundary = dict(ODD_QUERY, id='boundary', state=[1, 1])
        self.assertEqual(call(observed(PATH), [boundary])['reason'],
                         'NO_SUPPORTED_QUERY')

    def test_cold_restore_preserves_hypothesis_proposal_and_bytes(self):
        m = observed(PATH)
        checkpoint = m.checkpoint()
        restored = NativeGrid5Evidence.restore(
            checkpoint, hashlib.sha256(checkpoint).hexdigest())
        self.assertEqual(restored.checkpoint(), checkpoint)
        self.assertEqual(call(restored), call(m))

    def test_strict_input_bounds(self):
        m = observed(PATH)
        for action in (True, -1, 5, '0'):
            with self.assertRaises(ValueError):
                call(m, action=action)
        with self.assertRaises(ValueError):
            call(m, episode='wrong')
        for bad_budget in (True, -1, '2', 11):
            with self.assertRaises(ValueError):
                call(m, budget=bad_budget)
        invalid = dict(ODD_QUERY, action=1)
        with self.assertRaises(ValueError):
            call(m, [invalid])
        with self.assertRaises(ValueError):
            call(m, [ODD_QUERY, ODD_QUERY])
        with self.assertRaises(TypeError):
            call(object())

if __name__ == '__main__':
    unittest.main()
