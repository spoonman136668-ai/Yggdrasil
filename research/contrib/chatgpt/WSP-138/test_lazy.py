"""WSP138 exact selector behavior/performance and source custody."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import source as S
import selector as L
import experiment as E

class LazyOptimizationGate(unittest.TestCase):
    def test_guard_before_rng_for_original_and_unleased_sources(self):
        self.assertEqual(len(S.KNOWN),12)
        self.assertEqual(len(S.UNFAMILIAR),12)
        self.assertEqual(len(S.OFF),8)
        self.assertEqual(len(S.TRANSFER),6)
        with patch.object(S.random,'Random',side_effect=AssertionError('FORBIDDEN_RNG')):
            for seed in (True,False,"202000",201999,202012,203012,205008,204006,
                         202800,203800,204800,205800,198000,199000,201000,
                         194000,195000,190000,179000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn('source',L.__dict__)
        self.assertEqual(len(L.N.templates()),17640)
        self.assertEqual(len(L.original_ranked()),17640)
    def test_existing_original_contract_unmodified(self):
        self.assertEqual(len(L.available_pool()),48)
        self.assertEqual(len(L.common_held()),16)
        self.assertFalse(L.common_held()&L.available_pool())
        self.assertEqual(L.BASE.SCHEMA,'wsp137.active-sourceblind-latent.v1')
        self.assertTrue(issubclass(L.FastArm,L.BASE.DirectArm))
        v=S.world(202000)
        with self.assertRaises(PermissionError):S.Custodian(S.world(204000),204000).query(S.world(204000).subject(0))
        receipt=L.BASE.digest([v.fingerprint(),'begin'])
        a=L.BASE.DirectArm('active')
        b=L.FastArm('active')
        for k in range(4):
            x=a.choose(v,L.available_pool())
            self.assertEqual(x,b.choose(v,L.available_pool()))
            y=((x>>2)^(x>>3))&1 # MADE-UP PUBLIC UNIT DATA, NOT SOURCE EFFECT
            row=[v.law_id,v.subject(x),x,y]
            receipt=L.BASE.digest([receipt,row])
            e=SimpleNamespace(law_id=v.law_id,subject=v.subject(x),input=x,effect=y,receipt=receipt)
            a.observe(v,e,L.available_pool())
            b.observe(v,e,L.available_pool())
        self.assertEqual(a.states[v.law_id]['chooser'].events,b.states[v.law_id]['chooser'].events)
        self.assertIsNone(a.infer(v,v.subject(0)))
        self.assertIsNone(b.infer(v,v.subject(0)))
        # No positive source Custodian.query in source-free unit controls.
    def test_actual_frozen_new_source_same_outcomes(self):
        r=E.run()
        print('WSP138_RESULT_JSON='+S.canon(r))
        self.assertFalse(r['scientific_pass'])
        self.assertFalse(r['native_admission'])
        self.assertFalse(r['original_source_firstuse'])
        self.assertTrue(r['exact_full64_action_and_prediction_parity'])
        self.assertTrue(r['same_info_symbolic_prediction_parity'])
        self.assertTrue(r['cold_restore_byte_identical'])
        self.assertTrue(r['frozen_known_laws_preserved'])
        self.assertEqual(r['source_safe_calls'],1024)
        self.assertEqual(r['original_external_source_calls'],0)
        self.assertEqual(r['zero_action_transfer_same'],384)
        self.assertEqual(r['family_worlds'],{'known':12,'unfamiliar':12,'off':8,'transfer':6})
        self.assertEqual(sum(r['paired_scores'][x]['full_held']['held']
                             for x in ('known','unfamiliar','off')),1024)
        self.assertEqual(r['cost']['original_mutable_structural_bytes']>0,True)
        self.assertEqual(r['cost']['lazy_mutable_structural_bytes']>0,True)
        self.assertIn(r['status'],
          ('DEVELOPMENT_COST_OPTIMIZATION_SUPPORTED_PLATFORM',
           'DEVELOPMENT_COST_OPTIMIZATION_NO_GO_PLATFORM'))
        for name in ('known','unfamiliar','off'):
            self.assertEqual(r['matched_controls'][name]['symbolic'],
                             r['paired_scores'][name]['common'])
