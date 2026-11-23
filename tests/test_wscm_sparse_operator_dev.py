"""Unscored source-free negative controls for sparse-operator hypothesis screen."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'research/contrib/chatgpt/WSCM-SPARSE-OPERATOR-DEV-01/sparse_operator_dev.py'
SPEC = importlib.util.spec_from_file_location('sparse_operator_dev', SOURCE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def receipt(action, view, outcome, uid):
    return dict(source_mode=M.SOURCE_MODE, source_id=f'{uid:064x}',
                external_action_id=action, public_view=list(view), outcome=outcome)


class SparseOperatorDevTests(unittest.TestCase):
    def test_finite_bounded_grammar(self):
        self.assertEqual(len(M.MODELS), 114)
        self.assertEqual(len(M.STATES), 16)
        self.assertTrue(all(len(m[0]) <= 2 for m in M.MODELS))

    def test_no_witness_and_new_identity_abstain(self):
        self.assertEqual(M.analyze([], 1301, (0,0,0,0))['status'], 'ABSTAIN')
        rows = [receipt(1301, (0,0,0,0), 0, 1)]
        self.assertEqual(M.analyze(rows, 90017, (0,0,0,0))['status'], 'ABSTAIN')

    def test_partial_public_evidence_does_not_certify_unseen_rule(self):
        rows = [receipt(1301, (0,0,0,0), 0, 1)]
        v = M.analyze(rows, 1301, (1,1,1,1))
        self.assertEqual(v['status'], 'ABSTAIN')
        self.assertGreater(v['hypothesis_count'], 1)
        self.assertIsNone(v['predicted_outcome'])

    def test_even_witnessed_fit_is_labeled_hypothesis(self):
        rows = [receipt(1301, (0,0,0,0), 0, 1)]
        v = M.analyze(rows, 1301, (0,0,0,0))
        self.assertEqual(v['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(v['predicted_outcome'], 0)
        self.assertFalse(v['action_authorized'])

    def test_equal_evidence_order_is_deterministic(self):
        rows = [receipt(1301, b, b[0] ^ b[1], i+1) for i, b in enumerate(M.STATES[:8])]
        self.assertEqual(M.analyze(rows, 1301, (1,1,1,1)),
                         M.analyze(list(reversed(rows)), 1301, (1,1,1,1)))

    def test_public_operator_structure_can_entail_unseen_with_fixed_grammar(self):
        # Three observed, explicitly supplied public rows constrain a four-bit
        # two-parent family sufficiently for a nonwitnessed forecast.
        rows = [receipt(7, M.STATES[i], M.STATES[i][0] ^ M.STATES[i][1], i+1)
                for i in (0, 3, 4)]
        out = M.analyze(rows, 7, M.STATES[1])
        self.assertEqual(out['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertFalse(out['witnessed_query'])
        self.assertEqual(out['predicted_outcome'], 0)
        self.assertGreater(out['hypothesis_count'], 1)
        self.assertFalse(out['scientific_gain_verified'])

    def test_unanimity_is_sound_only_when_true_law_in_frozen_grammar(self):
        # Deterministic complete family screen, *not* independent science.
        train = (0, 3, 4, 15)
        for law_index, law in enumerate(M.MODELS):
            rows = [receipt(7, M.STATES[i], M._evaluate(law, M.STATES[i]), i+1)
                    for i in train]
            for state in M.STATES:
                result = M.analyze(rows, 7, state)
                if result['status'] == 'HYPOTHESIS_WITHIN_GRAMMAR':
                    self.assertEqual(result['predicted_outcome'], M._evaluate(law, state),
                                     msg=f'law={law_index} state={state}')
                else:
                    self.assertEqual(result['status'], 'ABSTAIN')

    def test_conflicting_public_effect_abstains(self):
        rows = [receipt(1301, (1,0,1,0), 0, 1), receipt(1301, (1,0,1,0), 1, 2)]
        self.assertEqual(M.analyze(rows, 1301, (0,1,0,1))['status'], 'CONTRADICTION')
        self.assertEqual(M.propose_public_probe(rows, 1301)['reason'], 'CONTRADICTION')

    def test_unknown_law_three_way_parity_rejected_when_full(self):
        rows = [receipt(1301, b, b[0] ^ b[1] ^ b[2], i+1)
                for i, b in enumerate(M.STATES)]
        result = M.analyze(rows, 1301, (1,1,1,1))
        self.assertEqual(result['status'], 'OUT_OF_GRAMMAR')
        self.assertIsNone(result['predicted_outcome'])

    def test_unseen_three_way_exception_can_fool_grammar(self):
        # Known-class predictive unanimity is never a scientific guarantee.
        # Find an excluded test point for a sparse all-zero training law.
        rows = [receipt(1301, b, 0, i+1) for i, b in enumerate(M.STATES)
                if b != (1,1,1,1)]
        r = M.analyze(rows, 1301, (1,1,1,1))
        self.assertEqual(r['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(r['predicted_outcome'], 0)
        self.assertFalse(r['scientific_gain_verified'])
        # A 4-way AND true law has the same 15 public witnesses but output=1.

    def test_probe_is_proposal_not_executable(self):
        rows = [receipt(1301, (0,0,0,0), 0, 1)]
        p = M.propose_public_probe(rows, 1301)
        self.assertEqual(p['status'], 'PROPOSED_UNCHARGED_HYPOTHETICAL')
        self.assertNotEqual(p['public_view'], (0,0,0,0))
        self.assertFalse(p['action_authorized'])
        self.assertFalse(p['charge_authenticated'])
        self.assertFalse(p['reachability_authenticated'])

    def test_invalid_types_private_fields_and_duplicate_replay_fail_closed(self):
        base = receipt(1301, (0,0,0,0), 0, 1)
        for bad in ({**base, 'role':'secret'}, {**base, 'source_mode':'real_world'},
                    {**base, 'external_action_id':True}, {**base, 'public_view':[0,0,True,0]},
                    {**base, 'outcome':0.0}, {**base, 'source_id':'A'*64}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                M.analyze([bad], 1301, (0,0,0,0))
        with self.assertRaisesRegex(ValueError,'WSCM_REPLAY_ID'):
            M.analyze([base,base],1301,(0,0,0,0))

    def test_caps_and_cross_action_isolation(self):
        rows = [receipt(i, (0,0,0,0), 1, i+1) for i in range(32)]
        self.assertIsNone(M.analyze(rows, 0, (1,1,1,1))['predicted_outcome'])
        with self.assertRaisesRegex(ValueError, 'WSCM_ACTION_CAP'):
            M.analyze(rows + [receipt(99,(0,0,0,0),1,99)], 0, (1,1,1,1))
        with self.assertRaisesRegex(ValueError,'WSCM_EVENT_CAP'):
            M.analyze([receipt(0,(0,0,0,0),1,i+1) for i in range(257)],0,(0,0,0,0))


if __name__ == '__main__':
    unittest.main()
