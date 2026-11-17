import unittest
from unittest.mock import patch
import source as S
import learner as N
import controls as C
import experiment as E

class WSP135SourceSafe(unittest.TestCase):
    def test_guard_before_rng(self):
        with patch.object(S.random,'Random',side_effect=AssertionError('PROTECTED_RNG')):
            for seed in (True,False,-1,'190000',179000,189999,190012,190800,191012,191800,192008,192800,193008,193800):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn('source',N.__dict__)
        self.assertNotIn('source',C.__dict__)
        self.assertEqual(len(N.templates()),17640)
    def test_public_actions_and_no_duplicate_source(self):
        v=S.world(190000);cust=S.Custodian(v,190000)
        self.assertFalse(hasattr(v,'seed'))
        self.assertFalse(hasattr(v,'hidden_ops'))
        self.assertEqual(len(v.records),64)
        for x in N.schedule():cust.query(v.subject(x))
        with self.assertRaises(PermissionError):cust.query(v.subject(N.schedule()[0]))
        with self.assertRaises(PermissionError):cust.query(v.subject(0))
        t=S.world(192000)
        with self.assertRaises(PermissionError):S.Custodian(t,192000).query(t.subject(0))
    def test_full_source_safe_frozen_development(self):
        result=E.run()
        print('WSP135_SOURCE_SAFE_RESULT_JSON='+S.canon(result))
        self.assertFalse(result['scientific_pass'])
        self.assertFalse(result['native_admission'])
        self.assertFalse(result['original_source_first_use'])
        self.assertEqual(result['transfer_prediction_identity'],512)
        self.assertEqual(result['resource']['synthetic_actions'],1024)
        self.assertEqual(result['resource']['original_external_actions'],0)
        self.assertIn(result['status'],('DEVELOPMENT_LATENT_FACTOR_SUPPORTED','DEVELOPMENT_LATENT_FACTOR_NO_GO'))
        for key,worlds in (('known',12),('unfamiliar',12),('off',8)):
            for arm in E.ARMS:
                s=result['score'][key][arm]
                self.assertEqual(s['held'],32*worlds)
                self.assertEqual(s['correct']+s['wrong_confident']+s['abstained'],s['held'])
            self.assertEqual(result['score'][key]['LATENT_NUMERIC'],result['score'][key]['INDEPENDENT_SYMBOLIC'])
        self.assertEqual(result['score']['transfer']['LATENT_NUMERIC'],result['score']['transfer']['INDEPENDENT_SYMBOLIC'])
