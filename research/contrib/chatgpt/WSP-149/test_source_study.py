"""WSP149 first public-synthetic source study: run ONLY after separate source-free pass."""
from unittest import TestCase
import source as S
import experiment as E

class WSP149OriginalSourceStudy(TestCase):
    def test_03_single_frozen_first_public_synthetic_study(self):
        result=E.run()
        print('WSP149_RESULT_JSON='+S.canon(result))
        self.assertIn(result['status'],(
            'DEVELOPMENT_EXACT_WEIGHT_MEMORY_TRANSFER_SUPPORTED',
            'DEVELOPMENT_EXACT_WEIGHT_MEMORY_TRANSFER_NO_GO'))
        self.assertFalse(result['scientific_pass'])
        self.assertFalse(result['native_admission'])
        self.assertEqual(result['all_exact_fits_32_effects'],192)
        self.assertEqual(result['source_safe_charged_public_effects'],6144)
        self.assertEqual(result['protected_original_effects'],0)
        self.assertEqual(result['cohorts'],
                         {'fit':16,'transfer':32,'known':8,'off':8})
        self.assertEqual(result['per_policy_charged_source_effects'],
                         {p:2048 for p in E.POLICIES})
        self.assertEqual(result['fit_experience_count_each_arm'],
                         {p:16 for p in E.POLICIES})
        self.assertEqual(result['cold_relabel_512'],
                         {p:512 for p in E.POLICIES})
        self.assertEqual(result['postseal_queryblind_held_per_world'],8)
        self.assertTrue(result['all_64_predictions_committed_before_any_held_selection'])
        self.assertEqual(len(result['per_world']),64)
        for family,n in result['cohorts'].items():
            for p in E.POLICIES:
                for model in E.METHODS:
                    a=result['scores'][family][p][model]['paired']
                    self.assertEqual(a['held'],n*8)
                    self.assertEqual(a['correct']+a['wrong_confident']+
                                     a['abstained'],n*8)
