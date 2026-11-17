"""WSP143: prospective four-term + generic rare-interaction witness guards."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import direct_weights as D
import symbolic_control as C
import experiment as E

class FourTermWitnessTests(TestCase):
    def test_protected_scientific_firstuse_and_unregistered_seeds_refused_before_rng(self):
        self.assertEqual(len(S.KNOWN),8)
        self.assertEqual(len(S.UNFAMILIAR),16)
        self.assertEqual(len(S.SWITCH),16)
        self.assertEqual(len(S.OFF),8)
        self.assertEqual(len(S.TRANSFER),4)
        self.assertFalse(S.ALLOWED&S.PROTECTED)
        with patch.object(S.random,"Random",
             side_effect=AssertionError("WSP143_UNAUTHORIZED_RNG")):
            for seed in (True,False,"250000",249999,250008,250800,251016,
                         251800,252016,252800,253008,253800,
                         254004,254800,240000,241000,242000,243000,244000,
                         230000,231000,232000,233000,234000,255000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",D.__dict__)
        self.assertNotIn("source",C.__dict__)
    def test_four_term_public_fixture_matches_fully_independent_symbolic(self):
        self.assertEqual(D.FEATURES,tuple(range(63)))
        self.assertEqual(len(D.FIVE_MASKS),6)
        self.assertEqual(len(E.N.schedule()),32)
        self.assertEqual(len(E.N.templates()),17640)
        # Public no-source fixture, NOT a WSP143 scored cohort.
        rows=tuple((x,int((x&7)==7)^int((x&12)==12)^((x>>4)&1)^1)
                   for x in E.N.schedule())
        numeric=D.fit(rows)
        symbolic=C.solve(rows)
        self.assertEqual(numeric,symbolic)
        self.assertTrue(numeric[0])
        for x,y in rows:
            self.assertEqual(D.predict(numeric,x),y)
        for x in range(64):
            self.assertEqual(D.predict(numeric,x),C.infer(symbolic,x))
        self.assertTrue(D.witness_missing(63,tuple(range(32))))
        self.assertFalse(D.witness_missing(7,tuple(range(32))))
        with self.assertRaises(ValueError):D.fit(rows[:-1])
        with self.assertRaises(ValueError):C.solve(rows[:-1])
        with self.assertRaises(ValueError):D.predict(numeric,64)
        with self.assertRaises(ValueError):C.infer(symbolic,64)
    def test_actual_source_has_32_paid_effects_only_and_cold_no_effects(self):
        view=S.world(250000)
        c=S.Custodian(view,250000)
        with self.assertRaises(PermissionError):c.score_once({})
        e=c.query(view.subject(0))
        self.assertEqual(e.input,0)
        with self.assertRaises(PermissionError):c.query(view.subject(0))
        cold=S.world(254000)
        self.assertEqual(cold.law_id,view.law_id)
        self.assertEqual(S.Custodian(cold,254000).budget,0)
        with self.assertRaises(PermissionError):
            S.Custodian(cold,254000).query(cold.subject(0))
    def test_frozen_source_safe_development_and_negative_thresholds(self):
        r=E.run()
        print("WSP143_RESULT_JSON="+S.canon(r))
        self.assertEqual(r["source_calls"],1536)
        self.assertEqual(r["cohorts"],{"known":8,"three":16,"five":16,"off":8,"zero_effect_cold":4})
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_yggdrasil_qualified"])
        self.assertEqual(r["original_firstuse_source_effects"],0)
        self.assertTrue(r["rare_five_way_witness_guard"])
        self.assertTrue(r["original_wsp142_three_term_frozen_baseline"])
        self.assertTrue(r["source_blind_equal_information_symbolic_exact_tie"])
        self.assertTrue(r["previous_known_world_predictions_preserved"])
        self.assertEqual(r["max_induced_sparse_terms"],4)
        self.assertEqual(r["feature_dictionary_size"],63)
        self.assertEqual(len(r["per_world"]),48)
        self.assertEqual(r["cold_relabel_exact_identity"],
          {"direct":256,"independent_symbolic":256,"original_three":256,
           "wsp135":256,"cart":256})
        for fam,nworlds in (("known",8),("three",16),("five",16),("off",8)):
            for method in E.METHODS:
                for name,count in (("future",16),("all_unseen",32)):
                    s=r["scores"][fam][method][name]
                    self.assertEqual(s["held"],nworlds*count)
                    self.assertEqual(s["held"],s["correct"]+s["wrong_confident"]+s["abstained"])
            self.assertEqual(r["scores"][fam]["direct"],r["scores"][fam]["independent_symbolic"])
        self.assertIn(r["status"],
          ("DEVELOPMENT_FOUR_TERM_WITNESS_SUPPORTED","DEVELOPMENT_FOUR_TERM_WITNESS_NO_GO"))
