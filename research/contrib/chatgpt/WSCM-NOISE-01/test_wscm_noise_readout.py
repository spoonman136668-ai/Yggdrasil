"""WSCM-NOISE-01 isolated source-free contract/negative tests."""
import hashlib
import itertools
import json
import math
import unittest
import wscm_noise_readout as m


class WSCMNoiseGate(unittest.TestCase):
    def setUp(self):
        self.rows = []
        self.counter = 0

    def add(self, action, state, outcome):
        self.counter += 1
        sid = f'{self.counter:064x}'
        view = list(m.STATES[state])
        receipt = {'schema': m.RECEIPT_SCHEMA, 'source_mode': m.SOURCE_MODE,
                   'source_id': sid, 'external_action_id': action,
                   'public_view': view, 'outcome': outcome}
        self.rows.append([sid, action, view, outcome, m.sha256(m.canonical(receipt))])

    def data(self, rows=None):
        raw = m.canonical({'schema': m.SOURCE_SCHEMA, 'source_mode': m.SOURCE_MODE,
                           'records': self.rows if rows is None else rows})
        return raw, m.sha256(raw)

    def result(self):
        return m.evaluate(*self.data(), 1301, 90017)

    def test_empty_evidence_gives_symmetric_uncertainty(self):
        r = self.result()
        self.assertAlmostEqual(r['reuse_probability'], .5)
        self.assertAlmostEqual(r['maximum_function_probability'], 1/16)
        self.assertEqual(r['probability_one_by_view'], (.5,) * 4)
        self.assertFalse(r['provisional_role_binding'])

    def test_duplicate_outcomes_are_aggregated_not_permanent_abstention(self):
        truth = (0, 0, 1, 1)
        for action, n in ((1301, 6), (90017, 8)):
            for state in range(4):
                for j in range(n):
                    self.add(action, state, truth[state] ^ int(j == 0))
        r = self.result()
        self.assertEqual(r['old_witnesses'], 24)
        self.assertEqual(r['new_witnesses'], 32)
        self.assertGreater(r['maximum_function_probability'], 0.999)
        for s, outcome in enumerate(truth):
            self.assertAlmostEqual(r['probability_one_by_view'][s], outcome, delta=0.001)
        self.assertFalse(r['provisional_role_binding'])

    def test_unidentifiable_reuse_event_has_strict_ceiling(self):
        for action in (1301, 90017):
            for state, outcome in enumerate((0, 0, 1, 1)):
                for _ in range(20):
                    self.add(action, state, outcome)
        r = self.result()
        cap = .5 / (.5 + .5/16)
        self.assertAlmostEqual(r['reuse_probability'], cap, places=6)
        self.assertLess(r['reuse_probability'], .95)
        self.assertFalse(r['provisional_role_binding'])

    def test_independent_exact_bayesian_control_ties(self):
        for action, seq in ((1301, [(0, 1), (0, 0), (1, 0), (2, 1), (3, 1)]),
                            (90017, [(0, 0), (1, 0), (2, 1), (2, 0)])):
            for s, o in seq:
                self.add(action, s, o)
        r = self.result()
        a = {1301: [], 90017: []}
        for _, action, view, outcome, _ in self.rows:
            a[action].append((m.STATES.index(tuple(view)), outcome))
        def w(samples, f):
            z = 1.0
            for state, outcome in samples:
                z *= .9 if f[state] == outcome else .1
            return z
        lo = [w(a[1301], f) for f in m.FUNCTIONS]
        old = [x / sum(lo) for x in lo]
        mixed = [.5*x + .5/16 for x in old]
        ln = [w(a[90017], f) for f in m.FUNCTIONS]
        new = [x*y/sum(p*l for p, l in zip(mixed, ln))
               for x, y in zip(mixed, ln)]
        conventional = [sum(p*f[s] for p, f in zip(new, m.FUNCTIONS))
                        for s in range(4)]
        for x, y in zip(r['probability_one_by_view'], conventional):
            self.assertAlmostEqual(x, y, places=12)

    def test_unobserved_new_id_does_not_become_certain(self):
        for s, o in enumerate((0, 0, 1, 1)):
            for _ in range(6):
                self.add(1301, s, o)
        r = self.result()
        self.assertFalse(r['provisional_role_binding'])
        self.assertLess(r['maximum_function_probability'], .6)
        self.assertEqual(r['new_witnesses'], 0)

    def test_strict_bool_action_alias_rejected(self):
        raw, pin = self.data()
        with self.assertRaisesRegex(ValueError, 'WSCM_ACTION_ID'):
            m.evaluate(raw, pin, True, 90017)

    def test_strict_bool_view_alias_rejected(self):
        self.add(1301, 0, 0)
        rows = json.loads(self.data()[0])['records']
        rows[0][2] = [False, 0]
        raw, pin = self.data(rows)
        with self.assertRaisesRegex(ValueError, 'WSCM_FIXTURE_REJECTED'):
            m.evaluate(raw, pin, 1301, 90017)

    def test_rehashed_outer_tampered_outcome_rejected(self):
        self.add(1301, 0, 0)
        rows = json.loads(self.data()[0])['records']
        rows[0][3] = 1
        raw, pin = self.data(rows)
        with self.assertRaisesRegex(ValueError, 'WSCM_FIXTURE_REJECTED'):
            m.evaluate(raw, pin, 1301, 90017)

    def test_hidden_role_metadata_rejected(self):
        obj = json.loads(self.data()[0])
        obj['phase'] = 'A_return'
        raw = m.canonical(obj)
        with self.assertRaisesRegex(ValueError, 'WSCM_FIXTURE_REJECTED'):
            m.evaluate(raw, m.sha256(raw), 1301, 90017)

    def test_conflicting_duplicate_witness_id_rejected(self):
        self.add(1301, 0, 0)
        with self.assertRaisesRegex(ValueError, 'WSCM_FIXTURE_REJECTED'):
            m.evaluate(*self.data(self.rows + self.rows), 1301, 90017)

    def test_sha_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'WSCM_FIXTURE_PIN'):
            m.evaluate(*self.data()[:1], '0'*64, 1301, 90017)

    def test_no_native_or_scientific_promotion(self):
        r = self.result()
        self.assertIs(r['scientific_pass'], False)
        self.assertIs(r['native_accepted'], False)
        self.assertEqual(r['source_mode'], m.SOURCE_MODE)


if __name__ == '__main__':
    unittest.main()
