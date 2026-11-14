"""Fixture-only controls and first-use safeguards; no PUBLIC/RESERVE scoring."""
import pathlib
import unittest

from controls import SymbolicInducer, PolynomialGradient, TanhGradient
from experiment import METHODS, classify, one_world

HERE = pathlib.Path(__file__).resolve().parent


class WSP98ControlsTests(unittest.TestCase):
    def test_fixture_controls_are_independent_and_source_matched(self):
        # 999 is not in either frozen cohort. This is NOT original research evidence.
        result = one_world(999)
        self.assertEqual(result['queries'], 20)
        self.assertTrue(result['cold_restore'])
        self.assertTrue(result['tamper_rejected'])
        self.assertTrue(result['replay_rejected'])
        self.assertTrue(result['unknown_refused'])
        self.assertEqual(result['predictions_correct']['direct_active'], 120)
        self.assertEqual(result['predictions_correct']['symbolic'], 120)
        self.assertEqual(result['predictions_correct']['polynomial_gradient'], 120)
        self.assertEqual(result['source_fit']['gradient'], 32)
        self.assertEqual(result['source_fit']['neural'], 32)
        self.assertEqual(len(result['pre_scoring_predictions_sha256']), 64)
        self.assertEqual(set(result['predictions_correct']), set(METHODS))

    def test_invalid_task_not_called_learning_failure(self):
        report = {
            'worlds': 20, 'queries': 400, 'passive_rows': 480,
            'active_actions': 160, 'random_actions': 160,
            'diagnostic_queries': 200, 'identifiable_active': 600,
            'identifiable_passive': 600,
            'correct': {'direct_active': 2300, 'passive_only': 1900, 'direct_random': 1900},
            'cold_restores': 20, 'tamper_rejections': 20,
            'replay_rejections': 20, 'unknown_refusals': 20,
            'interleaved_memory': True,
        }
        self.assertEqual(classify(report)['classification'], 'INVALID_UNINFORMATIVE')

    def test_no_original_cohort_first_use_in_any_unit_test(self):
        texts = {name: (HERE/name).read_text(encoding='utf-8')
                 for name in ('core.py','controls.py','experiment.py')}
        self.assertNotIn('98101', '\n'.join(texts.values()))
        self.assertNotIn('98140', '\n'.join(texts.values()))
        self.assertNotIn('one_world(980', texts['experiment.py'])
        self.assertIn("if __name__ == '__main__': main()", texts['experiment.py'])


if __name__ == '__main__':
    unittest.main()
