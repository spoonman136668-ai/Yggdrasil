"""Original AAI-08B evidence tests. No scientific first use or env imports."""
import gzip
import hashlib
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parent
def get(name):
    return json.loads((ROOT/name).read_text(encoding="utf8"))

class FirstUseCustody(unittest.TestCase):
    def test_negative_frozen_result(self):
        r=get("result-summary.json")
        self.assertEqual(r["classification"],"HEADROOM_INADEQUATE_NO_PROMOTION")
        self.assertFalse(r["checks"]["benchmark_headroom"])
        self.assertFalse(r["checks"]["candidate_over_strongest"])
        self.assertFalse(r["checks"]["candidate_over_one_slot"])
        self.assertFalse(r["checks"]["intact_historical_A_retrieved"])
        self.assertFalse(r["checks"]["shuffled_negative"])
        self.assertFalse(r["checks"]["learner_compute"])
        self.assertTrue(r["checks"]["cold_forks_exact"])
        self.assertTrue(r["checks"]["zero_probe_no_information"])
        self.assertEqual(r["integration"],"NONE")

    def test_byte_exact_original_and_full_worlds(self):
        p=get("provenance.json")
        raw=gzip.decompress((ROOT/"primary-original.json.gz").read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p["original_raw_json_sha256"])
        first=json.loads(raw)
        self.assertEqual(first["raw_worlds_sha256"],get("result-summary.json")["raw_worlds_sha256"])
        self.assertEqual({k:len(v) for k,v in first["world_records"].items()},
                         {"dev":16,"transfer":64,"negative":32})

    def test_first_use_is_once_and_original_source_unchanged(self):
        p=get("provenance.json")
        self.assertEqual(p["original_first_use_run"],43623979846)
        self.assertEqual(p["original_first_use_attempt"],1)
        self.assertTrue(p["source_preserved"])
        self.assertTrue(p["authorized_first_use"])
        self.assertEqual(p["first_uses_executed"],1)
        self.assertEqual(p["model_integration"],"NONE")
        self.assertFalse(p["native_model_changed"])

    def test_failed_quantitative_claims(self):
        x=get("result-summary.json")["primary_gains"]
        self.assertLess(x["candidate_minus_strongest"],0)
        self.assertLess(x["candidate_minus_one_slot"],0)
        self.assertLess(x["candidate_intact_A_retrieval_rate"],.60)
        self.assertLess(x["return_A_candidate_accuracy"],.80)
        self.assertGreater(x["candidate_to_fastest_model_time_ratio"],2.)

if __name__=="__main__":
    unittest.main()
