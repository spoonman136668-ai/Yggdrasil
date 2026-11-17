"""WSP135 source-safe public identifiability preflight and negative controls."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import oracle as O
import controls as C
import experiment as E

class IdentifiabilityPreflightTests(TestCase):
    def test_unregistered_and_original_science_denied_before_rng(self):
        self.assertFalse(S.ALLOWED & S.PROTECTED)
        self.assertEqual(len(S.KNOWN),64)
        self.assertEqual(len(S.UNFAMILIAR),32)
        with patch.object(S.random,"Random",side_effect=AssertionError("RNG_ON_DENIED_SOURCE")):
            for seed in (True,False,-1,"178000",169000,170000,171000,
                         174000,175000,176000,177000,177063,
                         178064,178800,178863,179032,179800,179831,
                         180000,180063,181000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",O.__dict__)
        self.assertNotIn("source",C.__dict__)
    def test_explicit_source_visibility_and_effect_budget(self):
        v=S.world(178000)
        self.assertFalse(hasattr(v,"seed"))
        self.assertFalse(hasattr(v,"truth"))
        self.assertFalse(hasattr(v,"source_operator"))
        self.assertEqual(len(v.records),64)
        self.assertEqual({x for s,x in v.records},set(range(64)))
        self.assertEqual({s for s,x in v.records},v.legal)
        cu=S.Custodian(v,178000)
        with self.assertRaises(PermissionError):S.Custodian(v,179000)
        for x in range(32):
            e=cu.query(v.subject(x))
            self.assertEqual(e.input,x)
            self.assertIn(e.effect,(0,1))
        self.assertEqual(len(cu.held()),32)
        with self.assertRaises(PermissionError):cu.query(v.subject(32))
        self.assertEqual(cu.score_once({s:None for s,x in cu.held()})["abstained"],32)
        with self.assertRaises(PermissionError):cu.score_once({})
    def test_oracle_is_source_blind_and_conservatively_unanimous(self):
        o=O.ExactOracle((0,(1<<64)-1))
        s=o.begin()
        self.assertIsNone(s.infer(13))
        self.assertEqual(s.adaptive_action(),0)
        s.observe(0,1)
        self.assertEqual(s.infer(13),1)
        self.assertEqual(s.restore().snapshot(),s.snapshot())
        with self.assertRaises(ValueError):s.observe(0,0)
    def test_original_new_world_preflight(self):
        result=E.run_development()
        print("WSP135_SOURCE_SAFE_JSON="+S.canonical(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["original_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["source_true_law_membership_count"],96)
        self.assertTrue(result["independent_oracle_bank_match"])
        self.assertEqual(result["source_calls_per_world_arm"],32)
        self.assertEqual(result["source_worlds"],{"known":64,"unfamiliar":32})
        self.assertGreater(result["oracle_unique_truth_tables"],100)
        for group,worlds in (("known",64),("unfamiliar",32)):
            for arm in E.ARMS:
                r=result["scores"][group][arm]
                self.assertEqual(r["held"],worlds*32)
                self.assertEqual(r["source_calls"],worlds*32)
                self.assertEqual(r["held"],r["correct"]+r["abstained"]+r["wrong_confident"])
                self.assertEqual(r["wrong_confident"],0)
        self.assertIn(result["status"],("IDENTIFIABLE_WITH_GIVEN_GRAMMAR",
                                        "UNDERIDENTIFIED_WITH_GIVEN_GRAMMAR"))
