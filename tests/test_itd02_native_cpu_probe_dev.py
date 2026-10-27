"""Small, offline, source-free CPU/RAM/storage qualification.

Hosted CI measurements are NOT proof of performance on retail equipment.
"""
import json
import math
import subprocess
import sys
import unittest

from yggdrasil.itd02_native_cpu_probe_dev import run_probe, MODE


class NativeCpuProbeTests(unittest.TestCase):
    def test_cpu_only_native_learning_cold_restore_accounting(self):
        result = run_probe(episodes=2, steps=2)
        self.assertEqual(result["status"], "SOURCE_FREE_DEVELOPMENT_ONLY")
        self.assertEqual(result["environment"], MODE)
        self.assertEqual(result["episodes"], 2)
        self.assertEqual(result["public_interactions"], 4)
        self.assertGreater(result["wall_ms"], 0)
        self.assertGreater(result["process_cpu_ms"], 0)
        self.assertGreater(result["interactions_per_wall_second"], 0)
        self.assertGreater(result["episode_p95_ms"], 0)
        self.assertGreater(result["cold_restore_p95_ms"], 0)
        self.assertGreater(result["durable_storage_bytes"], 0)
        self.assertGreater(result["bytes_per_interaction"], 0)
        self.assertTrue(result["gpu_required"] is False)
        self.assertTrue(result["paid_api_required"] is False)
        self.assertIsNone(result["energy_joules"])
        self.assertIsNone(result["process_tree_peak_rss_bytes"])
        self.assertFalse(result["true_retail_hardware_qualification"])
        self.assertFalse(result["authentic_original_world_executed"])
        self.assertFalse(result["independent_scientific_qualification"])
        self.assertTrue(result["original_native_parameter_changed"])
        self.assertTrue(result["native_memory_parameter_changed"])
        if result["final_peak_rss_bytes"] is not None:
            self.assertGreater(result["final_peak_rss_bytes"], 0)

    def test_invalid_budgets_rejected(self):
        for episodes, steps in ((0, 1), (33, 1), (1, 0), (1, 65),
                                (True, 1), (1, True)):
            with self.assertRaises(ValueError):
                run_probe(episodes=episodes, steps=steps)

    def test_clean_new_process_module_invocation(self):
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "yggdrasil.itd02_native_cpu_probe_dev",
             "--episodes", "2", "--steps", "2"],
            text=True, capture_output=True, timeout=30, check=True)
        result = json.loads(proc.stdout)
        self.assertEqual(result["public_interactions"], 4)
        self.assertIn("original-Yggdrasil", result["model"])
        self.assertFalse(result["authentic_original_world_executed"])


if __name__ == "__main__":
    unittest.main()
