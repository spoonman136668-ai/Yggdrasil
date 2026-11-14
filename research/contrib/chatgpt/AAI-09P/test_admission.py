"""AAI-09P exact mathematics and source contract only. No Gymnasium needed."""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import headroom as m

class ExactHeadroomTests(unittest.TestCase):
    def test_no_science_seeds_or_first_use(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-09P")
        self.assertFalse(p["future"]["scientific_first_use_authorized"])
        self.assertFalse(p["authority"]["first_use"])
        self.assertEqual(p["mechanical"]["reserved_seeds"],[887900,887901,887902,887903])
        self.assertEqual(p["analytic"]["budgets"],[0,1,2,4])
        self.assertEqual(p["upstream"]["git_sha"],m.UPSTREAM_SHA)
    def test_map_and_onehot_rewards(self):
        basis=m.source_basis()
        self.assertEqual(basis["RIGHT"]["states"],[22,13,29])
        self.assertEqual(basis["UP"]["states"],[13,20,22])
        self.assertEqual(basis["RIGHT"]["rewards"],[0,-1,-1])
        self.assertEqual(basis["UP"]["rewards"],[-1,0,0])
    def test_binomial_normalizes_and_zero_information(self):
        for laws in m.LAWS.values():
            pa,pb=laws["A"][0],laws["B"][0]
            for n in m.BUDGETS:
                for p in (pa,pb):
                    self.assertAlmostEqual(sum(m.binomial_mass(n,k,p) for k in range(n+1)),1,places=12)
                self.assertEqual(m.total_variation_binomial(n,pa,pb)==0,n==0)
            self.assertEqual(m.oracle_right(0,0,pa,pb),False)
            self.assertEqual(m.exact_condition(0,pa,pa,pb)["choose_right_prob"],0)
            self.assertEqual(m.exact_condition(0,pb,pa,pb)["choose_right_prob"],0)
    def test_transfer_predeclared_gain_not_model_success(self):
        r=m.inspect_exact()
        self.assertEqual(r["analytic_classification"],"ANALYTIC_HEADROOM_PASS_PENDING_OFFICIAL_SOURCE")
        self.assertEqual(r["worlds_executed"],0)
        self.assertFalse(r["scientific_first_use"])
        t=r["splits"]["transfer"]
        self.assertAlmostEqual(t["n2_return_gain"],.648,places=8)
        self.assertAlmostEqual(t["n2_hold_loss"],.00225,places=8)
        self.assertAlmostEqual(t["n4_return_gain"],.75816,places=8)
        self.assertAlmostEqual(t["n4_hold_loss"],.000433125,places=8)
        self.assertTrue(all(r["checks"].values()))
    def test_frozen_hypothesis_and_evaluation_fence(self):
        for fname in ("headroom.py","official_probe.py"):
            tree=ast.parse((HERE/fname).read_text(encoding="utf8"))
            disallowed={"unwrapped","get_planning_env","transition_matrix"}
            self.assertFalse(any(isinstance(x,ast.Attribute) and x.attr in disallowed for x in ast.walk(tree)))
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["parent_main"],"5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")
        self.assertTrue(p["no_post_result_tuning"])
    def test_deterministic_receipt(self):
        raw=m.deterministic_bytes(m.inspect_exact())
        self.assertEqual(raw,m.deterministic_bytes(m.inspect_exact()))
        self.assertEqual(len(hashlib.sha256(raw).hexdigest()),64)

if __name__=="__main__":
    unittest.main()
