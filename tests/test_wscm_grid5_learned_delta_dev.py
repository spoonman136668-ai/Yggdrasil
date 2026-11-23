"""Disclosed 120-map DEV regression, not scientific holdout or source use.

Only evaluator knows the hidden role map; native readout receives exactly five
public witnessed state/action/next-state triples. Each case is already consumed
development material. No original environment is imported or stepped.
"""
import itertools
import unittest

from test_native_grid5_evidence_dev import receipt
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence


_PUBLIC_ROLE_DELTAS = ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))


def evaluator_only_step(state, hidden_role):
    dx, dy = _PUBLIC_ROLE_DELTAS[hidden_role]
    return (max(0, min(8, state[0] + dx)),
            max(0, min(8, state[1] + dy)))


class LearnedDeltaDevelopmentScreen(unittest.TestCase):
    def test_disclosed_120_mapping_source_free_screen(self):
        total = correct = incorrect = abstained = 0
        for world in itertools.permutations(range(5)):
            # Fixed source-free protocol: start at corner; actions 0..4 once.
            m = NativeGrid5Evidence()
            state = (0, 0)
            seen = set()
            for action in range(5):
                after = evaluator_only_step(state, world[action])
                m = m.observe_public_receipt(*receipt(
                    action, act=action, before=state, after=after))
                seen.add((state, action))
                state = after
            for x in range(9):
                for y in range(9):
                    state = (x, y)
                    for action in range(5):
                        if (state, action) in seen:
                            continue
                        total += 1
                        expected = evaluator_only_step(state, world[action])
                        got = m.public_learned_delta_forecast(
                            [x, y], action, episode_id='a'*64)
                        pred = got['predicted_next_state']
                        if pred is None:
                            abstained += 1
                        elif tuple(pred) == expected:
                            correct += 1
                            self.assertEqual(got['status'], 'HYPOTHESIS')
                        else:
                            incorrect += 1
        self.assertEqual(total, 48000)
        self.assertEqual(incorrect, 0)
        self.assertGreater(correct, 0)
        self.assertEqual(correct + abstained, total)
        print('WSCM_DELTA_DEV_120_WORLDS '
              'correct=%s incorrect=%s abstain=%s coverage=%.8f '
              'reference_fitted_delta=0.62666667 '
              'reference_known_physics_exact=0.75600000' %
              (correct, incorrect, abstained, correct / total))


if __name__ == '__main__':
    unittest.main()
