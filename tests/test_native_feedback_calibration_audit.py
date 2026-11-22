"""Independent proper-score, source-equation and checkpoint-negative checks."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr30_test_audit",
 ROOT/"research/contrib/chatgpt/NKR-30/audit.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class FeedbackCalibrationTests(unittest.TestCase):
    def test_nominal_marginals_reproduce_published_boolean_source(self):
        k=audit.kernel()
        for state in (0,1):
            for action in (0,1):
                self.assertEqual(k[state,action][0],Fraction(41 if state==action else 9,50))
                self.assertEqual(k[state,action][1],Fraction(41 if state==action==0 else 9,50))

    def test_expected_brier_exact_noise_and_calibration_decomposition(self):
        for p in (Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(1)):
            for q in (Fraction(9,50),Fraction(41,50)):
                loss,floor,excess=audit.risk(p,q)
                self.assertEqual(loss,floor+excess)
                self.assertGreaterEqual(loss,audit.risk(q,q)[0])
        with self.assertRaises(ValueError): audit.risk(Fraction(2),Fraction(1,2))

    def test_hash_integrity_and_malformed_checkpoints_are_rejected(self):
        raw=audit.PublicCausalCells().snapshot()
        with self.assertRaises(ValueError):
            audit.inspect_checkpoint(raw.hex(),"0"*64,audit.kernel())
        altered=raw[:-1]+bytes([raw[-1]^1])
        with self.assertRaises(ValueError):
            audit.inspect_checkpoint(altered.hex(),audit.sha(altered),audit.kernel())
        with self.assertRaises(ValueError):
            audit.inspect_checkpoint("garbage",audit.sha(raw),audit.kernel())

    def test_unknown_native_bank_has_chance_risk_and_stays_unchanged(self):
        bank=audit.PublicCausalCells();raw=bank.snapshot()
        r=audit.inspect_checkpoint(raw.hex(),audit.sha(raw),audit.kernel())
        self.assertEqual(audit.fraction(r["expected_brier"]),Fraction(1,4))
        self.assertEqual(audit.fraction(r["irreducible_noise_floor"]),Fraction(369,2500))
        self.assertEqual(r["scored_conditions"],32)
        self.assertEqual(bank.snapshot(),raw)

if __name__=="__main__": unittest.main()
