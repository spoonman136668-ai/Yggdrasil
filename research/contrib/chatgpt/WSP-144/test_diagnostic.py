"""WSP144 high-order diagnostic interventions: prospective source-safe controls."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import experiment as E

class HighOrderDiagnosticSourceSafeTests(TestCase):
    def test_01_source_denial_before_rng_and_no_learner_source_import(self):
        self.assertEqual((len(S.KNOWN),len(S.UNFAMILIAR),len(S.SWITCH),
                          len(S.CROSS),len(S.OFF),len(S.TRANSFER)),(8,8,16,8,8,4))
        self.assertFalse(S.PROTECTED&S.ALLOWED)
        for learner in (E.H,E.F,E.D,E.N,E.C):
            self.assertNotIn('source',learner.__dict__)
        with patch.object(S.random,'Random',side_effect=AssertionError('SOURCE_FENCE_MUST_FAIL_BEFORE_RNG')):
            for seed in (True,False,'260000',259999,260008,260800,
                   261008,261800,262016,262800,263008,263800,
                   264008,264800,265004,265800,250000,251000,252000,
                   241000,241016,198000,996100,996600,266000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
    def test_02_three_source_blind_action_policies_share_unqueried_questions(self):
        fixed,diagnostic,held,eligible=E.schedules()
        self.assertEqual(len(fixed),32)
        self.assertEqual(len(diagnostic),32)
        self.assertEqual(len(held),16)
        self.assertEqual(len(eligible),48)
        self.assertTrue({31,55,62}<=set(held))
        self.assertEqual(set(held),set(S.COMMON_PUBLIC_HELD))
        self.assertTrue({47,59,61,63}<=set(diagnostic))
        self.assertFalse(63 in fixed)
        self.assertFalse(set(held)&set(fixed))
        self.assertFalse(set(held)&set(diagnostic))
        self.assertEqual([sum((x&m)==m for x in fixed)
                         for m in (31,47,55,59,61,62)],[0,1,0,0,0,0])
        self.assertEqual([sum((x&m)==m for x in diagnostic)
                         for m in (31,47,55,59,61,62)],[1,2,1,2,2,1])
        for seed in (260000,261000,262000,262015,264007):
            rand=E.choose_random(S.world(seed),eligible)
            v=S.world(seed)
            self.assertEqual(v.legal,frozenset(v.subject(x) for x in eligible))
            self.assertEqual(len(rand),32)
            self.assertEqual(len(set(rand)),32)
            self.assertFalse(set(rand)&set(held))
            self.assertTrue(set(rand)<=set(eligible))
    def test_03_original_frozen_new_public_source_three_arm_trial(self):
        r=E.run()
        print('WSP144_RESULT_JSON='+S.canon(r))
        self.assertIn(r['status'],('DEVELOPMENT_DIAGNOSTIC_HIGHORDER_ACQUISITION_SUPPORTED',
                                  'DEVELOPMENT_DIAGNOSTIC_HIGHORDER_ACQUISITION_NO_GO'))
        self.assertFalse(r['scientific_pass'])
        self.assertFalse(r['native_model_promoted'])
        self.assertEqual(r['original_protected_first_use'],0)
        self.assertEqual(r['new_public_source_effects'],4608)
        self.assertEqual(r['source_actions_per_arm'],{m:1536 for m in E.POLICIES})
        self.assertEqual(r['cohorts'],{'known':8,'three':8,'five':16,'cross':8,'off':8})
        self.assertEqual(r['cold_relabel_exact_identity'],{p:256 for p in E.POLICIES})
        self.assertTrue(r['full_same_information_symbolic_prediction_parity'])
        self.assertTrue(r['previous_known_knowledge_unchanged'])
        self.assertEqual(len(r['per_world']),48*3)
        self.assertEqual(len(r['common_held_inputs']),16)
        self.assertEqual(sum(v['held'] for v in (
              r['scores'][f]['diagnostic']['hierarchical']['paired']
              for f in r['cohorts'])),48*16)
        for family,n in r['cohorts'].items():
            for p in E.POLICIES:
                for method in E.METHODS:
                    for split,denom in (('paired',16*n),('unseen32',32*n)):
                        row=r['scores'][family][p][method][split]
                        self.assertEqual(row['held'],denom)
                        self.assertEqual(row['correct']+row['wrong_confident']+row['abstained'],denom)
                self.assertEqual(r['scores'][family][p]['hierarchical'],
                                 r['scores'][family][p]['equal_prior_symbolic'])
