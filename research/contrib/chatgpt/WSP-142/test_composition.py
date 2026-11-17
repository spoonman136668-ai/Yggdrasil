"""Frozen WSP142 new-interaction original public source-safe development tests."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import direct_weights as D
import symbolic_control as C
import experiment as E

class SparseRelationshipInductionTests(TestCase):
    def test_protected_original_and_other_seeds_denied_before_rng(self):
        self.assertEqual(len(S.KNOWN),8)
        self.assertEqual(len(S.UNFAMILIAR),16)
        self.assertEqual(len(S.SWITCH),16)
        self.assertEqual(len(S.OFF),8)
        self.assertEqual(len(S.TRANSFER),4)
        self.assertFalse(S.PROTECTED&S.ALLOWED)
        with patch.object(S.random,"Random",
                          side_effect=AssertionError("FORBIDDEN_RNG_BEFORE_FENCE")):
            for seed in (True,False,"240000",239999,240008,240800,241016,
                         241800,242016,242800,243008,243800,
                         244004,244800,230000,231000,232000,233000,
                         234000,203000,214000,245000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",D.__dict__)
        self.assertNotIn("source",C.__dict__)
    def test_generic_features_and_equal_information_symbolic_not_source_grammar(self):
        self.assertEqual(D.FEATURES,tuple(range(63)))
        self.assertEqual(len(E.N.schedule()),32)
        self.assertEqual(len(E.N.templates()),17640)
        # Independent public synthetic unit fixture: not a WSP142 source family
        # or a scored original source, just raw observed x/effect labels.
        samples=tuple((x, ((x&3)==3) ^ ((x>>2)&1))
                      for x in E.N.schedule())
        numeric=D.fit(samples)
        symbolic=C.symbolic_fit(samples)
        self.assertEqual(numeric,symbolic)
        self.assertTrue(len(numeric)>0)
        for x in range(64):
            self.assertEqual(D.predict(numeric,x),C.symbolic_predict(symbolic,x))
        with self.assertRaises(ValueError):D.fit(samples[:-1])
        with self.assertRaises(ValueError):C.symbolic_fit(samples[:-1])
        with self.assertRaises(ValueError):D.predict(numeric,64)
        with self.assertRaises(ValueError):C.symbolic_predict(symbolic,64)
    def test_one_shot_source_budget_and_zero_call_cold_view(self):
        v=S.world(240000)
        c=S.Custodian(v,240000)
        with self.assertRaises(PermissionError):
            c.score_once({})
        e=c.query(v.subject(0))
        self.assertEqual(e.input,0)
        with self.assertRaises(PermissionError):
            c.query(v.subject(0))
        t=S.world(244000)
        self.assertEqual(t.law_id,v.law_id)
        tc=S.Custodian(t,244000)
        self.assertEqual(tc.budget,0)
        with self.assertRaises(PermissionError):
            tc.query(t.subject(0))
    def test_original_frozen_source_safe_research_trial(self):
        r=E.run()
        print("WSP142_RESULT_JSON="+S.canon(r))
        self.assertEqual(r["source_calls"],1536)
        self.assertEqual(r["cohorts"],{"known":8,"three":16,"five":16,"off":8,"zero_effect_cold":4})
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_yggdrasil_qualified"])
        self.assertEqual(r["original_firstuse_source_effects"],0)
        self.assertTrue(r["generic_and_xor_primitives_presupplied"])
        self.assertTrue(r["no_predefined_complete_relationships"])
        self.assertTrue(r["source_blind_equal_information_symbolic_exact_tie"])
        self.assertEqual(len(r["per_world"]),48)
        self.assertEqual(r["feature_dictionary_size"],63)
        self.assertEqual(r["max_induced_sparse_terms"],3)
        self.assertTrue(r["previous_known_world_predictions_preserved"])
        self.assertEqual(r["cold_relabel_exact_identity"],
              {"direct":256,"independent_symbolic":256,"wsp135":256,"cart":256})
        for family,nworlds in (("known",8),("three",16),("five",16),("off",8)):
            for model in E.METHODS:
                for split,nper in (("future",16),("all_unseen",32)):
                    s=r["scores"][family][model][split]
                    self.assertEqual(s["held"],nworlds*nper)
                    self.assertEqual(s["held"],s["correct"]+s["wrong_confident"]+s["abstained"])
            self.assertEqual(r["scores"][family]["direct"],
                             r["scores"][family]["independent_symbolic"])
        self.assertIn(r["status"],(
           "DEVELOPMENT_NEW_CAUSAL_COMPOSITION_NO_GO",
           "DEVELOPMENT_NEW_CAUSAL_COMPOSITION_SUPPORTED"))
