"""Source-free conditional law grammar negatives; not scored new-world evidence."""
import unittest
from conditional_rule_dev import _infer_from_native_rows as infer

A = 'a' * 64
B = 'b' * 64


def rows(examples, episode=A):
    return tuple((f'{i+1:064x}', episode, i, tuple(state), 0,
                  tuple(after), 0, False, False, '0'*64)
                 for i, (state, after) in enumerate(examples))


# Example public effects only; unlike the native intake, these rows are not
# authenticating origin or claiming sequential receipt continuity.
FITTING = [((2, 2), (3, 2)), ((3, 2), (2, 2)),
           ((4, 2), (5, 2)), ((5, 2), (4, 2))]
AMBIGUOUS = [((2, 2), (3, 2)), ((3, 3), (2, 3)),
             ((4, 4), (5, 4)), ((5, 5), (4, 5))]


class ConditionalDevelopment(unittest.TestCase):
    def query(self, evidence, state=(6, 2), action=0, episode=A):
        return infer(evidence, list(state), action, episode_id=episode)

    def test_minimum_four_distinct_public_predecessors(self):
        for n in range(4):
            with self.subTest(witnesses=n):
                self.assertEqual(self.query(rows(FITTING[:n]))['status'], 'ABSTAIN')

    def test_one_identified_conditional_hypothesis(self):
        got = self.query(rows(FITTING))
        self.assertEqual((got['status'], got['split_axis'], got['predicted_next_state']),
                         ('HYPOTHESIS', 0, [7, 2]))
        self.assertFalse(got['planner_authorized'])
        self.assertFalse(got['scientific_gain_verified'])

    def test_two_indistinguishable_features_abstain(self):
        got = self.query(rows(AMBIGUOUS), state=(6, 4))
        self.assertEqual((got['status'], got['reason']),
                         ('ABSTAIN', 'AMBIGUOUS_GRAMMAR'))

    def test_same_public_predecessor_disagreement_is_not_split(self):
        data = FITTING + [((2, 2), (2, 3))]
        got = self.query(rows(data))
        self.assertEqual((got['status'], got['reason']),
                         ('CONTRADICTION', 'SAME_STATE_CONFLICT'))

    def test_missing_grammar_is_not_false_causal_entailment(self):
        data = [((2, 2), (3, 2)), ((3, 2), (2, 2)),
                ((4, 2), (4, 3)), ((5, 2), (4, 2))]
        got = self.query(rows(data))
        self.assertEqual((got['status'], got['reason']),
                         ('ABSTAIN', 'NO_FITTING_SPLIT'))

    def test_query_exact_witness_not_transferred(self):
        self.assertEqual(self.query(rows(FITTING), state=(4, 2))['reason'],
                         'EXACT_WITNESS_EXISTS')

    def test_cross_episode_no_leak(self):
        self.assertEqual(self.query(rows(FITTING), episode=B)['status'], 'ABSTAIN')

    def test_boundary_refusal(self):
        self.assertEqual(self.query(rows(FITTING), state=(0, 2))['reason'],
                         'UNSUPPORTED_BOUNDARY')

    def test_unchanged_rows_and_deterministic_readout(self):
        source = rows(FITTING)
        self.assertEqual(self.query(source), self.query(source))
        self.assertEqual(source, rows(FITTING))

    def test_invalid_action_and_episode_fail_closed(self):
        for action in (True, -1, 5, '0'):
            with self.assertRaises(ValueError):
                self.query(rows(FITTING), action=action)
        with self.assertRaises(ValueError):
            self.query(rows(FITTING), episode='bad')
        with self.assertRaises(ValueError):
            infer((), [5, 5], 0, episode_id=None)

    def test_unwitnessed_exception_can_invalidate_parity_model(self):
        got = self.query(rows(FITTING), state=(6, 3))
        self.assertEqual((got['status'], got['predicted_next_state']),
                         ('HYPOTHESIS', [7, 3]))
        # An alternative state-dependent rule matching EVERY witnessed input
        # but reversing x when y is odd at x>=6 yields a different future.
        alternative = (5, 3)
        self.assertNotEqual(got['predicted_next_state'], list(alternative))
        self.assertEqual(sum(abs(got_coord - s) for got_coord, s in zip(alternative, (6, 3))), 1)
        self.assertFalse(got['planner_authorized'])


if __name__ == '__main__':
    unittest.main()

