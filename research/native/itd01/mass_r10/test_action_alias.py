"""Falsify unsupported scientific claims with exact deterministic checks."""
import unittest
from fractions import Fraction as F
from action_alias import BUDGET, CASES, risk, allocation, minimax, audit

class FiniteActionProof(unittest.TestCase):
    def test_zero_observations(self):
        for p,q in CASES.values():
            self.assertEqual(risk(0,p,q),F(1,2))
    def test_equal_laws_identical_after_any_budget(self):
        for n in range(33):
            self.assertEqual(risk(n,F(1,2),F(1,2)),F(1,2))
    def test_world_exchange_symmetric(self):
        for p,q in CASES.values():
            for n in (1,8,16,32):
                self.assertEqual(risk(n,p,q),risk(n,q,p))
    def test_one_address_can_be_noninformative(self):
        for p,q in CASES.values():
            self.assertEqual(allocation(32,0,p,q),F(1,2))
    def test_all_33_fixed_allocations_and_budget(self):
        for p,q in CASES.values():
            result=minimax(p,q)
            self.assertEqual(result["allocation"],[16,16])
            self.assertEqual(result["enumerated_allocations"],33)
            self.assertEqual(result["worst_risk"],min(
                allocation(n,32-n,p,q) for n in range(33)))
            self.assertGreaterEqual(result["worst_risk"],result["known_address_risk"])
    def test_advisory_only_strong_feasible(self):
        for label,(p,q) in CASES.items():
            self.assertEqual(minimax(p,q)["worst_risk"]<=F(1,20),label=="STRONG")
    def test_invalid_arguments_fail_closed(self):
        for n,p,q in ((-1,F(1,2),F(1,2)),(32,F(-1,4),F(1,2)),(32,F(1,2),F(5,4))):
            with self.assertRaises(ValueError):risk(n,p,q)
        with self.assertRaises(TypeError):risk(32,.3,F(1,2))
        for n0,n1 in ((-1,33),(16,15),(33,-1)):
            with self.assertRaises(ValueError):allocation(n0,n1,F(1,4),F(3,4))
    def test_never_claim_source_or_controller_admission(self):
        r=audit()
        self.assertFalse(r["source_generator_created"])
        self.assertFalse(r["scientific_first_use"])
        self.assertEqual(r["sampled_rows"],0)
        self.assertEqual(r["actual_r10_source_certificate"],"NOT_ESTABLISHED")
        self.assertEqual(r["ckb_admission"],"NOT_OBSERVED")
        self.assertTrue(r["fixed_nonadaptive_only"])
        self.assertEqual(r["budget"],BUDGET)

if __name__=="__main__":
    unittest.main()
