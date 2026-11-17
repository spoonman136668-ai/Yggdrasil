"""WSP139 new-cohort query-blind generalization, source fences and frozen gates."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import experiment as E

class QueryBlindGeneralizationTests(TestCase):
    def test_original_science_and_other_cohorts_denied_before_rng(self):
        self.assertEqual(len(S.KNOWN),8)
        self.assertEqual(len(S.UNFAMILIAR),8)
        self.assertEqual(len(S.SWITCH),8)
        self.assertEqual(len(S.OFF),4)
        self.assertEqual(len(S.TRANSFER),4)
        self.assertFalse(S.ALLOWED & S.PROTECTED)
        with patch.object(S.random,'Random',side_effect=AssertionError('UNAUTHORIZED_RNG_CALLED')):
            for seed in (True,False,'210000',209999,210008,210800,211008,211800,
                         212008,212800,213004,213800,214004,214800,
                         198000,199000,200000,201000,202000,203000,204000,205000,206000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn('source',E.P.__dict__)
        self.assertNotIn('source',E.C.__dict__)
    def test_original_wsp137_active_chooser_has_all64_actions_available(self):
        v=S.world(210000)
        self.assertEqual(len(v.records),64)
        self.assertEqual(len(v.legal),64)
        self.assertEqual(E.ALL,frozenset(range(64)))
        self.assertEqual(len(E.P.fixed_schedule()),32)
        a=E.SourceBlindArm('active')
        c=S.Custodian(v,210000)
        for i in range(5):
            x=a.choose()
            self.assertTrue(x in E.ALL)
            e=c.query(v.subject(x))
            a.observe(e)
        self.assertEqual(len(c.events),5)
        with self.assertRaises(PermissionError):c.query(c.events[0][1])
        transfer=S.world(214000)
        self.assertEqual(transfer.law_id,v.law_id)
        with self.assertRaises(PermissionError):S.Custodian(transfer,214000).query(transfer.subject(0))
    def test_exact_original_source_safe_frozen_trial(self):
        r=E.run()
        print("WSP139_RESULT_JSON="+S.canon(r))
        self.assertEqual(r['source_calls_by_policy'],{'active':896,'fixed':896})
        self.assertEqual(r['total_charged_synthetic_actions'],1792)
        self.assertEqual(r['worlds'],{'known':8,'unfamiliar':8,'switch':8,'off':4,'transfer':4})
        self.assertTrue(r['future_query_positions_chosen_after_both_policies'])
        self.assertTrue(r['no_preexcluded_test_x'])
        self.assertTrue(r['paired_selection_conditioned_on_common_unseen'])
        self.assertFalse(r['scientific_pass'])
        self.assertFalse(r['native_admission'])
        self.assertEqual(r['firstuse_original_effects'],0)
        self.assertEqual(r['transfer_identity'],{'fixed':256,'active':256})
        self.assertTrue(r['old_known_state_unchanged'])
        self.assertTrue(r['independent_symbolic_parity'])
        self.assertTrue(r['cold_recomputed'])
        self.assertEqual(r['source_oracle_membership']['known'],8)
        self.assertEqual(r['source_oracle_membership']['unfamiliar'],8)
        self.assertEqual(len(r['per_world']),28)
        for f,n in (('known',8),('unfamiliar',8),('switch',8),('off',4)):
            for policy in ('fixed','active'):
                for method in E.ARMS:
                    for label,cap in (('paired',12*n),('arm_unqueried',32*n)):
                        s=r['scores'][f][policy][method][label]
                        self.assertLessEqual(s['held'],cap)
                        self.assertEqual(s['held'],s['correct']+s['wrong_confident']+s['abstained'])
                self.assertEqual(r['scores'][f][policy]['numeric'],r['scores'][f][policy]['symbolic'])
        for world in r['per_world']:
            self.assertLessEqual(world['paired_count'],12)
            self.assertEqual(world['paired_count'],min(12,world['common_unseen_count']))
            self.assertGreaterEqual(world['common_unseen_count'],4)  # first four qualified WSP137 actions identical
        self.assertIn(r['status'],('DEVELOPMENT_POSTACTION_QUERYBLIND_SUPPORTED',
                                  'DEVELOPMENT_POSTACTION_QUERYBLIND_NO_GO'))
