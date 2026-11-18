"""Source-only negative controls; pilot and primary seeds are NEVER invoked here."""
import importlib.util
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("ckad36_development",HERE/"campaign.py")
c=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class CKAD36Tests(unittest.TestCase):
    def test_frozen_first_use_seed_boundary(self):
        self.assertEqual(c.PILOT,(13961,13962))
        self.assertEqual(c.PRIMARY,(23961,23962,23963))
        self.assertFalse(set(c.PILOT)&set(c.PRIMARY))
        for seed in (*c.PRIMARY,88401):
            with self.assertRaisesRegex(ValueError,"ONLY_FROZEN_PILOT"):
                c.score(seed)

    def test_split_actions_are_input_only_and_sealed_held(self):
        for seed in (88401,88402): # development fixture namespace, not original pilots
            source,initial,held,pool=c.design(seed)
            self.assertEqual([len(source),len(initial),len(held),len(pool)],[42,10,16,38])
            self.assertEqual(len(set(initial+held+pool)),64)
            self.assertEqual(len(set(source)),42)
            self.assertEqual(len(c.C35.fit_independent(
                [[x&31,x>>5,0] for x in source])),42)

    def test_entropy_choice_does_not_see_labels(self):
        hypotheses=(0,1,2,3)
        self.assertEqual(c.entropy_probe(hypotheses,[0,2],88401,3,0),0)
        self.assertEqual(c.entropy_probe(hypotheses,[1,2],88401,3,0),1)
        self.assertEqual(c.entropy_probe((),[7],88401,3,0),7)
        # A filter sees actual observed consequences, never a target oracle.
        self.assertEqual(c.filter_known(hypotheses,[(0,0)]),(0,2))
        with self.assertRaises(ValueError):
            c.filter_known(hypotheses,[(0,2)])

    def test_cold_source_memory_and_conventional_parity_dev(self):
        seed=88401
        source,initial,held,pool=c.design(seed)
        native,conventional,witnesses,pressure,proof=c.source_memory(seed,source)
        self.assertEqual(native,conventional)
        self.assertEqual(len(witnesses),3)
        self.assertEqual(len(pressure),4)
        self.assertTrue(all(proof[k] for k in
            ("cold_restore_exact","all_64_donor_readouts_retained","contradiction_atomic")))
        h=c.bitmaps(native)
        self.assertEqual(len(h),23040)
        self.assertEqual(h,c.bitmaps(conventional))

    def test_actual_six_interventions_are_held_disjoint(self):
        seed=88402
        source,initial,held,pool=c.design(seed)
        native,conventional,_,_,_=c.source_memory(seed,source)
        hypotheses=c.bitmaps(native)
        for policy in c.POLICIES:
            record=c.public_interventions(seed,3,initial,pool,policy,hypotheses,held)
            self.assertEqual(record["source_count"],16)
            self.assertEqual(len(record["initial_source"]),10)
            self.assertEqual(len(record["actions"]),6)
            self.assertEqual(len(record["source_trace"]),6)
            actual=[v[0] for v in record["actions"]]
            self.assertEqual(len(set(actual)),6)
            self.assertTrue(set(actual).issubset(set(pool)))
            self.assertFalse(set(actual)&set(held))
            self.assertEqual(len(record["forecast"]),16)
            self.assertTrue(all(0<=v<=1 for v in record["forecast"]))
            if policy=="active":
                clone=c.public_interventions(seed,3,initial,pool,policy,
                                             c.bitmaps(conventional),held)
                self.assertEqual(record,clone)
            self.assertTrue(all(v["posterior_before"]>=v["posterior_after"]
                                for v in record["source_trace"]))

    def test_full_pipeline_only_on_disjoint_dev_world(self):
        cse=c._development_fixture_or_science(88403)
        self.assertEqual(cse["source_outcomes_per_policy"],390)
        self.assertEqual(cse["donor_source_outcomes"],126)
        self.assertEqual(cse["target_source_outcomes_per_policy"],96)
        self.assertEqual(cse["pressure_source_outcomes"],168)
        self.assertEqual(len(cse["target_held_inputs"]),16)
        self.assertEqual(set(cse["policy_source_cases"]),set(c.POLICIES))
        self.assertEqual(set(cse["metrics"]),set(c.FAMILIES))
        self.assertTrue(cse["native_custody"]["cold_restore_exact"])
        for fam in c.FAMILIES:
            for policy in c.POLICIES:
                x=cse["metrics"][fam][policy]
                self.assertEqual(x["analogue"]["cases"],48)
                self.assertEqual(x["analogue"]["brier"],
                                 x["conventional_active"]["brier"])
                for arm in c.ARM_NAMES:
                    self.assertTrue(0<=x[arm]["brier"]<=1)
        for policy,custody in cse["target_native_custody"].items():
            self.assertTrue(custody["cold_exact"])

    def test_exact_frozen_go_classification_without_science_promotion(self):
        def example(seed,active=.03,random=.12,wrong=0,ood=3):
            i={"analogue":{"brier":active},
               "fixed":{"brier":random},
               "random":{"brier":random}}
            cases={p:{"analogue":{"brier":active if p=="active" else random},
                      "conventional_active":{"brier":active},
                      "native_target":{"brier":.25},
                      "target_gf2":{"brier":.25}} for p in c.POLICIES}
            ooddata={p:{"analogue":{"brier":.25 if p=="active" else .35}}
                     for p in c.POLICIES}
            return {"seed":seed,"metrics":{"isomorphic":cases,
                     "quartic_shift":ooddata},
                    "committed_coverage":{"isomorphic":{"active":{"analogue":.7}}},
                    "confident_wrong":{"isomorphic":{"active":{"analogue":0}},
                                       "quartic_shift":{"active":{"analogue":wrong}}},
                    "policy_source_cases":{"active":{
                        str(s):{"final_survivors":0 if s<6+ood else 1}
                        for s in (6,7,8)}},
                    "native_custody":{"cold_restore_exact":True,
                        "all_64_donor_readouts_retained":True,
                        "contradiction_atomic":True},
                    "target_native_custody":{p:{"cold_exact":True}
                                             for p in c.POLICIES}}
        x=example(13961);y=example(13962)
        result=c.classify([x,y])
        self.assertEqual(result["decision"],"ENGINEERING_FEASIBLE")
        self.assertFalse(result["scientific_pass"])
        self.assertEqual(c.classify([x,example(13962,active=.13)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(c.classify([x,example(13962,wrong=1)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(c.classify([x,example(13962,ood=1)])["decision"],"SCREEN_NO_GO")
        with self.assertRaises(AssertionError):
            c.classify([y,x])


if __name__=="__main__":
    unittest.main()
