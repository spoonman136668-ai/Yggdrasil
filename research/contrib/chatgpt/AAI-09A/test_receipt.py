"""AAI-09A exact-source CI receipt, tests only. No external import or science."""
import json
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
class QualReceipt(unittest.TestCase):
    def test_expected_original_source(self):
        p=json.loads((HERE/"qualification.json").read_text(encoding="utf8"))
        self.assertEqual(p["prereg_commit"],"d9e9f3f11d04cdcf99c5e5b1e0c7a5008e0c2026")
        self.assertEqual(p["mechanical_source_head"],"116f4d5f31a5d82e6ec88b648611b6ed94921661")
        self.assertEqual(p["upstream_sha"],"127df4b714fe4fcf680721d8e9278a96090acd7e")
    def test_two_os_identical_real_transitions(self):
        p=json.loads((HERE/"qualification.json").read_text(encoding="utf8"))
        result=p["both_os"]
        self.assertEqual(result["linux"]["trace"],result["windows"]["trace"])
        self.assertEqual(result["linux"]["focused"],"15/15")
        self.assertEqual(result["windows"]["focused"],"15/15")
        self.assertEqual(result["linux"]["actual_official_cases"],"24/24")
        self.assertEqual(result["windows"]["actual_official_cases"],"24/24")
    def test_no_scientific_first_use_or_promotion(self):
        p=json.loads((HERE/"qualification.json").read_text(encoding="utf8"))
        self.assertFalse(p["scientific_first_use_executed"])
        self.assertFalse(p["scientific_first_use_authorized"])
        self.assertEqual(p["scientific_cohorts_executed"],0)
        self.assertEqual(p["integration"],"NONE")
        self.assertEqual(p["merge"],"NONE")
        self.assertTrue(p["native_owner_model_unchanged"])
if __name__=="__main__":unittest.main()
