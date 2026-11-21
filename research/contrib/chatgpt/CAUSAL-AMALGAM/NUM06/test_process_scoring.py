"""Cold-process and resource-accounting checks, no registered realization."""
import unittest
from numerical_source import RESERVED
from numerical_scoring import ARM_NAMES, score_arm_fixture
from process_scoring import (score_process_fixture, _worker, _restore,
                             _cpu_status, _check_head_accounting)


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
                for key in ("full_head_mse","late_head_mse","return_head_mse","pooled_head_mse"):
                    for head in ("delta_x","delta_y","reward"):
                        self.assertAlmostEqual(a[key][head],b[key][head],places=12)
                self.assertGreater(b["peak_rss_bytes"],0)
                self.assertGreaterEqual(b["worker_cpu_ns"],0)
                self.assertEqual(b["worker_cpu_status"],_cpu_status(b["worker_cpu_ns"]))
                self.assertGreater(b["cpu_reported_resolution_ns"],0)
                self.assertGreater(b["worker_wall_ns"],0)
                self.assertGreaterEqual(b["elapsed_wall_ns"],b["worker_wall_ns"])
                for k in ("predict_cpu_ns","observe_cpu_ns","restore_cpu_ns"):
                    self.assertGreaterEqual(b[k],0)
                    self.assertEqual(b["cpu_component_status"][k],_cpu_status(b[k]))
                self.assertFalse(b["resource_qualification"])
                self.assertFalse(b["scientific_gain_verified"])

    def test_timer_quantization_is_not_a_zero_cost_claim(self):
        self.assertEqual(_cpu_status(0),"BELOW_TIMER_DETECTION")
        self.assertEqual(_cpu_status(100),"OBSERVED_NONZERO")
        for bad in (-1,False,0.5,None):
            with self.assertRaisesRegex(ValueError,"CPU_COUNTER_INVALID"):
                _cpu_status(bad)


    def test_head_accounting_tampering_denied(self):
        _check_head_accounting([.1],[[.1,.1,.1]])
        for aggregate,heads in (([.1],[[.1,.1,.5]]),
                                ([.1],[[.1,.1]]),
                                ([.1],[[.1,.1,float("nan")]]),
                                ([],[]),([.1,.2],[[.1,.1,.1]])):
            with self.assertRaisesRegex(ValueError,"NUM06_HEAD_ACCOUNTING"):
                _check_head_accounting(aggregate,heads)

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
