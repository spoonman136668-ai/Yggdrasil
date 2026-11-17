"""WSP145 source-first-use denial, owner-held seal, true prospective CI study.

Do NOT issue any positive charged source query from ordinary mechanical unit
tests: only the sole frozen 6144-event end-to-end experiment may open source.
"""
from unittest import TestCase
from unittest.mock import patch
import source as S
import selector as P
import experiment as E

class OriginalSourceSafeDevelopment(TestCase):
    def test_01_forbidden_original_worlds_rejected_before_rng(self):
        self.assertEqual((len(S.KNOWN),len(S.UNFAMILIAR),len(S.SWITCH),
                          len(S.CROSS),len(S.OFF),len(S.TRANSFER)),
                         (8,8,32,8,8,8))
        self.assertFalse(S.PROTECTED&S.ALLOWED)
        for module in (P,P.H,E.F,E.D,E.N,E.C):
            self.assertNotIn('source',module.__dict__)
        with patch.object(S.random,'Random',
            side_effect=AssertionError('UNAUTHORIZED_SOURCE_RNG')):
            for seed in (True,False,'270000',269999,270008,270800,
                         271008,271800,272032,272800,273008,273800,
                         274008,274800,275008,275800,260000,262000,
                         250000,251000,272800,996100,996600,198000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
    def test_02_public_64_candidate_choices_and_owner_requires_sealed_effects(self):
        self.assertEqual(len(P.FIXED),32)
        self.assertEqual(len(P.WARM),20)
        self.assertEqual(len(set(P.WARM)),20)
        self.assertEqual(len(P.MASKS),63)
        v=S.world(270000)  # only public opaque IDs, NO paid effect
        self.assertEqual(len(v.legal),64)
        self.assertEqual(set(v.by_x),set(range(64)))
        with self.assertRaises(PermissionError):
            S.OwnerPostCommit(v,270000,{})
        with self.assertRaises(PermissionError):
            S.OwnerPostCommit(v,270000,{'fixed':None,'adaptive':None,'random':None}).score_once({})
        self.assertFalse(S.Custodian(v,270000).events)
        # Crucially: ZERO positive Custodian.query() in any unit fixture.
    def test_03_first_real_new_public_source_qualification(self):
        result=E.run()
        print('WSP145_RESULT_JSON='+S.canon(result))
        self.assertIn(result['status'],(
            'DEVELOPMENT_QUERYBLIND_ACTIVE_DISAMBIGUATION_SUPPORTED',
            'DEVELOPMENT_QUERYBLIND_ACTIVE_DISAMBIGUATION_NO_GO'))
        self.assertFalse(result['scientific_pass'])
        self.assertFalse(result['native_admission'])
        self.assertEqual(result['source_safe_charged_public_effects'],6144)
        self.assertEqual(result['protected_original_effects'],0)
        self.assertEqual(result['cohorts'],
            {'known':8,'three':8,'five':32,'cross':8,'off':8})
        self.assertEqual(result['per_policy_charged_source_effects'],
            {p:2048 for p in E.POLICIES})
        self.assertEqual(result['exact_cold_old_law_retention'],
            {p:512 for p in E.POLICIES})
        self.assertEqual(result['actual_queryblind_unseen_questions_per_world'],8)
        self.assertTrue(result['all_64_predictions_committed_before_any_held_selection'])
        self.assertTrue(result['equal_prior_independent_flat_symbolic_tie_all'])
        self.assertEqual(len(result['per_world']),64)
        for family,nworlds in result['cohorts'].items():
            for policy in E.POLICIES:
                self.assertEqual(result['scores'][family][policy]['hierarchical'],
                                 result['scores'][family][policy]['equal_prior_symbolic'])
                for model in E.METHODS:
                    for split,total in (('paired',8*nworlds),
                                        ('arm_unseen32',32*nworlds)):
                        row=result['scores'][family][policy][model][split]
                        self.assertEqual(row['held'],total)
                        self.assertEqual(row['correct']+row['wrong_confident']+
                                         row['abstained'],total)
