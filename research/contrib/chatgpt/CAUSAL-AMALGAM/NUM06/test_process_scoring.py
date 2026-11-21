"""Cold-process and resource-accounting checks, no registered realization."""
import unittest
from numerical_source import RESERVED
from numerical_scoring import ARM_NAMES, score_arm_fixture
from process_scoring import score_process_fixture, _worker, _restore


class ProcessScoringTests(unittest.TestCase):
    def test_all_arms_cold_process_match(self):
        for name in ARM_NAMES:
            with self.subTest(arm=name):
                a=score_arm_fixture(620001,name)
                b=score_process_fixture(620001,name)
                self.assertTrue(b["cold_exact"])
                self.assertNotEqual(*b["cold_process_ids"])
                for key in ("source_sha256","witness_count","full_mse","late_mse",
                            "return_mse","pooled_mse","final_state_bytes","cold_state_bytes"):
                    self.assertEqual(a[key] if key!="cold_state_bytes" else a["cold_bytes"],b[key],key)
                self.assertGreater(b["peak_rss_bytes"],0)
                self.assertGreater(b["worker_cpu_ns"],0)
                self.assertGreaterEqual(b["restore_cpu_ns"],0)
                self.assertFalse(b["resource_qualification"])
                self.assertFalse(b["scientific_gain_verified"])

    def test_reserved_seed_denied_before_worker(self):
        for seed in RESERVED:
            with self.assertRaisesRegex(ValueError,"RESERVED_DENIED"):
                score_process_fixture(seed,"candidate")
            with self.assertRaisesRegex(ValueError,"RESERVED_DENIED"):
                _worker({"seed":seed})

    def test_invalid_restore_and_oracle_arm(self):
        with self.assertRaisesRegex(ValueError,"COLD_HASH"):
            _restore("candidate",(.02,.04,.5),b"{}","0"*64)
        with self.assertRaisesRegex(ValueError,"PROCESS_ARM"):
            score_process_fixture(620001,"oracle")

if __name__=="__main__":
    unittest.main()
