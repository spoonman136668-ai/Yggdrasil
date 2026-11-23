"""Static DEV contracts only: no model training or new causal outcomes."""
import importlib.util
from pathlib import Path
import unittest

_P = (Path(__file__).resolve().parents[1] / 'research' / 'contrib' / 'chatgpt'
      / 'WSCM-GRID5-ROLE-DEV-01' / 'discrimination_preflight_dev.py')
_S = importlib.util.spec_from_file_location('wscm_discriminator', _P)
_M = importlib.util.module_from_spec(_S)
_S.loader.exec_module(_M)
propose_probe = _M.propose_probe


CANDIDATES = [
    {'id': 'repeat', 'state': [2, 2], 'action': 0,
     'travel_charge': 0, 'intervention_charge': 1},
    {'id': 'discriminator', 'state': [4, 4], 'action': 0,
     'travel_charge': 3, 'intervention_charge': 1},
]
# Two public candidate models agree on observed and repeat states but disagree
# at an unfamiliar state. These tables are NOT supplied to the native learner.
HYPOTHESES = [
    {'id': 'uniform-east', 'predictions': {
        'repeat': [3, 2], 'discriminator': [5, 4]}},
    {'id': 'context-gated', 'predictions': {
        'repeat': [3, 2], 'discriminator': [3, 4]}},
]


class DiscriminationPreflightDev(unittest.TestCase):
    def test_discriminating_query_is_ranked_not_executed(self):
        x = propose_probe(CANDIDATES, HYPOTHESES, remaining_charge_units=4)
        self.assertEqual(x['status'], 'PROPOSAL_ONLY')
        self.assertEqual(x['candidate_id'], 'discriminator')
        self.assertEqual(x['charged_units_if_executed'], 4)
        self.assertEqual(x['disagreeing_pairs'], 1)
        self.assertFalse(x['action_authorized'])
        self.assertFalse(x['scientific_gain_verified'])

    def test_unaffordable_informative_query_abstains(self):
        x = propose_probe(CANDIDATES, HYPOTHESES, remaining_charge_units=3)
        self.assertEqual(x['status'], 'BUDGET_EXHAUSTED')
        self.assertIsNone(x['candidate_id'])

    def test_indistinguishable_hypotheses_abstain(self):
        equal = [HYPOTHESES[0], {'id': 'different-id',
                                 'predictions': dict(HYPOTHESES[0]['predictions'])}]
        self.assertEqual(propose_probe(CANDIDATES, equal,
                                       remaining_charge_units=10)['status'], 'ABSTAIN')

    def test_missing_or_leaked_prediction_rejected(self):
        altered = [HYPOTHESES[0], {'id': 'missing', 'predictions': {'repeat': [3, 2]}}]
        with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_HYPOTHESIS'):
            propose_probe(CANDIDATES, altered, remaining_charge_units=10)
        with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_HYPOTHESIS'):
            propose_probe(CANDIDATES, [HYPOTHESES[0], HYPOTHESES[0]],
                          remaining_charge_units=10)

    def test_bad_charge_action_state_and_duplicate_rejected(self):
        for bad in (dict(CANDIDATES[0], travel_charge=-1),
                    dict(CANDIDATES[0], intervention_charge=0),
                    dict(CANDIDATES[0], action=True),
                    dict(CANDIDATES[0], state=[9, 0])):
            with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_CANDIDATE'):
                propose_probe([bad, CANDIDATES[1]], HYPOTHESES,
                              remaining_charge_units=10)
        with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_CANDIDATE'):
            propose_probe([CANDIDATES[0], CANDIDATES[0]], HYPOTHESES,
                          remaining_charge_units=10)

    def test_budget_and_shape_fail_closed(self):
        for cost in (True, -1, 1.1, '4', 11):
            with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_BOUNDS'):
                propose_probe(CANDIDATES, HYPOTHESES,
                              remaining_charge_units=cost)
        with self.assertRaisesRegex(ValueError, 'DISCRIMINATION_BOUNDS'):
            propose_probe([], HYPOTHESES, remaining_charge_units=10)

    def test_exact_cost_score_then_deterministic_tie_break(self):
        c = [{'id': 'z', 'state': [1, 1], 'action': 0, 'travel_charge': 2,
              'intervention_charge': 1},
             {'id': 'a', 'state': [2, 2], 'action': 0, 'travel_charge': 2,
              'intervention_charge': 1}]
        hs = [{'id': 'b', 'predictions': {'z': [2, 1], 'a': [3, 2]}},
              {'id': 'c', 'predictions': {'z': [0, 1], 'a': [1, 2]}}]
        self.assertEqual(propose_probe(c, hs, remaining_charge_units=3)['candidate_id'], 'a')


if __name__ == '__main__':
    unittest.main()
