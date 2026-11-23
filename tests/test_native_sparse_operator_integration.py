"""Original-native v9 sparse fixture envelope negatives, no source actions."""
import hashlib
import json
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, SPARSE_FIXTURE_SCHEMA,
    GRID5_FIXTURE_SCHEMA, EXTERNAL_FIXTURE_SCHEMA,
)
from yggdrasil.native_sparse_operator_evidence import (
    RECEIPT_SCHEMA, SOURCE_MODE,
)
from yggdrasil.native_external_action_identity import (
    RECEIPT_SCHEMA as EXTERNAL_RECEIPT_SCHEMA,
    SOURCE_MODE as EXTERNAL_MODE,
)
from yggdrasil.native_grid5_ingress import (
    SCHEMA as GRID5_RECEIPT_SCHEMA, SOURCE_MODE as GRID5_MODE,
)


def sparse(native, action=1301, state=(0, 0, 0, 0), outcome=0, sid=1):
    req = {'public_view': list(state), 'external_action_id': action}
    raw = canonical({'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                     'source_id': f'{sid:064x}', **req, 'outcome': outcome})
    return native.observe_sparse_fixture(req, raw, digest(raw))


def external(native):
    req = {'public_view': [0, 0], 'external_action_id': 90017}
    raw = canonical({'schema': EXTERNAL_RECEIPT_SCHEMA,
                     'source_mode': EXTERNAL_MODE,
                     'source_id': 'a'*64, **req, 'outcome': 0})
    return native.observe_external_fixture(req, raw, digest(raw))


def grid5(native):
    req = {'episode_id': 'a'*64, 'step_index': 0,
           'public_state': [0, 0], 'public_action': 0}
    raw = canonical({'schema': GRID5_RECEIPT_SCHEMA,
                     'source_mode': GRID5_MODE, 'source_id': 'b'*64,
                     **req, 'next_state': [1, 0], 'reward': 0,
                     'terminated': False, 'truncated': False})
    return native.observe_grid5_fixture(req, raw, digest(raw))


class NativeSparseV9Integration(unittest.TestCase):
    def test_default_legacy_v1_bytes_and_binary_forecast_unchanged(self):
        base = NativeEpisodeExperience()
        old = base.checkpoint()
        self.assertNotEqual(json.loads(old)['schema'], SPARSE_FIXTURE_SCHEMA)
        self.assertEqual(base.sparse_fixture_forecast([0, 0, 0, 0], 1301)['status'],
                         'ABSTAIN')
        self.assertEqual(NativeEpisodeExperience.restore(old, digest(old)).checkpoint(), old)
        binary = base.forecast((0, 0), 0)
        new = sparse(base)
        self.assertEqual(base.checkpoint(), old)
        self.assertEqual(base.forecast((0, 0), 0), binary)
        self.assertEqual(new.forecast((0, 0), 0), binary)
        self.assertEqual(new.info()['state_sha256'], base.info()['state_sha256'])
        self.assertEqual(new._transition.snapshot(), base._transition.snapshot())
        self.assertEqual(new._terminal.snapshot(), base._terminal.snapshot())

    def test_unseen_public_variable_hypothesis_v9_and_cold(self):
        m = NativeEpisodeExperience()
        for sid, (x, y) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1)), 1):
            m = sparse(m, state=(x, y, 0, 0), outcome=x ^ y, sid=sid)
        v = m.sparse_fixture_forecast([1, 1, 1, 1], 1301)
        self.assertEqual(v['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(v['predicted_outcome'], 0)
        raw = m.checkpoint()
        self.assertEqual(json.loads(raw)['schema'], SPARSE_FIXTURE_SCHEMA)
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.sparse_fixture_forecast([1, 1, 1, 1], 1301), v)
        self.assertEqual(cold.consolidate().checkpoint(), raw)
        self.assertFalse(v['action_authorized'])

    def test_legacy_v7_nested_v9_survives_exactly(self):
        base = external(NativeEpisodeExperience())
        baseline = base.checkpoint()
        self.assertEqual(json.loads(baseline)['schema'], EXTERNAL_FIXTURE_SCHEMA)
        staged = sparse(base)
        raw = staged.checkpoint()
        self.assertEqual(json.loads(raw)['schema'], SPARSE_FIXTURE_SCHEMA)
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.consolidate().checkpoint(), raw)
        self.assertEqual(cold.observed_external_fixture_value((0, 0), 90017),
                         base.observed_external_fixture_value((0, 0), 90017))
        self.assertEqual(base.checkpoint(), baseline)

    def test_legacy_v8_nested_v9_survives_exactly(self):
        base = grid5(NativeEpisodeExperience())
        baseline = base.checkpoint()
        self.assertEqual(json.loads(baseline)['schema'], GRID5_FIXTURE_SCHEMA)
        staged = sparse(base)
        raw = staged.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.consolidate().checkpoint(), raw)
        self.assertEqual(cold.grid5_fixture_forecast([0, 0], 0, episode_id='a'*64),
                         [1, 0])
        self.assertEqual(base.checkpoint(), baseline)

    def test_combined_v7_v8_v9_nested_no_loss(self):
        base = external(grid5(NativeEpisodeExperience()))
        raw = sparse(base).checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.consolidate().checkpoint(), raw)
        self.assertEqual(cold.info()['sparse_fixture_count'], 1)
        self.assertEqual(cold.info()['grid5_fixture_count'], 1)
        self.assertEqual(cold.info()['external_action_fixture_count'], 1)

    def test_forged_acceptance_and_even_rehashed_witness_rejected(self):
        m = sparse(NativeEpisodeExperience())
        raw = m.checkpoint()
        d = json.loads(raw)
        d['native_accepted'] = True
        forged = canonical(d)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(forged, digest(forged))
        d = json.loads(raw)
        d['sparse_checkpoint']['records'][0][3] = 1
        d['sparse_sha256'] = digest(canonical(d['sparse_checkpoint']))
        forged = canonical(d)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(forged, digest(forged))

    def test_replay_and_wrong_view_do_not_mutate_prior_state(self):
        m = sparse(NativeEpisodeExperience())
        prior = m.checkpoint()
        self.assertEqual(sparse(m).checkpoint(), prior)
        req = {'public_view': [0, 1, 0, 0], 'external_action_id': 1301}
        raw = canonical({'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                         'source_id': f'{12:064x}', 'public_view': [0, 0, 0, 0],
                         'external_action_id': 1301, 'outcome': 0})
        with self.assertRaisesRegex(ValueError, 'SPARSE_RECEIPT_MISMATCH'):
            m.observe_sparse_fixture(req, raw, digest(raw))
        self.assertEqual(m.checkpoint(), prior)

    def test_four_way_and_counterexample_retained_after_cold(self):
        m = NativeEpisodeExperience()
        for i in range(16):
            state = tuple((i >> b) & 1 for b in (3, 2, 1, 0))
            if state != (1, 1, 1, 1):
                m = sparse(m, state=state, outcome=0, sid=i+1)
        raw = m.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        v = cold.sparse_fixture_forecast([1, 1, 1, 1], 1301)
        self.assertEqual(v['status'], 'HYPOTHESIS_WITHIN_GRAMMAR')
        self.assertEqual(v['predicted_outcome'], 0)
        self.assertFalse(v['scientific_gain_verified'])

    def test_cumulative_parent_method_is_present_not_new_controller(self):
        from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
        self.assertTrue(callable(NativeCumulativeLearner.observe_sparse_fixture))
        self.assertTrue(callable(NativeCumulativeLearner.sparse_fixture_forecast))


if __name__ == '__main__':
    unittest.main()
