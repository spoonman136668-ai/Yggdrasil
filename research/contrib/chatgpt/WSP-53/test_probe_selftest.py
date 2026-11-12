"""WSP53 multi-arm engineering SELFTEST only: *not* DEV or PRIMARY."""
import json
import unittest
from probe_selftest import run_selftest

class ProbeContracts(unittest.TestCase):
    def test_all_selftest_worlds_same_charged_budget(self):
        receipts=[]
        for family in ("anchored_effect","noncommuting_order"):
            for seed in (9901,9902):
                for encoding in ("identity","permuted","rotated"):
                    with self.subTest(family=family,seed=seed,encoding=encoding):
                        data=run_selftest(family=family,seed=seed,encoding=encoding)
                        self.assertEqual(data["source"]["charged_actions"],60)
                        self.assertFalse(data["development_admitted"])
                        self.assertFalse(data["comparators_qualified"])
                        self.assertFalse(data["protected_primary_used"])
                        self.assertFalse(data["conventional_fully_trained"])
                        for name,arm in data["arms"].items():
                            self.assertEqual(arm["actions"],60)
                            self.assertEqual(arm["a"]["total"],48)
                            self.assertEqual(arm["b"]["total"],84)
                            self.assertEqual(arm["a_retained"]["total"],48)
                            if name!="erase":
                                self.assertTrue(arm["cold_restore_parity"])
                        receipts.append({
                            "family":family,"seed":seed,"encoding":encoding,
                            "source_hash":data["source"]["phase_a"][1],
                            "scores":{name:{
                                "a":v["a"]["correct"],"b":v["b"]["correct"],
                                "retained":v["a_retained"]["correct"],
                                "wrong_b":v["b"]["wrong_confident"]}
                                for name,v in data["arms"].items()},
                            "conventional_loss":data["arms"]["conventional_smoke"]["train_diagnostic"]["loss"]
                        })
        print("WSP53_SELFTEST_DIAGNOSTIC "+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_reject_non_fixture_seeds_and_bad_families(self):
        for seed in (3101,5101,True):
            with self.assertRaises(PermissionError):
                run_selftest(family="anchored_effect",seed=seed,encoding="identity")
        with self.assertRaises(PermissionError):
            run_selftest(family="unknown",seed=9901,encoding="identity")

if __name__=="__main__":
    unittest.main()
