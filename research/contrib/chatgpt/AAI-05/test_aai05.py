"""AAI-05 tests on reserved mechanical seeds only: no scientific first use."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("aai05",ROOT/"run.py")
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class MotifTests(unittest.TestCase):
    def test_disjoint_worlds_and_operators(self):
        self.assertTrue(a.audit())
        self.assertEqual(len(set(a.DEV)|set(a.TRANSFER)|set(a.NEGATIVE)),256)
        self.assertEqual({rid%4 for seed in (900000,900005,900010)
                          for rid in a.rule_ids(a.world(seed,False))}.issubset({0,1}),True)
        self.assertEqual({rid%4 for seed in (900001,900003,900011)
                          for rid in a.rule_ids(a.world(seed,True))}.issubset({2,3}),True)

    def test_causal_interventions_withheld_states(self):
        w=a.world(900000)
        obs,tasks=a.data_for(w)
        self.assertEqual(len(obs),16)
        self.assertEqual(len(tasks),12)
        self.assertFalse(set(e["state"] for e in obs)&set(state for state,_ in tasks))
        self.assertTrue(all("law" not in e for e in obs))

    def test_rule_catalog(self):
        self.assertEqual(len(a.RULES),60)
        bits=a.input_bits(13,2)
        for index in range(60):
            self.assertIn(a.apply_rule(index,bits),(0,1))

    def test_retention_and_negative_shuffled(self):
        w=a.world(900001,True)
        obs,tasks=a.data_for(w)
        for method in ("direct","bayes","logistic","cart","lookup","shuffled"):
            fitted=a.train(method,obs,w["seed"])
            encoded=a.serialize(fitted)
            self.assertEqual(json.loads(encoded),fitted)
            result1=a.terminal_reward(w,method,fitted,tasks)
            result2=a.terminal_reward(w,method,json.loads(encoded),tasks)
            self.assertEqual(result1,result2)
            self.assertLessEqual(result1[0],1)

    def test_interference_no_mutation(self):
        out=a.one_world(900002,True,("direct","bayes","logistic","cart","lookup"))
        self.assertTrue(all(v["cold_restored"] and v["interference_restored"] for v in out.values()))

    def test_commit_and_budget(self):
        self.assertEqual(a.PREREG,"d417e2aff50db08d2b12af7d02ced094d17983cc")
        self.assertEqual((a.PROBES,a.TASKS,a.LOGISTIC_EPOCHS),(16,12,300))
        self.assertEqual(a.BOOTSTRAP,1024)


if __name__=="__main__":
    unittest.main()
