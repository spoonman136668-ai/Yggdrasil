"""AAI-09P receipt verification only. No scientific seed consumption."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
HOME=Path(__file__).resolve().parent
sys.path.insert(0,str(HOME))
from headroom import inspect_exact,deterministic_bytes

class AdmissionReceipt(unittest.TestCase):
    def test_two_os_mechanical_identical(self):
        r=json.loads((HOME/"qualification.json").read_text(encoding="utf8"))
        self.assertEqual(r["linux"]["analytic_tests"],"6/6")
        self.assertEqual(r["windows"]["analytic_tests"],"6/6")
        self.assertEqual(r["linux"]["official_cases"],"24/24")
        self.assertEqual(r["windows"]["official_cases"],"24/24")
        self.assertEqual(r["linux"]["official_trace"],r["windows"]["official_trace"])
        self.assertEqual(r["linux"]["receipt"],r["windows"]["receipt"])
    def test_exact_independent_math_receipt(self):
        r=json.loads((HOME/"qualification.json").read_text(encoding="utf8"))
        outcome=inspect_exact()
        self.assertEqual(r["linux"]["receipt"],hashlib.sha256(deterministic_bytes(outcome)).hexdigest())
        self.assertEqual(outcome["analytic_classification"],"ANALYTIC_HEADROOM_PASS_PENDING_OFFICIAL_SOURCE")
        self.assertTrue(all(outcome["checks"].values()))
        self.assertEqual(r["classification"],"ANALYTIC_HEADROOM_ADMITTED_MECHANICAL_ONLY")
    def test_frozen_threshold_and_baseline(self):
        p=json.loads((HOME/"prereg.json").read_text(encoding="utf8"))
        r=json.loads((HOME/"qualification.json").read_text(encoding="utf8"))
        t=r["transfer_analytic"]
        self.assertGreaterEqual(t["oracle_return_gain_n2"],p["thresholds"]["oracle_return_gain_at_n2_min"])
        self.assertGreaterEqual(t["oracle_return_gain_n4"],p["thresholds"]["oracle_return_gain_at_n4_min"])
        self.assertLessEqual(t["oracle_B_continues_loss_n2"],p["thresholds"]["oracle_B_hold_loss_at_n2_max"])
        self.assertLessEqual(t["oracle_B_continues_loss_n4"],p["thresholds"]["oracle_B_hold_loss_at_n4_max"])
        self.assertEqual(r["prereg_commit"],"f19dd32f20bf05ae5e72fc913303843050a9217d")
    def test_no_model_or_owner_promotion(self):
        p=json.loads((HOME/"prereg.json").read_text(encoding="utf8"))
        r=json.loads((HOME/"qualification.json").read_text(encoding="utf8"))
        self.assertFalse(p["authority"]["first_use"])
        self.assertFalse(p["future"]["scientific_first_use_authorized"])
        self.assertTrue(r["no_scientific_first_use"])
        self.assertTrue(r["no_model_native_or_controller_changes"])
        self.assertTrue(r["no_merge_or_promotion"])

if __name__=="__main__":
    unittest.main()
