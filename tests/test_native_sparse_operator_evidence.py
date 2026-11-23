"""Read-only fixture-only native sparse-operator admission tests (no science)."""
import hashlib
import itertools
import json
import unittest
from yggdrasil.native_sparse_operator_evidence import (
    NativeSparseOperatorEvidence, RECEIPT_SCHEMA, SOURCE_MODE,
    STATES, MODELS, MAX_ACTIONS, MAX_EVENTS, _canonical, _eval,
)


def append(model, action, view, outcome, uid):
    receipt = {'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
               'source_id': f'{uid:064x}', 'public_view': list(view),
               'external_action_id': action, 'outcome': outcome}
    raw = _canonical(receipt)
    return model.observe_public_receipt({'public_view': list(view),
                                        'external_action_id': action},
                                        raw, hashlib.sha256(raw).hexdigest())


class SparseNativeTests(unittest.TestCase):
    def test_114_prior_models_not_oracle(self):
        self.assertEqual(len(MODELS), 114)
        self.assertTrue(all(len(parents) <= 2 for parents, _ in MODELS))

    def test_unknown_and_partial_abstain(self):
        model = append(NativeSparseOperatorEvidence(), 5, (0, 0, 0, 0), 0, 1)
        self.assertEqual(model.forecast([1, 1, 1, 1], 5)['status'], 'ABSTAIN')
        self.assertEqual(model.forecast([0, 0, 0, 0], 17)['status'], 'ABSTAIN')

    def test_in_grammar_unseen_forecast_is_provisional(self):
        model = NativeSparseOperatorEvidence()
        for idx, state in enumerate(STATES):
            if state in ((0, 1, 0, 1), (0, 1, 1, 1)):
                continue
            model = append(model, 5, state, state[0] ^ state[1], idx + 1)
        result = model.forecast([0, 1, 0, 1], 5)
        self.assertEqual(result['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(result['predicted_outcome'], 1)
        self.assertFalse(result['action_authorized'])

    def test_all_114_models_compatible_forecasts_sound_within_grammar(self):
        train = (0, 3, 4, 15)
        for law in MODELS:
            model = NativeSparseOperatorEvidence()
            for k, idx in enumerate(train):
                model = append(model, 5, STATES[idx], _eval(law, STATES[idx]), k+1)
            for state in STATES:
                result = model.forecast(list(state), 5)
                if result['status'] == 'HYPOTHESIS_WITHIN_GRAMMAR':
                    self.assertEqual(result['predicted_outcome'], _eval(law, state))

    def test_full_three_way_parity_is_out_of_grammar(self):
        model = NativeSparseOperatorEvidence()
        for idx, state in enumerate(STATES):
            model = append(model, 5, state, state[0] ^ state[1] ^ state[2], idx+1)
        self.assertEqual(model.forecast([0, 0, 0, 0], 5)['status'], 'OUT_OF_GRAMMAR')

    def test_four_way_and_is_false_certainty_negative(self):
        model = NativeSparseOperatorEvidence()
        for idx, state in enumerate(STATES):
            if state != (1, 1, 1, 1):
                model = append(model, 5, state, 0, idx+1)
        result = model.forecast([1, 1, 1, 1], 5)
        self.assertEqual(result['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(result['predicted_outcome'], 0)
        self.assertFalse(result['scientific_gain_verified'])
        # The unfamiliar four-way-AND law would instead output 1.

    def test_conflict_contradicts_and_no_memory_mutation(self):
        previous = append(NativeSparseOperatorEvidence(), 5, (0, 0, 0, 0), 0, 1)
        candidate = append(previous, 5, (0, 0, 0, 0), 1, 2)
        self.assertEqual(candidate.forecast([0, 0, 0, 0], 5)['status'], 'CONTRADICTION')
        self.assertEqual(previous.forecast([0, 0, 0, 0], 5)['predicted_outcome'], 0)

    def test_cold_checkpoint_exact_and_tamper_rejected(self):
        model = append(NativeSparseOperatorEvidence(), 5, (0, 0, 0, 0), 0, 1)
        raw = model.checkpoint()
        pin = hashlib.sha256(raw).hexdigest()
        self.assertEqual(NativeSparseOperatorEvidence.restore(raw, pin).checkpoint(), raw)
        doc = json.loads(raw)
        doc['records'][0][3] = 1
        forged = _canonical(doc)
        with self.assertRaisesRegex(ValueError, 'SPARSE_CHECKPOINT_REJECTED'):
            NativeSparseOperatorEvidence.restore(forged, hashlib.sha256(forged).hexdigest())

    def test_idempotent_replay_and_conflicting_source_refused(self):
        base = append(NativeSparseOperatorEvidence(), 5, (0, 0, 0, 0), 0, 1)
        self.assertIs(append(base, 5, (0, 0, 0, 0), 0, 1), base)
        with self.assertRaisesRegex(ValueError, 'SPARSE_REPLAY_CONFLICT'):
            append(base, 5, (0, 0, 0, 0), 1, 1)

    def test_leaked_hidden_fields_and_invalid_types_rejected(self):
        m = NativeSparseOperatorEvidence()
        receipt = {'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                   'source_id': f'{1:064x}', 'public_view': [0, 0, 0, 0],
                   'external_action_id': 5, 'outcome': 0}
        for change in ({'role': 2}, {'phase': 'B'}, {'source_mode': 'authenticated'},
                       {'outcome': True}, {'external_action_id': True},
                       {'public_view': [False, 0, 0, 0]}):
            bad = _canonical({**receipt, **change})
            with self.subTest(change=change), self.assertRaises(ValueError):
                m.observe_public_receipt({'public_view': [0, 0, 0, 0],
                                          'external_action_id': 5},
                                         bad, hashlib.sha256(bad).hexdigest())

    def test_action_and_record_caps(self):
        model = NativeSparseOperatorEvidence()
        for a in range(MAX_ACTIONS):
            model = append(model, a, (0, 0, 0, 0), 1, a+1)
        with self.assertRaisesRegex(ValueError, 'SPARSE_ACTION_CAPACITY'):
            append(model, 99, (0, 0, 0, 0), 1, 100)
        empty = NativeSparseOperatorEvidence()
        for k in range(MAX_EVENTS):
            empty = append(empty, 5, (0, 0, 0, 0), 0, k+1)
        with self.assertRaisesRegex(ValueError, 'SPARSE_EVENT_CAPACITY'):
            append(empty, 5, (0, 0, 0, 0), 0, 1000)

    def test_new_id_independence_and_no_permissions(self):
        first = append(NativeSparseOperatorEvidence(), 5, (1, 1, 1, 1), 1, 1)
        self.assertEqual(first.forecast([1, 1, 1, 1], 90017)['status'], 'ABSTAIN')
        self.assertFalse(first.forecast([1, 1, 1, 1], 5)['action_authorized'])
        self.assertFalse(first.forecast([1, 1, 1, 1], 5)['scientific_gain_verified'])


if __name__ == '__main__':
    unittest.main()
