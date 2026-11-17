"""WSP141 frozen prospective independent future-query and random32 controls."""
from unittest import TestCase
from unittest.mock import patch
import source as S
import experiment as E

class ThreePolicyFutureTaskTests(TestCase):
    def test_all_protected_and_other_cohorts_denied_before_rng(self):
        self.assertEqual(len(S.KNOWN),8)
        self.assertEqual(len(S.UNFAMILIAR),8)
        self.assertEqual(len(S.SWITCH),8)
        self.assertEqual(len(S.OFF),4)
        self.assertEqual(len(S.TRANSFER),4)
        self.assertFalse(S.ALLOWED & S.PROTECTED)
        with patch.object(S.random,"Random",side_effect=AssertionError("FORBIDDEN_RNG_CALLED")):
            for seed in (True,False,"230000",220000,221000,222000,223000,224000,
                         230008,230800,230863,231008,231800,
                         232008,232800,233004,233800,234004,234800,235000):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",E.P.__dict__)
        self.assertNotIn("source",E.C.__dict__)
    def test_three_separate_source_blind_policies_and_unconditional_future_tasks(self):
        view=S.world(230000)
        self.assertEqual(E.ALL,frozenset(range(64)))
        self.assertEqual(len(view.records),64)
        self.assertEqual(len(view.legal),64)
        self.assertEqual(len(E.P.fixed_schedule()),32)
        rand=E.random_schedule(view.law_id)
        self.assertEqual(len(rand),32)
        self.assertEqual(len(set(rand)),32)
        self.assertEqual(rand,E.random_schedule(view.law_id))
        self.assertNotEqual(rand,tuple(E.P.fixed_schedule()))
        future=E.future_questions(230000)
        self.assertEqual(len(future),16)
        self.assertEqual(len(set(future)),16)
        self.assertEqual(future,E.future_questions(230000))
        for name in E.POLICIES:
            arm=E.Arm(name,view)
            x=arm.choose()
            self.assertIn(x,E.ALL)
            self.assertTrue(arm.out is None)
        transfer=S.world(234000)
        self.assertEqual(transfer.law_id,view.law_id)
        with self.assertRaises(PermissionError):
            S.Custodian(transfer,234000).query(transfer.subject(0))
        self.assertEqual(len(E.P.N.templates()),17640)
        self.assertEqual(len(E.C.BASE.codebooks()),17640)
    def test_original_source_safe_future_utility_experiment(self):
        r=E.run()
        print("WSP141_RESULT_JSON="+S.canon(r))
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_admission"])
        self.assertFalse(r["original_source_first_use"])
        self.assertTrue(r["future_distribution_independent_of_actions"])
        self.assertTrue(r["future_seen_and_unseen_reported_separately"])
        self.assertTrue(r["random32_independent_of_source_and_future"])
        self.assertEqual(r["source_calls"],{"active":896,"fixed":896,"random":896})
        self.assertEqual(r["total_charged_public_effects"],2688)
        self.assertEqual(r["worlds"],{"known":8,"unfamiliar":8,"switch":8,"off":4,"transfer":4})
        self.assertTrue(r["symbolic_equal_information_tie"])
        self.assertTrue(r["known_readouts_unchanged"])
        self.assertTrue(r["cold_recompute"])
        self.assertEqual(r["transfer_identity"],{"active":256,"fixed":256,"random":256})
        self.assertEqual(r["source_oracle_membership"]["known"],8)
        self.assertEqual(r["source_oracle_membership"]["unfamiliar"],8)
        self.assertEqual(len(r["per_world"]),28)
        for fam,count in (("known",8),("unfamiliar",8),("switch",8),("off",4)):
            for p in E.POLICIES:
                for m in E.MODELS:
                    v=r["scores"][fam][p][m]
                    for label,n in (("future",16*count),("all64",64*count)):
                        a=v[label]
                        self.assertEqual(a["held"],n)
                        self.assertEqual(a["held"],a["correct"]+a["wrong_confident"]+a["abstained"])
                    for label in ("seen","unseen","joint_unseen"):
                        a=v[label]
                        self.assertEqual(a["held"],a["correct"]+a["wrong_confident"]+a["abstained"])
                    self.assertEqual(v["seen"]["held"]+v["unseen"]["held"],16*count)
                self.assertEqual(r["scores"][fam][p]["numeric"],r["scores"][fam][p]["symbolic"])
        for world in r["per_world"]:
            for p in E.POLICIES:
                self.assertEqual(world["arms"][p]["seen_future"]+world["arms"][p]["unseen_future"],16)
        self.assertIn(r["status"],(
          "DEVELOPMENT_RANDOM_CONTROL_FUTURE_UTILITY_SUPPORTED",
          "DEVELOPMENT_RANDOM_CONTROL_FUTURE_UTILITY_NO_GO"))
