"""WSP136 frozen public-only same-source oracle gap verification."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import experiment as E

class SameSourceGapTests(TestCase):
    def test_protected_original_seeds_denied_before_rng(self):
        with patch.object(S.random,'Random',side_effect=AssertionError('UNAUTHORIZED_RNG')):
            for seed in (True,False,'194000',193999,194012,195012,196006,194800,195800,196800,197800,190000,191000,192000,178000,179000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertEqual(len(S.KNOWN),12)
        self.assertEqual(len(S.UNFAMILIAR),12)
        self.assertEqual(len(S.TRANSFER),6)
        self.assertFalse(S.KNOWN&S.UNFAMILIAR)
        self.assertNotIn('source',E.N.__dict__)
        self.assertNotIn('source',E.C.__dict__)
        self.assertNotIn('source',E.O.__dict__)
    def test_custodian_counts_and_no_uncertain_replay(self):
        v=S.world(194000)
        c=S.Custodian(v,194000)
        self.assertFalse(hasattr(v,'seed'))
        self.assertFalse(hasattr(v,'hidden_operator'))
        for x in E.N.schedule():c.query(v.subject(x))
        self.assertEqual(len(c.events),32)
        with self.assertRaises(PermissionError):c.query(v.subject(E.N.schedule()[0]))
        with self.assertRaises(PermissionError):c.query(v.subject(0))
        t=S.world(196000)
        with self.assertRaises(PermissionError):S.Custodian(t,196000).query(t.subject(0))
        self.assertEqual(t.law_id,v.law_id)
    def test_frozen_mixed_prior_result_and_cold_replay(self):
        v=E.run()
        print('WSP136_RESULT_JSON='+S.canon(v))
        self.assertFalse(v['scientific_pass'])
        self.assertFalse(v['native_admission'])
        self.assertTrue(v['same_information_symbolic_parity'])
        self.assertTrue(v['cold_restore'])
        self.assertTrue(v['old_laws_unchanged'])
        self.assertEqual(v['source_membership_count'],24)
        self.assertEqual(v['synthetic_source_actions'],768)
        self.assertEqual(v['original_source_actions'],0)
        self.assertEqual(v['zero_call_identical_readouts'],384)
        self.assertEqual(v['worlds'],{'known':12,'unfamiliar':12,'transfer':6})
        for fam,held,actions in (('known',384,384),('unfamiliar',384,384),('transfer',384,0)):
            for arm in E.ARMS:
                d=v['scores'][fam][arm]
                self.assertEqual(d['held'],held)
                self.assertEqual(d['source_calls'],actions)
                self.assertEqual(d['held'],d['correct']+d['wrong_confident']+d['abstained'])
            self.assertEqual(v['scores'][fam]['DIRECT_LATENT'],v['scores'][fam]['SAME_PRIOR_SYMBOLIC'])
        self.assertIn(v['status'],('DEVELOPMENT_REPRESENTATION_GAP_CLOSED','DEVELOPMENT_REPRESENTATION_GAP_OPEN'))
