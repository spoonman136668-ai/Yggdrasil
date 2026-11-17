"""WSP137 fixed/policy matched-input public development and strict source fences."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import policy as P
import controls as C
import experiment as E

class ActiveStructureDevelopmentTests(TestCase):
    def test_protected_source_fence_before_any_rng(self):
        self.assertEqual(len(S.KNOWN),12)
        self.assertEqual(len(S.UNFAMILIAR),12)
        self.assertEqual(len(S.OFF),8)
        self.assertEqual(len(S.TRANSFER),6)
        with patch.object(S.random,'Random',side_effect=AssertionError('UNAUTHORIZED_RNG_CALLED')):
            for seed in (True,False,'198000',197999,198012,198800,199012,199800,
                         200006,200800,201008,201800,194000,195000,196000,190000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn('source',P.__dict__)
        self.assertNotIn('source',C.__dict__)
        self.assertEqual(len(P.N.templates()),17640)
        self.assertEqual(len(C.BASE.codebooks()),17640)
    def test_paired_holdout_and_budgeted_actual_feedback(self):
        self.assertEqual(len(P.common_held()),16)
        self.assertEqual(len(P.available_pool()),48)
        self.assertTrue(set(P.fixed_schedule())<=P.available_pool())
        self.assertFalse(set(P.fixed_schedule())&P.common_held())
        v=S.world(198000)
        c=S.Custodian(v,198000)
        m=P.DirectArm('active')
        for i in range(5):
            x=m.choose(v,P.available_pool())
            self.assertNotIn(x,P.common_held())
            e=c.query(v.subject(x))
            m.observe(v,e,P.available_pool())
        self.assertEqual(len(c.events),5)
        with self.assertRaises(PermissionError):c.query(c.events[0][1])
        self.assertIsNone(m.infer(v,v.subject(0)))  # require all 32 before readout
        t=S.world(200000)
        with self.assertRaises(PermissionError):S.Custodian(t,200000).query(t.subject(0))
        self.assertEqual(t.law_id,v.law_id)
    def test_complete_precommitted_source_safe_comparison(self):
        v=E.run()
        print('WSP137_RESULT_JSON='+S.canon(v))
        self.assertFalse(v['scientific_pass'])
        self.assertFalse(v['native_admission'])
        self.assertFalse(v['genuine_new_primitive_invented'])
        self.assertEqual(v['original_external_source_actions'],0)
        self.assertEqual(v['source_calls_by_policy'],{'fixed':1024,'active':1024})
        self.assertEqual(v['source_safe_total_synthetic_effects'],2048)
        self.assertEqual(v['transfer_identical'],{'fixed':384,'active':384})
        self.assertTrue(v['independent_symbolic_action_and_prediction_parity'])
        self.assertTrue(v['all_old_known_readouts_unchanged'])
        self.assertTrue(v['cold_restore'])
        self.assertEqual(len(v['shared_held']),16)
        self.assertEqual(v['eligible_source_actions'],48)
        self.assertEqual(v['family_worlds'],{'known':12,'unfamiliar':12,'off':8,'transfer':6})
        for family,n in (('known',12),('unfamiliar',12),('off',8)):
            for policy in ('fixed','active'):
                for arm in E.MODELS:
                    for key,held in (('common',16*n),('arm_unqueried',32*n)):
                        s=v['scores'][family][policy][arm][key]
                        self.assertEqual(s['held'],held)
                        self.assertEqual(s['correct']+s['wrong_confident']+s['abstained'],held)
                self.assertEqual(v['scores'][family][policy]['numeric'],
                                 v['scores'][family][policy]['symbolic'])
        self.assertEqual(v['source_oracle_membership']['known'],12)
        self.assertEqual(v['source_oracle_membership']['unfamiliar'],12)
        self.assertIn(v['status'],('DEVELOPMENT_ACTIVE_SELECTION_SUPPORTED','DEVELOPMENT_ACTIVE_SELECTION_NO_GO'))
